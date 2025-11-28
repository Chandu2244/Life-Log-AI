from sheets_reader import get_journal_rows

rows = get_journal_rows()
print(rows)

# backend/nlp_engine.py

import re
import spacy
from nltk.corpus import wordnet as wn

nlp = spacy.load("en_core_web_sm")

# 13 normalized life categories
NORMALIZED_CATEGORIES = [
    "spiritual", "learning", "coding", "fitness",
    "reading", "diet", "career", "wellbeing",
    "finance", "relationships", "productivity",
    "creativity", "hobby"
]

CATEGORY_DOCS = {cat: nlp(cat.lower()) for cat in NORMALIZED_CATEGORIES}


# --------- DATE DETECTION ---------

DATE_PATTERNS = [
    r"^\d{2}/\d{2}/\d{4}$",   # 06/10/2025
    r"^\d{2}-\d{2}-\d{4}$",   # 06-10-2025
    r"^\d{4}-\d{2}-\d{2}$",   # 2025-10-06
    r"^\d{4}/\d{2}/\d{2}$",   # 2025/10/06
]

def is_date_line(line: str) -> bool:
    text = line.strip()
    if not text:
        return False
    for pattern in DATE_PATTERNS:
        if re.match(pattern, text):
            return True
    return False


# --------- CATEGORY CLASSIFIER (spaCy + WordNet) ---------

def wordnet_boost(heading_word: str, cat_word: str) -> float:
    syn1 = wn.synsets(heading_word)
    syn2 = wn.synsets(cat_word)
    if not syn1 or not syn2:
        return 0.0

    best = 0.0
    for s1 in syn1:
        for s2 in syn2:
            sim = s1.wup_similarity(s2)
            if sim and sim > best:
                best = sim
    return best


def classify_text_to_category(text: str) -> str:
    """
    Classifies any short text (heading or sentence)
    into one of the 13 normalized categories.
    """
    doc = nlp(text.lower())
    best_category = "other"
    best_score = 0.0

    for category, cat_doc in CATEGORY_DOCS.items():
        spacy_score = doc.similarity(cat_doc)

        wn_scores = [
            wordnet_boost(token.text, category)
            for token in doc
            if token.is_alpha and not token.is_stop
        ]
        wn_score = max(wn_scores) if wn_scores else 0.0

        final_score = (spacy_score * 0.75) + (wn_score * 0.25)

        if final_score > best_score:
            best_score = final_score
            best_category = category

    return best_category


# --------- HEADING DETECTION (Case 1) ---------

def looks_like_heading(line: str) -> bool:
    """
    Heuristic: a heading is short (<=4 words),
    has no sentence punctuation, and is not empty.
    """
    text = line.strip()
    if not text:
        return False

    words = text.split()
    if len(words) == 0 or len(words) > 4:
        return False

    # If contains sentence punctuation, likely not a heading
    if any(p in text for p in [".", "!", "?", ",", ":"]):
        return False

    return True


def detect_mode(lines):
    """
    Decide if this day is 'heading' mode or 'plain' mode.
    If we see enough heading-like lines followed by content lines,
    we treat it as heading mode.
    """
    heading_like_count = 0
    content_after_heading = 0

    for i, line in enumerate(lines):
        if looks_like_heading(line):
            heading_like_count += 1
            # Check if there is some content after this
            if i + 1 < len(lines) and not looks_like_heading(lines[i + 1]):
                content_after_heading += 1

    # Simple rule: if there's at least 1–2 clear heading+content patterns,
    # go with heading mode.
    if heading_like_count >= 1 and content_after_heading >= 1:
        return "heading"
    else:
        return "plain"


# --------- PROCESSOR FOR HEADING + CONTENT CASE ---------

def process_heading_mode(lines, journal_date: str):
    sections = []
    current_heading = None
    current_content = []

    for line in lines:
        if looks_like_heading(line):
            # Save previous section if exists
            if current_heading is not None:
                sections.append({
                    "original_heading": current_heading,
                    "normalized_category": classify_text_to_category(current_heading),
                    "content_lines": current_content
                })
            # Start new section
            current_heading = line.strip()
            current_content = []
        else:
            if current_heading is not None:
                if line.strip():
                    current_content.append(line.strip())

    # Save last section
    if current_heading is not None:
        sections.append({
            "original_heading": current_heading,
            "normalized_category": classify_text_to_category(current_heading),
            "content_lines": current_content
        })

    return {
        "journal_date": journal_date,
        "mode": "heading",
        "sections": sections
    }


# --------- PROCESSOR FOR PLAIN CONTENT CASE ---------

def process_plain_mode(lines, journal_date: str):
    """
    No explicit headings. We treat each sentence,
    classify it, and group by category.
    """
    category_to_sentences = {}

    for line in lines:
        text = line.strip()
        if not text:
            continue

        doc = nlp(text)
        for sent in doc.sents:
            sent_text = sent.text.strip()
            if not sent_text:
                continue
            cat = classify_text_to_category(sent_text)
            category_to_sentences.setdefault(cat, []).append(sent_text)

    sections = []
    for cat, sents in category_to_sentences.items():
        sections.append({
            "original_heading": None,
            "normalized_category": cat,
            "content_lines": sents
        })

    return {
        "journal_date": journal_date,
        "mode": "plain",
        "sections": sections
    }


# --------- MAIN ENTRY FUNCTION ---------

def process_journal_lines(raw_lines):
    """
    raw_lines: list of strings for ONE day's journal
    (e.g., rows from Google Sheet for that date block)
    Returns: dict with journal_date, mode, and sections.
    """
    # 1. Detect journal date (top line that is only a date)
    journal_date = None
    content_lines = []

    for i, line in enumerate(raw_lines):
        if journal_date is None and is_date_line(line):
            journal_date = line.strip()
        else:
            content_lines.append(line)

    if journal_date is None:
        # Optional: raise error or assume unknown date
        journal_date = "unknown"

    # 2. Decide mode
    mode = detect_mode(content_lines)

    # 3. Process accordingly
    if mode == "heading":
        return process_heading_mode(content_lines, journal_date)
    else:
        return process_plain_mode(content_lines, journal_date)


# Quick debug example (run: python nlp_engine.py)
if __name__ == "__main__":
    example_lines_heading = [
        "06/10/2025",
        "God's Word",
        "Israel people groaned to God and He heard them.",
        "Workout",
        "Gym 1 hour, felt strong."
    ]

    example_lines_plain = [
        "06/10/2025",
        "Went to gym for 1 hour and felt energetic.",
        "Read Bible at night before sleep.",
        "Studied CSS Flexbox for 30 minutes."
    ]

    print("HEADING MODE EXAMPLE:")
    print(process_journal_lines(example_lines_heading))

    print("\nPLAIN MODE EXAMPLE:")
    print(process_journal_lines(example_lines_plain))
