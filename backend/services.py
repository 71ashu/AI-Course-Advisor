"""Business logic for recommendations and degree progress."""
from models import Course, Student, StudentCourse, db

REQUIRED_CREDITS = 120


def _serialize_progress_course(enrollment):
    course = Course.query.get(enrollment.course_id)
    if not course:
        return None
    return {
        'courseId': enrollment.course_id,
        'courseName': course.name,
        'units': course.units,
        'status': enrollment.status,
        'finalScore': enrollment.final_score,
        'finalLetter': enrollment.final_letter,
        'courseGPA': enrollment.course_gpa if enrollment.course_gpa is not None else enrollment.grade_points,
    }


def calculate_program_gpa(student):
    """Compute weighted GPA from completed courses with grade points."""
    completed = StudentCourse.query.filter_by(student_id=student.id, status='completed').all()
    total_units = 0
    total_quality_points = 0.0

    for sc in completed:
        per_course_gpa = sc.course_gpa if sc.course_gpa is not None else sc.grade_points
        if per_course_gpa is None:
            continue
        course = Course.query.get(sc.course_id)
        if not course or not course.units:
            continue
        total_units += course.units
        total_quality_points += per_course_gpa * course.units

    if total_units == 0:
        return 0.0
    return round(total_quality_points / total_units, 2)


def get_degree_progress(student):
    """Calculate degree progress for a student."""
    completed = StudentCourse.query.filter_by(student_id=student.id, status='completed').all()
    current = StudentCourse.query.filter_by(student_id=student.id, status='current').all()
    
    total_credits = 0
    for sc in completed + current:
        course = Course.query.get(sc.course_id)
        if course:
            total_credits += course.units
    
    progress_pct = min((total_credits / REQUIRED_CREDITS) * 100, 100)
    major_credits = int(total_credits * 0.6)  # Approximate major requirement
    computed_gpa = calculate_program_gpa(student)
    completed_with_grades = [
        data for data in (_serialize_progress_course(sc) for sc in completed) if data is not None
    ]
    current_with_grades = [
        data for data in (_serialize_progress_course(sc) for sc in current) if data is not None
    ]
    
    return {
        'totalCredits': total_credits,
        'requiredCredits': REQUIRED_CREDITS,
        'progressPercentage': round(progress_pct, 1),
        'majorCredits': major_credits,
        'completedCoursesCount': len(completed),
        'programGPA': student.program_gpa if student.program_gpa is not None else computed_gpa,
        'completedCourses': completed_with_grades,
        'currentCourses': current_with_grades,
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
