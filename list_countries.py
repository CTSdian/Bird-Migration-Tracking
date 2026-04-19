import json
from urllib.request import urlopen

# Fetch and list all countries
country_url = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson'
with urlopen(country_url) as response:
    country_geojson = json.loads(response.read())

print(f"Total features: {len(country_geojson['features'])}\n")
print("All countries in Natural Earth 110m:")

countries = []
for feature in country_geojson['features']:
    props = feature['properties']
    admin = props.get('ADMIN', '')
    countries.append(admin)

for country in sorted(countries):
    print(country)
