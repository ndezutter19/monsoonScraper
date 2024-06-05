import copy
import requests
import json

request_url = "https://api.umeprojects.com/api/v1/public/listings?orderBy=certified,verified&order=DESC,DESC&location=AZ&rooms=&bathrooms=&loanType=&sqft={%22min%22:%22%22,%22max%22:%22%22}&rate={%22min%22:%22%22,%22max%22:%22%22}&price={%22min%22:%22%22,%22max%22:%22500,000%22}&maxDownPayment={%22min%22:%22%22,%22max%22:%22%22}&status=[%22Active%22, %22Pending%22, %22Closed%22]&perPage=999999&page=0&bounds=&center=&zoom="

file = open("config.json", "r")
config = json.loads(file.read())
standard = config['listingDefinition']

def read_from_file():
    houses: list
    with open("HouseData.json", mode="r") as f:
        houses = json.load(f)
        return houses



def borrow_from_api():

    
    response = requests.get(request_url)
    data = response.json()
    houses = []
    with open("HouseData.json", mode="w") as f:
        houses_list: list = data['items']
        for house in houses_list:
            if house['Property']['listPrice'] < 500000:
                standardized = standardize_data(house)
                houses.append(standardized)
        f.write(json.dumps(houses))
    
    return houses

def standardize_data(house):
    standardized = copy.deepcopy(standard)
    standardized['listingNumber'] = None # Not sure if SparkListingId is the listing number
    standardized['address'] = house['Property']['address']
    standardized['postal'] = house['Property']['postal']
    standardized['parcel'] = house['Property']['parcel']
    standardized['county'] = house['Property']['country']
    standardized['city'] = house['Property']['city']
    standardized['streetPrefix'] = house['Property']['streetDirPrefix']
    standardized['streetSuffix'] = house['Property']['streetDirSuffix']
    standardized['route'] = house['Property']['route']
    standardized['streetNum'] = house['Property']['streetNumber']
    standardized['unitNum'] = house['Property']['unitNumber']
    standardized['mlsSource'] = house['Property']['source']
    standardized['propertyStatus'] =  house['Property']['StandardStatus']
    standardized['listPrice'] = house['Property']['listPrice']
    standardized['photos'] = house['Property']['photos']['all']
    standardized['violations'] = []
    standardized['agentFullName'] = house['Property']['metadata']['ListAgentFullName']
    return standardized
    
