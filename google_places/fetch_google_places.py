import json
import pymongo
import requests 
from datetime import datetime
from pytz import timezone    
import time

# currently unused, but you can use this to stop script from creating a huge bill
DAILY_LIMIT = 50

# If true, makes a call via rest. if false, fetches results from a local file.
# useful for debugging without making API calls
DATA_FROM_REST = True

# If true, Fetch a list of  places and stores it in a database
# requires input in the "inputs" collection
FETCH_PLACES = False

# If true, for each unique place from the previous API, fetches 
# requires input in the "detail_inputs" collection
FETCH_PLACE_DETAILS = True

# use free key when possible. un-comment only one key at a time
# paid
#key = 'myPaidApiKey'
# free
key = 'myFreeApiKey'

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["garages"]
garages = mydb["garages"]
details = mydb["details"]
location_results = mydb["location_results"]
place_detail_results = mydb["detail_results"]
inputs = mydb["inputs"]
detail_inputs = mydb["detail_inputs"]
calls = mydb["calls"]

# google resets the daily API count at PST time
pst= timezone('PST8PDT')
pst_time = datetime.now(pst)


# useful to find number of calls made since previous PST midnight
midnight = datetime.combine(pst_time, datetime.min.time())

# URL for the places call
URL = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
# URL for the details call
URL_detail = "https://maps.googleapis.com/maps/api/place/details/json?"

# Parses results from the Places call and stores it in db uniquely
def parse_results(data, display):
    results = {}
    if 'results' in data.keys():
        print "Parsing", len(data['results']), "results"
        for result in data['results']:
            result['_id'] = result['id']
            results[result['_id']] = result
            print('Name: ' + result['name'].encode('utf-8'))
            if display:
                print('address: ' + result['formatted_address'])
                print('id ' + result['_id'])
                print('place_id ' + result['place_id'])
                #print('compound code ' + result['plus_code']['compound_code'])
                #print('global code ' + result['plus_code']['global_code'])
                print("lat "+join(result['geometry']['location']['lat']).encode('utf-8'))
                print("lng "+join(result['geometry']['location']['lng']).encode('utf-8'))
                print("lng "+join(result['geometry']['location']['lng']).encode('utf-8'))
                print('rating ' + join(result['rating']).encode('utf-8'))
                types = ""
                for type in result['types']:
                    types += type + ", "
                    print('types ' + types[0:-2])
            garages.replace_one({'_id': result['_id']}, result, upsert=True)
    print " "
    if 'next_page_token' in data.keys():
        return data['next_page_token'], data['results']
    return None, data['results']


# Given a location, fetch all Google locations around that location
def fetch_places(lat, lng):
    
    PARAMS = {
    'input':'car service',
    'inputtype':'textquery',
    'location': ''.join([str(lat),', ',str(lng)]),
    'key':key,
    'fields':'address_component,adr_address,formatted_address,geometry,icon,name,permanently_closed,photos,place_id,plus_code,type,types,url,utc_offset,vicinity,formatted_phone_number,international_phone_number,opening_hours,website,price_level,rating,reviews,user_ratings_total'
    }

    same_request = True
    curr_rest_call = 1
    next_page_token = None
    # make calls untill we dont recieve a next_page_token
    while same_request:
        # keep a record of all rest calls made for audit
        calls.insert_one({"pst_time": datetime.now(pst), "ist_time": datetime.now(), "type":"places", "rest":DATA_FROM_REST})

        # count number of calls made since last PST midnight to monitor daily quota
        count = mydb.calls.find({"pst_time": {"$gte": midnight}}).count()
        count+= 1
        print "making rest call #"+ str(count)

        if DATA_FROM_REST:
            r = requests.get(url = URL, params = PARAMS)
            #print r.request.url
            #print r.request.headers
            #print r.json()
            # extracting data in json format 
            data = r.json()
        else:
            print "loading from file"
            if curr_rest_call == 3:
                file = 'results_no_next.json'
            else:
                file = 'results.json'
            curr_rest_call+= 1
            with open(file, 'r') as f:
                data = json.load(f)

        next_page_token, results = parse_results(data, False)
        #print "recieved token>>>", next_page_token 
        location_results.insert_one({'lat':lat, 'lng':lng, 'time':datetime.now(), 'results': results})
        if next_page_token:
            same_request = True
            # google requires a pause. removing this will cause invalid requests
            time.sleep(2)
            PARAMS['pagetoken'] = next_page_token
        else:
            # input is consumed, so delete the input from records
            inputs.delete_one({"lat":lat, "lng":lng})
            same_request = False


# given a place id, fetch place details
def fetch_place_detail(place_id):
    PARAMS = {
    'place_id': place_id,
    'key':key,
    'fields':'address_component,adr_address,formatted_address,geometry,icon,name,permanently_closed,photos,place_id,plus_code,type,types,url,utc_offset,vicinity,formatted_phone_number,international_phone_number,opening_hours,website,price_level,rating,reviews,user_ratings_total'
    }

    calls.insert_one({"pst_time": datetime.now(pst), "ist_time": datetime.now(), "type":"detail", "rest":DATA_FROM_REST})

    count = mydb.calls.find({"pst_time": {"$gte": midnight}}).count()
    count+= 1
    print "making rest call #"+ str(count)

    if DATA_FROM_REST:
        r = requests.get(url = URL_detail, params = PARAMS)
        #print r.request.url
        #print r.request.headers
        #print r.json()
        # extracting data in json format 
        data = r.json()
    else:
        print "loading from file"
        file = 'detail_results.json'
        with open(file, 'r') as f:
            data = json.load(f)

    place_detail_results.insert_one({'place':place_id, 'time':datetime.now(), 'results': data})
    if data['status'] == 'OK':
        result = data['result']
        details.replace_one({'_id': result['place_id']}, result, upsert=True)
        detail_inputs.delete_one({"place_id":place_id})
    else:
        print "query for", place_id, "failed with", data['status'], ", will trying again.."


if FETCH_PLACES:
    # might wanna use paid API for this since we use paging
    print "Fetching places around a given location.."
    for input in inputs.find():
        print "latitude: ", input['lat'], "longitude", input['lng']
        fetch_places(input['lat'], input['lng'])
        print "completed"
if FETCH_PLACE_DETAILS:
    # might wanna use free API for this
    print "Fetching place details.."
    detail_list = list(detail_inputs.find())
    for detail_input in detail_list:
        print "place id:", detail_input['place_id']
        fetch_place_detail(detail_input['place_id'])
        print "completed"
        #using free API once a minute works without errors
        time.sleep(60)

