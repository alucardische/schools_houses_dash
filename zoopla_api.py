import numpy as np
import requests
import json

url = "https://zoopla.p.rapidapi.com/properties/list"

def simple_request(postcode):
    querystring = {"area": postcode,"category":"residential","order_by":"age","ordering":"descending","page_number":"1",'radius': '1', 'listing_status': 'sale', 'minimum_beds': '3', "page_size":"40"}

    headers = {
        "X-RapidAPI-Key": "09d0601756msh0348545ff9d457ap112b91jsn9663254fb5c1",
        "X-RapidAPI-Host": "zoopla.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    json = response.json()
    return json

def get_floor_area(listing):
  try:
    if 'floor_area' not in listing:
      return None
    if 'min_floor_area' in listing['floor_area']:
      if listing['floor_area']['min_floor_area']['units'] == 'sq_feet':
        return int(np.round(np.float(listing['floor_area']['min_floor_area']['value']) * 0.092903))
      else:
        return int(np.round(np.float(listing['floor_area']['min_floor_area']['value'])))
  except:
    return np.nan

def prepare_link(link):
    return f"<a href='{link}' target='_blank'>link</a>"