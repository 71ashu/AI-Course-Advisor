"""Seed database with sample courses and a demo student."""
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
