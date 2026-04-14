import streamlit as st
from textblob import TextBlob
import pandas as pd
import requests
import re
import random
from collections import Counter
import time
import nltk
from datetime import datetime, timedelta

# --- SERVER SETUP ---
nltk.download('punkt', quiet=True)
nltk.download('brown', quiet=True)

# --- PAGE CONFIG ---
st.set_page_config(page_title="Customer Review Sentiment Analyzer", layout="wide", page_icon="📊")

# --- 1. DATA ENGINES ---
def get_asin_from_url(url):
    match = re.search(r"([A-Z0-9]{10})(?:[/?]|$)", url)
    return match.group(1) if match else None

def extract_all_reviews(data):
    found_reviews = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key.lower() in ['review', 'reviewtext', 'text', 'body', 'review_text']:
                if isinstance(value, str) and len(value) > 15:
                    found_reviews.append(value)
            else:
                found_reviews.extend(extract_all_reviews(value))
    elif isinstance(data, list):
        for item in data:
            found_reviews.extend(extract_all_reviews(item))
    return found_reviews

def get_real_reviews(url):
    asin = get_asin_from_url(url)
    if not asin:
        return None, "Invalid Amazon Link."

    api_url = "https://real-time-amazon-data.p.rapidapi.com/product-reviews"
    querystring = {
        "asin": asin,
        "country": "US",
        "sort_by": "TOP_REVIEWS",
        "star_rating": "ALL"
    }

    api_url = "https://real-time-amazon-data.p.rapidapi.com/product-reviews"
    querystring = {"asin":"B00939I7EK","country":"US","sort_by":"TOP_REVIEWS","star_rating":"ALL","verified_purchases_only":"false","images_or_videos_only":"false","current_format_only":"false"}

    headers = {
  "x-rapidapi-key": "07cad06a0amsh9baed78433f774ep14e4e5jsne01452ded97a",
  "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com",
  "Content-Type": "application/json"
}

    try:
        response = requests.get(api_url, headers=headers, params=querystring)

        if response.status_code != 200:
            return None, "API Key invalid or limit reached!"

        data = response.json()
        reviews = list(set(extract_all_reviews(data)))

        if not reviews:
            return None, "No text reviews found."

        return reviews, None

    except Exception as e:
        return None, f"Connection Error: {e}"

# --- ANALYSIS ---
def analyze_sentiment(reviews):
    sentiments = {"Positive": 0, "Neutral": 0, "Negative": 0}

    for review in reviews:
        score = TextBlob(review).sentiment.polarity
        if score > 0.1:
            sentiments["Positive"] += 1
        elif score < -0.1:
            sentiments["Negative"] += 1
        else:
            sentiments["Neutral"] += 1

    total = len(reviews)
    percent_pos = (sentiments["Positive"] / total) * 100 if total else 0
    return sentiments, percent_pos

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Developer Tools")
    use_demo = st.toggle("Demo Mode", value=True)

# --- RESPONSIVE TITLE ---
st.markdown("""
<style>
.responsive-title {
    text-align: center;
    font-weight: 700;
    font-size: clamp(1.8rem, 4vw, 3.2rem);
}

.responsive-subtitle {
    text-align: center;
    color: gray;
    font-size: clamp(0.9rem, 1.5vw, 1.3rem);
    margin-bottom: 20px;
}
</style>

<div class="responsive-title">📊 Customer Review Sentiment Analyzer</div>
<div class="responsive-subtitle">
Analyze customer reviews using AI-driven sentiment insights
</div>
""", unsafe_allow_html=True)

# --- INPUT ---
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    url = st.text_input("", placeholder="Paste product URL...")
    analyze = st.button("Analyze", use_container_width=True)

st.write("---")

# --- MAIN LOGIC ---
if analyze:
    if not url:
        st.error("Please enter a product URL")
    else:
        with st.spinner("Analyzing reviews..."):
            reviews = get_demo_data(url) if use_demo else get_real_reviews(url)[0]

            sentiments, percent_pos = analyze_sentiment(reviews)

            st.success(f"Analyzed {len(reviews)} reviews")

            c1, c2 = st.columns(2)
            c1.metric("Positive %", f"{percent_pos:.1f}%")
            c2.metric("Total Reviews", len(reviews))

            st.bar_chart(pd.DataFrame(sentiments.values(), index=sentiments.keys()))
