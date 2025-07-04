import requests
import time
import os
import json
import ast

# Airtable API config
API_KEY = "patYTVmRlbjgZsLyK.36e936cecbe99037db01f5a35b2cb1052c25ccaaba84347f541e4100ab2073a2"
BASE_ID = "appqkpDOLvi6AESlN"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

kitchen_setup_table = "tblNZQiFdZQzoLkVt"
client_servings_table = "tblVwpvUmsTS2Se51"

# Airtable table endpoints
CLIENT_SERVINGS_URL = f"https://api.airtable.com/v0/{BASE_ID}/{client_servings_table}"
KITCHEN_SETUP_URL = f"https://api.airtable.com/v0/{BASE_ID}/{kitchen_setup_table}"

# Django backend endpoint to forward result to
DJANGO_BACKEND_URL = "http://localhost:8000/api/latest-scan/"  # Update as needed

def fetch_kitchen_setup(station_prefix, dish):
    print(f"Client's Dish: {dish}")
    # List to store tuples of (ingredient, sequence)
    ingredients = []
    url = KITCHEN_SETUP_URL
    params = {}

    while True:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print("Failed to fetch kitchen screen setup:", response.text)
            break

        data = response.json()

        for record in data.get("records", []):
            fields = record.get("fields", {})
            stations = fields.get("Station", [])
            if not isinstance(stations, list):
                stations = [stations]

            # Extract these values at the record level since they're record-specific
            ingredient = fields.get("Ingredient")
            dish_name = fields.get("Dish Name")
            sequence = fields.get("Sequence", 1)  # Default to 1

            for station in stations:
                if isinstance(station, str) and station.lower().endswith(station_prefix.lower()):
                    if ingredient and (dish == dish_name):
                        ingredients.append((ingredient, sequence))
                    break

        if "offset" in data:
            params["offset"] = data["offset"]
        else:
            break

    # Sort by sequence and remove duplicates while preserving order
    ingredients.sort(key=lambda x: x[1])  # Sort by sequence (second element)
    
    # Remove duplicates while preserving order
    seen = set()
    ordered_ingredients = []
    for ingredient, sequence in ingredients:
        if ingredient not in seen:
            seen.add(ingredient)
            ordered_ingredients.append(ingredient)
    
    return ordered_ingredients


def fetch_client_servings(order_id):
    all_records = []
    params = {}

    while True:
        response = requests.get(CLIENT_SERVINGS_URL, headers=HEADERS, params=params)
        if response.status_code != 200:
            print("Failed to fetch client servings:", response.text)
            return []

        data = response.json()
        for record in data.get("records", []):
            fields = record.get("fields", {})
            record_id = str(fields.get("#"))  # Use '#' field from 'fields' dict
            if record_id == order_id:
                all_records.append(record)
                break

        if "offset" in data:
            params["offset"] = data["offset"]
        else:
            break

    return all_records


OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "data/latest_scan.json")

def process_scan(raw):
    prefix = ''.join([c for c in raw if c.isalpha()])
    order_id = ''.join([c for c in raw if c.isdigit()])[1:]

    if not prefix or not order_id:
        print(f"Invalid scan: {raw}")
        return

    print(f"\n📦 Scanner '{prefix}' read Order ID: {order_id}")

    # 1. Get client serving record
    client_records = fetch_client_servings(order_id)
    if not client_records:
        print("⚠️ No record found for this order ID.")
        return

    fields = client_records[0].get("fields", {})
    client_dish = fields.get("Dish")[0]

    # 2. Get allowed ingredients for this station
    allowed_ingredients = fetch_kitchen_setup(prefix, client_dish)
    print(f"Allowed ingredients for station '{prefix}': {allowed_ingredients}")

    # 3. Parse Modified Recipe Details (Python-style string dict)
    ingredient_results = []
    recipe_details_raw = fields.get("Modified Recipe Details", "{}")

    try:
        recipe_details = ast.literal_eval(recipe_details_raw)
    except Exception as e:
        print(f"❌ Failed to evaluate recipe details: {e}")
        recipe_details = {}

    # Process ingredients in the order they appear in allowed_ingredients
    for ingredient in allowed_ingredients:
        if ingredient in recipe_details:

            grams = recipe_details[ingredient]
            portion = f"{round(grams, 2)}g" if isinstance(grams, (int, float)) else "—"

            ingredient_clean = ' '.join(ingredient.split(' ')[1:]) if ' ' in ingredient else ingredient

            ingredient_results.append({
                "name": ingredient_clean,
                "portion": portion
            })

    # 4. Extract dietary restrictions
    dietary_restrictions = []
    notes = fields.get("Nutrition Notes")
    if notes:
        if isinstance(notes, list):
            dietary_restrictions = [str(n).strip() for n in notes]
        elif isinstance(notes, str):
            dietary_restrictions = [notes.strip()]

    # 5. Build output JSON structure
    output = {
        "clientName": fields.get("Customer Name", []),
        "mealType": fields.get("Order Type (from Linked OrderItem)", []),
        "dishName": fields.get("Dish", []),
        "dishNumber": int(order_id),
        "stationNumber": f"Station {prefix}",
        "barcodeNumber": raw,
        "ingredients": ingredient_results,
        "dietaryRestrictions": dietary_restrictions
    }

    # 6. Dump to file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"💾 Scan data written to {OUTPUT_FILE}")



print("🔄 Ready to scan barcodes (Ctrl+C to stop)...\n")

try:
    while True:
        raw = input().strip()
        process_scan(raw)
        time.sleep(1)  # Slight delay for safety

except KeyboardInterrupt:
    print("\n🛑 Scanner stopped.")