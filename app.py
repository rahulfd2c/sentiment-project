import streamlit as st
from textblob import TextBlob
import pandas as pd
import requests
import re

# --- 1. THE DATA ENGINE (REAL API) ---
def get_asin_from_url(url):
    """Extracts the 10-character Amazon Product ID from the URL."""
    match = re.search(r"([A-Z0-9]{10})(?:[/?]|$)", url)
    if match:
        return match.group(1)
    return None

def get_reviews(url):
    asin = get_asin_from_url(url)
    if not asin:
        return None, "Could not find a valid Amazon Product ID in that link."

    # This is the setup for a standard RapidAPI Amazon Scraper
    api_url = "https://real-time-amazon-data.p.rapidapi.com/product-reviews"
    querystring = {"asin":"B00939I7EK","country":"US","sort_by":"TOP_REVIEWS","star_rating":"ALL","verified_purchases_only":"false","images_or_videos_only":"false","current_format_only":"false"}

    headers = {
	"x-rapidapi-key": "07cad06a0amsh9baed78433f774ep14e4e5jsne01452ded97a",
	"x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com",
	"Content-Type": "application/json"
}


    try:
        response = requests.get(api_url, headers=headers, params=querystring)
        data = response.json()

		import streamlit as st
        st.warning("🔍 DEBUG MODE: Here is the raw data from the API:")
        st.json(data)
        
        # Extract just the text from the API's complex response
        reviews = []
        for item in data.get('result', []):
            if 'review' in item:
                reviews.append(item['review'])
                
        if not reviews:
            return None, "No reviews found or API limit reached."
            
        return reviews, None
        
    except Exception as e:
        return None, f"API Connection Error: {e}"

# --- 2. SENTIMENT BRAIN ---
def analyze_sentiment(reviews):
    sentiments = {"Positive": 0, "Neutral": 0, "Negative": 0}
    top_pos_review = {"text": "", "score": -1.0}
    top_neg_review = {"text": "", "score": 1.0}

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

    percent_positive = (sentiments["Positive"] / len(reviews)) * 100
    return percent_positive, top_pos_review, top_neg_review, sentiments

# --- 3. WEB INTERFACE & DASHBOARD ---
st.set_page_config(page_title="Review Sentiment Analyzer", layout="wide")
st.title("📊 Product Review Sentiment Analyzer")
st.markdown("Paste an Amazon product link below to generate a real-time sentiment dashboard.")

product_url = st.text_input("Enter Product Link:", placeholder="https://www.amazon.com/dp/B08N5WRWNW")

if st.button("Analyze Reviews", type="primary"):
    if product_url:
        with st.spinner("Connecting to Amazon API... This may take a few seconds."):
            
            # Fetch real data
            reviews, error = get_reviews(product_url)
            
            if error:
                st.error(error)
            else:
                percent_positive, best, worst, sentiment_counts = analyze_sentiment(reviews)
                
                st.success(f"Successfully analyzed {len(reviews)} live reviews!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.header(f"Overall Sentiment: {percent_positive:.0f}% Positive")
                    st.progress(int(percent_positive))
                    
                    st.subheader("Sentiment Distribution")
                    chart_data = pd.DataFrame(
                        list(sentiment_counts.values()), 
                        index=sentiment_counts.keys(), 
                        columns=["Number of Reviews"]
                    )
                    st.bar_chart(chart_data, color="#3498db")
                    
                with col2:
                    st.subheader("🌟 Top Positive Review")
                    st.info(f'"{best["text"]}" \n\n(Score: {best["score"]:.2f})')
                    
                    st.subheader("⚠️ Top Negative Review")
                    st.error(f'"{worst["text"]}" \n\n(Score: {worst["score"]:.2f})')
    else:
        st.warning("Please enter a URL first!")
