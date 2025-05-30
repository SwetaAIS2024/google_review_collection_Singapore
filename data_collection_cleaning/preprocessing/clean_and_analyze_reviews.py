import os
import pandas as pd
import numpy as np

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
INPUT_CSV = os.path.join(ROOT_DIR, 'all_reviews_flat.csv')
CLEAN_CSV = os.path.join(BASE_DIR, 'all_reviews_flat_clean.csv')
ANALYSIS_TXT = os.path.join(BASE_DIR, 'review_data_analysis.txt')

# 1. Load and clean data
print('Loading data...')
df = pd.read_csv(INPUT_CSV)
print(f'Original rows: {len(df)}')

# Remove rows with any empty (NaN) values
df_clean = df.dropna()
print(f'Rows after removing empty: {len(df_clean)}')
df_clean.to_csv(CLEAN_CSV, index=False)

# 2. Data analysis
analysis = []

# a. For each poi_type, how many unique users (reviewer_name)?
poi_type_user_counts = df_clean.groupby('poi_type')['reviewer_name'].nunique()
analysis.append('Unique users per poi_type:')
for poi_type, count in poi_type_user_counts.items():
    analysis.append(f'  {poi_type}: {count}')

# b. How many unique users (reviewer_name) overall?
unique_users = df_clean['reviewer_name'].nunique()
analysis.append(f'\nTotal unique users (reviewer_name): {unique_users}')

# c. How many unique places (name)?
unique_places = df_clean['name'].nunique()
analysis.append(f'Total unique places (name): {unique_places}')

# d. Review distribution per user
user_review_counts = df_clean['reviewer_name'].value_counts()
analysis.append(f'\nReview count per user (summary):')
analysis.append(str(user_review_counts.describe()))

# e. Review distribution per POI
poi_review_counts = df_clean['name'].value_counts()
analysis.append(f'\nReview count per POI (summary):')
analysis.append(str(poi_review_counts.describe()))

# f. Rating analysis
if 'rating' in df_clean.columns:
    ratings = pd.to_numeric(df_clean['rating'], errors='coerce').dropna()
    analysis.append(f'\nRating statistics:')
    analysis.append(str(ratings.describe()))
    # Average rating per POI
    avg_rating_per_poi = df_clean.groupby('name')['rating'].mean().sort_values(ascending=False)
    analysis.append(f'\nTop 5 POIs by average rating:')
    analysis.extend([f"  {name}: {avg:.2f}" for name, avg in avg_rating_per_poi.head(5).items()])
    analysis.append(f'\nBottom 5 POIs by average rating:')
    analysis.extend([f"  {name}: {avg:.2f}" for name, avg in avg_rating_per_poi.tail(5).items()])

# g. Review text length analysis
if 'review_text' in df_clean.columns:
    df_clean['review_length'] = df_clean['review_text'].astype(str).apply(len)
    analysis.append(f'\nReview text length statistics:')
    analysis.append(str(df_clean['review_length'].describe()))

# d. Count of each rating (1-5)
rating_counts = df_clean['rating'].value_counts().sort_index()
analysis.append('\nReview counts by rating:')
for rating in [5, 4, 3, 2, 1]:
    count = rating_counts.get(rating, 0)
    analysis.append(f'  {rating}-star: {count}')

# Save analysis
with open(ANALYSIS_TXT, 'w') as f:
    f.write('\n'.join(analysis))

print('Analysis complete. Results saved to review_data_analysis.txt')
