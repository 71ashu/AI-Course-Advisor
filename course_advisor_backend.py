"""
AI Course Advisor Backend - Flask API with Anthropic Claude Integration
Provides intelligent course recommendations and academic advising for university students
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from typing import List, Dict, Any

app = Flask(__name__)
CORS(app)

# Sample course database
COURSE_DATABASE = [
    {
        "id": "CS101",
        "name": "Introduction to Computer Science",
        "credits": 3,
        "difficulty": "beginner",
        "prerequisites": [],
        "description": "Fundamental concepts of computer science including programming basics, algorithms, and problem-solving.",
        "topics": ["programming", "algorithms", "problem-solving"],
        "department": "Computer Science"
    },
    {
        "id": "CS201",
        "name": "Data Structures and Algorithms",
        "credits": 4,
        "difficulty": "intermediate",
        "prerequisites": ["CS101"],
        "description": "In-depth study of fundamental data structures and algorithms, analysis of complexity.",
        "topics": ["data structures", "algorithms", "complexity analysis"],
        "department": "Computer Science"
    },
    {
        "id": "CS301",
        "name": "Machine Learning",
        "credits": 3,
        "difficulty": "advanced",
        "prerequisites": ["CS201", "MATH200"],
        "description": "Introduction to machine learning algorithms, supervised and unsupervised learning, neural networks.",
        "topics": ["machine learning", "neural networks", "AI"],
        "department": "Computer Science"
    }
]

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/courses', methods=['GET'])
def get_courses():
    return jsonify({"courses": COURSE_DATABASE})

@app.route('/api/recommend', methods=['POST'])
def recommend_courses():
    data = request.json
    return jsonify({"success": True, "recommendations": "AI recommendations here"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
