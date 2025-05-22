import os
import pandas as pd
from collections import defaultdict, Counter
from textblob import TextBlob
import re

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
INPUT_CSV = os.path.join(ROOT_DIR, 'preprocessing', 'all_reviews_flat_clean.csv')
OUTPUT_TXT = os.path.join(BASE_DIR, 'aspect_sentiment_summary.txt')

# Helper: Simple aspect extraction (noun phrases)
def extract_aspects(text):
    blob = TextBlob(text)
    return [np.lower() for np in blob.noun_phrases]

# Helper: Sentiment polarity
def get_sentiment(text):
    return TextBlob(text).sentiment.polarity

# Clean poi_type by removing 'point_of_interest' and 'establishment' from each value
def clean_poi_type(poi_type):
    if not isinstance(poi_type, str):
        return poi_type
    types = [t for t in poi_type.split(',') if t not in ('point_of_interest', 'establishment')]
    return ','.join(types).strip(',')

# Load data
df = pd.read_csv(INPUT_CSV)

# Group by poi_type (subtype)
results = defaultdict(lambda: defaultdict(list))

for _, row in df.iterrows():
    poi_type = clean_poi_type(row.get('poi_type', 'unknown'))
    review_text = str(row.get('review_text', ''))
    if not review_text.strip():
        continue
    aspects = extract_aspects(review_text)
    sentiment = get_sentiment(review_text)
    for aspect in aspects:
        results[poi_type][aspect].append(sentiment)

# Classify sentiment as positive, negative, or neutral
def classify_sentiment(score):
    if score > 0.1:
        return 'positive'
    elif score < -0.1:
        return 'negative'
    else:
        return 'neutral'

# Collect sentiment counts per poi_type
type_sentiment_counts = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})

summary_rows = []
for poi_type, aspect_dict in results.items():
    aspect_counts = Counter({a: len(slist) for a, slist in aspect_dict.items()})
    for aspect, count in aspect_counts.most_common(10):
        sentiments = aspect_dict[aspect]
        avg_sent = sum(sentiments) / len(sentiments) if sentiments else 0
        # Classify each sentiment
        sentiment_classes = [classify_sentiment(s) for s in sentiments]
        for sclass in sentiment_classes:
            type_sentiment_counts[poi_type][sclass] += 1
        summary_rows.append({
            'poi_type': poi_type,
            'aspect': aspect,
            'mentions': count,
            'avg_sentiment': round(avg_sent, 2),
            'positive': sentiment_classes.count('positive'),
            'negative': sentiment_classes.count('negative'),
            'neutral': sentiment_classes.count('neutral')
        })

# Save as text
summary_lines = []
for row in summary_rows:
    if not summary_lines or summary_lines[-1] != f"POI Type: {row['poi_type']}":
        summary_lines.append(f"POI Type: {row['poi_type']}")
    summary_lines.append(f"  Aspect: {row['aspect']} | Mentions: {row['mentions']} | Avg Sentiment: {row['avg_sentiment']:.2f} | +:{row['positive']} 0:{row['neutral']} -:{row['negative']}")
summary_lines.append('')

# Add overall sentiment analysis per poi_type
summary_lines.append('Sentiment counts per POI type:')
for poi_type, counts in type_sentiment_counts.items():
    summary_lines.append(f"{poi_type}: +{counts['positive']} 0:{counts['neutral']} -{counts['negative']}")

with open(OUTPUT_TXT, 'w') as f:
    f.write('\n'.join(summary_lines))

# Save as CSV
import pandas as pd
csv_path = os.path.join(BASE_DIR, 'aspect_sentiment_summary.csv')
pd.DataFrame(summary_rows).to_csv(csv_path, index=False)

# Save sentiment counts per poi_type as CSV
sentiment_count_csv = os.path.join(BASE_DIR, 'sentiment_counts_per_poi_type.csv')
pd.DataFrame([
    {'poi_type': k, 'positive': v['positive'], 'neutral': v['neutral'], 'negative': v['negative']}
    for k, v in type_sentiment_counts.items()
]).to_csv(sentiment_count_csv, index=False)

print('Aspect extraction and sentiment analysis complete. Results saved to aspect_sentiment_summary.txt, aspect_sentiment_summary.csv, and sentiment_counts_per_poi_type.csv')
