from flask import Flask, request, jsonify
import pandas as pd
import pickle
import os

app = Flask(__name__)

# Symptoms to predict
symptoms = ["Bloating", "Abdominal Pain", "Diarrhea", "Constipation"]

# Load models
models = {}
for symptom in symptoms:
    path = os.path.join("../models", f"{symptom.replace(' ', '_')}_model.pkl")
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
    user_input = {ing: 0 for ing in ingredients}
    for ing in data.get("ingredients", []):
        if ing in user_input:
            user_input[ing] = 1

    X = pd.DataFrame([user_input])
    result = {symptom: int(models[symptom].predict(X)[0]) for symptom in symptoms}
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
