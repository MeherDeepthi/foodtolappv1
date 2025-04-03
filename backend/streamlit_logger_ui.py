import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Food-Symptom Logger", layout="centered")
st.title("🥗 Log Your Meal & Predict Symptoms")

ingredients = sorted([
    "chili", "coconut", "curd", "flattened_rice", "ghee", "ginger", "moong_dal",
    "mustard", "oil", "onion", "pepper", "peanuts", "potato", "rice", "salt",
    "semolina", "tamarind", "toor_dal", "tomato", "turmeric", "urad_dal", "green_gram"
])

st.subheader("1. Select Ingredients in Your Meal")
selected = st.multiselect("Which ingredients did you eat today?", ingredients)

st.subheader("2. Get Prediction")
if st.button("🔍 Predict Symptoms"):
    try:
        res = requests.post("http://127.0.0.1:5000/predict", json={"ingredients": selected})
        if res.status_code == 200:
            result = res.json()
            st.success("Prediction received!")
            for symptom, val in result.items():
                if val:
                    st.error(f"⚠️ {symptom} likely")
                else:
                    st.success(f"✅ {symptom} unlikely")
        else:
            st.warning("Could not connect to API")
    except Exception as e:
        st.error(f"Error: {e}")

st.subheader("3. View Top Trigger Ingredients")
if st.button("📊 Show Triggers"):
    try:
        res = requests.get("http://127.0.0.1:5000/top_triggers")
        if res.status_code == 200:
            data = res.json()
            for symptom, items in data.items():
                st.markdown(f"**{symptom}**")
                for ing, score in items.items():
                    st.markdown(f"- {ing}: `{score:.3f}`")
        else:
            st.warning("Could not fetch trigger data")
    except Exception as e:
        st.error(f"Error: {e}")
