# load_dataset_to_sqlite.py
import pandas as pd
import sqlite3

# Load Excel dataset
excel_path = "../data/IndianFoodDatasetXLS.xlsx"
df_xlsx = pd.read_excel(excel_path)
df_xlsx_filtered = df_xlsx[["RecipeName", "TranslatedRecipeName", "TranslatedIngredients"]].dropna()

# Load CSV dataset
csv_path = "../data/indian_food.csv"
df_csv = pd.read_csv(csv_path)
df_csv_filtered = df_csv[["name", "ingredients"]].dropna()

# Connect to or create SQLite database
conn = sqlite3.connect("../backend/food_ingredients.db")
cursor = conn.cursor()

# # Drop old table if it exists (fix schema issues)
# cursor.execute("DROP TABLE IF EXISTS food_map")

# Create the table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS food_map (
    food TEXT PRIMARY KEY,
    translated_food TEXT,
    ingredients TEXT
)
""")

# Insert data from Excel file
for _, row in df_xlsx_filtered.iterrows():
    try:
        cursor.execute("""
        INSERT OR REPLACE INTO food_map (food, translated_food, ingredients)
        VALUES (?, ?, ?)
        """, (
            row["RecipeName"].strip(),
            row["TranslatedRecipeName"].strip(),
            row["TranslatedIngredients"].strip()
        ))
    except Exception as e:
        print(f"Skipping Excel row due to error: {e}")

# Insert data from CSV file
for _, row in df_csv_filtered.iterrows():
    try:
        cursor.execute("""
        INSERT OR REPLACE INTO food_map (food, translated_food, ingredients)
        VALUES (?, ?, ?)
        """, (
            row["name"].strip(),
            row["name"].strip(),  # using name as translated_food too
            row["ingredients"].strip()
        ))
    except Exception as e:
        print(f"Skipping CSV row due to error: {e}")

conn.commit()
conn.close()
print("✅ Database successfully created and populated from both datasets!")
