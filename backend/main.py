from sheets_reader import get_journal_rows
from nlp_engine import process_journal_lines
from habit_tracker import count_selected_habits_week
from nlp_engine import is_date_line  # Already exists in your file


rows=get_journal_rows()
print(rows)

def group_days_by_date(all_rows):
    grouped = []
    current_day = []

    for row in all_rows:
        # remove empty cells
        cleaned_cells = [cell.strip() for cell in row if cell and cell.strip()]

        if not cleaned_cells:
            continue

        first_value = cleaned_cells[0]

        # If first value is a date → new day starts
        if is_date_line(first_value):
            if current_day:
                grouped.append(current_day)
            current_day = [first_value]
        else:
            # Merge ALL meaningful cells into day
            current_day.extend(cleaned_cells)

    if current_day:
        grouped.append(current_day)

    return grouped


# ---- MAIN FLOW ----

all_rows = get_journal_rows()  # flat list of ALL rows in Sheet
day_blocks = group_days_by_date(all_rows)

print("\nGrouped Days:")
for d in day_blocks:
    print(d, "\n")

week_data = []
for day in day_blocks:
    processed = process_journal_lines(day)
    print("\nProcessed:", processed)
    week_data.append(processed)

habit_counts = count_selected_habits_week(week_data)
print("\nWEEKLY HABITS:")
print(habit_counts)
