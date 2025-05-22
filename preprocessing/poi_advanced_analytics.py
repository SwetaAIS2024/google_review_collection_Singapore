import os
import pandas as pd
import numpy as np
from collections import Counter

# Optional: For sentiment analysis and plotting, uncomment and install if needed
# from textblob import TextBlob
# import matplotlib.pyplot as plt
# import seaborn as sns

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
INPUT_CSV = os.path.join(BASE_DIR, 'all_reviews_flat_clean.csv')
POI_CSV = os.path.join(ROOT_DIR, 'all_singapore_pois_detailed.csv')
ANALYSIS_TXT = os.path.join(BASE_DIR, 'poi_advanced_analytics.txt')

# Load data
print('Loading cleaned review data...')
df = pd.read_csv(INPUT_CSV)

# Try to load POI master for geo analysis
if os.path.exists(POI_CSV):
    poi_df = pd.read_csv(POI_CSV)
else:
    poi_df = None

analysis = []

# 1. POI Popularity & Engagement
most_reviewed_pois = df['name'].value_counts().head(10)
least_reviewed_pois = df['name'].value_counts().tail(10)
analysis.append('Top 10 most reviewed POIs:')
analysis.extend([f'  {name}: {count}' for name, count in most_reviewed_pois.items()])
analysis.append('\nBottom 10 least reviewed POIs:')
analysis.extend([f'  {name}: {count}' for name, count in least_reviewed_pois.items()])

avg_rating_per_poi = df.groupby('name')['rating'].mean().sort_values(ascending=False)
analysis.append('\nTop 5 POIs by average rating:')
analysis.extend([f'  {name}: {avg:.2f}' for name, avg in avg_rating_per_poi.head(5).items()])
analysis.append('Bottom 5 POIs by average rating:')
analysis.extend([f'  {name}: {avg:.2f}' for name, avg in avg_rating_per_poi.tail(5).items()])

unique_reviewers_per_poi = df.groupby('name')['reviewer_name'].nunique().sort_values(ascending=False)
analysis.append('\nTop 5 POIs with most unique reviewers:')
analysis.extend([f'  {name}: {count}' for name, count in unique_reviewers_per_poi.head(5).items()])

# 2. POI Type Analysis
most_popular_types = df['poi_type'].value_counts().head(10)
analysis.append('\nTop 10 most popular POI types:')
analysis.extend([f'  {typ}: {count}' for typ, count in most_popular_types.items()])

avg_rating_per_type = df.groupby('poi_type')['rating'].mean().sort_values(ascending=False)
analysis.append('\nTop 5 POI types by average rating:')
analysis.extend([f'  {typ}: {avg:.2f}' for typ, avg in avg_rating_per_type.head(5).items()])
analysis.append('Bottom 5 POI types by average rating:')
analysis.extend([f'  {typ}: {avg:.2f}' for typ, avg in avg_rating_per_type.tail(5).items()])

# 3. Reviewer Behavior at POIs
top_reviewers_per_poi = df.groupby('name')['reviewer_name'].apply(lambda x: Counter(x).most_common(1)[0]).head(10)
analysis.append('\nTop reviewer for each of the top 10 POIs:')
for poi, (user, count) in top_reviewers_per_poi.items():
    analysis.append(f'  {poi}: {user} ({count} reviews)')

repeat_reviewers = df.groupby(['name', 'reviewer_name']).size().reset_index(name='count')
repeat_reviewers = repeat_reviewers[repeat_reviewers['count'] > 1]
analysis.append(f'\nNumber of (POI, reviewer) pairs with multiple reviews: {len(repeat_reviewers)}')

cross_poi_reviewers = df.groupby('reviewer_name')['name'].nunique().sort_values(ascending=False)
analysis.append('\nTop 5 users who reviewed the most unique POIs:')
analysis.extend([f'  {user}: {count}' for user, count in cross_poi_reviewers.head(5).items()])

# 4. Temporal Trends (if relative_time exists)
if 'relative_time' in df.columns:
    recent = df['relative_time'].str.extract(r'(\d+) (\w+)')
    recent.columns = ['num', 'unit']
    recent['num'] = pd.to_numeric(recent['num'], errors='coerce')
    # Example: count reviews by time unit
    time_counts = df['relative_time'].value_counts().head(10)
    analysis.append('\nTop 10 most common relative_time values:')
    analysis.extend([f'  {val}: {cnt}' for val, cnt in time_counts.items()])

# 5. Sentiment & Text Analysis (optional, requires TextBlob)
# if 'review_text' in df.columns:
#     sentiments = df['review_text'].astype(str).apply(lambda x: TextBlob(x).sentiment.polarity)
#     analysis.append(f'\nReview sentiment statistics:')
#     analysis.append(str(sentiments.describe()))

# 6. Geographical Analysis (if lat/lng available)
if poi_df is not None and 'lat' in poi_df.columns and 'lng' in poi_df.columns:
    analysis.append('\nGeographical analysis:')
    # POI density by area (simple: count by rounding lat/lng)
    poi_df['lat_rounded'] = poi_df['lat'].round(2)
    poi_df['lng_rounded'] = poi_df['lng'].round(2)
    density = poi_df.groupby(['lat_rounded', 'lng_rounded']).size().sort_values(ascending=False).head(10)
    analysis.append('Top 10 densest POI grid cells:')
    for (lat, lng), count in density.items():
        analysis.append(f'  ({lat}, {lng}): {count} POIs')

# 7. Outlier & Quality Analysis
only_1star = df[df['rating'] == 1]['name'].value_counts().head(5)
only_5star = df[df['rating'] == 5]['name'].value_counts().head(5)
analysis.append('\nTop 5 POIs with most 1-star reviews:')
analysis.extend([f'  {name}: {count}' for name, count in only_1star.items()])
analysis.append('Top 5 POIs with most 5-star reviews:')
analysis.extend([f'  {name}: {count}' for name, count in only_5star.items()])

rapid_growth = df.groupby('name').size().sort_values(ascending=False).head(5)
analysis.append('\nPOIs with most rapid review growth (by review count):')
analysis.extend([f'  {name}: {count}' for name, count in rapid_growth.items()])

# Save analysis
with open(ANALYSIS_TXT, 'w') as f:
    f.write('\n'.join(analysis))

print('Advanced POI analytics complete. Results saved to poi_advanced_analytics.txt')
