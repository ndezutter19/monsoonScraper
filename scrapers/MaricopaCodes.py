import json
import pprint
import requests
import selenium
import ScrapeTools
from selenium import webdriver
import selenium.webdriver
import selenium.webdriver.chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException

request_url = "https://api.umeprojects.com/api/v1/public/listings?orderBy=certified,verified&order=DESC,DESC&location=AZ&rooms=&bathrooms=&loanType=&sqft={%22min%22:%22%22,%22max%22:%22%22}&rate={%22min%22:%22%22,%22max%22:%22%22}&price={%22min%22:%22%22,%22max%22:%22%22}&maxDownPayment={%22min%22:%22%22,%22max%22:%22%22}&status=[%22Active%22, %22Pending%22, %22Closed%22]&perPage=1700&page=0&bounds=&center=&zoom="
form_url = "https://accela.maricopa.gov/CitizenAccessMCOSS/Cap/CapHome.aspx?module=PnD&TabName=PnD"

ph_code_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://nsdonline.phoenix.gov/CodeEnforcement',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

ph_code_payload = {
    'stNumber': '',
    'stDirection': '',
    'stName': ''
}

def checkCodeViolations(houses: list):
    bot = webdriver.Chrome()
    bot.get(form_url)
    wait = WebDriverWait(bot, timeout=3)
    
    for house in houses:
        
        # Identify all elements necessary to fill out form...
        street_from_box = ScrapeTools.check_element_viability(bot, By.XPATH, "//input[@title='Street No. From	']")
        street_from_box.send_keys(house['Property']['streetNumber'])
        
        street_to_box = ScrapeTools.check_element_viability(bot, By.XPATH, "//input[@title='Street No. To	']")
        street_to_box.send_keys(house['Property']['streetNumber'])
        
        street_type_box = ScrapeTools.check_element_viability(bot, By.XPATH, "//select[contains(@name, 'StreetSuffix')]")
        street_type_box.send_keys(house['Property']['streetDirSuffix'])
        
        zip_box = ScrapeTools.check_element_viability(bot, By.XPATH, "//input[contains(@name, 'ZipSearch')]")
        zip_box.send_keys(house['Property']['postal'])
        
        city_box = ScrapeTools.check_element_viability(bot, By.XPATH, "//input[contains(@name, 'txtGSCity')]")
        city_box.send_keys(house['Property']['city'])
        
        street_name_box = ScrapeTools.check_element_viability(bot, By.XPATH, "//input[contains(@name, 'txtGSStreetName')]")
        street_name_box.send_keys(house['Property']['route'])
        
        direction_box = ScrapeTools.check_element_viability(bot, By.XPATH, "//select[contains(@name, 'Direction')]")
        direction_box.send_keys(house['Property']['streetDirPrefix'])      
        
        search_button = ScrapeTools.check_element_viability(bot, By.XPATH, "//a[@title='Search']")
        # Click search button...
        ActionChains(bot)\
            .move_to_element(search_button)\
            .click()\
            .perform()
            
        check_redirect(bot, house['Property']['address'])
        
        # Clear form for next submission...
        clear_form(bot, wait)


def check_redirect(bot: webdriver.Chrome, address):
    try:
        wait_for_search
    except:
        check_for_record
        print(f'Record Found, address: {address}')


def check_for_record(bot: webdriver.Chrome):
    wait = WebDriverWait(bot, 2)
    wait.until(EC.presence_of_element_located([By.XPATH, "//div[@class='record-summary']"]))

def clear_form(bot, wait: WebDriverWait):
    try:
        clear_button = ScrapeTools.check_element_viability(bot, By.XPATH, "//a[@title='Clear']")
        wait_for_search(bot)
        
        ActionChains(bot)\
            .move_to_element(clear_button)\
            .click()\
            .pause(0.5)\
            .perform()
            
        wait_for_search(bot)
    except StaleElementReferenceException:
        clear_form(bot, wait)

    

def wait_for_search(bot: selenium.webdriver.Chrome):
    try:
        loading = bot.find_element(By.XPATH, "//div[@class='ACA_Global_Loading']")
        wait = WebDriverWait(bot, 2)
        wait.until_not(lambda d : "display: block" in loading.get_attribute('style'))
    except TimeoutException as e:
        raise e


def data_found(bot: webdriver.Chrome):
    if bot.current_url != form_url:
        return True
    
    return False