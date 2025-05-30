import pandas as pd
import os

INPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'all_reviews_from_db.csv')
OUTPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reviews_grouped_by_user.csv')

df = pd.read_csv(INPUT_CSV)
# Count reviews per user
user_counts = df['reviewer_name'].value_counts().reset_index()
user_counts.columns = ['reviewer_name', 'review_count']
# Merge review counts into main DataFrame
merged = df.merge(user_counts, on='reviewer_name')
# Sort by review_count (desc), then reviewer_name, then timestamp
merged_sorted = merged.sort_values(['review_count', 'reviewer_name', 'timestamp'], ascending=[False, True, True])
# Drop the review_count column for output if not needed, or keep if desired
merged_sorted.to_csv(OUTPUT_CSV, index=False)
print(f'Reviews sorted/grouped by user (descending by review count) and saved to {OUTPUT_CSV}')
