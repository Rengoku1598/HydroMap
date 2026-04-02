import urllib.request
import json

overpass_url = "http://overpass-api.de/api/interpreter"

# Query for Uzbekistan waterways (rivers, lakes, reservoirs)
overpass_query = """
[out:json][timeout:90];
area["name:en"="Uzbekistan"]->.searchArea;
(
  way["waterway"="river"](area.searchArea);
  way["waterway"="canal"](area.searchArea);
  relation["natural"="water"](area.searchArea);
);
out geom;
"""

print("Fetching water data from Overpass API (using urllib)...")
try:
    req = urllib.request.Request(overpass_url, data=overpass_query.encode('utf-8'))
    with urllib.request.urlopen(req, timeout=100) as response:
        data = json.loads(response.read().decode('utf-8'))
    
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    for element in data.get('elements', []):
        tags = element.get('tags', {})
        geom = element.get('geometry', [])
        
        if not geom:
            continue
            
        coords = [[pt['lon'], pt['lat']] for pt in geom]
        
        feature_type = "LineString"
        is_water_body = 'natural' in tags and tags['natural'] == 'water'
        
        if is_water_body and len(coords) > 2 and coords[0] == coords[-1]:
            feature_type = "Polygon"
            coords = [coords] # Polygon requires nested array
            
        # Simplified filtering for overly large output (just basic check)
        if len(coords) < 2: 
            continue
            
        feature = {
            "type": "Feature",
            "properties": {
                "name": tags.get("name", ""),
                "type": "waterbody" if is_water_body else "river"
            },
            "geometry": {
                "type": feature_type,
                "coordinates": coords
            }
        }
        geojson["features"].append(feature)

    output_path = r"d:\Hydromap\backend_django\static\js\uz_water.geojson"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f)

    print(f"Successfully saved {len(geojson['features'])} features to {output_path}")

except Exception as e:
    print(f"Error fetching data: {e}")
