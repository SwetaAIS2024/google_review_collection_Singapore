import os
import csv
import time
import requests
from typing import List, Dict
import logging
from rapidfuzz import fuzz

# Set your Google Places API key here or via environment variable
API_KEY = os.getenv('GOOGLE_PLACES_API_KEY', 'YOUR_API_KEY_HERE')

# Define the types of POIs you want to fetch
POI_TYPES = [
    'shopping_mall', 'bus_station', 'transit_station', 'restaurant', 'cafe', 'food', 'bar', 'night_club',
    'hawker_centre', 'hospital', 'doctor', 'pharmacy', 'clinic', 'supermarket', 'convenience_store',
    'atm', 'bank', 'school', 'university', 'library', 'museum', 'art_gallery', 'park', 'zoo', 'aquarium',
    'movie_theater', 'stadium', 'church', 'hindu_temple', 'mosque', 'synagogue', 'casino', 'amusement_park'
]

# Singapore bounding box (approximate)
MIN_LAT, MAX_LAT = 1.22, 1.47
MIN_LNG, MAX_LNG = 103.6, 104.0
GRID_STEP = 0.02  # ~2km grid (increased from 0.01)

OUTPUT_CSV = 'all_singapore_pois_detailed.csv'
CHECKPOINT_CSV = 'all_singapore_pois_checkpoint.csv'
CHECKPOINT_INTERVAL = 10  # Save after every 10 new POIs


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_places(lat: float, lng: float, place_type: str) -> List[Dict]:
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'location': f'{lat},{lng}',
        'radius': 1000,  # meters
        'type': place_type,
        'key': API_KEY
    }
    results = []
    while True:
        resp = requests.get(url, params=params)
        data = resp.json()
        # Log the full API response if no results or if there's an error
        if 'error_message' in data:
            logging.error(f"API error for {place_type} at {lat},{lng}: {data['error_message']}")
        if not data.get('results'):
            logging.warning(f"No results for {place_type} at {lat},{lng}. Full response: {data}")
        if 'results' in data:
            results.extend(data['results'])
        if 'next_page_token' in data:
            params['pagetoken'] = data['next_page_token']
            time.sleep(2)  # Google requires a short wait before next page
        else:
            break
    return results


def load_checkpoint():
    seen_place_ids = set()
    checkpoint_rows = []
    if os.path.exists(CHECKPOINT_CSV):
        with open(CHECKPOINT_CSV, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) > 1:
                    seen_place_ids.add(row[1])
                    checkpoint_rows.append(row)
        logging.info(f"Loaded checkpoint: {len(seen_place_ids)} POIs from {CHECKPOINT_CSV}")
    else:
        logging.info("No checkpoint found. Starting fresh.")
    return seen_place_ids, checkpoint_rows


def save_checkpoint(rows):
    if not rows:
        return
    write_header = not os.path.exists(CHECKPOINT_CSV)
    with open(CHECKPOINT_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['name', 'place_id', 'type', 'lat', 'lng', 'address'])
        writer.writerows(rows)
    logging.info(f"Checkpoint saved: {len(rows)} new POIs written to {CHECKPOINT_CSV}")


def is_approx_match(name1, name2, threshold=85):
    """Return True if names are approximately matching above the threshold."""
    return fuzz.ratio(name1.lower(), name2.lower()) >= threshold


def main():
    seen_place_ids, checkpoint_rows = load_checkpoint()
    seen_names = set(row[0].lower() for row in checkpoint_rows)  # Use names for fuzzy deduplication
    new_rows = []
    count_since_checkpoint = 0
    total_found = len(seen_place_ids)
    # If checkpoint exists, append to output, else create new output
    write_header = not os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['name', 'place_id', 'type', 'lat', 'lng', 'address'])
        # Write checkpointed rows to output if not already present
        if checkpoint_rows and write_header:
            writer.writerows(checkpoint_rows)
        lat = MIN_LAT
        while lat <= MAX_LAT:
            lng = MIN_LNG
            while lng <= MAX_LNG:
                for place_type in POI_TYPES:
                    logging.info(f"Querying type '{place_type}' at lat={lat:.4f}, lng={lng:.4f}")
                    try:
                        places = get_places(lat, lng, place_type)
                        logging.info(f"Found {len(places)} places for type '{place_type}' at lat={lat:.4f}, lng={lng:.4f}")
                        for place in places:
                            pid = place.get('place_id')
                            name = place.get('name', '')
                            # Fuzzy deduplication by name
                            if pid and pid not in seen_place_ids and not any(is_approx_match(name, n) for n in seen_names):
                                seen_place_ids.add(pid)
                                seen_names.add(name.lower())
                                row = [
                                    name,
                                    pid,
                                    place_type,
                                    place['geometry']['location']['lat'],
                                    place['geometry']['location']['lng'],
                                    place.get('vicinity', '')
                                ]
                                writer.writerow(row)
                                new_rows.append(row)
                                count_since_checkpoint += 1
                                total_found += 1
                                if total_found % 10 == 0:
                                    logging.info(f"Total POIs found so far: {total_found}")
                                if count_since_checkpoint >= CHECKPOINT_INTERVAL:
                                    save_checkpoint(new_rows)
                                    new_rows = []
                                    count_since_checkpoint = 0
                    except Exception as e:
                        logging.error(f"Error fetching {place_type} at {lat},{lng}: {e}")
                    time.sleep(0.1)  # Be gentle to the API
                lng += GRID_STEP
            lat += GRID_STEP
    if new_rows:
        save_checkpoint(new_rows)
    logging.info(f"Done! Output saved to {OUTPUT_CSV} and checkpoint to {CHECKPOINT_CSV}")


if __name__ == '__main__':
    main()
