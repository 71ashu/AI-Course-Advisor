"""LLM integration for AI Course Advisor using OpenAI gpt-4o-mini."""
import os
from openai import OpenAI

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your-openai-api-key-here":
            return None
        _client = OpenAI(api_key=api_key)
    return _client


def get_advisory_message(student, query: str, recommendations: list) -> str:
    """
    Generate a personalized advisory message using gpt-4o-mini.
    Falls back to a templated message if OPENAI_API_KEY is not configured.
    """
    client = _get_client()
    if client is None:
        return _fallback_message(student, query, recommendations)

    course_lines = "\n".join([
        f"- {c.get('course_number', '')} – {c.get('course_name', '')} "
        f"({c.get('units', 3)} units)"
        + (f" [prerequisites needed]" if not c.get('eligible', True) else "")
        for c in recommendations
    ]) or "No courses matched your current profile."

    completed = student.to_dict().get("completedCourses", [])
    current = student.to_dict().get("currentCourses", [])

    system_prompt = (
        "You are a friendly and knowledgeable academic advisor. "
        "Keep your response concise (2-4 sentences), warm, and specific to the student's situation. "
        "Do not list or re-describe the courses — that information is shown separately. "
        "Focus on why these picks make sense for their goals and what to watch out for."
    )

    user_content = (
        f"Student: {student.name}, {student.year} studying {student.major}.\n"
        f"University: {student.university or 'not specified'}.\n"
        f"Program: {student.program_enrolled or 'not specified'}.\n"
        f"Interests: {', '.join(student.interests or []) or 'not specified'}.\n"
        f"Career goals: {student.career_goals or 'not specified'}.\n"
        f"Completed courses: {', '.join(completed) or 'none yet'}.\n"
        f"Currently taking: {', '.join(current) or 'none'}.\n\n"
        f"Their question: \"{query}\"\n\n"
        f"Top recommended courses:\n{course_lines}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            max_tokens=200,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[llm] OpenAI call failed: {e}")
        return _fallback_message(student, query, recommendations)


def _fallback_message(student, query: str, recommendations: list) -> str:
    count = len(recommendations)
    return (
        f"Based on your profile as a {student.year} in {student.program_enrolled or student.major}, "
        f"I've found {count} course{'s' if count != 1 else ''} that align with your goals. "
        f"Check out the recommendations below!"
    )
