# reference: https://www.geeksforgeeks.org/python-program-to-recursively-scrape-all-the-urls-of-the-website/

from ssl import _create_unverified_context
import bs4
import selenium
import re
import json

from dataclasses import dataclass
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import re
import json
from time import sleep

@dataclass
class canon_product:
    p_cat: str          # product category
    p_scat: str         # product subcategory
    p_name: str         # product name
    url: str            # produt url 

catalogue: canon_product = []

SITE_ADDRESS = "https://www.canon-europe.com/support/business-product-support/"
PRODUCT_LIST = ['imageRUNNER', 'Document Scanners', 'imagePROGRAF', 'imagePRESS', 'WG Series', 'Canon Production Printing']  # for this particular site

def scrape_canon_europe():
    """
    Scrapes the site SITE_ADDRESS (will work for https://www.canon-europe.com/support/ ONLY!!!!)
    Returns list of canon_product objects and (redundant) dictionary 
     
    {
    "PIXMA": {
        "PIXMA MG Series": {
            "PIXMA MG2140": "https://www.canon-europe.com/support/consumer_products/products/fax__multifunctionals/inkjet/pixma_mg_series/pixma_mg2140.html"
            }
        }
    }
    """

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(SITE_ADDRESS)
    driver.maximize_window()


    card_captions: canon_product = []
    card_captions_dict: dict = {}
    product_card: str = ''
    product_category: str = ''
    device_finder_page: str = ''

    try:
        elem = driver.find_element(By.ID, '_evidon-accept-button')
        elem.click()
        driver.implicitly_wait(1)
    except NoSuchElementException:
        pass   # Yep this does not look good, but I need this to only close the popup which pops-up (except:) or does not (do nothing <=> pass)

    for product_card in PRODUCT_LIST:  # Looking through the main sections list; pre-defined with PRODUCT_LIST
        card_captions_dict[product_card] = {}
        driver.find_element(By.PARTIAL_LINK_TEXT, product_card).click()  # open the n-th card name
        device_finder_page = driver.page_source  # reload the changed \
        soup_finder = BeautifulSoup(device_finder_page, features="lxml")  # page contents

        for product_category in soup_finder.findAll('a', attrs={'data-tab': re.compile('tab\d*')}):  # loop through data-tab links
                                                    # <a href="#" data-tab="tab3">EOS</a> - the template
            product_category = product_category.text.strip('\n ')
            card_captions_dict[product_card][product_category] = {}
            sleep(1)
            try:
                driver.find_element(By.PARTIAL_LINK_TEXT, product_category).click()  # 
            except NoSuchElementException:
                driver.find_element(By.CSS_SELECTOR, 'a.active').click()  # most likely > needs to be pressed to scroll the carousel
                driver.implicitly_wait(1)  # probably redundant
                device_finder_page = driver.page_source  # re-read the refreshed page contents
                sleep(1)
                driver.find_element(By.PARTIAL_LINK_TEXT, product_category).click()
            except ElementClickInterceptedException:
                driver.find_element(By.CSS_SELECTOR, 'a.active').click()  # most likely > needs to be pressed to scroll the carousel
                driver.implicitly_wait(1)  # probably redundant
                device_finder_page = driver.page_source  # re-read the refreshed page contents
                sleep(1)
                driver.find_element(By.PARTIAL_LINK_TEXT, product_category).click()    

            # ======================================== looking for the particular product page links

            soup_finder = BeautifulSoup(device_finder_page, features="lxml")  # page contents
            for tab_container in soup_finder.find_all('div', class_='tab-container', limit=1):
                                                    # <div class="tab-container"> - the template
                soup_finder = BeautifulSoup(str(tab_container), features="lxml")
                for links in soup_finder.find_all('a'):  # all the links within the tab container
                    #  Here is the error; it adds links multiple times.
                    add:bool = True
                    for check_prod in card_captions:
                        if check_prod.url == f"https://www.canon-europe.com{links['href']}":
                            add = False
                            break
                    if add:
                        prod = canon_product(product_card, product_category, links['data-tealiumeventmetadata'], f"https://www.canon-europe.com{links['href']}")
                        card_captions.append(prod)
                        card_captions_dict[product_card][product_category][links['data-tealiumeventmetadata']] = f"https://www.canon-europe.com{links['href']}"
                    # ^^This workaround sucks, it adds once, but does not add to proper category.
        driver.back()  # click Back button in browser to return to the main list

    
    return(card_captions) # , card_captions_dict)

def main():
    linkset: canon_product = scrape_canon_europe()
    
    with open(r'D:\Programming\Python\_AIT\CanonClicker\_intermit.txt', 'w') as f:
        f.write(str(linkset))
    #print(linkset)

if __name__ == '__main__':
    main()
