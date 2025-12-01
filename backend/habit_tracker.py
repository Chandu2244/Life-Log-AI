from datetime import datetime

TRACKED_CATEGORIES = [
    "spiritual", "learning", "coding", "fitness",
    "reading", "creativity", "hobby"
]

def count_selected_habits_week(journal_data):
    """
    journal_data: list of processed day results from process_journal_lines()
    Returns: weekly habit counts for selected categories only
    {(year, week): {category: count}}
    """
    weekly_habits = {}

    for day in journal_data:
        date_str = day.get("journal_date", "")
        if date_str == "unknown":
            continue

        try:
            date = datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            continue

        year, week, _ = date.isocalendar()
        week_key = (year, week)

        if week_key not in weekly_habits:
            weekly_habits[week_key] = {cat: 0 for cat in TRACKED_CATEGORIES}

        for section in day["sections"]:
            cat = section["normalized_category"]

            if cat in TRACKED_CATEGORIES and section["content_lines"]:
                weekly_habits[week_key][cat] += 1

    return weekly_habits
