import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle
import os

# Load your dataset
df = pd.read_excel("food_symptom_data.xlsx")

# Define symptoms and features
symptoms = ["Bloating", "Abdominal Pain", "Diarrhea", "Constipation"]
features = list(df.columns[2:-4])  # Exclude Date, Meal, Symptoms

# Create output folder if not exists
os.makedirs("../models", exist_ok=True)

for symptom in symptoms:
    print(f"\n🔁 Training model for: {symptom}")

    X = df[features]
    y = (df[symptom] > 0).astype(int)  # Convert to binary (0 = no symptom, 1 = any severity)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # Evaluate
    print("✅ Classification Report:")
    print(classification_report(y_test, model.predict(X_test)))

    # Save model
    filename = f"../models/{symptom.replace(' ', '_')}_model.pkl"
    with open(filename, "wb") as f:
        pickle.dump(model, f)
    print(f"📦 Model saved: {filename}")
