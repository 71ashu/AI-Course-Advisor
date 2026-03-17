"""Business logic for recommendations and degree progress."""
import re
from models import Course, Program, ProgramCourse, Student, StudentCourse, db

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


def _normalize_program_text(value):
    normalized = (value or '').lower().replace('&', ' and ')
    normalized = re.sub(r'\band\b', ' ', normalized)
    return re.sub(r'[^a-z0-9]+', '', normalized)


def _resolve_program_for_student(student):
    program_text = (student.program_enrolled or '').strip()
    if not program_text:
        return None

    direct_match = Program.query.filter(
        Program.program_name.ilike(program_text)
    ).first()
    if direct_match:
        return direct_match

    normalized_target = _normalize_program_text(program_text)
    for program in Program.query.all():
        normalized_name = _normalize_program_text(program.program_name)
        normalized_id = _normalize_program_text(program.program_id)
        if normalized_target and (
            normalized_target in normalized_name
            or normalized_name in normalized_target
            or normalized_target in normalized_id
            or normalized_id in normalized_target
        ):
            return program
    return None


def _build_program_requirement_items(program):
    if not program:
        return []

    requirements = []
    if program.total_units_required:
        requirements.append(f"{program.total_units_required} total units required")
    if program.minimum_gpa:
        requirements.append(f"Minimum GPA: {program.minimum_gpa:.2f}")

    linked_courses = (
        db.session.query(Course)
        .join(ProgramCourse, ProgramCourse.course_id == Course.id)
        .filter(ProgramCourse.program_id == program.program_id)
        .all()
    )
    core_courses = [c for c in linked_courses if (c.level or '').lower() == 'graduate core']
    core_units = sum((c.units or 0) for c in core_courses)

    if core_courses:
        requirements.append(
            f"{len(core_courses)} graduate core courses ({core_units} units)"
        )
        elective_units = max((program.total_units_required or 0) - core_units, 0)
        if elective_units:
            requirements.append(f"At least {elective_units} units of graduate electives")

    nested_requirements = program.requirements or {}
    if isinstance(nested_requirements, dict):
        for key, value in nested_requirements.items():
            if isinstance(value, (str, int, float)) and value not in ('', None):
                requirements.append(f"{str(key).replace('_', ' ').title()}: {value}")

    return requirements


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

    matched_program = _resolve_program_for_student(student)
    required_credits = (
        matched_program.total_units_required
        if matched_program and matched_program.total_units_required
        else REQUIRED_CREDITS
    )
    progress_pct = min((total_credits / required_credits) * 100, 100) if required_credits else 0
    major_credits = total_credits if matched_program else int(total_credits * 0.6)
    requirement_items = _build_program_requirement_items(matched_program)
    computed_gpa = calculate_program_gpa(student)
    completed_with_grades = [
        data for data in (_serialize_progress_course(sc) for sc in completed) if data is not None
    ]
    current_with_grades = [
        data for data in (_serialize_progress_course(sc) for sc in current) if data is not None
    ]
    
    return {
        'totalCredits': total_credits,
        'requiredCredits': required_credits,
        'progressPercentage': round(progress_pct, 1),
        'majorCredits': major_credits,
        'completedCoursesCount': len(completed),
        'programGPA': student.program_gpa if student.program_gpa is not None else computed_gpa,
        'programName': matched_program.program_name if matched_program else (student.program_enrolled or ''),
        'programDegreeType': matched_program.degree_type if matched_program else '',
        'programRequirementItems': requirement_items,
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
