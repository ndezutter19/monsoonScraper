import concurrent.futures
import json
import random
import time
import datetime
import pprint
import requests
import ScrapeTools
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
from selenium.common.exceptions import NoSuchElementException

from CodeEnforcementEntry import CodeEnforcementEntry
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

request_url = "https://api.umeprojects.com/api/v1/public/listings?orderBy=certified,verified&order=DESC,DESC&location=AZ&rooms=&bathrooms=&loanType=&sqft={%22min%22:%22%22,%22max%22:%22%22}&rate={%22min%22:%22%22,%22max%22:%22%22}&price={%22min%22:0,%22max%22:500000}&maxDownPayment={%22min%22:%22%22,%22max%22:%22%22}&status=[%22Active%22, %22Pending%22, %22Closed%22]&perPage=1700&page=0&bounds=&center=&zoom="
form_url = "https://aca-prod.accela.com/MESA/Cap/CapHome.aspx?module=Permits&TabName=Permits&globalsearch=true"

MAX_THREADS = 1
MAX_AGENTS = 1
MAX_TIMEOUT = 10

def execute_task(proxies, houses: list, id):    
    # proxy_string = proxies[random.randint(0, len(proxies))]
    # proxy = {
    #     "http": f"http://{proxy_string}",
    #     "https": f"https://{proxy_string}"
    # }
    
    # Create options to detail driver behavior.
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
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
        address = ScrapeTools.break_down_address(house['address'])
        if address is None:
            continue
        
        # Collect elements...
        parent = ScrapeTools.check_element_viability(bot, By.XPATH, "//div[@id='ctl00_PlaceHolderMain_updatePanel']")
        open_date_box = ScrapeTools.check_element_viability(parent, By.XPATH, ".//input[@id='ctl00_PlaceHolderMain_generalSearchForm_txtGSStartDate']")
        street_num_from = ScrapeTools.check_element_viability(parent, By.XPATH, ".//input[@title='Street No. From	']")
        street_num_to = ScrapeTools.check_element_viability(parent, By.XPATH, ".//input[@title='Street No. To	']")
        direction_select = ScrapeTools.check_element_viability(parent, By.XPATH, ".//select[@id='ctl00_PlaceHolderMain_generalSearchForm_ddlGSDirection']")
        street_name_box = ScrapeTools.check_element_viability(parent, By.XPATH, ".//input[@id='ctl00_PlaceHolderMain_generalSearchForm_txtGSStreetName']")
        street_type_select = ScrapeTools.check_element_viability(parent, By.XPATH, ".//select[@id='ctl00_PlaceHolderMain_generalSearchForm_ddlGSStreetSuffix']")
        
        # Clear, get current date - no of months that are considered recent...
        current_date = datetime.now()
        delta_date = current_date - relativedelta(months=MONTHS_RECENT)
        
        open_date_box.clear()
        delta_string = delta_date.strftime("%d%m%Y")
        open_date_box.click()
        open_date_box.send_keys(delta_string)
        
        # Fill out other informations using broken down address...
        street_num_from.send_keys(address['streetNum'])
        street_num_to.send_keys(address['streetNum'])
        direction_select.send_keys(address['streetDirection'])
        street_name_box.send_keys(address['streetName'])
        street_type_select.send_keys(address['streetType'])
        
        if address['unitNo'] != None:
            unit_no_box = ScrapeTools.check_element_viability(parent, By.XPATH, ".//input[@id='ctl00_PlaceHolderMain_generalSearchForm_txtGSUnitNo']")
            unit_no_box.send_keys(address['unitNo'])
            
        # Get search button and press...
        search_btn = ScrapeTools.check_element_viability(bot, By.XPATH, ".//a[@id='ctl00_PlaceHolderMain_btnNewSearch']")
        ActionChains(bot)\
            .move_to_element(search_btn)\
            .click()\
            .perform()
        
        wait_for_search(bot)
        rec = records_returned(bot)
        print(f"Records Returned: {rec}")
        if rec:
            process_records(bot)
        
        # Get clear button and press...
        clear_btn = ScrapeTools.check_element_viability(bot, By.XPATH, ".//a[@id='ctl00_PlaceHolderMain_btnResetSearch' and @title='Clear']")
        ActionChains(bot)\
            .move_to_element(clear_btn)\
            .click()\
            .perform()
        
        wait_for_search(bot)
        
        
def process_records(bot: webdriver.Chrome):
    table_element = bot.find_element(By.XPATH, "//table[@class='ACA_GridView ACA_Grid_Caption']")
    
    entries =  table_element.find_elements(By.XPATH, ".//tr[@class='ACA_TabRow_Odd' or @class='ACA_TabRow_Even']")
    print("stop")
                

def records_returned(bot: webdriver.Chrome):
    try:
        wait = WebDriverWait(bot, 5)
        wait.until(lambda d : EC.presence_of_element_located((By.XPATH, "//span[@id='ctl00_PlaceHolderMain_RecordSearchResultInfo_lblSearchResultCountNumSummary']")) or
                   EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_PlaceHolderMain_RecordSearchResultInfo_noDataMessageForSearchResultList_messageBar' and @class='ACA_Message_Notice ACA_Message_Notice_FontSize']")))
    except TimeoutException as e:
        raise e
    
    try:
        bot.find_element(By.XPATH, "//span[@id='ctl00_PlaceHolderMain_RecordSearchResultInfo_lblSearchResultCountNumSummary']")
        return True
    except NoSuchElementException as e:
        return False
    
        
def wait_for_search(bot: webdriver.Chrome):
    try:
        loading = bot.find_element(By.XPATH, "//div[@class='ACA_Global_Loading']")
        wait = WebDriverWait(bot, 5)
        wait.until_not(lambda d : "display: block" in loading.get_attribute('style'))
    except TimeoutException as e:
        raise e

def start_threads(houses : list):
    proxies = None # get_proxies()
    properties_in_violation = []
    
    set_globals()
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

def set_globals():
    with open("config.json", "r") as f:
        config = json.loads(f.read())
        global MONTHS_RECENT
        MONTHS_RECENT = config['recentMonths']

with open("response_data_active.json", "r") as f:
    set_globals()
    houses = json.loads(f.read())
    execute_task(None, houses, 1)