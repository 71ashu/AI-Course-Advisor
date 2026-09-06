"""LLM integration for AI Course Advisor using OpenAI gpt-4o-mini.

Provides: advisory message generation with explainability-aware prompting.
"""
import logging
import os
from openai import OpenAI

from services import _parse_query_focus, _subject_prefix

logger = logging.getLogger(__name__)

_client = None
DEFAULT_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your-openai-api-key-here":
            return None
        _client = OpenAI(api_key=api_key)
    return _client


def get_advisory_message(student, query: str, recommendations: list) -> str:
    """Generate a personalized advisory message using gpt-4o-mini.
    Includes structured explanation factors for better explainability.
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
        "You are a friendly and knowledgeable academic advisor in a chat-style conversation. "
        "Answer their actual question first: mirror concrete asks (subject codes like EMGT/ENGR, "
        "\"non-CSEN\", topics they named). "
        "Keep your reply concise (3-6 sentences), warm, and specific. "
        "Do not list or re-describe the courses — that appears separately — but do relate your "
        "reasoning to how these picks respond to what they typed. "
        "Use the scoring factors when explaining WHY (prerequisites, peer patterns, predicted grades). "
        "If a course might lower their GPA, briefly mention the trade-off."
    )

    # If the student named specific subjects but none of the recommended
    # courses are actually in those subjects, tell the model plainly instead
    # of letting it present unrelated courses as if they satisfy the ask.
    query_focus = _parse_query_focus(query)
    if query_focus and query_focus['include_prefixes']:
        rec_prefixes = set()
        for c in recommendations:
            rec_prefixes.add(_subject_prefix(c.get('course_number', '')))
            for alt in c.get('alt_codes', []) or []:
                rec_prefixes.add(_subject_prefix(alt))
        if not (rec_prefixes & query_focus['include_prefixes']):
            requested = '/'.join(sorted(query_focus['include_prefixes']))
            system_prompt += (
                f" IMPORTANT: the student specifically asked about {requested} courses, but none of the "
                f"courses below are actually in that subject. Say this plainly up front (e.g. \"there aren't "
                f"any {requested} courses that fit right now\"), then explain why the alternatives below are "
                f"still worth considering. Do not present them as if they satisfy the {requested} request."
            )

    user_content = (
        f"Student: {student.name}, {student.year} studying {student.major}.\n"
        f"University: {student.university or 'not specified'}.\n"
        f"Program: {student.program_enrolled or 'not specified'}.\n"
        f"Interests: {', '.join(student.interests or []) or 'not specified'}.\n"
        f"Career goals: {student.career_goals or 'not specified'}.\n"
        f"Current GPA: {student.program_gpa or 'not available'}.\n"
        f"Completed courses: {', '.join(completed) or 'none yet'}.\n"
        f"Currently taking: {', '.join(current) or 'none'}.\n\n"
        f"Their question: \"{query}\"\n\n"
        f"Top recommended courses (with scoring factors):\n{course_block}"
    )

    try:
        response = client.chat.completions.create(
            model=DEFAULT_CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning("OpenAI advisory call failed: %s", e)
        return _fallback_message(student, query, recommendations)


def _fallback_message(student, query: str, recommendations: list) -> str:
    count = len(recommendations)
    q = (query or '').strip()
    query_note = f' Regarding "{q}",' if q else ''
    base = (
        f"Based on your profile as a {student.year} in {student.program_enrolled or student.major},"
        f"{query_note} I've surfaced {count} course{'s' if count != 1 else ''} that fit what you asked."
    )

    collab_note = ""
    collab_courses = [
        c for c in recommendations
        if any(f.get('type') == 'collaborative' for f in c.get('explanationFactors', []))
    ]
    if collab_courses:
        collab_note = f" Students with similar backgrounds frequently chose these courses."

    return f"{base}{collab_note} Check out the recommendations below!"
