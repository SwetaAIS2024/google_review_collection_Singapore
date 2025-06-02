import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Load the Foursquare-style checkins file
google_fsq = pd.read_csv('../google_reviews_as_fsq_checkins.txt', sep='\t', header=None, names=['user_id', 'poi_id', 'datetime', 'timezone'])
# Load the original Google reviews for POI type info
reviews = pd.read_csv('../all_reviews_with_timestamp.csv')

# 1. Number of checkins per place (descending)
checkins_per_place = google_fsq['poi_id'].value_counts().reset_index()
checkins_per_place.columns = ['poi_id', 'checkin_count']
checkins_per_place.to_csv('../checkins_per_place.txt', sep='\t', index=False)

# 2. Number of checkins per user (descending)
checkins_per_user = google_fsq['user_id'].value_counts().reset_index()
checkins_per_user.columns = ['user_id', 'checkin_count']
checkins_per_user.to_csv('../checkins_per_user.txt', sep='\t', index=False)

# 3. Top 20 POI categories (from reviews, by checkin count)
# Map POI id to type using reviews
poi_type_map = reviews.drop_duplicates('place_id').set_index('place_id')['poi_type'].to_dict()
google_fsq['poi_type'] = google_fsq['poi_id'].map(poi_type_map)
# Flatten categories (comma separated)
all_types = google_fsq['poi_type'].dropna().str.split(',').explode()
# Remove 'point_of_interest' and 'establishment' from the list for plotting
all_types = all_types[~all_types.str.strip().isin(['point_of_interest', 'establishment'])]
top20_types = all_types.value_counts().head(20)
plt.figure(figsize=(10,6))
top20_types.plot(kind='bar')
plt.title('Top 20 POI Categories by Check-ins (Google Reviews)')
plt.xlabel('POI Type')
plt.ylabel('Number of Check-ins')
plt.tight_layout()
plt.savefig('../top20_poi_types_vs_checkins.png')
plt.close()

# 4. Summary stats
n_checkins = len(google_fsq)
n_users = google_fsq['user_id'].nunique()
n_places = google_fsq['poi_id'].nunique()
avg_per_user = round(n_checkins / n_users, 2) if n_users else 0
avg_per_place = round(n_checkins / n_places, 2) if n_places else 0
most_active_user = checkins_per_user.iloc[0]
most_popular_place = checkins_per_place.iloc[0]

with open('../google_reviews_analysis_summary.txt', 'w') as f:
    f.write(f"Total check-ins: {n_checkins}\n")
    f.write(f"Number of unique users: {n_users}\n")
    f.write(f"Number of unique places: {n_places}\n")
    f.write(f"Average check-ins per user: {avg_per_user}\n")
    f.write(f"Average check-ins per place: {avg_per_place}\n")
    f.write(f"Most active user: {most_active_user['user_id']} with {most_active_user['checkin_count']} check-ins\n")
    f.write(f"Most popular place: {most_popular_place['poi_id']} with {most_popular_place['checkin_count']} check-ins\n")

print('Analysis complete. Outputs: checkins_per_place.txt, checkins_per_user.txt, top20_poi_types_vs_checkins.png, google_reviews_analysis_summary.txt')
