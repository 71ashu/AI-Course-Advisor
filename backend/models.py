"""Database models for AI Course Advisor."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class ProgramCourse(db.Model):
    """Junction table linking programs to their courses (many-to-many)."""
    __tablename__ = 'program_courses'

    program_id = db.Column(db.String(50), db.ForeignKey('programs.program_id', ondelete='CASCADE'), primary_key=True)
    course_id = db.Column(db.String(20), db.ForeignKey('courses.id', ondelete='CASCADE'), primary_key=True)

    program = db.relationship('Program', backref=db.backref('program_courses', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('program_courses', lazy='dynamic'))


class Course(db.Model):
    __tablename__ = 'courses'

    # course_number is the natural key, e.g. "AMTH 200", "CSEN 342"
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    units = db.Column(db.Integer, default=3)
    # level: "Graduate", "Graduate Core", "Advanced Graduate", "Graduate (300-level)", "Graduate Lab"
    level = db.Column(db.String(50))
    description = db.Column(db.Text)
    department = db.Column(db.String(100))
    prerequisites = db.Column(db.JSON, default=list)

    # Legacy fields retained for backwards-compatibility with seeded demo data
    difficulty = db.Column(db.String(20))
    topics = db.Column(db.JSON, default=list)

    def to_dict(self):
        return {
            'course_number': self.id,
            'course_name': self.name,
            'units': self.units,
            'level': self.level or '',
            'description': self.description or '',
            'department': self.department or '',
            'prerequisites': self.prerequisites or [],
        }


class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    name = db.Column(db.String(100), nullable=False)
    university = db.Column(db.String(200), default='Unknown University')
    program_enrolled = db.Column(db.String(200), default='Undeclared')
    major = db.Column(db.String(100), default='Computer Science')
    year = db.Column(db.String(20), default='Sophomore')  # Freshman, Sophomore, Junior, Senior
    interests = db.Column(db.JSON, default=list)  # e.g. ["AI", "Web Development"]
    career_goals = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        completed = StudentCourse.query.filter_by(student_id=self.id, status='completed').all()
        current = StudentCourse.query.filter_by(student_id=self.id, status='current').all()
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'university': self.university or '',
            'program': self.program_enrolled or '',
            'major': self.major,
            'year': self.year,
            'interests': self.interests or [],
            'careerGoals': self.career_goals or '',
            'completedCourses': [sc.course_id for sc in completed],
            'currentCourses': [sc.course_id for sc in current]
        }


class Program(db.Model):
    __tablename__ = 'programs'

    program_id = db.Column(db.String(50), primary_key=True)
    program_name = db.Column(db.String(200), nullable=False)
    degree_type = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(200))
    description = db.Column(db.Text)
    total_units_required = db.Column(db.Integer)
    minimum_gpa = db.Column(db.Float)

    # Complex nested structures stored as JSONB
    requirements = db.Column(db.JSON, default=dict)
    concentrations = db.Column(db.JSON, default=list)
    learning_outcomes = db.Column(db.JSON, default=list)
    admission_requirements = db.Column(db.JSON, default=dict)

    # Optional fields present only on some programs
    special_features = db.Column(db.JSON, default=list)
    time_limit = db.Column(db.String(200))

    def to_dict(self):
        return {
            'program_id': self.program_id,
            'program_name': self.program_name,
            'degree_type': self.degree_type,
            'department': self.department,
            'description': self.description,
            'total_units_required': self.total_units_required,
            'minimum_gpa': self.minimum_gpa,
            'requirements': self.requirements or {},
            'concentrations': self.concentrations or [],
            'learning_outcomes': self.learning_outcomes or [],
            'admission_requirements': self.admission_requirements or {},
            'special_features': self.special_features or [],
            'time_limit': self.time_limit,
        }


class StudentCourse(db.Model):
    __tablename__ = 'student_courses'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.String(20), db.ForeignKey('courses.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'completed' or 'current'
    
    student = db.relationship('Student', backref=db.backref('enrollments', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('enrollments', lazy='dynamic'))
