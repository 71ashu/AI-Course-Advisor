"""Seed database with sample courses and sample student data."""
from app import app
from models import db, Course, Student, StudentCourse

COURSES = [
    {"id": "CS101", "name": "Introduction to Computer Science", "units": 3, "difficulty": "beginner",
     "prerequisites": [], "description": "Fundamental concepts of computer science including programming basics, algorithms, and problem-solving.",
     "topics": ["programming", "algorithms", "problem-solving"], "department": "Computer Science"},
    {"id": "CS201", "name": "Data Structures and Algorithms", "units": 4, "difficulty": "intermediate",
     "prerequisites": ["CS101"], "description": "In-depth study of fundamental data structures and algorithms, analysis of complexity.",
     "topics": ["data structures", "algorithms", "complexity analysis"], "department": "Computer Science"},
    {"id": "CS301", "name": "Machine Learning", "units": 3, "difficulty": "advanced",
     "prerequisites": ["CS201", "MATH200"], "description": "Introduction to machine learning algorithms, supervised and unsupervised learning, neural networks.",
     "topics": ["machine learning", "neural networks", "AI"], "department": "Computer Science"},
    {"id": "CS350", "name": "Web Development", "units": 3, "difficulty": "intermediate",
     "prerequisites": ["CS101"], "description": "Full-stack web development including HTML, CSS, JavaScript, and modern frameworks.",
     "topics": ["web development", "frontend", "backend"], "department": "Computer Science"},
    {"id": "CS250", "name": "Database Systems", "units": 3, "difficulty": "intermediate",
     "prerequisites": ["CS201"], "description": "Database design, SQL, normalization, and transaction management.",
     "topics": ["databases", "SQL", "data management"], "department": "Computer Science"},
    {"id": "MATH100", "name": "Calculus I", "units": 4, "difficulty": "beginner",
     "prerequisites": [], "description": "Limits, derivatives, and integrals of single-variable functions.",
     "topics": ["calculus", "mathematics"], "department": "Mathematics"},
    {"id": "MATH200", "name": "Linear Algebra", "units": 3, "difficulty": "intermediate",
     "prerequisites": ["MATH100"], "description": "Vectors, matrices, eigenvalues, and applications.",
     "topics": ["linear algebra", "mathematics"], "department": "Mathematics"},
    {"id": "ENG101", "name": "English Composition", "units": 3, "difficulty": "beginner",
     "prerequisites": [], "description": "Academic writing, research, and critical analysis.",
     "topics": ["writing", "communication"], "department": "English"},
    {"id": "PHY101", "name": "Physics I", "units": 4, "difficulty": "intermediate",
     "prerequisites": ["MATH100"], "description": "Mechanics, thermodynamics, and waves.",
     "topics": ["physics", "mechanics"], "department": "Physics"},
]

GRADE_BY_COURSE = {
    "CS101": ("A-", 3.7, 92.0),
    "CS201": ("B+", 3.3, 88.0),
    "MATH100": ("A", 4.0, 95.0),
    "MATH200": ("A-", 3.7, 91.0),
    "ENG101": ("A", 4.0, 94.0),
    "PHY101": ("B", 3.0, 84.0),
}

SPECIAL_STUDENT_PREFILLS = {
    # Add per-user seed prefills here if needed.
}


def _calculate_program_gpa(student):
    completed = StudentCourse.query.filter_by(student_id=student.id, status='completed').all()
    total_units = 0
    total_quality_points = 0.0

    for enrollment in completed:
        per_course_gpa = enrollment.course_gpa if enrollment.course_gpa is not None else enrollment.grade_points
        if per_course_gpa is None:
            continue
        course = db.session.get(Course, enrollment.course_id)
        if not course:
            continue
        total_units += course.units or 0
        total_quality_points += per_course_gpa * (course.units or 0)

    if total_units == 0:
        return 0.0
    return round(total_quality_points / total_units, 2)


def prefill_student_grades(email):
    """Prefill student course grades and computed GPA for an existing user."""
    student = Student.query.filter_by(email=email).first()
    if not student:
        print(f'No student found for {email}; skipping prefill.')
        return

    special_prefill = SPECIAL_STUDENT_PREFILLS.get(email)
    if special_prefill:
        for field_name, field_value in special_prefill['profile'].items():
            setattr(student, field_name, field_value)

        StudentCourse.query.filter_by(student_id=student.id).delete()

        for course_id in special_prefill['completed_courses']:
            if db.session.get(Course, course_id):
                db.session.add(
                    StudentCourse(student_id=student.id, course_id=course_id, status='completed')
                )
        for course_id in special_prefill['current_courses']:
            if db.session.get(Course, course_id):
                db.session.add(
                    StudentCourse(student_id=student.id, course_id=course_id, status='current')
                )
        db.session.flush()
        enrollments = StudentCourse.query.filter_by(student_id=student.id).all()
        grade_by_course = special_prefill['grades']
    else:
        enrollments = StudentCourse.query.filter_by(student_id=student.id).all()
        if not enrollments:
            for course_id in ['CS101', 'CS201', 'MATH100', 'MATH200', 'ENG101']:
                if db.session.get(Course, course_id):
                    db.session.add(
                        StudentCourse(student_id=student.id, course_id=course_id, status='completed')
                    )
            if db.session.get(Course, 'PHY101'):
                db.session.add(StudentCourse(student_id=student.id, course_id='PHY101', status='current'))
            db.session.flush()
            enrollments = StudentCourse.query.filter_by(student_id=student.id).all()
        grade_by_course = GRADE_BY_COURSE

    for enrollment in enrollments:
        grade_tuple = grade_by_course.get(enrollment.course_id)
        if not grade_tuple:
            continue
        enrollment.final_letter = grade_tuple[0]
        enrollment.course_gpa = grade_tuple[1]
        enrollment.grade_points = grade_tuple[1]
        enrollment.final_score = grade_tuple[2]

    student.program_gpa = _calculate_program_gpa(student)
    db.session.commit()
    print(f'Prefilled grades for {email}; program GPA = {student.program_gpa}')


def seed():
    with app.app_context():
        for c in COURSES:
            if not db.session.get(Course, c['id']):
                db.session.add(Course(**c))
        
        # Demo student
        demo = Student.query.filter_by(email='alex@demo.edu').first()
        if not demo:
            demo = Student(
                email='alex@demo.edu',
                name='Alex Johnson',
                university='Santa Clara University',
                program_enrolled='MS Computer Science and Engineering',
                major='Computer Science',
                year='Junior',
                interests=['AI', 'Web Development', 'Machine Learning'],
                career_goals='Software Engineer at a tech company'
            )
            demo.set_password('demo123')
            db.session.add(demo)
            db.session.commit()
            
            for cid in ['CS101', 'CS201', 'MATH100', 'MATH200', 'ENG101']:
                db.session.add(StudentCourse(student_id=demo.id, course_id=cid, status='completed'))
            db.session.add(StudentCourse(student_id=demo.id, course_id='PHY101', status='current'))
        
        db.session.commit()
        print('Database seeded successfully!')
        print('Demo login: alex@demo.edu / demo123')

if __name__ == '__main__':
    seed()
