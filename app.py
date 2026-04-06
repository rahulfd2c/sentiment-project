def get_reviews(url):
    asin = get_asin_from_url(url)
    if not asin:
        return None, "Could not find a valid Amazon Product ID in that link."

    # 1. PASTE THE AMAZON53 URL HERE:
    api_url = "https://real-time-amazon-data.p.rapidapi.com/product-reviews"    
    # 2. PASTE THE QUERYSTRING HERE (but keep 'asin': asin so it stays dynamic):
    querystring = {"asin":"B00939I7EK","country":"US","sort_by":"TOP_REVIEWS","star_rating":"ALL","verified_purchases_only":"false","images_or_videos_only":"false","current_format_only":"false"}

    # 3. PASTE THE HEADERS HERE:
    headers =  {
	"x-rapidapi-key": "07cad06a0amsh9baed78433f774ep14e4e5jsne01452ded97a",
	"x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com",
	"Content-Type": "application/json"
}

    try:
        response = requests.get(api_url, headers=headers, params=querystring)
        data = response.json() # This translates the API response into a Python dictionary
        
        # --- THE JSON PARSING PUZZLE ---
        # Every API hides the reviews under different names. 
        # For example, Amazon53 might call it data['reviews'] instead of data['result'].
        
        reviews = []
        
        # YOU MIGHT NEED TO CHANGE 'result' and 'review' BASED ON AMAZON53'S FORMAT
        for item in data.get('result', []): 
            if 'review' in item:
                reviews.append(item['review'])
                
        if not reviews:
            return None, "No reviews found. We might need to check the JSON format."
            
        return reviews, None
        
    except Exception as e:
        return None, f"API Connection Error: {e}"
