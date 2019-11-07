import math
import pymongo

R = 6378.1 #Radius of the Earth
brng_east = 1.5708 #Bearing is 90 degrees converted to radians.
brng_south = 3.14159
d = 40 #Distance in km

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["garages"]
inputs = mydb["inputs"]

# given a location, bearing (east or south), and distance, calculate new location
def get_lat_lng(lat, long, brng, d):
    lat1 = math.radians(lat) #Current lat point converted to radians
    lon1 = math.radians(long) #Current long point converted to radians

    lat2 = math.asin( math.sin(lat1)*math.cos(d/R) +
        math.cos(lat1)*math.sin(d/R)*math.cos(brng))

    lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat1),
        math.cos(d/R)-math.sin(lat1)*math.sin(lat2))

    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return lat2, lon2

# starting position
start_lat = 17.540980
start_lng = 78.246450

# for 30 kms, at 5 kms distance each bearing south
for south_dist in range(0, 30, 5):
    lat_new_south, lng_new_south = get_lat_lng(start_lat, start_lng, brng_south, south_dist)
    inputs.insert_one({"lat":lat_new_south, "lng":lng_new_south})
    print(str(lat_new_south)+","+str(lng_new_south))

    # for 35 kms, at 5 kms distance each bearing east
    for east_dist in range(5, 40, 5):
        lat_new_east, lng_new_east = get_lat_lng(lat_new_south, lng_new_south, brng_east, east_dist)
        inputs.insert_one({"lat":lat_new_east, "lng":lng_new_east})
        print(str(lat_new_east)+","+str(lng_new_east))
    print(" ")
