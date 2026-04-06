"""Seed database with sample courses, demo user, and synthetic students for collaborative filtering."""
import random
from app import app
from models import db, Course, Student, StudentCourse

COURSES = [
    {
        "id": "CS101", "name": "Introduction to Computer Science", "units": 3, "difficulty": "beginner",
        "prerequisites": [],
        "description": "Fundamental concepts of computer science including programming basics, algorithms, and problem-solving.",
        "topics": ["programming", "algorithms", "problem-solving"], "department": "Computer Science",
    },
    {
        "id": "CS201", "name": "Data Structures and Algorithms", "units": 4, "difficulty": "intermediate",
        "prerequisites": ["CS101"],
        "description": "In-depth study of fundamental data structures and algorithms, analysis of complexity.",
        "topics": ["data structures", "algorithms", "complexity analysis"], "department": "Computer Science",
    },
    {
        "id": "CS301", "name": "Machine Learning", "units": 3, "difficulty": "advanced",
        "prerequisites": ["CS201", "MATH200"],
        "description": "Introduction to machine learning algorithms, supervised and unsupervised learning, neural networks.",
        "topics": ["machine learning", "neural networks", "AI"], "department": "Computer Science",
    },
    {
        "id": "CS350", "name": "Web Development", "units": 3, "difficulty": "intermediate",
        "prerequisites": ["CS101"],
        "description": "Full-stack web development including HTML, CSS, JavaScript, and modern frameworks.",
        "topics": ["web development", "frontend", "backend"], "department": "Computer Science",
    },
    {
        "id": "CS250", "name": "Database Systems", "units": 3, "difficulty": "intermediate",
        "prerequisites": ["CS201"],
        "description": "Database design, SQL, normalization, and transaction management.",
        "topics": ["databases", "SQL", "data management"], "department": "Computer Science",
    },
    {
        "id": "MATH100", "name": "Calculus I", "units": 4, "difficulty": "beginner",
        "prerequisites": [],
        "description": "Limits, derivatives, and integrals of single-variable functions.",
        "topics": ["calculus", "mathematics"], "department": "Mathematics",
    },
    {
        "id": "MATH200", "name": "Linear Algebra", "units": 3, "difficulty": "intermediate",
        "prerequisites": ["MATH100"],
        "description": "Vectors, matrices, eigenvalues, and applications.",
        "topics": ["linear algebra", "mathematics"], "department": "Mathematics",
    },
    {
        "id": "ENG101", "name": "English Composition", "units": 3, "difficulty": "beginner",
        "prerequisites": [],
        "description": "Academic writing, research, and critical analysis.",
        "topics": ["writing", "communication"], "department": "English",
    },
    {
        "id": "PHY101", "name": "Physics I", "units": 4, "difficulty": "intermediate",
        "prerequisites": ["MATH100"],
        "description": "Mechanics, thermodynamics, and waves.",
        "topics": ["physics", "mechanics"], "department": "Physics",
    },
]

GRADE_BY_COURSE = {
    "CS101": ("A-", 3.7, 92.0),
    "CS201": ("B+", 3.3, 88.0),
    "MATH100": ("A", 4.0, 95.0),
    "MATH200": ("A-", 3.7, 91.0),
    "ENG101": ("A", 4.0, 94.0),
    "PHY101": ("B", 3.0, 84.0),
}

SPECIAL_STUDENT_PREFILLS = {}

# ---------------------------------------------------------------------------
# Synthetic students for collaborative filtering & GPA prediction
# ---------------------------------------------------------------------------

_PREREQ_MAP = {c["id"]: set(c["prerequisites"]) for c in COURSES}
_ALL_COURSE_IDS = [c["id"] for c in COURSES]

_INTEREST_POOLS = [
    ["AI", "Machine Learning", "Data Science"],
    ["Web Development", "Frontend", "Backend"],
    ["Databases", "Data Management", "Cloud"],
    ["Mathematics", "Algorithms", "Theory"],
    ["Systems", "Networking", "Security"],
    ["AI", "Web Development"],
    ["Machine Learning", "Mathematics"],
    ["Data Science", "Databases"],
]

_CAREER_POOLS = [
    "Software Engineer at a tech company",
    "Machine Learning Engineer",
    "Data Scientist",
    "Full-Stack Web Developer",
    "Backend Engineer",
    "Research Scientist in AI",
    "Data Engineer",
    "Product Manager in tech",
    "DevOps Engineer",
    "Quantitative Analyst",
]

SYNTHETIC_STUDENTS = []

random.seed(42)

def _valid_enrollment(completed_set, course_id):
    return _PREREQ_MAP.get(course_id, set()).issubset(completed_set)

def _build_random_path():
    """Build a prerequisite-respecting random enrollment path."""
    completed = set()
    available = [cid for cid in _ALL_COURSE_IDS if not _PREREQ_MAP.get(cid)]
    path = []

    num_to_complete = random.randint(3, 7)
    while len(path) < num_to_complete and available:
        pick = random.choice(available)
        path.append(pick)
        completed.add(pick)
        available = [
            cid for cid in _ALL_COURSE_IDS
            if cid not in completed and _valid_enrollment(completed, cid)
        ]
    return path

def _random_grade(base_gpa):
    """Generate a realistic grade around a base GPA."""
    gpa = max(0.0, min(4.0, base_gpa + random.gauss(0, 0.4)))
    gpa = round(gpa, 1)
    if gpa >= 3.7:
        letter, gpa_val = "A-", round(max(3.7, gpa), 2)
    elif gpa >= 3.3:
        letter, gpa_val = "B+", round(max(3.3, gpa), 2)
    elif gpa >= 3.0:
        letter, gpa_val = "B", round(max(3.0, gpa), 2)
    elif gpa >= 2.7:
        letter, gpa_val = "B-", round(max(2.7, gpa), 2)
    elif gpa >= 2.3:
        letter, gpa_val = "C+", round(max(2.3, gpa), 2)
    else:
        letter, gpa_val = "C", round(max(2.0, gpa), 2)
    score = round(gpa_val * 25, 1)
    return (letter, gpa_val, score)

_FIRST_NAMES = [
    "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn", "Dakota",
    "Reese", "Cameron", "Skyler", "Emerson", "Finley", "Rowan", "Sage", "Parker",
    "Blake", "Hayden", "Kendall", "Peyton", "Drew", "Kai", "Arden", "Marlowe",
    "Phoenix", "Remy", "Shiloh", "Tatum", "Winter", "Zion",
]

_LAST_NAMES = [
    "Lee", "Patel", "Garcia", "Kim", "Nguyen", "Chen", "Wilson", "Martinez",
    "Anderson", "Thomas", "Jackson", "White", "Harris", "Clark", "Lewis",
    "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott",
    "Adams", "Baker", "Green", "Nelson", "Hill", "Ramirez", "Campbell", "Mitchell",
]

_YEARS = ["Freshman", "Sophomore", "Junior", "Senior"]

for i in range(30):
    base_gpa = random.uniform(2.5, 4.0)
    completed_courses = _build_random_path()
    grades = {cid: _random_grade(base_gpa) for cid in completed_courses}

    current_completed_set = set(completed_courses)
    possible_current = [
        cid for cid in _ALL_COURSE_IDS
        if cid not in current_completed_set and _valid_enrollment(current_completed_set, cid)
    ]
    current_courses = random.sample(possible_current, min(random.randint(0, 2), len(possible_current)))

    SYNTHETIC_STUDENTS.append({
        "email": f"student{i+1}@demo.edu",
        "name": f"{_FIRST_NAMES[i]} {_LAST_NAMES[i]}",
        "university": "Santa Clara University",
        "program_enrolled": "MS Computer Science and Engineering",
        "major": "Computer Science",
        "year": random.choice(_YEARS),
        "interests": random.choice(_INTEREST_POOLS),
        "career_goals": random.choice(_CAREER_POOLS),
        "completed": completed_courses,
        "current": current_courses,
        "grades": grades,
    })


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


def _seed_synthetic_student(data):
    """Create one synthetic student with enrollments and grades."""
    existing = Student.query.filter_by(email=data['email']).first()
    if existing:
        return

    student = Student(
        email=data['email'],
        name=data['name'],
        university=data['university'],
        program_enrolled=data['program_enrolled'],
        major=data['major'],
        year=data['year'],
        interests=data['interests'],
        career_goals=data['career_goals'],
        is_synthetic=True,
        onboarding_completed=True,
    )
    student.set_password('synthetic')
    db.session.add(student)
    db.session.flush()

    for course_id in data['completed']:
        if db.session.get(Course, course_id):
            grade = data['grades'].get(course_id, ("B", 3.0, 82.0))
            db.session.add(StudentCourse(
                student_id=student.id, course_id=course_id, status='completed',
                final_letter=grade[0], course_gpa=grade[1],
                grade_points=grade[1], final_score=grade[2],
            ))

    for course_id in data.get('current', []):
        if db.session.get(Course, course_id):
            db.session.add(StudentCourse(
                student_id=student.id, course_id=course_id, status='current'))

    db.session.flush()
    student.program_gpa = _calculate_program_gpa(student)


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
                career_goals='Software Engineer at a tech company',
                onboarding_completed=True,
            )
            demo.set_password('demo123')
            db.session.add(demo)
            db.session.commit()

            for cid in ['CS101', 'CS201', 'MATH100', 'MATH200', 'ENG101']:
                db.session.add(StudentCourse(student_id=demo.id, course_id=cid, status='completed'))
            db.session.add(StudentCourse(student_id=demo.id, course_id='PHY101', status='current'))

        # Synthetic students for collaborative filtering
        for syn_data in SYNTHETIC_STUDENTS:
            _seed_synthetic_student(syn_data)

        db.session.commit()
        print('Database seeded successfully!')
        print(f'Demo login: alex@demo.edu / demo123')
        print(f'Synthetic students: {len(SYNTHETIC_STUDENTS)} created')

if __name__ == '__main__':
    seed()
