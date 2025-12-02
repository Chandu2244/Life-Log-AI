import re
import spacy
from nltk.corpus import wordnet as wn

nlp = spacy.load("en_core_web_sm")

# Normalized categories
NORMALIZED_CATEGORIES = [
    "spiritual", "learning", "coding", "fitness",
    "reading", "diet", "career", "wellbeing",
    "finance", "relationships", "productivity",
    "creativity", "hobby"
]

CATEGORY_KEYWORDS = {
    "spiritual": ["god", "bible", "prayer", "faith", "holy", "church"],
    "learning": ["learn", "study", "lecture", "class", "concept"],
    "coding": ["code", "coding", "javascript", "node", "python", "css", "html", "flexbox", "practice"],
    "fitness": ["gym", "workout", "exercise", "run", "walk"],
    "reading": ["read", "reading", "book", "novel"],
    "diet": ["diet", "food", "eat", "meal", "calorie"],
    "career": ["job", "career", "office", "interview"],
    "wellbeing": ["mental", "feeling", "emotion", "health"],
    "finance": ["money", "expense", "salary", "budget"],
    "relationships": ["friend", "family", "love", "people"],
    "productivity": ["task", "plan", "focus", "todo"],
    "creativity": ["create", "draw", "design", "art"],
    "hobby": ["game", "movie", "music", "fun"]
}



# --------- DATE DETECTION ---------
DATE_PATTERNS = [
    r"^\d{2}/\d{2}/\d{4}$",
    r"^\d{2}-\d{2}-\d{4}$",
    r"^\d{4}-\d{2}-\d{2}$",
    r"^\d{4}/\d{2}/\d{2}$",
]

def is_date_line(line: str) -> bool:
    return any(re.match(p, line.strip()) for p in DATE_PATTERNS)


# --------- CATEGORY DETECTION ---------
def classify_text_to_category(text: str) -> str:
    text_lower = text.lower()

    # Rule-based first
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(word in text_lower for word in keywords):
            return category

    return "other"  # fallback


# --------- JOURNAL PROCESSOR ---------
def process_journal_lines(raw_rows):
    journal_date = None
    valid_sentences = []

    for row in raw_rows:
        # Merge multiple columns into one text block
        if isinstance(row, list):
            text = " ".join(str(c).strip() for c in row if c and str(c).strip())
        else:
            text = str(row).strip()

        if not text:
            continue

        # Detect date
        if journal_date is None and is_date_line(text):
            journal_date = text
            continue

        text_lower = text.lower()

        # Filter out junk
        if text.isdigit():
            continue
        if len(text.split()) <= 2:
            continue

        # Split into sentences and filter again
        doc = nlp(text)
        for sent in doc.sents:
            s = sent.text.strip()
            if len(s.split()) <= 2:  # too short after splitting
                continue
            if s.isdigit():
                continue

            valid_sentences.append(s)

    if journal_date is None:
        journal_date = "unknown"

    # Group into categories
    category_map = {}
    for sent in valid_sentences:
        cat = classify_text_to_category(sent)
        category_map.setdefault(cat, []).append(sent)

    sections = [{"normalized_category": cat, "content_lines": sents}
                for cat, sents in category_map.items()]

    return {
        "journal_date": journal_date,
        "sections": sections
    }


# Debug
if __name__ == "__main__":
    sample = [
        ["06/10/2025"],
        ["God's Word", "", "Israel people groaned to God.\nGod listened their cry and remebered\nthe promise he made with Abraham,Issac and Jacob\nand knew it's time to act."],
        ["Concepts", "CSS Flexbox > Introduction to CSS Flexbox | Part 2 - Flex wrap"],
        ["Problems", "CSS Flexbox > Coding Practice 2\nCoding pratice 3"],
        ["Note", "8"]
    ]

    from pprint import pprint
    pprint(process_journal_lines(sample))
