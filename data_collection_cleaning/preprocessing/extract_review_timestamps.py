import os
import json
import pandas as pd
from datetime import datetime

POI_REVIEWS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../poi_reviews')
OUTPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'all_reviews_with_timestamp.csv')

rows = []
for fname in os.listdir(POI_REVIEWS_DIR):
    if fname.endswith('.json'):
        fpath = os.path.join(POI_REVIEWS_DIR, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Only process if data is a dict (not a list)
        if not isinstance(data, dict):
            print(f"Skipping {fname}: not a dict (type={type(data)})")
            continue
        place_id = data.get('place_id', '')
        name = data.get('name', '')
        lat = data.get('geometry', {}).get('location', {}).get('lat', '')
        lng = data.get('geometry', {}).get('location', {}).get('lng', '')
        poi_types = ','.join(data.get('types', []))
        for review in data.get('reviews', []):
            author = review.get('author_name', '')
            rating = review.get('rating', '')
            text = review.get('text', '')
            rel_time = review.get('relative_time_description', '')
            unix_time = review.get('time', '')
            # Convert unix_time to ISO date and datetime if present
            if unix_time:
                try:
                    review_date = datetime.utcfromtimestamp(int(unix_time)).strftime('%Y-%m-%d')
                    processed_timestamp = datetime.utcfromtimestamp(int(unix_time)).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    review_date = ''
                    processed_timestamp = ''
            else:
                review_date = ''
                processed_timestamp = ''
            rows.append({
                'reviewer_name': author,
                'place_id': place_id,
                'name': name,
                'poi_type': poi_types,
                'rating': rating,
                'review_text': text,
                'relative_time': rel_time,
                'timestamp': unix_time,
                'review_date': review_date,
                'processed_timestamp': processed_timestamp,
                'lat': lat,
                'lng': lng
            })

pd.DataFrame(rows).to_csv(OUTPUT_CSV, index=False)
print(f'Extracted reviews with timestamps and spatial context to {OUTPUT_CSV}')
