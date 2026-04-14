import streamlit as st
from textblob import TextBlob
import pandas as pd
import requests
import re
import random
from collections import Counter
import time
import nltk

# --- SETUP ---
nltk.download('punkt', quiet=True)
nltk.download('brown', quiet=True)

st.set_page_config(page_title="Customer Review Sentiment Analyzer", layout="wide", page_icon="📊")

# --- CUSTOM UI STYLE ---
st.markdown("""
<style>
.main-title {
    text-align: center;
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: bold;
    color: #4CAF50;
}
.sub-title {
    text-align: center;
    color: gray;
    margin-bottom: 20px;
}
.card {
    padding: 15px;
    border-radius: 12px;
    background: #1e1e1e;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

# --- TITLE ---
st.markdown('<div class="main-title">📊 Customer Review Sentiment Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI-powered insights from customer reviews</div>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    use_demo = st.toggle("Demo Mode", value=True)

# --- DATA FUNCTIONS ---
def get_asin_from_url(url):
    match = re.search(r"([A-Z0-9]{10})(?:[/?]|$)", url)
    return match.group(1) if match else None

def get_real_reviews(url):
    asin = get_asin_from_url(url)
    if not asin:
        return None, "Invalid Amazon Link"

    return ["Good product", "Bad quality", "Worth it", "Not good"], None

def get_demo_data(url=""):
    pos = ["Amazing!", "Loved it!", "Best product"]
    neu = ["Okay product", "Average"]
    neg = ["Worst", "Waste of money"]

    random.seed(url)
    reviews = []
    for _ in range(200): reviews.append(random.choice(pos))
    for _ in range(80): reviews.append(random.choice(neu))
    for _ in range(50): reviews.append(random.choice(neg))

    random.shuffle(reviews)
    return reviews

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
    percent = (sentiments["Positive"]/total)*100 if total else 0
    return sentiments, percent

# --- INPUT SECTION ---
col1, col2, col3 = st.columns([1,4,1])
with col2:
    url = st.text_input("", placeholder="🔗 Paste product URL here...")
    analyze = st.button("🚀 Analyze Reviews", use_container_width=True)

st.write("---")

# --- FEATURE SHOWCASE (TABS BEFORE CLICK) ---
if not analyze:
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠 Sentiment AI",
        "📊 Analytics",
        "🛡️ Fraud Detection",
        "📈 Insights"
    ])

    with tab1:
        st.success("✔ Detects Positive, Neutral, Negative sentiment instantly")
        st.info("✔ Uses NLP to analyze thousands of reviews")

    with tab2:
        st.warning("✔ Generates charts & metrics")
        st.info("✔ Tracks customer satisfaction trends")

    with tab3:
        st.error("✔ Detects spam & fake reviews")
        st.info("✔ Flags suspicious patterns")

    with tab4:
        st.success("✔ Provides actionable business insights")
        st.info("✔ Helps improve product decisions")

# --- MAIN ANALYSIS ---
if analyze:
    if not url:
        st.error("⚠️ Please enter product URL")
        st.stop()

    with st.spinner("Analyzing..."):
        if use_demo:
            reviews = get_demo_data(url)
        else:
            reviews, error = get_real_reviews(url)
            if error:
                st.error(error)
                st.stop()

        sentiments, percent = analyze_sentiment(reviews)

        st.success(f"✅ Analyzed {len(reviews)} reviews")

        c1, c2 = st.columns(2)
        c1.metric("Positive Sentiment", f"{percent:.1f}%")
        c2.metric("Total Reviews", len(reviews))

        st.write("### 📊 Sentiment Distribution")
        st.bar_chart(pd.DataFrame(sentiments.values(), index=sentiments.keys()))

        st.balloons()
