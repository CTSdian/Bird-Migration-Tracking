import json
import unicodedata
from urllib.request import urlopen
from backend.data_loader import get_route_aggregated_counts, normalize_geo_name

# Fetch Natural Earth data
print("Fetching Natural Earth GeoJSON...")
try:
    country_url = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson'
    with urlopen(country_url) as response:
        country_geojson = json.loads(response.read())
    print(f"Loaded {len(country_geojson['features'])} countries")
    
    admin1_url = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_1_states_provinces.geojson'
    with urlopen(admin1_url) as response:
        admin1_geojson = json.loads(response.read())
    print(f"Loaded {len(admin1_geojson['features'])} admin-1 features")
except Exception as e:
    print(f"Error fetching: {e}")
    exit(1)

# Load aggregated counts
agg = get_route_aggregated_counts(None)
agg_counts_dict = {}  # key format: "country::province"
for item in agg['counts']:
    country = item.get('country', '')
    province = item.get('province', '')
    count = item.get('count', 0)
    if country:
        # Try both with and without province
        if province and province != 'None':
            key = f"{country}::{province}"
            agg_counts_dict[key] = count
        country_key = country
        if country_key not in agg_counts_dict:
            agg_counts_dict[country_key] = 0
        agg_counts_dict[country_key] += count

print(f"\nAggregated {len(agg_counts_dict)} unique keys")

# Test matching for African countries
print("\n=== Testing African Country Matches ===")
african_countries = ['Morocco', 'Kenya', 'Angola', 'Algeria', 'Nigeria', 'Egypt', 'Ethiopia']

for country in african_countries:
    # Find in aggregated data
    agg_key = next((k for k in agg_counts_dict.keys() if k.split('::')[0].lower() == country.lower()), None)
    
    if agg_key:
        count = agg_counts_dict[agg_key]
        # Try to find in Natural Earth countries
        ne_name = next((f['properties'].get('name', '') for f in country_geojson['features'] 
                       if f['properties'].get('name', '').lower() == country.lower() or
                          f['properties'].get('name_en', '').lower() == country.lower()), None)
        
        if ne_name:
            print(f"✓ {country:15s} (agg_count={count:4d}) -> MATCHED: {ne_name}")
        else:
            print(f"✗ {country:15s} (agg_count={count:4d}) -> NO MATCH in Natural Earth")
    else:
        print(f"? {country:15s} -> NOT FOUND in aggregated data")

print("\nTest complete.")
