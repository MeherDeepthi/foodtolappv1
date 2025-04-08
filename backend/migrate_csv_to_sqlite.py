# migrate_csv_to_sqlite.py
import pandas as pd
import sqlite3
import os

# Paths
csv_path = "../data/meal_logs.csv"
db_path = "../backend/meal_logs.db"

# Load CSV if it exists
if not os.path.exists(csv_path):
    print("❌ CSV file not found.")
    exit()

df = pd.read_csv(csv_path)

# Add user_id column (default to 'guest') if not exists
if "user_id" not in df.columns:
    df["user_id"] = "guest"

# Create or connect to SQLite DB
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the table
columns = [
    "user_id TEXT",
    "Date TEXT",
    "Food TEXT",
    "Ingredients TEXT",
    "Bloating TEXT",
    "Bloating_Triggers TEXT",
    "Abdominal_Pain TEXT",
    "Abdominal_Pain_Triggers TEXT",
    "Diarrhea TEXT",
    "Diarrhea_Triggers TEXT",
    "Constipation TEXT",
    "Constipation_Triggers TEXT"
]
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS meal_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    {', '.join(columns)}
)
""")

# Insert rows
for _, row in df.iterrows():
    cursor.execute(f"""
        INSERT INTO meal_logs (
            user_id, Date, Food, Ingredients,
            Bloating, Bloating_Triggers,
            Abdominal_Pain, Abdominal_Pain_Triggers,
            Diarrhea, Diarrhea_Triggers,
            Constipation, Constipation_Triggers
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row.get("user_id", "guest"),
        row.get("Date", None),
        row.get("Food", None),
        row.get("Ingredients", None),
        row.get("Bloating", None),
        row.get("Bloating_Triggers", None),
        row.get("Abdominal Pain", None),
        row.get("Abdominal_Pain_Triggers", None),
        row.get("Diarrhea", None),
        row.get("Diarrhea_Triggers", None),
        row.get("Constipation", None),
        row.get("Constipation_Triggers", None)
    ))

conn.commit()
conn.close()

print("✅ CSV successfully migrated to SQLite (meal_logs.db)")
