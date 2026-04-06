import streamlit as st
from textblob import TextBlob
import pandas as pd
import requests
import re

# --- 1. THE SMART DATA ENGINE ---
def get_asin_from_url(url):
    """Extracts the unique Amazon Product ID."""
    match = re.search(r"([A-Z0-9]{10})(?:[/?]|$)", url)
    if match:
        return match.group(1)
    return None

def extract_all_reviews(data):
    """A heat-seeking missile that finds reviews in ANY Api format."""
    found_reviews = []
    if isinstance(data, dict):
        for key, value in data.items():
            # Look for keys commonly used for review text
            if key.lower() in ['review', 'reviewtext', 'text', 'body', 'review_text']:
                if isinstance(value, str) and len(value) > 15: # Ignore short useless strings
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

    # RapidAPI Amazon53 Setup
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
        
        # Use the smart extractor
        reviews = extract_all_reviews(data)
        
        # Remove duplicates just in case the API sends them twice
        reviews = list(set(reviews))
        
        if len(reviews) == 0:
            return None, "No text reviews found for this specific product."
            
        return reviews, None
        
    except Exception as e:
        return None, f"Connection Error: {e}"

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

# Layout: Search bar and button next to each other
col_input, col_btn = st.columns([4, 1])
with col_input:
    product_url = st.text_input("Amazon URL:", placeholder="https://www.amazon.com/dp/B08N5WRWNW", label_visibility="collapsed")
with col_btn:
    analyze_clicked = st.button("Generate Dashboard", type="primary", use_container_width=True)

st.divider()

if analyze_clicked:
    if product_url:
        with st.spinner("🚀 Scraping live data from Amazon..."):
            
            reviews, error = get_real_reviews(product_url)
            
            if error:
                st.error(f"⚠️ {error}")
            else:
                percent_positive, best, worst, sentiment_counts = analyze_sentiment(reviews)
                
                # --- DASHBOARD LAYOUT ---
                st.success(f"Successfully analyzed {len(reviews)} real reviews!")
                
                # Top Row Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Reviews Scraped", len(reviews))
                m2.metric("Overall Sentiment", f"{percent_positive:.1f}% Positive")
                m3.metric("Neutral / Mixed", f"{sentiment_counts['Neutral']} Reviews")
                
                st.write("") # Spacing
                
                # Bottom Row Charts & Text
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
        st.warning("Paste a link first!")
