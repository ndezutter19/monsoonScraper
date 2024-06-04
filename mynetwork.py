import requests
import json

# URL for the POST request
url = "https://mymonsoon.com/api/properties/thin-search"

# Body of the POST request
payload = {
    "pageNumber": 1,
    "searchType": "ListingResidentialSale",
    "addedSearchFields": [
        {"id": 96, "name": "GeographicShapeSet", "placeholderText": "Geographic Shape", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": -1, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 20, "name": "ListingNumber", "placeholderText": "MLS Number", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 1, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 116, "name": "SourceMLSId", "placeholderText": "MLS", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 1, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 18, "name": "ListingStatusId", "placeholderText": "Listing Status", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 2, "lowValue": "", "highValue": "", "listValues": ["1"], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 17, "name": "ListingPrice", "placeholderText": "Listing Price", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 3, "lowValue": "", "highValue": "500000", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 24, "name": "PropertyTypeId", "placeholderText": "Dwelling Type", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 4, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 6, "name": "CountyId", "placeholderText": "County", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 5, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 97, "name": "ListingAddress", "placeholderText": "Address", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 6, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 5, "name": "CityId", "placeholderText": "City", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 7, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 31, "name": "ZipId", "placeholderText": "Zip Code", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 8, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 10, "name": "InteriorAreaSqFt", "placeholderText": "SqFt", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 9, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 4, "name": "BedroomCount", "placeholderText": "# of Bedrooms", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 10, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 3, "name": "BathroomCount", "placeholderText": "# of Bathrooms", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 11, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 70, "name": "ListingTypeId", "placeholderText": "-", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 12, "lowValue": "", "highValue": "", "listValues": [1], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 102, "name": "SubdivisionName", "placeholderText": "Subdivision Name", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 13, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
        {"id": 19, "name": "ListingStatusTime", "placeholderText": "Status Change Date", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 14, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "}
    ],
    "savedSearches": [],
    "hasNoSavedSearches": False,
    "isAddingSavedSearch": False,
    "isMobile": False,
    "sortList": [],
    "selectedSort": 25,
    "hasSearched": False,
    "isDirty": True
}

# Set the headers for the request
headers = {
    "Content-Type": "application/json"
}

# Make the POST request
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    
    # Save the data to a JSON file
    with open('response_data.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    print("Data saved to response_data.json")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
