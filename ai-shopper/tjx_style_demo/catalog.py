import json, os
from .config import CATALOG_CACHE

# A small, static sample catalog (works offline). Feel free to add items or real URLs.
SAMPLE = [
    {"name": "Cable Knit Sweater - Cream", "price": 39.99, "url": "https://example.com/sweater", "image": None},
    {"name": "Classic Wool Coat - Black",  "price": 99.99, "url": "https://example.com/coat",    "image": None},
    {"name": "Mid-Rise Straight Jeans",    "price": 29.99, "url": "https://example.com/jeans",   "image": None},
    {"name": "Leather Chelsea Boots",      "price": 59.99, "url": "https://example.com/boots",   "image": None},
    {"name": "Canvas Tote - Beige",        "price": 19.99, "url": "https://example.com/tote",    "image": None},
]

def load_or_buildCatalog(max_products: int = 40):
    """
    If a cache exists, load it; otherwise seed it with SAMPLE data.
    Replace SAMPLE with real extraction if/when you turn on live fetching.
    """
    if os.path.exists(CATALOG_CACHE):
        with open(CATALOG_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)

    catalog = SAMPLE[:max_products]
    with open(CATALOG_CACHE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)
    return catalog
