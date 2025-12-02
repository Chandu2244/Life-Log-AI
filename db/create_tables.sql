-- Table 1: Raw Day Content (original input)
CREATE TABLE IF NOT EXISTS journal_day_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    journal_date TEXT NOT NULL UNIQUE,
    merged_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Processed Daily Sections (categorized content)
CREATE TABLE IF NOT EXISTS journal_day_processed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    journal_date TEXT NOT NULL,
    category TEXT NOT NULL,
    content_lines TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (journal_date) REFERENCES journal_day_raw (journal_date)
);

-- Table 3: Weekly Habit Summary (fast analytics)
CREATE TABLE IF NOT EXISTS weekly_habit_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    category TEXT NOT NULL,
    count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
