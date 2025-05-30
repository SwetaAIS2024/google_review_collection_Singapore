# Google Review POI Crawler (Singapore)

This project is a Python-based crawler for extracting Google reviews for Singapore Points of Interest (POIs), with a focus on identifying and analyzing reviewers who have contributed more than 500 reviews.

## Features
- Discover and collect POIs across Singapore using the Google Places API.
- Fetch and store reviews for each POI in both CSV and JSON formats.
- Flatten and aggregate all reviews for further analysis.
- Filter and analyze reviewers with more than 500 reviews.
- Output data in CSV/JSON format for downstream use.

## Setup
1. Ensure you have Python 3.8+ installed.
2. (Recommended) Create and activate a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set your Google Places API key as an environment variable:
   ```sh
   export GOOGLE_PLACES_API_KEY=your_api_key_here
   ```

## Workflow

1. **Generate POI List**  
   Run `generate_granular_pois.py` to collect a detailed list of POIs across Singapore.  
   Output: `all_singapore_pois_detailed.csv`

2. **Fetch Reviews for POIs**  
   Run `main_updated.py` to fetch reviews for each POI using the Google Places API.  
   Reviews for each POI are saved in the `poi_reviews/` directory as both CSV and JSON files.

3. **Flatten and Aggregate Reviews**  
   Run `flatten_reviews.py` to combine all individual POI review files into a single flat file.  
   Output: `all_reviews_flat.csv` and `all_reviews_flat.json`  
   - Reviews older than 3 years are filtered out.
   - Reviews are sorted by reviewer frequency and name.

4. **Filter Top Reviewers**  
   Use the provided filtering logic (see `main.py` or `flatten_reviews.py`) to identify reviewers with more than 500 reviews for further analysis.

## Usage

- To run the main review collection process:
  ```sh
  python main_updated.py
  ```
- To flatten and filter reviews:
  ```sh
  python flatten_reviews.py
  ```

## Data Output

- `all_singapore_pois_detailed.csv`: List of all discovered POIs.
- `poi_reviews/`: Directory containing per-POI review files (CSV/JSON).
- `all_reviews_flat.csv` / `all_reviews_flat.json`: Aggregated and filtered review data.

## Notes

- Respect Google’s terms of service and robots.txt.
- For research/educational use only.
- This project is for ethical, non-commercial use. Excessive or automated scraping of Google services may violate their terms.
