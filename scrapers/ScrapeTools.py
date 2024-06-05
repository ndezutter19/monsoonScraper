import re

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
    pattern = r'(\d+)\s+(\w+)\s+([\w\s]+)\s+(\w+)$'
    
    match = re.match(pattern, address)
    
    if not match:
        raise ValueError("Address format is incorrect. Expected format: 'streetNumber streetDirection streetName streetType'")
    
    street_number = match.group(1)
    street_direction = match.group(2)
    street_name = match.group(3)
    street_type = match.group(4)
    
    return street_number, street_direction, street_name, street_type