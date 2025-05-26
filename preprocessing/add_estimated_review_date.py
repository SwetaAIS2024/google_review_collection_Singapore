import os
import pandas as pd
import re
from datetime import datetime, timedelta

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(BASE_DIR, 'all_reviews_flat_clean.csv')
OUTPUT_CSV = os.path.join(BASE_DIR, 'all_reviews_flat_with_date.csv')

# Crawl date (YYYY-MM-DD)
CRAWL_DATE = datetime(2025, 5, 22)

# Helper to parse relative_time
RELATIVE_TIME_PATTERN = re.compile(r'(\d+|a|an)\s+(second|minute|hour|day|week|month|year)s?\s+ago', re.I)

UNIT_TO_KWARGS = {
    'second': 'seconds',
    'minute': 'minutes',
    'hour': 'hours',
    'day': 'days',
    'week': 'weeks',
    'month': 'days',  # Approximate months as 30 days
    'year': 'days',   # Approximate years as 365 days
}

UNIT_TO_MULTIPLIER = {
    'second': 1,
    'minute': 1,
    'hour': 1,
    'day': 1,
    'week': 1,
    'month': 30,
    'year': 365,
}

def estimate_date(relative_time):
    if not isinstance(relative_time, str):
        return ''
    m = RELATIVE_TIME_PATTERN.search(relative_time)
    if not m:
        return ''
    num, unit = m.group(1), m.group(2).lower()
    if num in ('a', 'an'):
        num = 1
    else:
        try:
            num = int(num)
        except Exception:
            return ''
    if unit in ('month', 'year'):
        days = int(num) * UNIT_TO_MULTIPLIER[unit]
        return (CRAWL_DATE - timedelta(days=days)).strftime('%Y-%m-%d')
    elif unit in UNIT_TO_KWARGS:
        kwargs = {UNIT_TO_KWARGS[unit]: int(num) * UNIT_TO_MULTIPLIER[unit]}
        return (CRAWL_DATE - timedelta(**kwargs)).strftime('%Y-%m-%d')
    return ''

# Load POI spatial context
df_poi = pd.read_csv(os.path.join(BASE_DIR, '../all_singapore_pois_detailed.csv'))
poi_lookup = df_poi.set_index('place_id')[['lat', 'lng']]

# Merge spatial context into review data
df = pd.read_csv(INPUT_CSV)
df['estimated_review_date'] = df['relative_time'].apply(estimate_date)
df = df.merge(poi_lookup, how='left', left_on='place_id', right_index=True)

df.to_csv(OUTPUT_CSV, index=False)
print(f'Estimated review dates and spatial context added. Output saved to {OUTPUT_CSV}')
