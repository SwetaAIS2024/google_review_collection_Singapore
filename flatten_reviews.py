import os
import pandas as pd
import json
from datetime import datetime, timedelta

POI_REVIEWS_DIR = 'poi_reviews'
OUTPUT_CSV = 'all_reviews_flat.csv'
OUTPUT_JSON = 'all_reviews_flat.json'

# Read the flat reviews file
flat_reviews = pd.read_csv(OUTPUT_CSV)

# Remove reviews that are 3 years old or more
# Use the 'relative_time' column (e.g., '3 months ago', 'a year ago', '4 years ago')
def is_within_3_years(rel_time):
    if pd.isna(rel_time):
        return False
    rel_time = str(rel_time).strip().lower()
    if 'year' in rel_time:
        # Handle 'a year ago', '2 years ago', etc.
        if rel_time.startswith('a year'):
            return True
        try:
            n_years = int(rel_time.split()[0])
            return n_years < 3
        except Exception:
            return False
    if 'month' in rel_time or 'week' in rel_time or 'day' in rel_time:
        return True
    return False

flat_reviews = flat_reviews[flat_reviews['relative_time'].apply(is_within_3_years)]

# Count reviewer frequencies
reviewer_freq = flat_reviews['reviewer_name'].value_counts()
# Map frequency to each review
flat_reviews['reviewer_freq'] = flat_reviews['reviewer_name'].map(reviewer_freq)
# Sort by reviewer frequency (descending), then reviewer name (ascending for tie-breaker)
flat_reviews_sorted = flat_reviews.sort_values(by=['reviewer_freq', 'reviewer_name'], ascending=[False, True], kind='stable')
# Drop the helper column for output
flat_reviews_sorted = flat_reviews_sorted.drop(columns=['reviewer_freq'])
# Save sorted CSV
flat_reviews_sorted.to_csv(OUTPUT_CSV, index=False)
# Save sorted JSON
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(flat_reviews_sorted.to_dict(orient='records'), f, ensure_ascii=False, indent=2)

print(f"Filtered, sorted, and saved {len(flat_reviews_sorted)} reviews (only <3 years old) by reviewer frequency (descending) and reviewer name.")
