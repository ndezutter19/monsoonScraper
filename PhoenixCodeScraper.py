import concurrent.futures
import json
import random
import time
import pprint
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.support.relative_locator import locate_with
from selenium.common.exceptions import StaleElementReferenceException
from CodeEnforcementEntry import CodeEnforcementEntry
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

request_url = "https://api.umeprojects.com/api/v1/public/listings?orderBy=certified,verified&order=DESC,DESC&location=AZ&rooms=&bathrooms=&loanType=&sqft={%22min%22:%22%22,%22max%22:%22%22}&rate={%22min%22:%22%22,%22max%22:%22%22}&price={%22min%22:0,%22max%22:500000}&maxDownPayment={%22min%22:%22%22,%22max%22:%22%22}&status=[%22Active%22, %22Pending%22, %22Closed%22]&perPage=1700&page=0&bounds=&center=&zoom="
form_url = "https://nsdonline.phoenix.gov/CodeEnforcement"

MAX_THREADS = 1
MAX_AGENTS = 1
MAX_TIMEOUT = 10
MONTHS_RECENT = 6
proxies = []

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A5341f Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-N960U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/10.1 Chrome/71.0.3578.99 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:80.0) Gecko/20100101 Firefox/80.0"
]

def isRecent(open, close):
    # If no close date found then it must be recent or active
    if close == None or close == '':
        return True
    
    # Convert into datetime for comparison
    date = datetime.strptime(open, '%m/%d/%Y')
    current_date = datetime.now()
    
    delta_date = current_date - relativedelta(months=MONTHS_RECENT)
    if delta_date <= date <= current_date:
        return True
    else:
        return False

def execute_task(proxies, houses: list, id):    
    # proxy_string = proxies[random.randint(0, len(proxies))]
    # proxy = {
    #     "http": f"http://{proxy_string}",
    #     "https": f"https://{proxy_string}"
    # }
    
    # Create options to detail driver behavior.
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    #options.add_argument(f"--proxy-server={proxy_string}")
    bot = webdriver.Chrome(options)
    bot.set_page_load_timeout(30)
    bot.set_script_timeout(30)
    bot.get(form_url)
    

    
    properties_with_violations = {}
    
    # While there are still houses in the houses array pop and look for violations.
    while len(houses) > 0:
        house = houses.pop()
        if house['Property']['city'] != "Phoenix":
            continue
        
        try:
            properties_with_violations[house['Property']['address']] = check_code_violations(bot, house)
        except:
            print(f"Error encountered while checking address: {house['Property']['address']}")
            continue
    
    return properties_with_violations

def check_code_violations(bot, house):
    violations = {}
    
    # Get data from house json.
    prop_num = house['Property']['streetNumber']
    prop_st_dir = house['Property']['streetDirPrefix']
    prop_st_name = house['Property']['route']
    
    # Enter data into text input fields.
    st_number_box = check_element_viability(bot, By.XPATH, "//input[@name='stNumber']")
    st_number_box.send_keys(prop_num)
    
    st_direction_box = check_element_viability(bot, By.XPATH, "//input[@name='stDirection']")
    st_direction_box.send_keys(prop_st_dir)
    
    st_name_box = check_element_viability(bot, By.XPATH, "//input[@name='stName']")
    st_name_box.send_keys(prop_st_name)
    
    # Click search.
    search_button = check_element_viability(bot, By.XPATH, "//input[@type='submit' and @value='Search by Address']")
    ActionChains(bot)\
        .move_to_element(search_button)\
        .click()\
        .perform()
        
    # If results are found then check them.
    results_found = check_results(bot, search_button)
    if results_found:
        violations = process_results(bot)

    
    # Clear old data.
    search_button = check_element_viability(bot, By.XPATH, "//input[@type='submit' and @value='Search by Address']")
    clear_button_locator = locate_with(By.XPATH, "//input[@type='reset']").to_right_of(search_button)
    clear_button = bot.find_element(clear_button_locator)
    ActionChains(bot)\
        .move_to_element(clear_button)\
        .click()\
        .perform()

    return violations
       
def process_results(bot: webdriver.Chrome):
    """
    Scrapes the table of results for their violation codes and statuses returning
    recent violations.

    Args:
        bot (webdriver.Chrome): The webdriver processing these results.

    Returns:
        entries: Recent violation entries
    """
    
    # Locate needed elements.
    search_results = bot.find_element(By.XPATH, "//div[@id='search-results-container']")
    table_body = search_results.find_element(By.TAG_NAME, "tbody")
    table_results = table_body.find_elements(By.XPATH, "./tr")
    
    recent_entries = []
    
    # For every item in the table check if recent.
    for item in table_results:
        data_set = item.find_elements(By.XPATH, './*')
        
        case_opened = data_set[3]
        case_closed = data_set[4]
        
        # If entry isn't recent immediately move on else add to entries list.
        if not isRecent(case_opened, case_closed):
            continue
        
        case_number = data_set[0]
        address = data_set[1]
        case_status = data_set[2]
        owner = data_set[5]
        link = case_number.find_element(By.XPATH, './a').get_attribute('href')
        entry = CodeEnforcementEntry(case_number.text, address.text, case_status.text, case_opened.text, case_closed.text, owner.text, link)
    
        recent_entries.append(entry)

    # For every recent entry scrape violation types from their links.
    entries = []
    for entry in recent_entries:
        get_violations(bot, entry)
        entries.append(entry.to_dict())
    
    
    bot.get(form_url)
    return entries
        
def get_violations(bot: webdriver.Chrome, entry: CodeEnforcementEntry):
    # Go to the violations URL and load violations pane content.
    bot.get(entry.link)
    tab_button = bot.find_element(By.CSS_SELECTOR, "ul.nav-tabs").find_element(By.XPATH, ".//a[@href='#propertyViolationsPane']")
    ActionChains(bot)\
        .move_to_element(tab_button)\
        .click()\
        .perform()
    
    violations_tab = bot.find_element(By.CSS_SELECTOR, "div#propertyViolationsPane")
    violations_headers = violations_tab.find_elements(By.CSS_SELECTOR, 'span.lead')
    
    # For every violation found trim the prefix string out and append this violation to entry's violations list.
    for violation in violations_headers:
        trim = violation.text.removeprefix("Violation Code: ")
        entry.violations.append(trim)


def check_results(bot: webdriver.Chrome, search_button):
    # Checks if results were returned by the search.
    try:
        form = bot.find_element(By.XPATH, "//form[@id='addressSearchForm']")
        results_locator = locate_with(By.TAG_NAME, 'p').below(form)
        results = bot.find_element(results_locator)
        if "no results" in results.text:
            return False
        else:
            return True
    except:
        print("Could not find the results 'p' object")
        return False


def check_element_viability(bot: webdriver.Chrome, locator_type, locator_value):
    # Checks if an element is a valid target for actions to avoid stale element error.
    wait = WebDriverWait(bot, timeout=MAX_TIMEOUT)
    try:
        check_element = wait.until(EC.presence_of_element_located([locator_type, locator_value]))
        wait.until(EC.element_to_be_clickable(check_element))
        wait.until_not(EC.staleness_of(check_element))
        return check_element
    except StaleElementReferenceException:
        return check_element_viability(bot, locator_type, locator_value)
    except TimeoutException:
        print(f'Timed out while looking for element with {locator_type}:{locator_value}')
    
def read_from_file():
    # Reads data from file instead of requesting it for the sake of speed.
    houses: list
    with open("HouseData.json", mode="r") as f:
        houses = json.load(f)
        return houses
    
def borrow_from_api():
    # "Borrows" the data from the API.
    response = requests.get(request_url)
    data = response.json()
    houses = []
    with open("HouseData.json", mode="w") as f:
        houses_list: list = data['items']
        for house in houses_list:
            if house['Property']['listPrice'] < 500000:
                houses.append(house)
        f.write(json.dumps(houses))
    
    print(len(houses))
    
    return houses

def start_threads(houses : list):
    proxies = None # get_proxies()
    properties_in_violation = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(execute_task, proxies, houses, i + 1): i for i in range(MAX_AGENTS)}
        
        for future in concurrent.futures.as_completed(futures):
            try:
                properties = future.result()
                if properties is not None:
                    for p in properties:
                        properties_in_violation.append(p)
            except Exception as e:
                print(f"Error occurred: {e}")
                raise e
    
    return properties_in_violation

def get_proxies():
    prox = []
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    bot = webdriver.Chrome(options)
    bot.get("https://sslproxies.org/")
    
    table = bot.find_element(By.XPATH, "//table[@class='table table-striped table-bordered']/tbody")
    entries = table.find_elements(By.TAG_NAME, 'tr')
    for entry in entries:
        temp = entry.find_elements(By.TAG_NAME, 'td')
        prox.append(f"{temp[0].text}:{temp[1].text}")
    
    bot.close()
    return prox
