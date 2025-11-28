import os

folders = [
    "notebooks",
    "backend",
    "db/migration_tools",
    "logs",
    "scheduler",
    "utils"
]

files = {
    "backend/main.py": "",
    "backend/nlp_engine.py": "",
    "backend/ai_insights.py": "",
    "backend/sheets_reader.py": "",
    "backend/weekly_update.py": "",
    "backend/monthly_update.py": "",
    "backend/config.py": "",
    "db/db_connect.py": "",
    "db/create_tables.sql": "",
    "db/queries.py": "",
    "scheduler/weekly_cron.py": "",
    "scheduler/monthly_cron.py": "",
    "scheduler/run_once.py": "",
    "utils/helpers.py": "",
    "utils/category_map.json": "{}",
    "requirements.txt": "",
    "README.md": "",
    ".gitignore": ""
}

for folder in folders:
    os.makedirs(folder, exist_ok=True)

for file_path, content in files.items():
    with open(file_path, "w") as f:
        f.write(content)

print("🚀 Folder structure created successfully!")
