# core/rules.py
import re


ASSIGNMENT_KEYWORDS = [
"assigned", "assignment", "next project", "please start",
"deadline", "due by", "kickoff", "sow", "statement of work", "po attached"
]


def detect_assignment(subject: str, snippet: str):
    text = f"{subject} {snippet}".lower()
    tags, hit = [], False
    for kw in ASSIGNMENT_KEYWORDS:
        if kw in text:
            tags.append(kw.replace(" ", "_"))
            hit = True
    if re.search(r"\bby\s+\w+\s+\d{1,2}\b", text):
        tags.append("has_due_date_phrase")
        hit = True
    return hit, tags