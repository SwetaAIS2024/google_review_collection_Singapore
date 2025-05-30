import pandas as pd
from datetime import datetime
import hashlib

# Input and output paths
INPUT_CSV = "../all_reviews_with_timestamp.csv"
OUTPUT_TSV = "../google_reviews_as_fsq_checkins.txt"

# Read Google reviews
reviews = pd.read_csv(INPUT_CSV)

# Helper: anonymize user to integer id (like Foursquare)
def get_user_id(name):
    # Use a hash for stable anonymization, then mod to a large int range
    return int(hashlib.sha256(name.encode()).hexdigest(), 16) % 1000000

# Helper: convert timestamp to Foursquare datetime string
# Foursquare: 'Tue Apr 03 18:10:51 +0000 2012'
def to_fsq_datetime(ts):
    # Use processed_timestamp if available, else timestamp
    if pd.isnull(ts):
        return ''
    try:
        dt = datetime.strptime(str(ts), "%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            dt = datetime.strptime(str(ts), "%Y-%m-%d")
        except Exception:
            return ''
    return dt.strftime("%a %b %d %H:%M:%S +0000 %Y")

rows = []
for _, row in reviews.iterrows():
    user_id = get_user_id(str(row['reviewer_name']))
    poi_id = row['place_id']
    # Prefer processed_timestamp, else review_date, else timestamp
    dt_str = ''
    if 'processed_timestamp' in row and pd.notnull(row['processed_timestamp']):
        dt_str = to_fsq_datetime(row['processed_timestamp'])
    elif 'review_date' in row and pd.notnull(row['review_date']):
        dt_str = to_fsq_datetime(row['review_date'])
    elif 'timestamp' in row and pd.notnull(row['timestamp']):
        try:
            dt = datetime.utcfromtimestamp(int(row['timestamp']))
            dt_str = dt.strftime("%a %b %d %H:%M:%S +0000 %Y")
        except Exception:
            dt_str = ''
    # Singapore timezone offset is 480
    rows.append([user_id, poi_id, dt_str, 480])

with open(OUTPUT_TSV, 'w') as f:
    for r in rows:
        f.write("\t".join(map(str, r)) + "\n")

print(f"Wrote Foursquare-style checkins to {OUTPUT_TSV}")
