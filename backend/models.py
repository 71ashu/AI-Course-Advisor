"""Database models for AI Course Advisor."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    credits = db.Column(db.Integer, default=3)
    difficulty = db.Column(db.String(20), default='intermediate')  # beginner, intermediate, advanced
    description = db.Column(db.Text)
    department = db.Column(db.String(100))
    topics = db.Column(db.JSON, default=list)  # e.g. ["AI", "machine learning"]
    
    # Prerequisites stored as JSON array of course IDs
    prerequisites = db.Column(db.JSON, default=list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'credits': self.credits,
            'difficulty': self.difficulty,
            'description': self.description,
            'department': self.department or '',
            'topics': self.topics or [],
            'prerequisites': self.prerequisites or []
        }


class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    name = db.Column(db.String(100), nullable=False)
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
            'major': self.major,
            'year': self.year,
            'interests': self.interests or [],
            'careerGoals': self.career_goals or '',
            'completedCourses': [sc.course_id for sc in completed],
            'currentCourses': [sc.course_id for sc in current]
        }


class StudentCourse(db.Model):
    __tablename__ = 'student_courses'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.String(20), db.ForeignKey('courses.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'completed' or 'current'
    
    student = db.relationship('Student', backref=db.backref('enrollments', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('enrollments', lazy='dynamic'))
