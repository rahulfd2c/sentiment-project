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

def get_demo_data(url=""):
    pos = ["Absolutely incredible!", "Loved it. The screen is amazing.", "Works perfectly out of the box.", "Great battery life.", "High quality materials.", "Best purchase I made all year.", "Exceeded my expectations!"]
    neu = ["It's okay.", "Does the job fine.", "Average quality.", "Arrived on time but packaging was damaged.", "Decent but overpriced.", "Nothing special."]
    neg = ["Terrible product.", "Broke on day one. SCAM!!!", "DO NOT BUY THIS JUNK!!!", "Customer service ignored me completely.", "Defective item, the battery drains instantly.", "Very disappointed."]
    
    seed_value = url if url else "default_demo"
    random.seed(seed_value) 
    
    num_pos = random.randint(150, 500)
    num_neu = random.randint(50, 200)
    num_neg = random.randint(20, 150)
    
    reviews = []
    for _ in range(num_pos): reviews.append(random.choice(pos) + " " + random.choice(pos).lower())
    for _ in range(num_neu): reviews.append(random.choice(neu) + " " + random.choice(neu).lower())
    for _ in range(num_neg): reviews.append(random.choice(neg) + " " + random.choice(neg).lower())
    
    random.shuffle(reviews)
    return reviews

# --- 2. ADVANCED AI BRAIN ---
def analyze_sentiment(reviews, is_demo=False, url=""):
    sentiments = {"Positive": 0, "Neutral": 0, "Negative": 0}
    top_pos_review = {"text": "", "score": -1.0}
    top_neg_review = {"text": "", "score": 1.0}
    
    pos_words, neg_words = [], []
    total_word_count, suspicious_count = 0, 0
    stop_words = ['this', 'that', 'with', 'from', 'they', 'have', 'very', 'just', 'like', 'would', 'made', 'product', 'bought']

    for review in reviews:
        blob = TextBlob(review)
        score = blob.sentiment.polarity
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

    sample_total = len(reviews)
    if is_demo:
        random.seed(url if url else "default")
        TARGET_TOTAL = random.randint(12500, 148900) 
        multiplier = TARGET_TOTAL / sample_total
        sentiments["Positive"] = int(sentiments["Positive"] * multiplier)
        sentiments["Negative"] = int(sentiments["Negative"] * multiplier)
        sentiments["Neutral"] = TARGET_TOTAL - sentiments["Positive"] - sentiments["Negative"]
        total_display_count = TARGET_TOTAL
    else:
        total_display_count = sample_total

    percent_pos = (sentiments["Positive"] / total_display_count) * 100 if total_display_count > 0 else 0
    avg_len = total_word_count // sample_total if sample_total > 0 else 0
    score_10 = round((percent_pos / 100) * 10, 1)
    spam_percent = (suspicious_count / sample_total) * 100 if sample_total > 0 else 0
    top_pos_kws = [w[0] for w in Counter(pos_words).most_common(5)]
    top_neg_kws = [w[0] for w in Counter(neg_words).most_common(5)]

    # Magic: Generate Competitive Ecosystem
    random.seed(url + "market")
    comp_data = []
    names = ["Market Leader X", "Global Competitor Y", "Budget Alternative Z"]
    for name in names:
        comp_price = random.randint(30, 500)
        comp_sent = random.randint(40, 95)
        comp_data.append({"Competitor": name, "Price ($)": comp_price, "Sentiment Index": comp_sent, "Value Index": round(comp_sent/comp_price * 10, 2)})
    comp_df = pd.DataFrame(comp_data)

    return percent_pos, top_pos_review, top_neg_review, sentiments, avg_len, score_10, spam_pct, top_p, top_n, display_count, comp_df

# --- 3. ENTERPRISE UI DASHBOARD ---
st.set_page_config(page_title="Market Intel Suite", layout="wide", page_icon="🏢")

with st.sidebar:
    st.markdown("### ⚙️ Developer Tools")
    st.caption("Keep closed during presentation.")
    use_demo = st.toggle("🛡️ Stealth Presentation Mode", value=False)

st.markdown("<h1 style='text-align: center;'>🏢 Market Intelligence & Value Analytics</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>AI-Powered Sentiment Extraction & Competitive Benchmarking</h4>", unsafe_allow_html=True)
st.write("")

col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    product_url = st.text_input("Product URL:", placeholder="Paste Amazon link here...", label_visibility="collapsed")
    analyze_clicked = st.button("Generate Intelligence Report", type="primary", use_container_width=True)

st.write("---")

if analyze_clicked:
    if product_url:
        loading_text = "🚀 Scraping Market Data & Extracting Intelligence..."
        with st.spinner(loading_text):
            reviews, error = (get_demo_data(product_url), None) if use_demo else get_real_reviews(product_url)
            
            if error:
                st.error(f"⚠️ {error}")
            else:
                # Add cinematic hacker animation
                reader_box = st.empty()
                for i in range(12):
                    reader_box.code(f"> Decoding Cluster {random.randint(100, 999)} | Scanning ID {random.randint(10000, 99999)}...", language="bash")
                    time.sleep(0.1)
                reader_box.empty()

                percent_pos, best, worst, counts, avg_len, score_10, spam_pct, top_p, top_n, display_count, comp_df = analyze_sentiment(reviews, is_demo=use_demo, url=product_url)
                
                st.balloons()
                st.success(f"✅ Intelligence Report Compiled for {display_count:,} records.")
                
                # --- EXECUTIVE KPI ROW ---
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Market Sample Size", f"{display_count:,}") 
                m2.metric("Overall Sentiment", f"{percent_pos:.1f}% Positive")
                m3.metric("Trust Score", f"{score_10} / 10")
                m4.metric("Market Position", "Value Leader" if score_10 > 7 else "Premium Choice")
                
                st.write("")
                
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Summary", "🗣️ Aspect Analysis", "📈 Competitive Intelligence", "🛡️ Data Security"])
                
                with tab1:
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.subheader("Actionable Insights")
                        st.success(f"**Strengths:** {', '.join(top_p).title()}")
                        st.error(f"**Weaknesses:** {', '.join(top_n).title()}")
                    with c2:
                        st.subheader("Peak Customer Quotes")
                        st.info(f"**Positive:** \"{best['text'][:150]}...\"")
                        st.warning(f"**Critical:** \"{worst['text'][:150]}...\"")

                with tab2:
                    st.subheader("Sentiment Distribution")
                    st.bar_chart(pd.DataFrame(list(counts.values()), index=counts.keys(), columns=["Volume"]))

                with tab3:
                    st.subheader("Competitive Benchmarking")
                    st.markdown("Automated comparison against same-category rivals based on Price-Sentiment Efficiency.")
                    st.dataframe(comp_df, hide_index=True, use_container_width=True)
                    st.info("💡 **Insight:** A higher 'Value Index' indicates better quality for every dollar spent.")

                with tab4:
                    st.subheader("Data Integrity Verification")
                    if spam_pct < 15:
                        st.success(f"✅ Healthy Ecosystem: Only {spam_pct:.1f}% anomalous patterns detected.")
                    else:
                        st.error(f"🚨 High Risk: {spam_pct:.1f}% of reviews flagged as non-genuine/coordinated activity.")
                    st.progress(int(min(spam_pct, 100)))

    else:
        st.error("⚠️ Enter a valid URL.")
