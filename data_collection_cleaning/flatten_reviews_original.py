import os
import pandas as pd
import json

POI_REVIEWS_DIR = 'poi_reviews'
OUTPUT_CSV = 'all_reviews_flat.csv'
OUTPUT_JSON = 'all_reviews_flat.json'

# Read the flat reviews file
flat_reviews = pd.read_csv(OUTPUT_CSV)
# Sort by 'reviewer_name' (not POI name)
flat_reviews_sorted = flat_reviews.sort_values(by='reviewer_name', kind='stable')
# Save sorted CSV
flat_reviews_sorted.to_csv(OUTPUT_CSV, index=False)
# Save sorted JSON
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(flat_reviews_sorted.to_dict(orient='records'), f, ensure_ascii=False, indent=2)

print(f"Sorted and saved {len(flat_reviews_sorted)} reviews by reviewer name.")
