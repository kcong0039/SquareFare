from django.http import JsonResponse
import json
import os
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import re
import math

@csrf_exempt
def latest_scan_view(request):
    # Path to JSON file
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_file_path = os.path.join(project_root, "api", "data", "latest_scan.json")
    
    if not os.path.exists(json_file_path):
        return JsonResponse({"message": "No scan yet"}, status=204)

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Process ingredients - handle both formats
        ingredients = []
        if "ingredients" in raw_data:
            for item in raw_data["ingredients"]:
                # Handle both direct name/portion and ingredient/weight formats
                name = item.get("name") or item.get("ingredient")
                portion = item.get("portion") or format_portion(item.get("weight"))

                weight = extract_number_and_string(portion)
                
                if name is not None:  # Only include if name exists
                    ingredients.append({
                        "name": str(name).strip(),
                        "portion": str(weight).strip() if weight else "—"
                    })

        # Build response data
        response_data = {
            "clientName": unpack_value(raw_data.get("clientName")),
            "mealType": unpack_value(raw_data.get("mealType")),
            "dishName": unpack_value(raw_data.get("dishName")),
            "dishNumber": raw_data.get("dishNumber"),
            "stationNumber": unpack_value(raw_data.get("stationNumber")),
            "barcodeNumber": unpack_value(raw_data.get("barcodeNumber")),
            "ingredients": ingredients,
            "dietaryRestrictions": raw_data.get("dietaryRestrictions")
        }
        
        return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse(
            {"error": f"Data processing error: {str(e)}"},
            status=500
        )

def unpack_value(value):
    """Safely extract value from potential array wrapper"""
    if isinstance(value, list):
        return value[0].strip() if value and isinstance(value[0], str) else value[0] if value else ""
    return value.strip() if isinstance(value, str) else value

def format_portion(weight):
    """Convert weight to portion string"""
    if weight is None:
        return "—"
    try:
        return f"{float(weight):g} oz" if float(weight) != 0 else "—"
    except (ValueError, TypeError):
        return str(weight)
    
def extract_number_and_string(s):
    match = re.match(r"^([+-]?\d*\.?\d+)\s*([a-zA-Z]+)$", s)
    if match:
        number = match.group(1)
        unit = match.group(2)

        number = str(math.floor(float(number) + 0.5))       # round off to nearest int

        return str(number) + " " + str(unit)
    return "-"

@csrf_exempt
def scan_result(request):
    """Endpoint for scanner.py to post data"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Ensure directory exists
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.makedirs(os.path.join(project_root, "api", "data"), exist_ok=True)
            
            # Save the raw data
            json_file_path = os.path.join(project_root, "api", "data", "latest_scan.json")
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return JsonResponse({"status": "success"})
        
        except Exception as e:
            return JsonResponse(
                {"error": str(e)},
                status=400
            )
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

def index(request):
    return render(request, 'index.html')