"""LLM integration for AI Course Advisor using OpenAI gpt-4o-mini.

Provides: advisory message generation, job skill extraction, and
explainability-aware prompting.
"""
import json
import os
from openai import OpenAI

_client = None
_job_skills_cache = {}


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your-openai-api-key-here":
            return None
        _client = OpenAI(api_key=api_key)
    return _client


def extract_job_skills(job_title):
    """Extract relevant technical skills for a job title using GPT-4o-mini.
    Returns a list of lowercase skill strings. Cached per title.
    Falls back to an empty list if LLM is unavailable.
    """
    if not job_title:
        return []

    normalized = job_title.strip().lower()
    if normalized in _job_skills_cache:
        return _job_skills_cache[normalized]

    client = _get_client()
    if client is None:
        skills = _fallback_job_skills(job_title)
        _job_skills_cache[normalized] = skills
        return skills

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You extract technical skills relevant to job titles. "
                        "Return ONLY a JSON array of 5-10 lowercase skill slugs "
                        "(e.g. [\"python\", \"machine-learning\", \"sql\"]). "
                        "No explanation, no markdown, just the JSON array."
                    ),
                },
                {"role": "user", "content": f"Job title: {job_title}"},
            ],
            max_tokens=150,
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()
        skills = json.loads(raw)
        if isinstance(skills, list):
            skills = [s.lower().strip() for s in skills if isinstance(s, str)]
            _job_skills_cache[normalized] = skills
            return skills
    except Exception as e:
        print(f"[llm] Job skill extraction failed: {e}")

    skills = _fallback_job_skills(job_title)
    _job_skills_cache[normalized] = skills
    return skills


def _fallback_job_skills(job_title):
    """Keyword-based fallback when LLM is unavailable."""
    title_lower = (job_title or '').lower()
    skills = []
    mapping = {
        'ml': ['python', 'machine-learning', 'neural-networks', 'data-analysis', 'tensorflow', 'scikit-learn'],
        'machine learning': ['python', 'machine-learning', 'neural-networks', 'data-analysis', 'tensorflow'],
        'data scientist': ['python', 'machine-learning', 'sql', 'data-analysis', 'statistical-modeling'],
        'data engineer': ['python', 'sql', 'database-design', 'data-modeling', 'postgresql'],
        'full-stack': ['javascript', 'react', 'node-js', 'sql', 'html-css', 'rest-apis'],
        'frontend': ['javascript', 'react', 'html-css', 'typescript'],
        'backend': ['python', 'sql', 'rest-apis', 'database-design', 'node-js'],
        'software engineer': ['python', 'data-structures', 'algorithm-design', 'sql', 'rest-apis', 'javascript'],
        'ai': ['python', 'machine-learning', 'neural-networks', 'data-analysis', 'linear-algebra'],
        'research': ['python', 'machine-learning', 'mathematical-modeling', 'linear-algebra', 'data-analysis'],
        'devops': ['python', 'sql', 'rest-apis', 'linux', 'cloud'],
        'quant': ['python', 'mathematical-modeling', 'linear-algebra', 'calculus', 'data-analysis'],
    }
    for keyword, mapped_skills in mapping.items():
        if keyword in title_lower:
            skills.extend(mapped_skills)
    return list(set(skills)) if skills else ['python', 'problem-solving', 'data-structures']


def get_advisory_message(student, query: str, recommendations: list) -> str:
    """Generate a personalized advisory message using gpt-4o-mini.
    Now includes structured explanation factors for better explainability.
    Falls back to a templated message if OPENAI_API_KEY is not configured.
    """
    client = _get_client()
    if client is None:
        return _fallback_message(student, query, recommendations)

    course_lines = []
    for c in recommendations:
        line = (
            f"- {c.get('course_number', '')} – {c.get('course_name', '')} "
            f"({c.get('units', 3)} units)"
        )
        if not c.get('eligible', True):
            line += " [prerequisites needed]"

        factors = c.get('explanationFactors', [])
        if factors:
            factor_strs = [f"{f['type']}: {f['description']}" for f in factors if f.get('points', 0) != 0]
            if factor_strs:
                line += f"  Factors: {'; '.join(factor_strs)}"

        pred = c.get('predictedGrade')
        if pred:
            line += f"  [Predicted: {pred['predictedLetter']}]"

        course_lines.append(line)

    course_block = "\n".join(course_lines) or "No courses matched your current profile."

    completed = student.to_dict().get("completedCourses", [])
    current = student.to_dict().get("currentCourses", [])

    system_prompt = (
        "You are a friendly and knowledgeable academic advisor. "
        "Keep your response concise (3-5 sentences), warm, and specific to the student's situation. "
        "Do not list or re-describe the courses — that information is shown separately. "
        "Focus on WHY these picks make sense by referencing the scoring factors provided "
        "(prerequisites, peer patterns, career alignment, predicted grades). "
        "If a course might lower their GPA, briefly mention the trade-off. "
        "If career alignment factors are present, connect the recommendation to their career goal."
    )

    job_context = ""
    if student.target_job_title:
        job_context = f"Target career: {student.target_job_title}.\n"

    user_content = (
        f"Student: {student.name}, {student.year} studying {student.major}.\n"
        f"University: {student.university or 'not specified'}.\n"
        f"Program: {student.program_enrolled or 'not specified'}.\n"
        f"Interests: {', '.join(student.interests or []) or 'not specified'}.\n"
        f"Career goals: {student.career_goals or 'not specified'}.\n"
        f"{job_context}"
        f"Current GPA: {student.program_gpa or 'not available'}.\n"
        f"Completed courses: {', '.join(completed) or 'none yet'}.\n"
        f"Currently taking: {', '.join(current) or 'none'}.\n\n"
        f"Their question: \"{query}\"\n\n"
        f"Top recommended courses (with scoring factors):\n{course_block}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[llm] OpenAI call failed: {e}")
        return _fallback_message(student, query, recommendations)


def _fallback_message(student, query: str, recommendations: list) -> str:
    count = len(recommendations)
    base = (
        f"Based on your profile as a {student.year} in {student.program_enrolled or student.major}, "
        f"I've found {count} course{'s' if count != 1 else ''} that align with your goals."
    )

    career_note = ""
    if student.target_job_title:
        career_courses = [
            c for c in recommendations
            if any(f.get('type') == 'career' for f in c.get('explanationFactors', []))
        ]
        if career_courses:
            career_note = (
                f" {len(career_courses)} of these build skills relevant to your "
                f"'{student.target_job_title}' career goal."
            )

    collab_note = ""
    collab_courses = [
        c for c in recommendations
        if any(f.get('type') == 'collaborative' for f in c.get('explanationFactors', []))
    ]
    if collab_courses:
        collab_note = f" Students with similar backgrounds frequently chose these courses."

    return f"{base}{career_note}{collab_note} Check out the recommendations below!"
