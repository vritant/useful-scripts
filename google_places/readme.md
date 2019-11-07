# [location_compute](location_compute.py)
* this script computes a grid given a location, distance between two locations, and how many locations east and south to compute

# [fetch_google_places](fetch_google_places.py)
* This script performs two functions:
   * given a location and a search text, make 3 google Places calls to fetch 60 locations nearby matching that text
      * requires input documents in the "inputs" collection of the format: {"lat": 12.312, "lng":31.21 }
   * given a google business  place id, return place details by making a single api call
      * requires input documents in the "detail_inputs" collection of the format: {"place_id": "asdajsldajlsdjk" }
      

