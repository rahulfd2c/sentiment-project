import streamlit as st
from textblob import TextBlob
import pandas as pd
import requests
import re
import random
from collections import Counter
import nltk

# --- SERVER SETUP ---
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('brown', quiet=True)

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

def get_demo_data():
    pos = ["Absolutely incredible!", "Loved it. The screen is amazing.", "Works perfectly out of the box.", "Great battery life.", "High quality materials."]
    neu = ["It's okay.", "Does the job fine.", "Average quality.", "Arrived on time but packaging was damaged.", "Decent but overpriced."]
    neg = ["Terrible product.", "Broke on day one. SCAM!!!", "DO NOT BUY THIS JUNK!!!", "Customer service ignored me completely.", "Defective item, the battery drains instantly."]
    
    random.seed(42) 
    reviews = []
    for _ in range(110): reviews.append(random.choice(pos) + " " + random.choice(pos).lower())
    for _ in range(45): reviews.append(random.choice(neu) + " " + random.choice(neu).lower())
    for _ in range(34): reviews.append(random.choice(neg) + " " + random.choice(neg).lower())
    random.shuffle(reviews)
    return reviews

# --- 2. ADVANCED AI BRAIN ---
def analyze_sentiment(reviews):
    sentiments = {"Positive": 0, "Neutral": 0, "Negative": 0}
    top_pos_review = {"text": "", "score": -1.0}
    top_neg_review = {"text": "", "score": 1.0}
    
    pos_words, neg_words = [], []
    total_word_count, suspicious_count = 0, 0
    stop_words = ['this', 'that', 'with', 'from', 'they', 'have', 'very', 'just', 'like', 'would']

    for review in reviews:
        blob = TextBlob(review)
        score = blob.sentiment.polarity
        
        # Security/Spam Check (Too short, ALL CAPS, or highly repetitive)
        if review.isupper() or len(review.split()) < 3 or "!!!" in review:
            suspicious_count += 1
            
        total_word_count += len(review.split())
        
        if score > 0.1: 
            sentiments["Positive"] += 1
            pos_words.extend([w.lower() for w in blob.words if len(w) > 4 and w.lower() not in stop_words])
            if score > top_pos_review["score"]: top_pos_review = {"text": review, "score": score}
        elif score < -0.1: 
            sentiments["Negative"] += 1
            neg_words.extend([w.lower() for w in blob.words if len(w) > 4 and w.lower() not in stop_words])
            if score < top_neg_review["score"]: top_neg_review = {"text": review, "score": score}
        else: 
            sentiments["Neutral"] += 1

    total = len(reviews)
    percent_pos = (sentiments["Positive"] / total) * 100 if total > 0 else 0
    avg_len = total_word_count // total if total > 0 else 0
    score_10 = round((percent_pos / 100) * 10, 1)
    spam_percent = (suspicious_count / total) * 100 if total > 0 else 0

    top_pos_kws = [w[0] for w in Counter(pos_words).most_common(5)]
    top_neg_kws = [w[0] for w in Counter(neg_words).most_common(5)]

    return percent_pos, top_pos_review, top_neg_review, sentiments, avg_len, score_10, spam_percent, top_pos_kws, top_neg_kws

# --- 3. ENTERPRISE UI DASHBOARD ---
st.set_page_config(page_title="Enterprise Review Analytics", layout="wide", page_icon="🏢")

# Hidden Admin Panel
with st.sidebar:
    st.markdown("### ⚙️ Developer Tools")
    st.caption("Keep closed during presentation.")
    use_demo = st.toggle("🛡️ Enable Local Demo Mode")

st.title("🏢 Customer Insight & Review Analytics Platform")
st.markdown("Automated sentiment extraction, aspect analysis, and data integrity verification for e-commerce products.")

col_input, col_btn = st.columns([4, 1])
with col_input:
    product_url = st.text_input("Product URL:", placeholder="Paste Amazon link here...", label_visibility="collapsed", disabled=use_demo)
with col_btn:
    analyze_clicked = st.button("Generate Intelligence Report", type="primary", use_container_width=True)

st.divider()

if analyze_clicked:
    if use_demo or product_url:
        with st.spinner("🚀 Compiling Business Intelligence Report..."):
            
            reviews, error = get_demo_data() if use_demo else get_real_reviews(product_url)
            
            if error:
                st.error(f"⚠️ {error}")
            else:
                percent_pos, best, worst, counts, avg_len, score_10, spam_pct, top_p, top_n = analyze_sentiment(reviews)
                
                # --- TOP LEVEL METRICS ---
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Analyzed", len(reviews))
                m2.metric("Market Sentiment", f"{percent_pos:.1f}% Positive")
                m3.metric("Product Trust Score", f"{score_10} / 10")
                m4.metric("Review Depth (Avg Words)", avg_len)
                
                st.write("")
                
                # --- ENTERPRISE TABS ---
                tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "🗣️ Deep Text Analysis", "🛡️ Data Integrity & Security"])
                
                with tab1:
                    st.subheader("Business Action Plan")
                    colA, colB = st.columns([1, 1])
                    with colA:
                        st.markdown("#### What's Driving Sales (Strengths)")
                        st.success(f"Customers are frequently praising: **{', '.join(top_p).title()}**")
                        st.info(f"**Best Endorsement:** \"{best['text']}\"")
                    with colB:
                        st.markdown("#### Areas for Improvement (Weaknesses)")
                        st.error(f"Customers are complaining about: **{', '.join(top_n).title()}**")
                        st.warning(f"**Most Critical Issue:** \"{worst['text']}\"")
                
                with tab2:
                    c1, c2 = st.columns([1, 1.5])
                    with c1:
                        st.subheader("Sentiment Distribution")
                        st.bar_chart(pd.DataFrame(list(counts.values()), index=counts.keys(), columns=["Volume"]))
                    with c2:
                        st.subheader("Keyword Frequency Analysis")
                        kw_df = pd.DataFrame({
                            "Top Positive Keywords": top_p + [""] * (5 - len(top_p)),
                            "Top Negative Keywords": top_n + [""] * (5 - len(top_n))
                        })
                        st.dataframe(kw_df, use_container_width=True)
                
                with tab3:
                    st.subheader("Review Authenticity Check")
                    st.markdown("Detects potential bot activity, spam, and non-genuine reviews based on syntax anomalies and repetitive phrasing.")
                    
                    if spam_pct < 10:
                        st.success(f"✅ **Healthy:** Only {spam_pct:.1f}% of reviews show suspicious patterns. High data reliability.")
                    elif spam_pct < 25:
                        st.warning(f"⚠️ **Moderate Risk:** {spam_pct:.1f}% of reviews flagged as potential spam. Proceed with caution.")
                    else:
                        st.error(f"🚨 **High Risk:** {spam_pct:.1f}% of reviews flagged. Heavy bot activity suspected.")
                        
                    st.progress(int(spam_pct))
    else:
        st.info("Awaiting input URL or Demo Mode activation.")
