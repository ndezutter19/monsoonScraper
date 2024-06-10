import re
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium import webdriver

def check_element_viability(bot, locator_type, locator_value):
    wait = WebDriverWait(bot, timeout=10)
    try:
        check_element = wait.until(EC.presence_of_element_located([locator_type, locator_value]))
        wait.until(EC.element_to_be_clickable(check_element))
        wait.until_not(EC.staleness_of(check_element))
        return check_element
    except StaleElementReferenceException:
        return check_element_viability(bot, locator_type, locator_value)
    except TimeoutException:
        print(f'Timed out while looking for element with {locator_type}:{locator_value}')
        
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

def break_down_address(address):
    # Define the regular expression pattern
    pattern = r'(?P<streetNum>\d+)\s+(?P<streetDirection>[NSEW])\s+(?P<streetName>[a-zA-Z0-9\s]+)\s+(?P<streetType>[a-zA-Z]+)(?:\s+#(?P<unitNo>\d+))?'

    # Match the pattern against the address
    match = re.match(pattern, address, re.IGNORECASE)
    
    if match:
        logging.debug(f"Successfully Parsed Address: {address}")
        return match.groupdict()
    else:
        logging.warning(f"Could Not Parse Address: {address}")
        return None

def break_down_address_op(address):
    # Log the input address
    logging.debug(f"Parsing address: {address}")

    # Define the regular expression pattern
    # Define the regular expression pattern
    pattern = (r'(?P<streetDirection>[NSEW][a-z]*)\s+'
               r'(?P<streetName>[a-zA-Z0-9\s]+)\s+'
               r'(?P<streetType>[a-zA-Z]+)\s+'
               r'(?:(?P<suffixDirection>[NSEW])\s+)?'
               r'(?P<streetNum>\d+)')

    # Match the pattern against the address
    match = re.match(pattern, address, re.IGNORECASE)
    
    if match:
        logging.debug("Address matched successfully.")
        return match.groupdict()
    else:
        logging.warning("Address could not be parsed.")
        return None

def get_abbreviated(suffix: str):
    temp = suffix.lower()
    
    # Dictionary mapping full street suffixes to USPS standard abbreviations
    suffix_dict = {
        'alley': 'ALY',
        'avenue': 'AVE',
        'boulevard': 'BLVD',
        'circle': 'CIR',
        'court': 'CT',
        'drive': 'DR',
        'expressway': 'EXPY',
        'highway': 'HWY',
        'lane': 'LN',
        'parkway': 'PKWY',
        'place': 'PL',
        'road': 'RD',
        'square': 'SQ',
        'street': 'ST',
        'trail': 'TRL',
        'way': 'WAY'
    }
    
    try:
        abbreviated = suffix_dict[temp]
        return abbreviated
    except KeyError:
        logging.warning(f"Abbreviated version of {temp} not found, returning input string, append to dictionary if need be.")
        return temp.upper()