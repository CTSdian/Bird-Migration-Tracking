import json
from urllib.request import urlopen

# Fetch Natural Earth countries
country_url = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson'
with urlopen(country_url) as response:
    country_geojson = json.loads(response.read())

# Get all country names to look for African ones
names = set()
for feature in country_geojson['features']:
    props = feature['properties']
    name = props.get('name', '')
    if name:
        names.add(name)

# Sort and print all names
for name in sorted(names):
    if any(word in name for word in ['Africa', 'Morocco', 'Egypt', 'Algeria', 'Nigeria', 'Kenya', 'Angola', 'Ethiopia', 'Sudan', 'South Africa']):
        print(f"FOUND: {name}")

# If not found, show all names for manual inspection
print("\n\nAll countries (first 50):")
for i, name in enumerate(sorted(names)):
    if i < 50:
        print(f"  {name}")
