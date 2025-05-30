import os
import json
import sqlite3
from datetime import datetime

POI_REVIEWS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../poi_reviews')
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reviews.db')

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS reviews (
    reviewer_name TEXT,
    place_id TEXT,
    name TEXT,
    poi_type TEXT,
    rating INTEGER,
    review_text TEXT,
    relative_time TEXT,
    timestamp INTEGER,
    review_date TEXT,
    processed_timestamp TEXT,
    lat REAL,
    lng REAL
)
''')

for fname in os.listdir(POI_REVIEWS_DIR):
    if fname.endswith('.json'):
        fpath = os.path.join(POI_REVIEWS_DIR, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
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
            c.execute('INSERT INTO reviews VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (
                author,
                place_id,
                name,
                poi_types,
                rating,
                text,
                rel_time,
                unix_time,
                review_date,
                processed_timestamp,
                lat,
                lng
            ))
conn.commit()
conn.close()
print(f'All reviews from poi_reviews/ stored in {DB_PATH}')
