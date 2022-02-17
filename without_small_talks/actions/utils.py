__all__ = ["get_pincode_details"]

import requests
from functools import lru_cache


@lru_cache(maxsize=None)
def get_pincode_details(pincode):
    url = f"https://api.postalpincode.in/pincode/{pincode}"
    json_data = requests.get(url).json()
    return json_data
