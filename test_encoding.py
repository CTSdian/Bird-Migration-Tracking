from backend.data_loader import normalize_geo_name, standardize_country_name

# Test broken names from the data
test_names = [
    "Hu¨ªla",  # Should become "huila"
    "H¨¡ Nam",  # Should become "ha nam"
    "H?fu?borgarsv??i",  # Should become "hofuborgarsvadi"
    "Morocco",
    "Kenya",
    "Algeria",
]

print("Testing encoding fixes:")
for name in test_names:
    normalized = normalize_geo_name(name)
    standardized = standardize_country_name(name)
    print(f"  {name:20s} -> normalized: {normalized:20s} standardized: {standardized}")
