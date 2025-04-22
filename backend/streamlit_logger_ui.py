# streamlit_logger_ui.py
import streamlit as st
import pandas as pd
import requests
import datetime
import sqlite3
import os

st.set_page_config(page_title="Food Symptom Tracker", layout="centered")
st.title("🥗 Meal Logger & Trigger Predictor")

# Input user ID and food name
st.subheader("1. Enter Your Meal")
user_id = st.text_input("User ID (optional, default: guest)", "guest")
food = st.text_input("Food Name (e.g., Pongal, Sambar, Dosa)", "")

# Predict symptoms button
if st.button("🔍 Predict Symptoms") and food:
    try:
        res = requests.post("http://127.0.0.1:5000/predict", json={"food": food})
        if res.status_code == 200:
            result = res.json()
            st.success("✅ Prediction received!")

            # Display predictions
            all_ingredients = []
            summary = {
                "user_id": user_id,
                "Date": str(datetime.datetime.now().date()),
                "Food": food
            }

            for symptom, details in result.items():
                if details["likely"]:
                    st.error(f"⚠️ {symptom} likely")
                    triggers = details.get("trigger_ingredients", [])
                    st.markdown(f"🔍 Trigger Ingredients: `{', '.join(triggers)}`")
                    all_ingredients.extend(triggers)
                    summary[symptom] = "Likely"
                    summary[f"{symptom}_Triggers"] = ", ".join(triggers)
                else:
                    st.success(f"✅ {symptom} unlikely")
                    summary[symptom] = "Unlikely"
                    summary[f"{symptom}_Triggers"] = ""

            summary["Ingredients"] = ", ".join(sorted(set(all_ingredients)))

            # Save log to SQLite
            try:
                DB_PATH = os.path.join(os.path.dirname(__file__), "meal_logs.db")
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO meal_logs (
                        user_id, Date, Food, Ingredients,
                        Bloating, Bloating_Triggers,
                        Abdominal_Pain, Abdominal_Pain_Triggers,
                        Diarrhea, Diarrhea_Triggers,
                        Constipation, Constipation_Triggers
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    summary["user_id"],
                    summary["Date"],
                    summary["Food"],
                    summary["Ingredients"],
                    summary.get("Bloating", ""),
                    summary.get("Bloating_Triggers", ""),
                    summary.get("Abdominal_Pain", ""),
                    summary.get("Abdominal_Pain_Triggers", ""),
                    summary.get("Diarrhea", ""),
                    summary.get("Diarrhea_Triggers", ""),
                    summary.get("Constipation", ""),
                    summary.get("Constipation_Triggers", "")
                ))
                conn.commit()
                conn.close()
                st.info("📁 Meal and prediction saved to SQLite!")
            except Exception as e:
                st.error(f"🔥 Failed to save to database: {e}")

        else:
            st.error("❌ Prediction failed from API")
    except Exception as e:
        st.error(f"🔥 Error: {e}")

# View trends section
st.subheader("2. Symptom Trends and Triggers")
if st.button("📊 Show Stats"):
    try:
        DB_PATH = os.path.join(os.path.dirname(__file__), "meal_logs.db")
        conn = sqlite3.connect(DB_PATH)
        df_log = pd.read_sql_query("SELECT * FROM meal_logs", conn)
        conn.close()

        if not df_log.empty:
            st.markdown("### Symptom Frequency")
            symptom_counts = {}
            for col in ["Bloating", "Abdominal_Pain", "Diarrhea", "Constipation"]:
                symptom_counts[col] = (df_log[col] == "Likely").sum()
            st.bar_chart(symptom_counts)

            st.markdown("### Top Trigger Ingredients")
            triggers = df_log[[col for col in df_log.columns if col.endswith("_Triggers")]]
            flat = triggers.values.flatten().tolist()
            flat = [x.strip() for x in flat if isinstance(x, str) and x.strip()]
            top_triggers = pd.Series(flat).value_counts().head(10)
            st.bar_chart(top_triggers)

        else:
            st.info("📭 No data yet. Log a meal first.")
    except Exception as e:
        st.error(f"Failed to load or plot data: {e}")

# Personalized trigger suggestion
st.subheader("3. Personalized Triggers (Beta)")
if st.button("💡 Analyze My Triggers"):
    try:
        DB_PATH = os.path.join(os.path.dirname(__file__), "meal_logs.db")
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM meal_logs WHERE user_id = ?", conn, params=(user_id,))
        conn.close()

        st.markdown(f"Showing results for **user: {user_id}**")
        if df.empty:
            st.warning("No data found for this user.")
        else:
            for symptom in ["Bloating", "Abdominal_Pain", "Diarrhea", "Constipation"]:
                symptom_df = df[df[symptom] == "Likely"]
                all_symptom_triggers = symptom_df[f"{symptom}_Triggers"].dropna().tolist()
                all_symptom_triggers = [i.strip() for sublist in all_symptom_triggers for i in sublist.split(",") if i.strip()]
                if all_symptom_triggers:
                    counts = pd.Series(all_symptom_triggers).value_counts()
                    st.markdown(f"#### Top triggers for {symptom.replace('_', ' ')}")
                    st.bar_chart(counts.head(10))
                else:
                    st.info(f"No trigger patterns found yet for {symptom.replace('_', ' ')}.")
    except Exception as e:
        st.error(f"Failed to generate personalized triggers: {e}")
