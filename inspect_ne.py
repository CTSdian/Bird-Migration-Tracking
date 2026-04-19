import json
from urllib.request import urlopen

# Fetch and examine structure
country_url = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson'
with urlopen(country_url) as response:
    country_geojson = json.loads(response.read())

print(f"Total features: {len(country_geojson['features'])}\n")
print("Sample properties from first feature:")
if country_geojson['features']:
    props = country_geojson['features'][0]['properties']
    for key, value in sorted(props.items()):
        print(f"  {key}: {value}")

print("\n\nAll countries in dataset:")
countries = []
for feature in country_geojson['features']:
    props = feature['properties']
    # Try different name fields
    name = props.get('NAME', props.get('name', props.get('ADMIN', '')))
    if name:
        countries.append(name)

for i, country in enumerate(sorted(countries), 1):
    print(f"{i:3d}. {country}")
