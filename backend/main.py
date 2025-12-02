import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sheets_reader import get_journal_rows
from nlp_engine import process_journal_lines, is_date_line
from habit_tracker import count_selected_habits_week
from db.db_connect import (
    init_database,
    insert_raw_day,
    insert_processed_section,
    insert_weekly_stats
)



def group_days_by_date(all_rows):
    grouped = []
    current_day = []

    for row in all_rows:
        cleaned_cells = [cell.strip() for cell in row if cell and str(cell).strip()]

        if not cleaned_cells:
            continue

        first_value = cleaned_cells[0]

        # Detect new day when date appears
        if is_date_line(first_value):
            if current_day:
                grouped.append(current_day)
            current_day = cleaned_cells[:]  # include date + content
        else:
            current_day.extend(cleaned_cells)

    if current_day:
        grouped.append(current_day)

    return grouped


# ---------------- MAIN EXECUTION ---------------- #

print("\n📌 Starting Journal Processing Pipeline...")

# Initialize DB (create tables if not exist)
init_database()

# 1️⃣ Load from Google Sheets
all_rows = get_journal_rows()

# 2️⃣ Group rows by date into days
grouped_days = group_days_by_date(all_rows)
print(f"✔ Grouped {len(grouped_days)} days")

# 3️⃣ Process NLP categorization for each day
processed_days = []
for day in grouped_days:
    result = process_journal_lines(day)
    processed_days.append(result)

print(f"✔ Processed NLP for {len(processed_days)} days")

# 4️⃣ Weekly habit statistics
weekly_stats = count_selected_habits_week(processed_days)
print("✔ Weekly Habit Stats Generated")


# ---------------- SAVE TO DATABASE ---------------- #

print("\n💾 Saving data into database...")

# Save raw grouped days
for day in grouped_days:
    journal_date = day[0]
    merged_content = day[1:]
    insert_raw_day(journal_date, merged_content)

print("✔ Raw day data saved")

# Save processed sections (category + content list)
for day in processed_days:
    journal_date = day["journal_date"]
    for section in day["sections"]:
        insert_processed_section(
            journal_date,
            section["normalized_category"],
            section["content_lines"]
        )

print("✔ Processed categorized data saved")

# Save weekly stats (skip 0 count categories)
for (year, week), stats in weekly_stats.items():
    for category, count in stats.items():
        if count > 0:  # Only store if user actually did that habit
            insert_weekly_stats(year, week, category, count)

print("✔ Weekly habit stats saved (only non-zero categories)")



# ---------------- OUTPUT FOR DEBUG ---------------- #

print("\n📌 FINAL OUTPUT ------")
print("1️⃣ GROUPED DAYS:")
print(grouped_days)

print("\n2️⃣ PROCESSED DAYS:")
print(processed_days)

print("\n3️⃣ WEEKLY HABIT STATS:")
print(weekly_stats)

print("\n🎯 All data successfully processed and stored in DB!")
