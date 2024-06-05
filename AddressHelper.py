from geopy.geocoders import Nominatim
import json
import time

def get_city(geolocator, lat, lng):
    long =  str(lng)
    lati = str(lat)
    
    location = geolocator.reverse(lati+ "," + long)
    address = location.raw['address']
    city = address.get('city', '')
    
    return city

            
def run_thread(complete_flag, buffer: list, end_point: list):
    geolocator = Nominatim(user_agent="code_scrape_proj")
    
    # While the listing collection process is not complete and the buffer is not empty
    # continue to get properties from buffer.
    while(complete_flag.flag != True or len(buffer) != 0):
        # If buffer is empty but process is not complete then sleep...
        try:
            house =  buffer.pop()
        except IndexError as e:
            time.sleep(0.5)
            continue
            
        lat = house['lat']
        lng = house['lng']
        
        city = get_city(geolocator, lat, lng)
        house['city'] = city
        end_point.append(house)