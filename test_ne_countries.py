import json
from urllib.request import urlopen

# Fetch Natural Earth countries
print("Fetching Natural Earth 110m countries...")
country_url = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson'
with urlopen(country_url) as response:
    country_geojson = json.loads(response.read())

print(f"Total features: {len(country_geojson['features'])}\n")

# Look for specific countries
targets = ['Morocco', 'Kenya', 'Algeria', 'Nigeria', 'Angola', 'Egypt', 'Ethiopia']

for target in targets:
    found = False
    for feature in country_geojson['features']:
        props = feature['properties']
        # Check all relevant fields
        fields_to_check = ['name', 'name_en', 'admin', 'geounit', 'subunit', 'formal_en', 'brk_name']
        for field in fields_to_check:
            val = props.get(field, '')
            if isinstance(val, str) and target.lower() in val.lower():
                print(f"✓ Found '{target}' in property '{field}': {val}")
                found = True
                break
        if found:
            break
    if not found:
        print(f"✗ '{target}' NOT FOUND in Natural Earth 110m")

# Try 50m version for countries
print("\n\nTrying Natural Earth 50m countries...")
country_url_50m = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson'
try:
    with urlopen(country_url_50m) as response:
        country_geojson_50m = json.loads(response.read())
    print(f"50m features: {len(country_geojson_50m['features'])}\n")
    
    for target in targets:
        found = False
        for feature in country_geojson_50m['features']:
            props = feature['properties']
            fields_to_check = ['name', 'name_en', 'admin', 'geounit', 'subunit', 'formal_en', 'brk_name']
            for field in fields_to_check:
                val = props.get(field, '')
                if isinstance(val, str) and target.lower() in val.lower():
                    print(f"✓ Found '{target}' in 50m property '{field}': {val}")
                    found = True
                    break
            if found:
                break
        if not found:
            print(f"✗ '{target}' NOT FOUND in 50m either")
except Exception as e:
    print(f"Error fetching 50m: {e}")
