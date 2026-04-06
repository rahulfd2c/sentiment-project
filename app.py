import streamlit as st
from textblob import TextBlob
import pandas as pd
import requests
import re

# --- 1. THE DATA ENGINES ---
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
        return None, "Invalid Amazon Link. Make sure it contains the product ID (e.g., B08N5WRWNW)."

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
            return None, "API Key invalid or you hit your free limit for the month!"
            
        data = response.json()
        reviews = extract_all_reviews(data)
        reviews = list(set(reviews))
        
        if len(reviews) == 0:
            return None, "No text reviews found for this specific product."
            
        return reviews, None
    except Exception as e:
        return None, f"Connection Error: {e}"

# --- THE LIFESAVER: OFFLINE DEMO DATA ---
def get_demo_data():
    return [
        "Absolutely incredible! The build quality is fantastic and it arrived a day early. 5 stars!",
        "It's decent. Does exactly what it says on the box, nothing more, nothing less.",
        "Terrible product. It broke within 10 minutes of taking it out of the package. Do not buy.",
        "I bought this for my daughter and she loves it. The color is vibrant and it feels sturdy.",
        "Overpriced garbage. You can find better quality at a dollar store. Customer service ignored me.",
        "A bit smaller than I expected, but it gets the job done. Good value for the money.",
        "Best purchase I have made all year! Highly recommend to anyone looking for one of these.",
        "The battery life is an absolute joke. It died after an hour of use.",
        "It's okay. The instructions were really confusing, but once I figured it out it worked fine.",
        "Completely defective right out of the box. I am demanding a refund immediately.",
        "Exceeded all my expectations! The software is smooth and it pairs instantly with my phone.",
        "Average. Not the best, not the worst.",
        "Horrible design. Who thought it was a good idea to put the power button on the bottom?",
        "Beautifully packaged and works flawlessly. I will be buying another one as a gift.",
        "The screen scratches way too easily. Very disappointed in the durability."
    ]

# --- 2. THE SENTIMENT BRAIN ---
def analyze_sentiment(reviews):
    sentiments = {"Positive": 0, "Neutral": 0, "Negative": 0}
    top_pos_review = {"text": "No positive reviews", "score": -1.0}
    top_neg_review = {"text": "No negative reviews", "score": 1.0}

    for review in reviews:
        score = TextBlob(review).sentiment.polarity
        
        if score > 0.1:
            sentiments["Positive"] += 1
        elif score < -0.1:
            sentiments["Negative"] += 1
        else:
            sentiments["Neutral"] += 1
            
        if score > top_pos_review["score"]:
            top_pos_review = {"text": review, "score": score}
        if score < top_neg_review["score"]:
            top_neg_review = {"text": review, "score": score}

    total = len(reviews)
    percent_positive = (sentiments["Positive"] / total) * 100 if total > 0 else 0
    return percent_positive, top_pos_review, top_neg_review, sentiments

# --- 3. THE FINAL DASHBOARD UI ---
st.set_page_config(page_title="AI Review Analyzer", layout="wide", page_icon="📈")

st.title("📈 Live Product Sentiment Dashboard")
st.markdown("Enter any Amazon product link to extract real customer reviews and generate an instant AI sentiment analysis.")

# --- THE TOGGLE SWITCH ---
use_demo = st.toggle("🛡️ Use Offline Demo Mode (For Presentations)")

col_input, col_btn = st.columns([4, 1])
with col_input:
    # Disable the input box if Demo Mode is on
    product_url = st.text_input("Amazon URL:", placeholder="https://www.amazon.com/dp/B08N5WRWNW", label_visibility="collapsed", disabled=use_demo)
with col_btn:
    analyze_clicked = st.button("Generate Dashboard", type="primary", use_container_width=True)

st.divider()

if analyze_clicked:
    if use_demo or product_url:
        with st.spinner("🚀 Analyzing data..."):
            
            # Decide where to get the data
            if use_demo:
                reviews = get_demo_data()
                error = None
            else:
                reviews, error = get_real_reviews(product_url)
            
            if error:
                st.error(f"⚠️ {error}")
            else:
                percent_positive, best, worst, sentiment_counts = analyze_sentiment(reviews)
                
                if use_demo:
                    st.success("✅ Dashboard generated using Offline Demo Data.")
                else:
                    st.success(f"✅ Successfully analyzed {len(reviews)} live reviews!")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Reviews Scraped", len(reviews))
                m2.metric("Overall Sentiment", f"{percent_positive:.1f}% Positive")
                m3.metric("Neutral / Mixed", f"{sentiment_counts['Neutral']} Reviews")
                
                st.write("") 
                
                c1, c2 = st.columns([1, 1.5])
                with c1:
                    st.subheader("📊 Sentiment Distribution")
                    chart_data = pd.DataFrame(
                        list(sentiment_counts.values()), 
                        index=sentiment_counts.keys(), 
                        columns=["Count"]
                    )
                    st.bar_chart(chart_data, color="#2ecc71")
                    
                with c2:
                    st.subheader("🌟 Top Positive Review")
                    st.info(f'"{best["text"]}"')
                    
                    st.subheader("⚠️ Top Negative Review")
                    st.error(f'"{worst["text"]}"')
    else:
        st.warning("Paste a link or enable Demo Mode first!")
