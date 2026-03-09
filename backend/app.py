"""
AI Course Advisor - Full Stack Backend
Flask API with PostgreSQL database, authentication, and intelligent recommendations
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from models import db, Course, Student, StudentCourse
from services import get_degree_progress, get_recommendations

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


# ============ Auth Routes ============

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'error': 'Email, password, and name required'}), 400
    
    if Student.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    student = Student(
        email=data['email'],
        name=data['name'],
        major=data.get('major', 'Computer Science'),
        year=data.get('year', 'Sophomore'),
        interests=data.get('interests', []),
        career_goals=data.get('careerGoals', '')
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
    if data.get('major'): student.major = data['major']
    if data.get('year'): student.year = data['year']
    if data.get('interests') is not None: student.interests = data['interests']
    if data.get('careerGoals') is not None: student.career_goals = data['careerGoals']
    
    # Update courses
    if data.get('completedCourses') is not None:
        StudentCourse.query.filter_by(student_id=student.id, status='completed').delete()
        for cid in data['completedCourses']:
            if Course.query.get(cid):
                db.session.add(StudentCourse(student_id=student.id, course_id=cid, status='completed'))
    if data.get('currentCourses') is not None:
        StudentCourse.query.filter_by(student_id=student.id, status='current').delete()
        for cid in data['currentCourses']:
            if Course.query.get(cid):
                db.session.add(StudentCourse(student_id=student.id, course_id=cid, status='current'))
    
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
    return jsonify({'recommendations': recommendations})


@app.route('/api/progress', methods=['GET'])
def progress():
    student = get_current_student()
    if not student:
        return jsonify({'error': 'Not authenticated'}), 401
    
    progress_data = get_degree_progress(student)
    return jsonify(progress_data)


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
