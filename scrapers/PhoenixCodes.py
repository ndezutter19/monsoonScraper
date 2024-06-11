import concurrent.futures
from io import StringIO
import json
from lxml import etree
import logging
import ScrapeTools
import time
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
from bs4 import BeautifulSoup

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

def violationConfirmed(status: str):
    temp = status.lower()
    if temp == "closed no violation found":
        return False
    return True
    
    
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

def execute_task(houses: list):    
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
    
    count = 1
    average_lap = 0
    # While there are still houses in the houses array pop and look for violations.
    while len(houses) > 0:
        lap_start = time.time()
        house = houses.pop()
        print(f"Processing house {count} of {total_length}...")
        violations = check_code_violations(bot, house)
        
        lap_end = time.time()
        lap_delta = lap_end - lap_start
        print(f"Took: {lap_delta}s")
        average_lap += lap_delta
        if count != 1:
            average_lap /= 2
            
        count += 1
        if violations == {} or violations is None:
            continue
        
        properties_with_violations[house] = violations
    
    print(f"Average Lap: {average_lap}s")
    return properties_with_violations

def check_code_violations(bot : webdriver.Chrome, address):
    violations = {}
    
    breakdown = ScrapeTools.break_down_address_op(address)
    try:
        prop_num = breakdown['streetNum']
        prop_st_dir = breakdown['streetDirection']
        type_abbr = ScrapeTools.get_abbreviated(breakdown['streetType'])
        prop_st_name = f"{breakdown['streetName']} {type_abbr}"
    except TypeError:
        logging.WARNING(f"Error in input data, address: {address}")
        return {}
    
    if breakdown['suffixDirection'] is not None:
        prop_st_name += breakdown['suffixDirection']
    
    # Get form that is parent to all needed elements to reduce XPATH traversal time.
    parent = ScrapeTools.check_element_viability(bot, By.XPATH, "//form[@action='/CodeEnforcement' and @id='addressSearchForm']")
    
    # Enter data into text input fields.
    st_number_box = ScrapeTools.check_element_viability(parent, By.XPATH, ".//input[@name='stNumber']")
    st_number_box.send_keys(prop_num)
    
    st_direction_box = ScrapeTools.check_element_viability(parent, By.XPATH, ".//input[@name='stDirection']")
    st_direction_box.send_keys(prop_st_dir[0])
    
    st_name_box = ScrapeTools.check_element_viability(parent, By.XPATH, ".//input[@name='stName']")
    st_name_box.send_keys(prop_st_name)
    
    # Click search.
    search_button = ScrapeTools.check_element_viability(parent, By.XPATH, ".//input[@type='submit' and @value='Search by Address']")
    ActionChains(bot)\
        .move_to_element(search_button)\
        .click()\
        .perform()
        
    # If results are found then check them.
    results_found = check_results(bot, search_button)
    if results_found:
        violations = process_results(bot)

    
    # Clear old data.
    search_button = ScrapeTools.check_element_viability(bot, By.XPATH, ".//input[@type='submit' and @value='Search by Address']")
    clear_button_locator = locate_with(By.XPATH, ".//input[@type='reset']").to_right_of(search_button)
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
        
        case_status = data_set[2].text
        case_opened = data_set[3].text
        case_closed = data_set[4].text
        
        
        # If entry isn't recent immediately move on, else add to entries list.
        if not isRecent(case_opened, case_closed):
            continue
        
        if not violationConfirmed(case_status):
            continue
        
        print('Found recent entry, logging...')
        
        case_number = data_set[0]
        address = data_set[1]
        owner = data_set[5]
        link = case_number.find_element(By.XPATH, './a').get_attribute('href')
        entry = CodeEnforcementEntry(case_number.text, address.text, case_status, case_opened, case_closed, owner.text, link)
    
        recent_entries.append(entry)

    # For every recent entry scrape violation types from their links.
    entries = []
    for entry in recent_entries:
        if get_violations(bot, entry):
            entries.append(entry.to_dict())
    
    
    bot.get(form_url)
    if len(entries) == 0:
        return None
    
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
    
    if len(violations_headers) == 0:
        return False
    
    # For every violation found trim the prefix string out and append this violation to entry's violations list.
    for violation in violations_headers:
        trim = violation.text.removeprefix("Violation Code: ")
        entry.violations.append(trim)
        
    return True


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
    
    
start_time = time.time()
#with open("data/PhoenixAddressesTrunc.json", "r") as f:
#    houses = json.loads(f.read())['addresses']
#    global total_length
#    total_length = len(houses)
#    output = execute_task(houses)
    
#    with open("data/PhoenixAddressResults.json", "w") as res:
#        res.write(json.dumps(output))


end_time = time.time()
delta_time = end_time - start_time
print(f"Altogether took: {delta_time}s")