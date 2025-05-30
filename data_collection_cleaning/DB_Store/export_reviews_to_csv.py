import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reviews.db')
OUTPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'all_reviews_from_db.csv')

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query('SELECT * FROM reviews', conn)
df.to_csv(OUTPUT_CSV, index=False)
conn.close()
print(f'Exported all reviews from DB to {OUTPUT_CSV}')
