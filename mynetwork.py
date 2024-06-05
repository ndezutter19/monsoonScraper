import requests
import json
import threading
from AddressHelper import run_thread as city_thread

# URL for the POST request
url = "https://mymonsoon.com/api/properties/thin-search"

# List of zip codes
zip_code_numbers = [
    206273, 30003, 30004, 30005, 30006, 30008, 30009, 30011, 206274, 30012, 
    30013, 30014, 30015, 30016, 30017, 30018, 30019, 30020, 30021, 30022, 
    30023, 30024, 30025, 206142, 30026, 30027, 30028, 30029, 30030, 30031, 
    30032, 30033, 30034, 30035, 30036, 30037, 30038, 30039, 30040, 206275, 
    30041, 30042, 30043, 30044, 30045, 206143, 30047, 30048, 206144, 206145, 
    206146, 30049, 30050, 30051, 30052, 30053, 206147, 206148, 206149, 30054, 
    206150, 206151, 206152, 206153, 206154, 206155, 206276, 206156, 206157, 
    30055, 206158, 206159, 30056, 206160, 206451, 206161, 206162, 206163, 
    206164, 206165, 206166, 206167, 206168, 30058, 30059, 30060, 30061, 
    30062, 30063, 30064, 30065, 30066, 30067, 206169, 30068, 30069, 206170, 
    30070, 206171, 30076, 30077, 30078, 30080, 30081, 30082, 30086, 30087, 
    30088, 30089, 30090, 30091, 30092, 30093, 30094, 30095, 30096, 30097, 
    30098, 30099, 206172, 30100, 30101, 30102, 30103, 30104, 30105, 206173, 
    30106, 30107, 30109, 30110, 30111, 30112, 30113, 206277, 206450, 30116, 
    30117, 30118, 30119, 206174, 30120, 30121, 30122, 30123, 30124, 30125, 
    30126, 30127, 30128, 30129, 30130, 30131, 30132, 30133, 30134, 206278, 
    206279, 30135, 30136, 206280, 30137, 30138, 30139, 206281, 30140, 30141, 
    206282, 30142, 30143, 30144, 30145, 30146, 30147, 206283, 30148, 30149, 
    206284, 206285, 206286, 30150, 30151, 206287, 30152, 30153, 30154, 
    206288, 206289, 30155, 206290, 30156, 30157, 206291, 30158, 206292, 
    206293, 30159, 206294, 206295, 30160, 30161, 30162, 30163, 30164, 
    30165, 30166, 30167, 30168, 30169, 30170, 206175, 30171, 30172, 30173, 
    30175, 30176, 30177, 206296, 206297, 206298, 206299, 206300, 206301, 
    206302, 206176, 206303, 206304, 206305, 206306, 206307, 206308, 206309, 
    206310, 206311, 206312, 206313, 206187, 206177, 206314, 206315, 206316, 
    206317, 206318, 206319, 206320, 206188, 206189, 206321, 206322, 206323, 
    206178, 206190, 206324, 206325, 206191, 206179, 206326, 206327, 206328, 
    206329, 206330, 206192, 206331, 206180, 206332, 206333, 206226, 206334, 
    206335, 206193, 206336, 206337, 206194, 206338, 206339, 206340, 206181, 
    206341, 206182, 206195, 206196, 206197, 206198, 206227, 206199, 206228, 
    206200, 206201, 206202, 206203, 206204, 206205, 206206, 206207, 206208, 
    206229, 206230, 206231, 206209, 206342, 206232, 206233, 206210, 206211, 
    206212, 206183, 206213, 206214, 206215, 206234, 206216, 206217, 206218, 
    206219, 206220, 206221, 206343, 206222, 206223, 206224, 206344, 206345, 
    206346, 206347, 206348, 206349, 206350, 206351, 206352, 206353, 206354, 
    206355, 206356, 206357, 206358, 206359, 206360, 206361, 206362, 206363, 
    206364, 206365, 206366, 206367, 206368, 206369, 206370, 206371, 206372, 
    206373, 206374, 206375, 206376, 206377, 206378, 206379, 206380, 206381, 
    206382, 206383, 206384, 206385, 206386, 206387, 206389, 206390, 206391, 
    206392, 206393, 206396, 206397, 206398, 206399, 206400, 206401, 206402, 
    206403, 206404, 206405, 206406, 206407, 206408, 206409, 206410, 206411, 
    206412, 206413, 206414, 206415, 206416, 206417, 206418, 206419, 206420, 
    206421, 206422, 206423, 139999, 206424, 206425, 206426, 206427, 206428, 
    206429, 206430, 206431, 206432, 206433, 206434, 206435, 206436, 206437, 
    206438, 206439, 206440, 206441, 206442, 206443, 206444, 206445, 206446, 
    206447, 206449, "Unknown"
]

# Set the headers for the request
headers = {
    "Content-Type": "application/json"
}

# Initialize an empty list to hold all data
all_data = []

# Buffer for houses that do not yet have their extended information
buffer = [] 

# The compelte flag must be wrapped in order to pass the boolean value by reference...
class FlagWrap:
    def __init__(self, flag: bool):
        self.flag = flag

    def toggle(self, value):
        self.flag = value
        
complete = FlagWrap(False)

# Function to make the POST request and append data to the list
def fetch_data(zip_code):
    payload = {
        "pageNumber": 1,
        "searchType": "ListingResidentialSale",
        "addedSearchFields": [
            {"id": 96, "name": "GeographicShapeSet", "placeholderText": "Geographic Shape", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": -1, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 20, "name": "ListingNumber", "placeholderText": "MLS Number", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 1, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 116, "name": "SourceMLSId", "placeholderText": "MLS", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 2, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 18, "name": "ListingStatusId", "placeholderText": "Listing Status", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 3, "lowValue": "", "highValue": "", "listValues": ["1"], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 17, "name": "ListingPrice", "placeholderText": "Listing Price", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 4, "lowValue": "", "highValue": "500000", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 24, "name": "PropertyTypeId", "placeholderText": "Dwelling Type", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 5, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 6, "name": "CountyId", "placeholderText": "County", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 6, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 97, "name": "ListingAddress", "placeholderText": "Address", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 7, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 5, "name": "CityId", "placeholderText": "City", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 8, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 31, "name": "ZipId", "placeholderText": "Zip Code", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 9, "lowValue": "", "highValue": "", "listValues": [zip_code], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 10, "name": "InteriorAreaSqFt", "placeholderText": "SqFt", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 10, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 4, "name": "BedroomCount", "placeholderText": "# of Bedrooms", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 11, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 3, "name": "BathroomCount", "placeholderText": "# of Bathrooms", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 12, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 70, "name": "ListingTypeId", "placeholderText": "-", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 13, "lowValue": "", "highValue": "", "listValues": [1], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 102, "name": "SubdivisionName", "placeholderText": "Subdivision Name", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 14, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 19, "name": "ListingStatusTime", "placeholderText": "Status Change Date", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 15, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 73, "name": "OffMarketDate", "placeholderText": "Off Market Date", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 16, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "},
            {"id": 92, "name": "LastCOEPrice", "placeholderText": "Sold Price", "placeholderTextMin": "Min", "placeholderTextMax": "Max", "defaultDisplayIndex": 17, "lowValue": "", "highValue": "", "listValues": [], "listValuesByName": [], "isNot": False, "searchTextType": 0, "selectedTextType": "Contains", "showIsNotButton": False, "isDisabled": True, "shapes": [], "notButtonText": "Is "}
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

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Append the data to the list
        buffer.extend(data)
        
        print(f"Data for zip code {zip_code} fetched successfully.")
    else:
        print(f"Failed to fetch data for zip code {zip_code}. Status code: {response.status_code}")



def main():
        # Initialize an empty list to hold all data
    all_data = []

    # Buffer for houses that do not yet have their extended information
    buffer = [] 

    # The compelte flag must be wrapped in order to pass the boolean value by reference...            
    complete = FlagWrap(False)
    
    # Fetch data for all zip codes
    get_cities = threading.Thread(target=city_thread, args=(complete, buffer, all_data))
    get_cities.start()
    # for zip_code in zip_code_numbers:
        # fetch_data(zip_code)
    with open("response_data_active.json", 'r') as readFile:
        buffer.extend(json.loads(readFile.read()))

    # Toggle flag to tell thread retrieval process is complete
    complete.toggle(True)
    get_cities.join()

    # Save all data to a JSON file
    with open('response_data_active.json', 'w') as f:
        json.dump(all_data, f, indent=4)

    # Print the count of elements in the data
    print(f"Total number of elements in the data: {len(all_data)}")

if __name__ == "__main__":
    main()