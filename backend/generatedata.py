import pandas as pd
import random

# Define meals and their ingredients
food_ingredient_map = {
    "Idli": ["rice", "urad_dal"],
    "Chutney": ["coconut", "chili", "salt"],
    "Sambar": ["toor_dal", "tamarind", "chili", "onion", "tomato"],
    "Upma": ["semolina", "mustard", "chili", "onion", "ghee"],
    "Curd Rice": ["rice", "curd", "mustard", "ghee"],
    "Pongal": ["rice", "moong_dal", "pepper", "ghee"],
    "Poha": ["flattened_rice", "peanuts", "mustard", "onion"],
    "Pesarattu": ["green_gram", "ginger", "onion", "chili"],
    "Dosa": ["rice", "urad_dal", "oil"],
    "Aloo Curry": ["potato", "chili", "onion", "turmeric"]
}

symptoms = ["Bloating", "Abdominal Pain", "Diarrhea", "Constipation"]

# Generate 30 days of sample data
records = []
for day in range(30):
    food_items = random.sample(list(food_ingredient_map), k=2)
    ingredients = set()
    for food in food_items:
        ingredients.update(food_ingredient_map[food])

    row = {ing: 1 for ing in ingredients}
    for ing in set(sum(food_ingredient_map.values(), [])):
        row.setdefault(ing, 0)

    for symptom in symptoms:
        row[symptom] = random.choices([0, 1, 2, 3], weights=[0.6, 0.2, 0.15, 0.05])[0]

    row["Date"] = pd.Timestamp("2025-03-01") + pd.Timedelta(days=day)
    row["Meal"] = " + ".join(food_items)
    records.append(row)

# Save to Excel
df = pd.DataFrame(records)
cols = ["Date", "Meal"] + sorted(set(sum(food_ingredient_map.values(), []))) + symptoms
df = df[cols]
df.to_excel("food_symptom_data.xlsx", index=False)

print("✅ Dataset saved as food_symptom_data.xlsx")
