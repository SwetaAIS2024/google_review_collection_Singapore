import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Placeholder for Google review crawling logic

def crawl_google_reviews(poi_url):
    """
    Crawl reviews for a given POI URL (to be implemented).
    """
    pass

def filter_top_reviewers(reviews, min_reviews=500):
    """
    Filter reviewers with more than min_reviews reviews.
    Args:
        reviews (list of dict): List of review dicts, each with a 'reviewer' key containing a dict with 'name' and 'review_count'.
        min_reviews (int): Minimum number of reviews to qualify.
    Returns:
        list of dict: Filtered list of reviewers.
    """
    filtered = [r for r in reviews if r.get('reviewer', {}).get('review_count', 0) >= min_reviews]
    return filtered

def save_reviewers_to_csv(reviewers, filename):
    """
    Save filtered reviewers to a CSV file.
    """
    df = pd.DataFrame([{
        'name': r['reviewer']['name'],
        'review_count': r['reviewer']['review_count'],
        'review': r.get('review', '')
    } for r in reviewers])
    df.to_csv(filename, index=False)

def save_reviewers_to_json(reviewers, filename):
    """
    Save filtered reviewers to a JSON file.
    """
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(reviewers, f, ensure_ascii=False, indent=2)

def crawl_google_reviews_from_html(html_file):
    """
    Parse a saved Google Maps POI HTML file and extract reviews and reviewer info.
    Args:
        html_file (str): Path to the saved HTML file.
    Returns:
        list of dict: List of reviews with reviewer info.
    Note:
        The HTML file should be downloaded manually from Google Maps.
    """
    reviews = []
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        # Example selectors - these must be updated based on actual HTML structure
        review_blocks = soup.select('.jftiEf')  # Google Maps review block class (may change)
        for block in review_blocks:
            name_tag = block.select_one('.d4r55')  # Reviewer name class
            count_tag = block.select_one('.RfnDt span')  # Review count class
            review_text_tag = block.select_one('.wiI7pd')  # Review text class
            name = name_tag.text.strip() if name_tag else 'Unknown'
            try:
                review_count = int(count_tag.text.replace(',', '').split()[0]) if count_tag else 0
            except Exception:
                review_count = 0
            review_text = review_text_tag.text.strip() if review_text_tag else ''
            reviews.append({
                'reviewer': {'name': name, 'review_count': review_count},
                'review': review_text
            })
    return reviews

def get_google_place_reviews(place_id, api_key):
    """
    Fetch up to 5 reviews for a Google Place using the Places API.
    Args:
        place_id (str): The Google Place ID.
        api_key (str): Your Google Places API key.
    Returns:
        list of dict: List of review dicts from the API.
    """
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=reviews,name,rating,user_ratings_total&key={api_key}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data.get('result', {}).get('reviews', [])
    else:
        print(f"API request failed: {resp.status_code}")
        return []

def get_google_place_reviews_v1(place_id, api_key):
    """
    Fetch place details (including reviews) using the new Places API v1.
    Args:
        place_id (str): The Google Place ID.
        api_key (str): Your Google Places API key.
    Returns:
        dict: Place details response from the API.
    """
    url = f"https://places.googleapis.com/v1/places/{place_id}?fields=reviews,displayName,rating,userRatingCount"
    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "reviews,displayName,rating,userRatingCount"
    }
    resp = requests.get(url, headers=headers)
    print(f"Status code: {resp.status_code}")
    print(f"Response: {resp.text}")
    if resp.status_code == 200:
        return resp.json()
    else:
        return None

def get_place_id_v1(query, api_key):
    """
    Use Places API v1 Text Search to get place IDs for a query.
    Args:
        query (str): The text query (e.g., 'Sentosa, Singapore').
        api_key (str): Your Google Places API key.
    Returns:
        list: List of places with their IDs and display names.
    """
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName"
    }
    data = {"textQuery": query}
    resp = requests.post(url, headers=headers, json=data)
    print(f"Text Search status: {resp.status_code}")
    print(f"Text Search response: {resp.text}")
    if resp.status_code == 200:
        return resp.json().get('places', [])
    else:
        return []

def process_multiple_pois(poi_queries, api_key, min_rating=4):
    """
    For each POI query, fetch reviews, filter by rating, and save results.
    Args:
        poi_queries (list): List of POI search queries.
        api_key (str): Google Places API key.
        min_rating (int): Minimum rating to filter reviews.
    """
    for query in poi_queries:
        print(f"\nProcessing POI: {query}")
        places = get_place_id_v1(query, api_key)
        if not places:
            print(f"No places found for query: {query}")
            continue
        place_id = places[0]['id']
        print(f"Using Place ID: {place_id}")
        details = get_google_place_reviews_v1(place_id, api_key)
        if details and 'reviews' in details:
            reviews = details['reviews']
            # Save all reviews
            base = query.replace(",", "").replace(" ", "_")
            all_csv = f"{base}_all_reviews.csv"
            all_json = f"{base}_all_reviews.json"
            pd.DataFrame(reviews).to_csv(all_csv, index=False)
            with open(all_json, 'w', encoding='utf-8') as f:
                import json
                json.dump(reviews, f, ensure_ascii=False, indent=2)
            print(f"All reviews saved to {all_csv} and {all_json}")
            # Filter by rating
            filtered = [r for r in reviews if r.get('rating', 0) >= min_rating]
            filtered_csv = f"{base}_filtered_reviews.csv"
            filtered_json = f"{base}_filtered_reviews.json"
            pd.DataFrame(filtered).to_csv(filtered_csv, index=False)
            with open(filtered_json, 'w', encoding='utf-8') as f:
                json.dump(filtered, f, ensure_ascii=False, indent=2)
            print(f"Filtered reviews (rating >= {min_rating}) saved to {filtered_csv} and {filtered_json}")
        else:
            print(f"No reviews returned for {query}.")

def fetch_all_pois_in_singapore(api_key, place_types=None):
    """
    Fetch all POIs in Singapore for a list of place types using Places API v1 Text Search and save their names and Place IDs.
    Args:
        api_key (str): Google Places API key.
        place_types (list): List of place types to search for. If None, uses a default set.
    """
    import time, json
    if place_types is None:
        place_types = [
            "tourist_attraction", "museum", "art_gallery", "park", "shopping_mall", "restaurant", "cafe", "bar", "night_club", "zoo", "aquarium", "stadium", "university", "library", "church", "hindu_temple", "mosque", "synagogue", "amusement_park", "casino", "movie_theater"
        ]
    all_pois = []
    for place_type in place_types:
        print(f"\nFetching POIs for type: {place_type}")
        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.id,places.displayName"
        }
        text_query = f"{place_type.replace('_', ' ')} near Singapore"
        data = {"textQuery": text_query}
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code != 200:
            print(f"API v1 Text Search failed for {place_type}: {resp.status_code} {resp.text}")
            continue
        places = resp.json().get('places', [])
        for p in places:
            all_pois.append({
                "name": p.get("displayName", {}).get("text"),
                "place_id": p.get("id"),
                "type": place_type
            })
        time.sleep(0.5)  # Be polite to the API
    # Remove duplicates by place_id
    unique_pois = {poi['place_id']: poi for poi in all_pois}.values()
    df = pd.DataFrame(unique_pois)
    df.to_csv("all_singapore_pois.csv", index=False)
    print(f"Saved {len(df)} unique POIs to all_singapore_pois.csv")

def fetch_reviews_for_all_pois(csv_path, api_key, output_dir="poi_reviews"): 
    """
    Fetch reviews for all POIs listed in a CSV and save each POI's reviews to a CSV and JSON file in the output directory.
    Args:
        csv_path (str): Path to the CSV file with columns: name, place_id, type.
        api_key (str): Google Places API key.
        output_dir (str): Directory to save review files.
    """
    import os, json
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    df = pd.read_csv(csv_path)
    for idx, row in df.iterrows():
        name = str(row['name']).replace(",", "").replace(" ", "_").replace("/", "_")
        place_id = row['place_id']
        print(f"Fetching reviews for {name} ({place_id}) [{idx+1}/{len(df)}]")
        details = get_google_place_reviews_v1(place_id, api_key)
        if details and 'reviews' in details:
            reviews = details['reviews']
            csv_file = os.path.join(output_dir, f"{name}_reviews.csv")
            json_file = os.path.join(output_dir, f"{name}_reviews.json")
            pd.DataFrame(reviews).to_csv(csv_file, index=False)
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(reviews, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(reviews)} reviews to {csv_file} and {json_file}")
        else:
            print(f"No reviews found for {name} ({place_id})")

if __name__ == "__main__":
    print("\nGoogle Review POI Crawler - Singapore (Google Places API mode)")
    # Use the stored API key
    api_key = os.getenv('GOOGLE_API_KEY')
    # Sentosa Place ID: 'ChIJyY4rtGcX2jERIKTarqz3AAQ'
    place_id = 'ChIJyY4rtGcX2jERIKTarqz3AAQ'  # Sentosa, Singapore
    reviews = get_google_place_reviews(place_id, api_key)
    import pprint
    print("Full API response for debugging:")
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=reviews,name,rating,user_ratings_total&key={api_key}"
    resp = requests.get(url)
    pprint.pprint(resp.json())
    for r in reviews:
        print(f"Reviewer: {r['author_name']}, Rating: {r['rating']}, Review: {r['text']}")
    # Save API reviews to CSV/JSON
    import pandas as pd, json
    if reviews:
        df = pd.DataFrame(reviews)
        df.to_csv('api_reviews.csv', index=False)
        with open('api_reviews.json', 'w', encoding='utf-8') as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
        print("API reviews saved to api_reviews.csv and api_reviews.json")
    else:
        print("No reviews returned by the API.")
    print("\nGoogle Review POI Crawler - Singapore (Google Places API v1 mode)")
    api_key = os.getenv('GOOGLE_API_KEY')
    place_id = 'ChIJyY4rtGcX2jERIKTarqz3AAQ'  # Sentosa, Singapore
    details = get_google_place_reviews_v1(place_id, api_key)
    if details and 'reviews' in details:
        for r in details['reviews']:
            print(f"Reviewer: {r.get('authorDisplayName')}, Rating: {r.get('rating')}, Review: {r.get('text')}")
        import pandas as pd, json
        df = pd.DataFrame(details['reviews'])
        df.to_csv('api_reviews_v1.csv', index=False)
        with open('api_reviews_v1.json', 'w', encoding='utf-8') as f:
            json.dump(details['reviews'], f, ensure_ascii=False, indent=2)
        print("API v1 reviews saved to api_reviews_v1.csv and api_reviews_v1.json")
    else:
        print("No reviews returned by the API v1.")
    print("\nGoogle Places API v1 Text Search for Place ID...")
    api_key = os.getenv('GOOGLE_API_KEY')
    query = "Sentosa, Singapore"
    places = get_place_id_v1(query, api_key)
    if places:
        print("Places found:")
        for p in places:
            print(f"ID: {p.get('id')}, Name: {p.get('displayName', {}).get('text')}")
        # Use the first place ID for review fetching
        place_id = places[0]['id']
        print(f"\nFetching reviews for Place ID: {place_id}")
        details = get_google_place_reviews_v1(place_id, api_key)
        if details and 'reviews' in details:
            for r in details['reviews']:
                print(f"Reviewer: {r.get('authorDisplayName')}, Rating: {r.get('rating')}, Review: {r.get('text')}")
            import pandas as pd, json
            df = pd.DataFrame(details['reviews'])
            df.to_csv('api_reviews_v1.csv', index=False)
            with open('api_reviews_v1.json', 'w', encoding='utf-8') as f:
                json.dump(details['reviews'], f, ensure_ascii=False, indent=2)
            print("API v1 reviews saved to api_reviews_v1.csv and api_reviews_v1.json")
        else:
            print("No reviews returned by the API v1.")
    else:
        print("No places found for query.")
    print("\nAutomated review extraction for multiple POIs...")
    api_key = os.getenv('GOOGLE_API_KEY')
    poi_queries = [
        "Sentosa, Singapore",
        "Marina Bay Sands, Singapore",
        "Gardens by the Bay, Singapore"
    ]
    process_multiple_pois(poi_queries, api_key, min_rating=4)
    print("\nFetching all types of POIs in Singapore...")
    api_key = os.getenv('GOOGLE_API_KEY')
    fetch_all_pois_in_singapore(api_key)
    print("\nFetching reviews for all POIs in the CSV...")
    csv_path = "all_singapore_pois.csv"
    output_dir = "poi_reviews"
    fetch_reviews_for_all_pois(csv_path, api_key, output_dir)
    print("\nFetching reviews for all POIs in all_singapore_pois.csv ...")
    fetch_reviews_for_all_pois("all_singapore_pois.csv", api_key)
