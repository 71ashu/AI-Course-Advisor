"""LLM integration for AI Course Advisor using OpenAI gpt-4o-mini.

Provides: advisory message generation with explainability-aware prompting,
plus a conversational course-detail mode for when a student asks about one
specific course instead of asking for recommendations.
"""
import json
import logging
import os
import random
import re
from openai import OpenAI

from services import (
    _parse_query_focus, _subject_prefix, count_course_codes,
    looks_like_recommendation_request,
)

logger = logging.getLogger(__name__)

_client = None
DEFAULT_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

MAX_HISTORY_TURNS = 6


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your-openai-api-key-here":
            return None
        _client = OpenAI(api_key=api_key)
    return _client


def _history_messages(history):
    """Convert prior {role, content} chat turns into OpenAI message dicts,
    capped to the most recent turns so prompts stay small. Passing real
    conversation history (instead of treating every turn as a fresh call)
    is what lets the model avoid repeating itself and answer follow-ups
    like "why not the second one" or "what about its workload"."""
    if not history:
        return []
    trimmed = history[-MAX_HISTORY_TURNS:]
    messages = []
    for turn in trimmed:
        role = turn.get('role')
        content = (turn.get('content') or '').strip()
        if role in ('user', 'assistant') and content:
            messages.append({"role": role, "content": content})
    return messages


def interpret_request(query: str, history: list = None) -> dict:
    """Route a chat message and, for recommendation requests, turn it into a
    standalone search query.

    Returns {"intent": "recommend" | "course_detail" | "general",
             "search_query": str}.

    Ranking only sees one query string, so follow-ups like "recommend more of
    these" or "those aren't 300-level" must be resolved against earlier turns
    into something like "CSEN 300-level courses" — otherwise the constraints
    the student already stated are silently dropped. Falls back to keyword
    heuristics when no LLM is available."""
    client = _get_client()
    if client is None:
        return _fallback_interpret(query)

    system_prompt = (
        "You route messages in an academic advisor chat. Reply with a JSON object "
        "{\"intent\": ..., \"search_query\": ...}.\n"
        "intent is one of:\n"
        "- \"recommend\": the student wants courses suggested, listed, or filtered for them. This includes "
        "\"what courses can I take\", \"show me 300-level courses\", \"more like these\", \"anything easier?\", "
        "and corrections to earlier picks such as \"those aren't 300-level\" or \"I meant CSEN\".\n"
        "- \"course_detail\": they ask about ONE specific named course (what it covers, workload, prerequisites).\n"
        "- \"general\": anything else (requirements, credits, GPA, careers, policies, greetings, thanks).\n"
        "search_query: for \"recommend\", a short standalone description of the courses they want now, "
        "resolving references to earlier turns (\"these\", \"more\", \"instead\") and keeping every constraint "
        "still in force: subject codes (e.g. CSEN, EMGT), exclusions (e.g. \"non-CSEN\"), course level written "
        "like \"300-level\" (course numbers 3XX), and topics. Always write subjects as their catalog codes "
        "(CSEN, EMGT, ENGR, AMTH, ECEN, MECH), never as department names, and write an exclusion only if the "
        "student still wants it — a later message asking for a subject overrides an earlier exclusion of it. "
        "To restrict to a subject, just name it (e.g. \"CSEN 300-level courses\"); never use double negatives "
        "like \"excluding non-CSEN\". "
        "Do not include individual course codes. "
        "Use an empty string for other intents."
    )
    try:
        response = client.chat.completions.create(
            model=DEFAULT_CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                *_history_messages(history),
                {"role": "user", "content": query},
            ],
            max_tokens=80,
            temperature=0,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content or '{}')
        intent = data.get('intent')
        if intent in ('recommend', 'course_detail', 'general'):
            search_query = (data.get('search_query') or '').strip()
            return {'intent': intent, 'search_query': search_query or query}
    except Exception as e:
        logger.warning("OpenAI request routing failed: %s", e)
    return _fallback_interpret(query)


def _fallback_interpret(query: str) -> dict:
    if count_course_codes(query) == 1 and not looks_like_recommendation_request(query):
        intent = 'course_detail'
    elif looks_like_recommendation_request(query):
        intent = 'recommend'
    else:
        intent = 'general'
    return {'intent': intent, 'search_query': query}


def get_general_message(student, query: str, progress: dict = None, history: list = None) -> str:
    """Answer a general question (requirements, GPA, careers, small talk) without
    attaching a recommendation list."""
    client = _get_client()
    if client is None:
        return _fallback_general_message(student, progress)

    completed = student.to_dict().get("completedCourses", [])
    current = student.to_dict().get("currentCourses", [])

    system_prompt = (
        "You are a friendly, knowledgeable academic advisor in an ongoing chat with a student. "
        "Answer their actual question directly and concisely (2-5 sentences), using their profile "
        "and degree progress where relevant. No course list is shown with this reply, so do not "
        "say things like \"see the recommendations below\" and do not volunteer a list of courses. "
        "Never name course codes or course titles the student didn't mention themselves — you don't have "
        "the catalog in this reply, so any course you name would be made up. If they'd benefit from "
        "suggestions, briefly offer to recommend courses instead. "
        "If you don't know something specific (e.g. a university policy), say so rather than guessing. "
        "Vary your phrasing from earlier turns in this conversation."
    )

    progress_note = ""
    if progress:
        progress_note = (
            f"Degree progress: {progress.get('totalCredits', 0)} of "
            f"{progress.get('requiredCredits', 'unknown')} credits completed "
            f"({progress.get('progressPercentage', 0)}%).\n"
        )

    user_content = (
        f"Student: {student.name}, {student.year} studying {student.major}.\n"
        f"University: {student.university or 'not specified'}.\n"
        f"Program: {student.program_enrolled or 'not specified'}.\n"
        f"Interests: {', '.join(student.interests or []) or 'not specified'}.\n"
        f"Career goals: {student.career_goals or 'not specified'}.\n"
        f"Current GPA: {student.program_gpa or 'not available'}.\n"
        f"Completed courses: {', '.join(completed) or 'none yet'}.\n"
        f"Currently taking: {', '.join(current) or 'none'}.\n"
        f"{progress_note}\n"
        f"Their message: \"{query}\""
    )

    try:
        response = client.chat.completions.create(
            model=DEFAULT_CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                *_history_messages(history),
                {"role": "user", "content": user_content},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning("OpenAI general-reply call failed: %s", e)
        return _fallback_general_message(student, progress)


def get_advisory_message(student, query: str, recommendations: list, history: list = None,
                         search_query: str = None) -> str:
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
        "You are a friendly and knowledgeable academic advisor in an ongoing chat-style "
        "conversation. Answer their actual question first: mirror concrete asks (subject codes "
        "like EMGT/ENGR, \"non-CSEN\", topics they named). "
        "Keep your reply concise (3-6 sentences), warm, and specific. "
        "Do not list or re-describe the courses — that appears separately — but do relate your "
        "reasoning to how these picks respond to what they typed. "
        "Only mention courses from the list provided — never name any other course code or title, "
        "since anything outside the list may not exist in this catalog. If the list is short, that's "
        "everything available that matches; say so rather than padding it. "
        "Use the scoring factors when explaining WHY (prerequisites, peer patterns, predicted grades). "
        "If a course might lower their GPA, briefly mention the trade-off. "
        "This is a multi-turn conversation: look at the earlier turns before writing your reply, and "
        "vary your opening line and phrasing rather than reusing the same sentence structure you or "
        "the student have already seen — treat each reply as a continuation, not a reset."
    )

    # If the student named specific subjects but none of the recommended
    # courses are actually in those subjects, tell the model plainly instead
    # of letting it present unrelated courses as if they satisfy the ask.
    query_focus = _parse_query_focus(search_query or query)
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

    if query_focus and query_focus['levels']:
        rec_levels = {
            int(m.group(1)) for c in recommendations
            for m in [re.search(r'(\d)\d\d', c.get('course_number', ''))] if m
        }
        if not (rec_levels & query_focus['levels']):
            wanted = '/'.join(f"{lvl}00-level" for lvl in sorted(query_focus['levels']))
            system_prompt += (
                f" IMPORTANT: the student asked for {wanted} courses, but none of the courses below are at "
                f"that level. Say so plainly up front instead of presenting them as {wanted}."
            )

    interpreted = ""
    if search_query and search_query.strip() != (query or '').strip():
        interpreted = f"What they're looking for (from the conversation so far): \"{search_query}\"\n"

    user_content = (
        f"Student: {student.name}, {student.year} studying {student.major}.\n"
        f"University: {student.university or 'not specified'}.\n"
        f"Program: {student.program_enrolled or 'not specified'}.\n"
        f"Interests: {', '.join(student.interests or []) or 'not specified'}.\n"
        f"Career goals: {student.career_goals or 'not specified'}.\n"
        f"Current GPA: {student.program_gpa or 'not available'}.\n"
        f"Completed courses: {', '.join(completed) or 'none yet'}.\n"
        f"Currently taking: {', '.join(current) or 'none'}.\n\n"
        f"Their question: \"{query}\"\n"
        f"{interpreted}\n"
        f"Top recommended courses (with scoring factors):\n{course_block}\n\n"
        f"Only these courses may be named in your reply: "
        f"{', '.join(c.get('course_number', '') for c in recommendations) or 'none'}. "
        f"Earlier turns may mention other courses; ignore them unless they are in this list."
    )

    try:
        response = client.chat.completions.create(
            model=DEFAULT_CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                *_history_messages(history),
                {"role": "user", "content": user_content},
            ],
            max_tokens=300,
            temperature=0.85,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning("OpenAI advisory call failed: %s", e)
        return _fallback_message(student, query, recommendations)


def get_course_detail_message(student, query: str, course: dict, history: list = None) -> str:
    """Generate a conversational, deep-dive answer about ONE specific course the
    student asked about by name/code, instead of framing the reply around a
    ranked list of recommendations."""
    client = _get_client()
    if client is None:
        return _fallback_course_detail_message(student, course)

    system_prompt = (
        "You are a friendly, knowledgeable academic advisor having an ongoing chat with a student "
        "who just asked about ONE specific course. Answer conversationally, like you're describing "
        "the course to them in person: what it actually covers, what kind of work to expect, and how "
        "it fits (or doesn't) their interests, career goals, and prerequisite status. "
        "This is not a recommendation list — do not present alternative courses. "
        "Keep it to 3-6 sentences, concrete and specific to this course's real description and level, "
        "and end by inviting a natural follow-up (e.g. about workload, prerequisites, or what comes after it) "
        "rather than repeating a stock closing line. "
        "Vary your phrasing from earlier turns in this conversation instead of reusing the same sentence shapes."
    )

    prereq_note = (
        "already completed" if course.get('status') == 'completed'
        else "currently enrolled in it" if course.get('status') == 'current'
        else "eligible to take it now" if course.get('eligible')
        else f"missing prerequisites: {', '.join(course.get('missingPrerequisites') or []) or 'unclear from the catalog'}"
    )
    pred = course.get('predictedGrade')
    pred_note = f"Predicted grade if taken now: {pred['predictedLetter']} (~{pred['predictedGPA']} GPA)." if pred else ""

    user_content = (
        f"Student: {student.name}, {student.year} studying {student.major}.\n"
        f"Interests: {', '.join(student.interests or []) or 'not specified'}.\n"
        f"Career goals: {student.career_goals or 'not specified'}.\n"
        f"Current GPA: {student.program_gpa or 'not available'}.\n\n"
        f"Their question: \"{query}\"\n\n"
        f"Course: {course.get('course_number')} - {course.get('course_name')} ({course.get('units', 3)} units)\n"
        f"Level: {course.get('level') or 'not specified'}\n"
        f"Department: {course.get('department') or 'not specified'}\n"
        f"Description: {course.get('description') or 'No catalog description available.'}\n"
        f"Prerequisites: {', '.join(course.get('prerequisites') or []) or 'none'}\n"
        f"Student status: {prereq_note}\n"
        f"{pred_note}"
    )

    try:
        response = client.chat.completions.create(
            model=DEFAULT_CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                *_history_messages(history),
                {"role": "user", "content": user_content},
            ],
            max_tokens=300,
            temperature=0.85,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning("OpenAI course-detail call failed: %s", e)
        return _fallback_course_detail_message(student, course)


_FALLBACK_OPENERS = [
    "Based on your profile as a {year} in {program},",
    "Looking at where you're at as a {year} in {program},",
    "Given your progress so far as a {year} in {program},",
    "Taking your background as a {year} in {program} into account,",
]


def _fallback_message(student, query: str, recommendations: list) -> str:
    count = len(recommendations)
    q = (query or '').strip()
    query_note = f' regarding "{q}",' if q else ''

    opener = random.choice(_FALLBACK_OPENERS).format(
        year=student.year, program=student.program_enrolled or student.major,
    )
    base = f"{opener}{query_note} I've surfaced {count} course{'s' if count != 1 else ''} that fit what you asked."

    notes = []
    collab_courses = [
        c for c in recommendations
        if any(f.get('type') == 'collaborative' for f in c.get('explanationFactors', []))
    ]
    if collab_courses:
        notes.append("Students with similar backgrounds frequently chose these courses.")

    interest_courses = [
        c for c in recommendations
        if any(f.get('type') == 'interest' for f in c.get('explanationFactors', []))
    ]
    if interest_courses:
        notes.append("A few of these line up directly with the interests on your profile.")

    warned = [c for c in recommendations if any(f.get('type') == 'gpa_warning' for f in c.get('explanationFactors', []))]
    if warned:
        notes.append("One or two could be a tougher grade for you, so weigh that against how much you want the material.")

    ineligible = [c for c in recommendations if not c.get('eligible', True)]
    if ineligible:
        notes.append(f"{len(ineligible)} of these still need a prerequisite first, so check that column before you register.")

    note = f" {random.choice(notes)}" if notes else ""
    return f"{base}{note} Check out the recommendations below!"


def _fallback_general_message(student, progress: dict = None) -> str:
    """No-API-key fallback for general questions. Without an LLM we can't
    answer free-form questions, so share what we know and point the student
    at what the advisor can do."""
    parts = []
    if progress:
        parts.append(
            f"You've completed {progress.get('totalCredits', 0)} of "
            f"{progress.get('requiredCredits', 'the required')} credits so far."
        )
    parts.append(
        "I can recommend courses for you (try \"what should I take next semester?\") "
        "or tell you about a specific course if you name its code."
    )
    return " ".join(parts)


def _fallback_course_detail_message(student, course: dict) -> str:
    """No-API-key fallback for course-detail questions. Built straight from the
    course's own catalog data, so it's naturally specific to that course rather
    than a generic wrapper sentence repeated for every query."""
    name = course.get('course_name') or course.get('course_number')
    number = course.get('course_number')
    units = course.get('units', 3)
    level = course.get('level')
    description = (course.get('description') or '').strip()
    prereqs = course.get('prerequisites') or []

    lines = [f"{number} – {name} is a {units}-unit course" + (f" ({level})." if level else ".")]

    if description:
        lines.append(description)

    if course.get('status') == 'completed':
        lines.append("You've already completed this one.")
    elif course.get('status') == 'current':
        lines.append("You're currently enrolled in it.")
    elif course.get('eligible'):
        lines.append("You've met the prerequisites, so you're eligible to take it now.")
    else:
        missing = course.get('missingPrerequisites') or []
        if missing:
            lines.append(f"You'd need to complete {', '.join(missing)} first.")
        elif prereqs:
            lines.append(f"Prerequisites: {', '.join(prereqs)}.")

    pred = course.get('predictedGrade')
    if pred:
        lines.append(f"Based on your history, students with a similar GPA tend to land around a {pred['predictedLetter']}.")

    return " ".join(lines)
