import streamlit as st
from textblob import TextBlob
import pandas as pd
import requests
import re
import random
from collections import Counter
import nltk # <--- ADD THIS

# --- DOWNLOAD THE DICTIONARY FOR THE CLOUD ---
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('brown', quiet=True)

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
        return None, "Invalid Amazon Link. Make sure it contains the product ID."

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
            return None, "API Key invalid or you hit your free limit!"
            
        data = response.json()
        reviews = extract_all_reviews(data)
        reviews = list(set(reviews))
        
        if len(reviews) == 0:
            return None, "No text reviews found for this product."
            
        return reviews, None
    except Exception as e:
        return None, f"Connection Error: {e}"

# --- THE LIFESAVER: 189 MIXED DEMO REVIEWS ---
def get_demo_data():
    pos_phrases = ["Absolutely incredible!", "Loved it.", "Works perfectly out of the box.", "Highly recommend to everyone.", "Great quality for the price.", "Exceeded my expectations.", "Will definitely buy again.", "Five stars all the way!"]
    neu_phrases = ["It's okay.", "Does the job fine.", "Nothing special.", "Average quality.", "Arrived on time.", "Decent but a bit overpriced.", "Not bad, but not great either."]
    neg_phrases = ["Terrible product.", "Broke on day one.", "Do not buy this.", "Complete waste of money.", "Customer service ignored me.", "Very disappointed.", "Defective item."]
    
    random.seed(42) # Keeps the generation consistent
    reviews = []
    
    # Generate 189 total reviews (110 Pos, 45 Neu, 34 Neg)
    for _ in range(110): reviews.append(random.choice(pos_phrases) + " " + random.choice(pos_phrases).lower())
    for _ in range(45): reviews.append(random.choice(neu_phrases) + " " + random.choice(neu_phrases).lower())
    for _ in range(34): reviews.append(random.choice(neg_phrases) + " " + random.choice(neg_phrases).lower())
    
    random.shuffle(reviews)
    return reviews

# --- 2. THE SENTIMENT & METRICS BRAIN ---
def analyze_sentiment(reviews):
    sentiments = {"Positive": 0, "Neutral": 0, "Negative": 0}
    top_pos_review = {"text": "No positive reviews", "score": -1.0}
    top_neg_review = {"text": "No negative reviews", "score": 1.0}
    
    all_words = []
    total_word_count = 0

    for review in reviews:
        blob = TextBlob(review)
        score = blob.sentiment.polarity
        
        # Dashboard Metric 1: Track words for keywords (ignoring short words)
        for word in blob.words:
            if len(word) > 5:
                all_words.append(word.lower())
                
        # Dashboard Metric 2: Track length
        total_word_count += len(review.split())
        
        if score > 0.1: sentiments["Positive"] += 1
        elif score < -0.1: sentiments["Negative"] += 1
        else: sentiments["Neutral"] += 1
            
        if score > top_pos_review["score"]: top_pos_review = {"text": review, "score": score}
        if score < top_neg_review["score"]: top_neg_review = {"text": review, "score": score}

    total = len(reviews)
    percent_positive = (sentiments["Positive"] / total) * 100 if total > 0 else 0
    
    # Calculate new dashboard metrics
    avg_length = total_word_count // total if total > 0 else 0
    common_words = [w[0] for w in Counter(all_words).most_common(5)]
    score_out_of_10 = round((percent_positive / 100) * 10, 1)

    return percent_positive, top_pos_review, top_neg_review, sentiments, avg_length, common_words, score_out_of_10

# --- 3. THE FINAL DASHBOARD UI ---
st.set_page_config(page_title="AI Review Analyzer", layout="wide", page_icon="📈")

# --- HIDDEN ADMIN SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Admin Settings")
    st.caption("Close this sidebar during presentation.")
    use_demo = st.toggle("🛡️ Use Offline Demo Mode")

# --- MAIN APP ---
st.title("📈 Live Product Sentiment Dashboard")
st.markdown("Enter any Amazon product link to extract real customer reviews and generate an instant AI sentiment analysis.")

col_input, col_btn = st.columns([4, 1])
with col_input:
    product_url = st.text_input("Amazon URL:", placeholder="https://www.amazon.com/dp/B08N5WRWNW", label_visibility="collapsed", disabled=use_demo)
with col_btn:
    analyze_clicked = st.button("Get Review Sentiment", type="primary", use_container_width=True)

st.divider()

if analyze_clicked:
    if use_demo or product_url:
        with st.spinner("🚀 Analyzing data..."):
            
            if use_demo:
                reviews = get_demo_data()
                error = None
            else:
                reviews, error = get_real_reviews(product_url)
            
            if error:
                st.error(f"⚠️ {error}")
            else:
                percent_pos, best, worst, counts, avg_len, top_words, score_10 = analyze_sentiment(reviews)
                
                if use_demo:
                    st.success("✅ Dashboard generated successfully (Demo Mode Active).")
                else:
                    st.success(f"✅ Successfully analyzed {len(reviews)} live reviews!")
                
                # --- NEW EXTENDED DASHBOARD ---
                # Row 1: Primary Metrics
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Reviews Scraped", len(reviews))
                m2.metric("Overall Sentiment", f"{percent_pos:.1f}% Positive")
                m3.metric("Trust Score", f"{score_10} / 10")
                m4.metric("Avg. Review Length", f"{avg_len} words")
                
                st.write("") 
                
                # Row 2: Charts and Text
                c1, c2 = st.columns([1, 1.5])
                with c1:
                    st.subheader("📊 Sentiment Breakdown")
                    chart_data = pd.DataFrame(
                        list(counts.values()), 
                        index=counts.keys(), 
                        columns=["Count"]
                    )
                    # Using Streamlit's built in color mapping
                    st.bar_chart(chart_data)
                    
                    st.subheader("🔑 Frequent Keywords")
                    st.write(", ".join(top_words).title() if top_words else "Not enough data.")
                    
                with c2:
                    st.subheader("🌟 Top Positive Review")
                    st.info(f'"{best["text"]}"')
                    
                    st.subheader("⚠️ Top Negative Review")
                    st.error(f'"{worst["text"]}"')
    else:
        st.warning("Paste a link first!")
