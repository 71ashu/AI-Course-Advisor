"""Business logic for recommendations and degree progress."""
from models import Course, Student, StudentCourse, db

REQUIRED_CREDITS = 120

def get_degree_progress(student):
    """Calculate degree progress for a student."""
    completed = StudentCourse.query.filter_by(student_id=student.id, status='completed').all()
    current = StudentCourse.query.filter_by(student_id=student.id, status='current').all()
    
    total_credits = 0
    for sc in completed + current:
        course = Course.query.get(sc.course_id)
        if course:
            total_credits += course.credits
    
    progress_pct = min((total_credits / REQUIRED_CREDITS) * 100, 100)
    major_credits = int(total_credits * 0.6)  # Approximate major requirement
    
    return {
        'totalCredits': total_credits,
        'requiredCredits': REQUIRED_CREDITS,
        'progressPercentage': round(progress_pct, 1),
        'majorCredits': major_credits,
        'completedCoursesCount': len(completed)
    }


def get_recommendations(student, query=''):
    """Get course recommendations based on student profile and query."""
    completed_ids = set(
        sc.course_id for sc in 
        StudentCourse.query.filter_by(student_id=student.id, status='completed').all()
    )
    current_ids = set(
        sc.course_id for sc in 
        StudentCourse.query.filter_by(student_id=student.id, status='current').all()
    )
    taken = completed_ids | current_ids
    
    interests = set((student.interests or []))
    query_lower = query.lower() if query else ''
    
    all_courses = Course.query.all()
    scored = []
    
    for course in all_courses:
        if course.id in taken:
            continue
            
        # Check eligibility (prerequisites met)
        prereqs_met = all(pid in completed_ids for pid in (course.prerequisites or []))
        
        # Score based on interest match
        score = 0
        match_reason = None
        
        if prereqs_met:
            score += 50
            match_reason = "You've met all prerequisites"
        
        # Topic/interest matching
        for topic in (course.topics or []):
            if topic.lower() in [i.lower() for i in interests]:
                score += 30
                match_reason = f"Aligns with your interest in {topic}"
                break
        
        # Query matching
        if query_lower:
            if any(t in query_lower for t in ['ml', 'machine learning', 'ai', 'artificial intelligence']):
                if 'machine learning' in (course.name or '').lower() or 'ai' in (course.topics or []):
                    score += 40
                    match_reason = "Matches your ML/AI interest"
            if any(t in query_lower for t in ['web', 'next semester', 'recommend']):
                score += 10
        
        # Default match reason
        if not match_reason:
            match_reason = "Complements your academic profile"
        
        scored.append({
            'course': course,
            'score': score,
            'eligible': prereqs_met,
            'matchReason': match_reason
        })
    
    # Sort by score, take top 6
    scored.sort(key=lambda x: x['score'], reverse=True)
    top = scored[:6]
    
    return [
        {
            **item['course'].to_dict(),
            'eligible': item['eligible'],
            'matchReason': item['matchReason']
        }
        for item in top
    ]
