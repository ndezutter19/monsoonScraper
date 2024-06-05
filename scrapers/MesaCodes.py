import concurrent.futures
import json
import random
import time
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
from monsoonScraper.scrapers.CodeEnforcementEntry import CodeEnforcementEntry
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

request_url = "https://api.umeprojects.com/api/v1/public/listings?orderBy=certified,verified&order=DESC,DESC&location=AZ&rooms=&bathrooms=&loanType=&sqft={%22min%22:%22%22,%22max%22:%22%22}&rate={%22min%22:%22%22,%22max%22:%22%22}&price={%22min%22:0,%22max%22:500000}&maxDownPayment={%22min%22:%22%22,%22max%22:%22%22}&status=[%22Active%22, %22Pending%22, %22Closed%22]&perPage=1700&page=0&bounds=&center=&zoom="
form_url = "https://nsdonline.phoenix.gov/CodeEnforcement"

MAX_THREADS = 1
MAX_AGENTS = 1
MAX_TIMEOUT = 10
MONTHS_RECENT = 6

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