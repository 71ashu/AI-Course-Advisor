"""
AI Course Advisor - Full Stack Backend
Flask API with PostgreSQL database, authentication, and intelligent recommendations.
Features: knowledge graph, collaborative filtering, GPA prediction,
explainability, and cold start handling.
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from models import db, Course, Program, ProgramCourse, Student, StudentCourse
from services import get_degree_progress, get_recommendations
from llm import get_advisory_message
from knowledge_graph import get_path_to_course, get_graph_summary

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, supports_credentials=True, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
db.init_app(app)
migrate = Migrate(app, db)


def get_current_student():
    """Get currently logged-in student from session."""
    student_id = session.get('student_id')
    if student_id:
        return Student.query.get(student_id)
    return None


def _normalize_course_input(item):
    """Normalize course payload from string id or object."""
    if isinstance(item, str):
        return item, {}, False

    if not isinstance(item, dict):
        return None, {}, False

    course_id = item.get('courseId') or item.get('course_id') or item.get('id')
    updates = {}
    has_grade_payload = False

    if 'finalScore' in item or 'final_score' in item:
        updates['final_score'] = item.get('finalScore', item.get('final_score'))
        has_grade_payload = True
    if 'finalLetter' in item or 'final_letter' in item:
        updates['final_letter'] = item.get('finalLetter', item.get('final_letter'))
        has_grade_payload = True
    if 'courseGPA' in item or 'course_gpa' in item:
        updates['course_gpa'] = item.get('courseGPA', item.get('course_gpa'))
        has_grade_payload = True
    if 'gradePoints' in item or 'grade_points' in item:
        updates['grade_points'] = item.get('gradePoints', item.get('grade_points'))
        has_grade_payload = True

    if 'course_gpa' in updates and 'grade_points' not in updates:
        updates['grade_points'] = updates['course_gpa']
    if 'grade_points' in updates and 'course_gpa' not in updates:
        updates['course_gpa'] = updates['grade_points']

    return course_id, updates, has_grade_payload


def _sync_student_courses(student_id, status, course_items):
    """Upsert enrollments for one status while preserving existing grades."""
    existing = StudentCourse.query.filter_by(student_id=student_id, status=status).all()
    by_course_id = {row.course_id: row for row in existing}

    desired_ids = set()
    for item in course_items:
        course_id, updates, has_grade_payload = _normalize_course_input(item)
        if not course_id:
            continue
        if not Course.query.get(course_id):
            continue

        desired_ids.add(course_id)
        enrollment = by_course_id.get(course_id)
        if not enrollment:
            enrollment = StudentCourse(student_id=student_id, course_id=course_id, status=status)
            db.session.add(enrollment)

        if has_grade_payload:
            for field_name, value in updates.items():
                setattr(enrollment, field_name, value)

    for row in existing:
        if row.course_id not in desired_ids:
            db.session.delete(row)


# ============ Auth Routes ============

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    if (
        not data
        or not data.get('email')
        or not data.get('password')
        or not data.get('name')
        or not data.get('university')
        or not data.get('program')
    ):
        return jsonify({'error': 'Email, password, name, university, and program are required'}), 400
    
    if Student.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    student = Student(
        email=data['email'],
        name=data['name'],
        university=data['university'],
        program_enrolled=data['program'],
        major=data.get('major', 'Computer Science'),
        year=data.get('year', 'Sophomore'),
        interests=data.get('interests', []),
        career_goals=data.get('careerGoals', ''),
    )
    student.set_password(data['password'])
    db.session.add(student)
    db.session.commit()
    
    session.permanent = True
    session['student_id'] = student.id
    return jsonify({'student': student.to_dict()})


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    student = Student.query.filter_by(email=data['email']).first()
    if not student or not student.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    session.permanent = True
    session['student_id'] = student.id
    return jsonify({'student': student.to_dict()})


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('student_id', None)
    return jsonify({'success': True})


@app.route('/api/auth/me', methods=['GET'])
def me():
    student = get_current_student()
    if not student:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({'student': student.to_dict()})


# ============ Profile Routes ============

@app.route('/api/profile', methods=['GET', 'PUT'])
def profile():
    student = get_current_student()
    if not student:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if request.method == 'GET':
        return jsonify({'student': student.to_dict()})
    
    data = request.json
    if data.get('name'): student.name = data['name']
    if data.get('university'): student.university = data['university']
    if data.get('program'): student.program_enrolled = data['program']
    if data.get('major'): student.major = data['major']
    if data.get('year'): student.year = data['year']
    if data.get('interests') is not None: student.interests = data['interests']
    if data.get('careerGoals') is not None: student.career_goals = data['careerGoals']
    
    if data.get('completedCourses') is not None:
        _sync_student_courses(student.id, 'completed', data['completedCourses'])
    if data.get('currentCourses') is not None:
        _sync_student_courses(student.id, 'current', data['currentCourses'])
    
    db.session.commit()
    return jsonify({'student': student.to_dict()})


# ============ Course Routes ============

@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify({'courses': [c.to_dict() for c in courses]})


# ============ Advisor Routes ============

@app.route('/api/recommend', methods=['POST'])
def recommend():
    student = get_current_student()
    if not student:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json or {}
    query = data.get('query', '')

    recommendations = get_recommendations(student, query)
    message = get_advisory_message(student, query, recommendations)
    return jsonify({'recommendations': recommendations, 'message': message})


@app.route('/api/progress', methods=['GET'])
def progress():
    student = get_current_student()
    if not student:
        return jsonify({'error': 'Not authenticated'}), 401
    
    progress_data = get_degree_progress(student)
    return jsonify(progress_data)


# ============ Prerequisite Graph Routes ============

@app.route('/api/prerequisite-path', methods=['GET'])
def prerequisite_path():
    target = request.args.get('target')
    if not target:
        return jsonify({'error': 'target query parameter is required'}), 400

    course = Course.query.get(target)
    if not course:
        return jsonify({'error': f'Course {target} not found'}), 404

    student = get_current_student()
    completed_ids = set()
    if student:
        completed_ids = set(
            sc.course_id for sc in
            StudentCourse.query.filter_by(student_id=student.id, status='completed').all()
        )

    path = get_path_to_course(completed_ids, target)
    path_details = []
    for cid in path:
        c = Course.query.get(cid)
        if c:
            path_details.append({
                'courseId': c.id,
                'courseName': c.name,
                'completed': cid in completed_ids,
            })

    return jsonify({'target': target, 'path': path_details})


@app.route('/api/prerequisite-graph', methods=['GET'])
def prerequisite_graph():
    return jsonify(get_graph_summary())


# ============ Onboarding Routes ============

@app.route('/api/onboarding', methods=['POST'])
def onboarding():
    """Process onboarding quiz answers for cold-start users."""
    student = get_current_student()
    if not student:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.json or {}

    interests = data.get('interests', [])
    if interests:
        student.interests = interests

    career_goals = data.get('careerGoals', '')
    if career_goals:
        student.career_goals = career_goals

    experience_level = data.get('experienceLevel', '')
    if experience_level:
        existing_interests = student.interests or []
        if experience_level == 'beginner' and 'Programming Fundamentals' not in existing_interests:
            student.interests = existing_interests + ['Programming Fundamentals']

    student.onboarding_completed = True
    db.session.commit()

    return jsonify({'student': student.to_dict()})


# ============ Program Routes ============

@app.route('/api/programs', methods=['GET'])
def get_programs():
    query = Program.query

    degree_type = request.args.get('degree_type')
    if degree_type:
        query = query.filter(Program.degree_type.ilike(f'%{degree_type}%'))

    department = request.args.get('department')
    if department:
        query = query.filter(Program.department.ilike(f'%{department}%'))

    programs = query.order_by(Program.program_name).all()
    return jsonify({'programs': [p.to_dict() for p in programs]})


@app.route('/api/programs/<string:program_id>', methods=['GET'])
def get_program(program_id):
    program = Program.query.get_or_404(program_id)

    linked_courses = (
        db.session.query(Course)
        .join(ProgramCourse, ProgramCourse.course_id == Course.id)
        .filter(ProgramCourse.program_id == program_id)
        .all()
    )

    result = program.to_dict()
    result['courses'] = [c.to_dict() for c in linked_courses]
    return jsonify(result)


# ============ Health ============

@app.route('/api/health', methods=['GET'])
def health():
    try:
        db.session.execute(db.text('SELECT 1'))
        db_status = 'connected'
    except Exception:
        db_status = 'disconnected'
    return jsonify({'status': 'healthy', 'database': db_status})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
