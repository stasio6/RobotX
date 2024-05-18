import math

def calculate_bearing(x, y):
    magnitude = math.sqrt(x**2 + y**2)
    x /= magnitude
    y /= magnitude
    angle_rad = math.atan2(y, x)
    angle_deg = math.degrees(angle_rad)
    bearing = (angle_deg + 360) % 360
    return bearing

def add_distance_to_coordinates(lat, lon, x, y):
    # Earth radius in meters
    R = 6378137.0

    # Convert latitude and longitude to radians
    lat_rad = math.radians(lat / 1e7)
    lon_rad = math.radians(lon / 1e7)

    # pythagoreans therem 
    distance = math.sqrt(x**2 + y**2)

    bearing = calculate_bearing(x, y)
    bearing_rad = math.radians(bearing)

    angular_distance = distance / R

    new_lat_rad = math.asin(math.sin(lat_rad) * math.cos(angular_distance) +
                            math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing_rad))
    new_lon_rad = lon_rad + math.atan2(math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat_rad),
                                       math.cos(angular_distance) - math.sin(lat_rad) * math.sin(new_lat_rad))

    new_lat = float(math.degrees(new_lat_rad) * 1e7)
    new_lon = float(math.degrees(new_lon_rad) * 1e7)

    return new_lat, new_lon

# # Test the function
# lat = 328815281
# lon = -1172330594
# x = 30  
# y = 40

# print(f'Original latitude: {lat}, Original longitude: {lon}')

# new_lat, new_lon = add_distance_to_coordinates(lat, lon, x, y)
# print(f'New latitude: {new_lat}, New longitude: {new_lon}')

# print("Testing")

# new_lat, new_lon = add_distance_to_coordinates(new_lat, new_lon, -x, -y)
# print(f'New latitude: {new_lat}, New longitude: {new_lon}')







import math

def calculate_distance(lat1, lon1, lat2, lon2):
    # Earth radius in meters
    R = 6378137.0

    # Convert latitude and longitude to degrees
    lat1_deg = lat1 / 1e7
    lon1_deg = lon1 / 1e7
    lat2_deg = lat2 / 1e7
    lon2_deg = lon2 / 1e7

    # Convert latitude and longitude to radians
    lat1_rad = math.radians(lat1_deg)
    lon1_rad = math.radians(lon1_deg)
    lat2_rad = math.radians(lat2_deg)
    lon2_rad = math.radians(lon2_deg)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

# # Test the function
# lat1 = 328815281
# lon1 = -1172330594
# lat2 = 328825381
# lon2 = -1172350694

# distance = calculate_distance(lat1, lon1, lat2, lon2)
# print(f'Distance between the two points: {distance} meters')