import pandas as pd
import os
import requests
import time
import logging
import json

API_KEY = os.getenv('GOOGLE_PLACES_API_KEY', 'YOUR_API_KEY_HERE')
INPUT_CSV = 'all_singapore_pois_detailed.csv'
OUTPUT_DIR = 'poi_reviews'
CHECKPOINT_FILE = 'review_fetch_checkpoint.txt'
BATCH_SIZE = 1000  # Number of POIs per batch
SLEEP_BETWEEN_REQUESTS = 0.2  # seconds

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def safe_filename(name):
    return (
        name.replace(' ', '_')
            .replace('/', '_')
            .replace('"', '')
            .replace("'", '')
            .replace('|', '')
            .replace(':', '')
            .replace('?', '')
            .replace('(', '')
            .replace(')', '')
            .replace('&', 'and')
    )

def fetch_reviews(place_id):
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        'place_id': place_id,
        'fields': 'name,reviews,place_id,url,user_ratings_total,rating,types,geometry,formatted_address,vicinity',
        'key': API_KEY
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        logging.error(f"HTTP error {resp.status_code} for place_id {place_id}")
        return None
    data = resp.json()
    if 'error_message' in data:
        logging.error(f"API error for place_id {place_id}: {data['error_message']}")
        return None
    return data.get('result', {})

def save_reviews_csv(poi_name, reviews, meta):
    filename = os.path.join(OUTPUT_DIR, f"{safe_filename(poi_name)}_reviews.csv")
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = pd.DataFrame([
            {
                'author_name': r.get('author_name', ''),
                'rating': r.get('rating', ''),
                'text': r.get('text', ''),
                'relative_time_description': r.get('relative_time_description', ''),
                'reviewer_total_reviews': r.get('author_user_rating_count', ''),
                'reviewer_profile_url': r.get('author_url', '')
            } for r in reviews
        ])
        writer.to_csv(f, index=False)
    # Save meta as JSON
    meta_filename = os.path.join(OUTPUT_DIR, f"{safe_filename(poi_name)}_reviews.json")
    with open(meta_filename, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return int(f.read().strip())
    return 0

def save_checkpoint(idx):
    with open(CHECKPOINT_FILE, 'w') as f:
        f.write(str(idx))

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    df = pd.read_csv(INPUT_CSV)
    start_idx = load_checkpoint()
    total = len(df)
    logging.info(f"Starting from index {start_idx} of {total}")
    for idx in range(start_idx, total):
        row = df.iloc[idx]
        name = row['name']
        place_id = row['place_id']
        logging.info(f"[{idx+1}/{total}] Fetching reviews for {name} ({place_id})")
        result = fetch_reviews(place_id)
        if not result:
            logging.warning(f"No result for {name} ({place_id})")
            save_checkpoint(idx+1)
            continue
        reviews = result.get('reviews', [])
        if not reviews:
            logging.info(f"No reviews found for {name} ({place_id})")
        save_reviews_csv(name, reviews, result)
        if (idx+1) % BATCH_SIZE == 0:
            save_checkpoint(idx+1)
            logging.info(f"Checkpoint saved at index {idx+1}")
        time.sleep(SLEEP_BETWEEN_REQUESTS)
    save_checkpoint(total)
    logging.info("Done fetching reviews for all POIs.")

if __name__ == '__main__':
    main()
