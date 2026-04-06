import streamlit as st
from textblob import TextBlob
import pandas as pd

# --- 1. MOCK SCRAPER ---
def get_reviews(url):
    return [
        "Absolutely love this product! It changed my life and works perfectly.",
        "It's pretty good, does the job well enough.",
        "Terrible experience. It broke after two days and the seller ignored me.",
        "Not bad, but a bit overpriced for what you get.",
        "Best purchase I've made all year. Highly recommend!",
        "The battery life is awful. Do not buy this.",
        "Decent quality, arrived on time."
    ]

# --- 2. SENTIMENT BRAIN ---
def analyze_sentiment(reviews):
    sentiments = {"Positive": 0, "Neutral": 0, "Negative": 0}
    top_pos_review = {"text": "", "score": -1.0}
    top_neg_review = {"text": "", "score": 1.0}

    for review in reviews:
        score = TextBlob(review).sentiment.polarity
        
        # Categorize for the chart
        if score > 0.1:
            sentiments["Positive"] += 1
        elif score < -0.1:
            sentiments["Negative"] += 1
        else:
            sentiments["Neutral"] += 1
            
        # Find extremes
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

product_url = st.text_input("Enter Product Link:", placeholder="https://www.amazon.com/...")

if st.button("Analyze Reviews", type="primary"):
    if product_url:
        with st.spinner("Extracting and analyzing reviews..."):
            # Process data
            reviews = get_reviews(product_url)
            percent_positive, best, worst, sentiment_counts = analyze_sentiment(reviews)
            
            st.success("Analysis Complete!")
            
            # Create two columns for a professional dashboard look
            col1, col2 = st.columns(2)
            
            with col1:
                st.header(f"Overall Sentiment: {percent_positive:.0f}% Positive")
                st.progress(int(percent_positive))
                
                # Generate a Bar Chart using Pandas
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
