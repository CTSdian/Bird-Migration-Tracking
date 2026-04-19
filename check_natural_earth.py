import json
from urllib.request import urlopen

# Fetch Natural Earth countries
country_url = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson'
with urlopen(country_url) as response:
    country_geojson = json.loads(response.read())

# Extract all country names and find African ones
print("Natural Earth Countries with 'Africa' or target countries:")
african_keywords = ['Africa', 'morocc', 'egypt', 'algeria', 'niger', 'kenya', 'angola', 'ethiopia']

for feature in country_geojson['features']:
    props = feature['properties']
    name = props.get('name', '')
    continent = props.get('CONTINENT', '')
    
    if any(kw in name.lower() or kw in continent.lower() for kw in african_keywords):
        print(f"  name={name:40s} name_en={props.get('name_en', 'N/A'):30s} ADMIN={props.get('ADMIN', 'N/A')}")
