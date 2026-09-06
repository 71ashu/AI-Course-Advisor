"""Best-effort extraction of course grades from an uploaded transcript PDF.

Transcript layouts vary a lot between institutions, so this does not attempt
a full structured parse. Instead it scans each line of text for something
that looks like a course code (e.g. "CSEN 342") next to a letter grade
(e.g. "A-") and treats that as one completed course. Lines that don't carry
both are skipped.
"""
import re

import pdfplumber

GRADE_POINTS = {
    'A+': 4.0, 'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D': 1.0, 'D-': 0.7,
    'F': 0.0,
}

_GRADE_PATTERN = re.compile(r'(?<![A-Za-z])(A\+|A-|A|B\+|B-|B|C\+|C-|C|D\+|D-|D|F)(?![A-Za-z0-9])')
_COURSE_CODE_PATTERN = re.compile(r'\b([A-Z]{2,6})\s?-?\s?(\d{3}[A-Z]?)\b')


def parse_transcript_pdf(file_stream):
    """Scan a transcript PDF and return {"DEPT 123": "A-"} for each course/grade
    pair found. A course code appearing on more than one line (e.g. a retake)
    keeps the grade from its last occurrence."""
    lines = []
    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            lines.extend((page.extract_text() or '').splitlines())

    grades_by_course = {}
    for line in lines:
        course_match = _COURSE_CODE_PATTERN.search(line)
        grade_match = _GRADE_PATTERN.search(line)
        if course_match and grade_match:
            course_code = f'{course_match.group(1)} {course_match.group(2)}'
            grades_by_course[course_code] = grade_match.group(1)

    return grades_by_course
