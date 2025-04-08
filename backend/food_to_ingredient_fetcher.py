# food_to_ingredient_fetcher.py
import sqlite3
import requests

# Initialize or connect to database
conn = sqlite3.connect("food_ingredients.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS food_map (
    food TEXT PRIMARY KEY,
    ingredients TEXT
)
""")
conn.commit()

def get_from_db(food):
    food = food.lower()
    with sqlite3.connect("food_ingredients.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ingredients FROM food_map
            WHERE LOWER(food) = ? OR LOWER(translated_food) = ?
        """, (food, food))
        result = cursor.fetchone()
        return result[0].split(", ") if result else None

def save_to_db(food, ingredients):
    cursor.execute("REPLACE INTO food_map (food, ingredients) VALUES (?, ?)", (food.lower(), ", ".join(ingredients)))
    conn.commit()

# Try TheMealDB as free fallback API
def fetch_from_mealdb(food):
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={food}"
    try:
        response = requests.get(url)
        data = response.json()
        if data["meals"]:
            meal = data["meals"][0]
            ingredients = []
            for i in range(1, 21):
                ing = meal.get(f"strIngredient{i}")
                if ing and ing.strip():
                    ingredients.append(ing.strip().lower())
            return ingredients
    except:
        return None
    return None

# Main logic
def get_ingredients(food):
    # Step 1: Check local DB
    local_ings = get_from_db(food)
    if local_ings:
        print(f"✅ Found locally: {local_ings}")
        return local_ings

    # Step 2: Try fetching from MealDB
    print("🌐 Searching online...")
    online_ings = fetch_from_mealdb(food)
    if online_ings:
        print(f"🌟 Fetched from MealDB: {online_ings}")
        confirm = input("Save these ingredients? (y/n): ").lower()
        if confirm == 'y':
            save_to_db(food, online_ings)
        return online_ings

    print("❌ No ingredients found.")

    # Step 3: Ask user to enter manually
    manual = input("Would you like to add ingredients manually? (y/n): ").strip().lower()
    if manual == 'y':
        user_ings = input("Enter ingredients separated by comma: ").strip().lower().split(",")
        user_ings = [i.strip() for i in user_ings if i.strip()]
        save_to_db(food, user_ings)
        print(f"✅ Saved manually entered ingredients: {user_ings}")
        return user_ings

    return []

# Test it
if __name__ == "__main__":
    while True:
        f = input("\nEnter food name (or 'q' to quit): ").strip()
        if f.lower() == 'q':
            break
        get_ingredients(f)
