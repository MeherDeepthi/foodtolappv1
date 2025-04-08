# live_symptom_api.py
from flask import Flask, request, jsonify
import pandas as pd
import pickle
import os
from food_to_ingredient_fetcher import get_ingredients

app = Flask(__name__)

# Symptoms to predict
symptoms = ["Bloating", "Abdominal Pain", "Diarrhea", "Constipation"]

# Load models
models = {}
for symptom in symptoms:
    path = os.path.join("C:/Users/mmdee/OneDrive/Desktop/Data Science/projects/foodtolappv1/models", f"{symptom.replace(' ', '_')}_model.pkl")
    with open(path, "rb") as f:
        models[symptom] = pickle.load(f)

# Ingredient list used in training (must match!)
ingredients = sorted([
    "chili", "coconut", "curd", "flattened_rice", "ghee", "ginger", "moong_dal",
    "mustard", "oil", "onion", "pepper", "peanuts", "potato", "rice", "salt",
    "semolina", "tamarind", "toor_dal", "tomato", "turmeric", "urad_dal", "green_gram"
])

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    food = data.get("food")
    user_ingredients = get_ingredients(food)

    ingredient_input = {ing: 1 if ing in user_ingredients else 0 for ing in ingredients}
    X = pd.DataFrame([ingredient_input])

    result = {}
    for symptom in symptoms:
        model = models[symptom]
        pred = model.predict(X)[0]
        if pred:
            coefs = pd.Series(model.coef_[0], index=ingredients)
            triggers = [ing for ing in user_ingredients if ing in coefs.index and coefs[ing] > 0]
            result[symptom] = {
                "likely": True,
                "trigger_ingredients": triggers
            }
        else:
            result[symptom] = {"likely": False}

    return jsonify(result)

@app.route("/top_triggers", methods=["GET"])
def top_triggers():
    importance = {}
    for symptom in symptoms:
        model = models[symptom]
        coefs = pd.Series(model.coef_[0], index=ingredients)
        importance[symptom] = coefs.abs().sort_values(ascending=False).head(5).to_dict()
    return jsonify(importance)

if __name__ == "__main__":
    app.run(debug=True)

