import pip
from dataclasses import dataclass

"""
def import_or_install(package):
    try:
        __import__(package)
    except ImportError:
        pip.main(['install', package])
"""

import bs4
import selenium
import re
import json
import logging

from os import listdir, remove, makedirs
from os.path import isfile, join
import glob

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, InvalidSessionIdException, NoSuchWindowException
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import re

from time import sleep


import a_scraper
from a_scraper import scrape_canon_europe  # dependency! a_scraper.py must be within the project.

class DoNotDownload(Exception):
    pass

@dataclass
class canon_product:
    p_cat: str          # product category
    p_scat: str         # product subcategory
    p_name: str         # product name
    url: str            # produt url 

catalogue: canon_product = []

def make_struct(dic: dict) -> list[canon_product]:
    for pc in dic.keys():
        for psc in dic[pc]:
            for pname in dic[pc][psc].keys():
                prod = canon_product(pc, psc, pname, dic[pc][psc][pname])
                catalogue.append(prod)
    return(catalogue)          

def make_catal_from_string(catalogue: str) -> list[canon_product]:
    catal = []
    catalogue = catalogue.split('), ')
    
    for i, s in enumerate(catalogue):
        catalogue[i] = catalogue[i].strip('[](')[14:]
        pc = ''
        psc = ''
        pn = ''
        u = ''
        k = 0
        quot: bool = False
        for c in catalogue[i]:
            
            if c == "'":   ## looking for ', adding chars between '' to corrsponding stings; k == 0 -> p_cat; ... k == 3 -> url.
               quot = not quot
               if not quot:
                k = k+1
            if quot and c != "'":
                if k == 0:
                    pc += c
                if k == 1:
                    psc += c
                if k == 2:
                    pn += c
                if k == 3:
                    u += c            
        catal.append(canon_product(pc, psc, pn, u))
    
    return(catal)

def read_prod_from_file(filename: str) -> list[canon_product]:
    with open(filename, 'r') as f:
        return(make_catal_from_string(f.read()))
    

def make_dict(product_list: list[canon_product]) -> dict:
    pass

def check_exists_by_xpath(xpath: str, driver: selenium.webdriver):  # not needed here
    driver.implicitly_wait(1)
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        driver.implicitly_wait(IMPLICIT_WAIT)
        return False
    driver.implicitly_wait(IMPLICIT_WAIT)
    return True

def check_survey(driver, xpath = '//a[@class="SurveyPopupViewOk"]'):  # not needed here
    if check_exists_by_xpath(xpath, driver):
        el=driver.find_element(By.XPATH, xpath)
        action = webdriver.common.action_chains.ActionChains(driver)
        action.move_to_element_with_offset(el, 5, 5)
        action.click()
        action.perform()
        sleep(2)

def download_wait(directory, timeout, pathname='F:\\Canon', nfiles=None):
    """
    https://stackoverflow.com/questions/34338897/python-selenium-find-out-when-a-download-has-completed
    Wait for downloads to finish with a specified timeout.

    Args
    ----
    directory : str
        The path to the folder where the files will be downloaded.
    timeout : int
        How many seconds to wait until timing out.
    nfiles : int, defaults to None
        If provided, also wait for the expected number of files.

    """
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        sleep(1)
        dl_wait = False
        files = listdir(directory)
        if nfiles and len(files) != nfiles:
            dl_wait = True

        for fname in files:
            if fname.endswith('.crdownload'):
                dl_wait = True

        seconds += 1
        if seconds == timeout:
            fList = glob.glob(''.join((pathname, '\\**\\*.crdownload')), recursive=True) # deleting .crdownload files: you snooze - you lose
            logging.info("Trying to delete .crdownload files")
            for filePath in fList:
                try:
                    logging.info(f"Deleting {filePath}...")
                    remove(filePath)
                except OSError:
                    logging.info("Error while deleting .crdownload file")
    return seconds


def click_n_get(catalogue: [canon_product]):
    """
    product_list dictionary structure: 
        {PRODUCT_CATEGORY(str): {PRODUCT_SUBCATEGORY(str): {PRODUCT_NAME(str): PRODUCT_SITE_LINK(URL)}}}
    """
    selenium_options = webdriver.ChromeOptions()
    
    #STANDARD_DOWNLOAD_FOLDER: str = selenium_options.experimental_options[prefs]["download.default_directory"]
    #print(STANDARD_DOWNLOAD_FOLDER)
    
    DOWNLOADS_FOLDER: str = 'F:\Canon_Business'
    OLD_DOWNLOADS_FOLDER: str = 'D:\Downloads'
    FILELIST: str = []
    LANG_LIST: str = ['UK', 'EN']
    IMPLICIT_WAIT: int = 3   
    temporary_catalogue: str = 'D:\Programming\Python\_AIT\CanonClicker\_intermit.txt'
    ln = len(catalogue)
    iter = 0
    while True:
      # looping through the products
        prod: canon_product = catalogue[0]
        
        
        try:
            fNotDownload: bool = False
            for lang in LANG_LIST: # looping through languages
                new_down_path: str = f"{DOWNLOADS_FOLDER}\{prod.p_cat}\{prod.p_scat}\{prod.p_name}\{lang}"
                try:
                    makedirs(new_down_path)
                except:
                    logging.error(f"Could not create folder {new_down_path}")    
                logging.info(f'Setting the download folder as {new_down_path}...')
                selenium_options = webdriver.ChromeOptions()
                
                selenium_options.add_experimental_option('prefs', {"download.default_directory": new_down_path,
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "safebrowsing-disable-download-protection": True,
            "excludeSwitches": ["enable-logging"]
            })
                
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=selenium_options)
                logging.info(f'Setting the download folder as {new_down_path}... Done.')
                driver.implicitly_wait(IMPLICIT_WAIT)
                driver.get(prod.url)
                driver.maximize_window()
                                
                try:
                    driver.find_element(By.ID, '_evidon-accept-button').click()
                except NoSuchElementException:
                    pass   # Yep this does not look good, but I need this to only close the popup which pops-up (except:) or does not (do nothing <=> pass)
                # .....could set a cookie though......
                
                driver.add_cookie({"name" : "SupportSurvey", "value" : "1", "domain": "www.canon-europe.com", "path": "/"})  # to eliminate survey prompt.. 
                
                
                
                try:
                    
                    try:
                        sleep(2)
                        driver.find_element(By.XPATH, '//a[@data-tabname="MANUALS"]').click()
                        #sleep(1)
                    except NoSuchElementException:
                        logging.error(f'Could not find "MANUALS" section on page {prod.url}. Trying to reload...')
                        driver.refresh()
                        sleep(3)
                        try:
                            
                            driver.find_element(By.XPATH, '//a[@data-tabname="MANUALS"]').click()
                        except Exception as e:
                            logging.error(f"FATAL ERROR\nException---\n{e}\nThe issue was with {prod.p_name}, {lang}, {prod.url}\nCould not find MANUALS section. Download stopped. Quitting.")
                            with open(temporary_catalogue, 'w') as f:
                                f.write(str(catalogue))
                            driver.close()
                            quit()
                        
                    try:
                        driver.find_element(By.XPATH, '//select[@id="download-language"]').click()
                        #sleep(1)
                    except NoSuchElementException:
                        logging.error(f'Could not find "LANGUAGE PICKER" section for {lang} on page {prod.url}. Download skipped.')
                        catalogue.pop(0)
                        fNotDownload = True
                        with open(temporary_catalogue, 'w') as f:
                            f.write(str(catalogue))
                        break
                        
                    try:
                        driver.find_element(By.XPATH, f'//option[@value="{lang}"]').click()
                        #sleep(1)
                                        
                    except Exception as e: # most probably, no such language to download
                        logging.info(f"{prod.p_name} {prod.url}\nLooks like there are no files in one of languages ({lang}) to download.\nNo need to download at all.")
                        fNotDownload = True
                        break
                    original_window = driver.current_window_handle
                    for down_button in driver.find_elements(By.CSS_SELECTOR, 'a.pl-btn.pl-btn--blue.pl-btn--medium.download-btn.inline.downloaddisclaimer'):
                                        
                        # check_survey(driver)
                        down_button.click()
                        #sleep(1)
                        driver.find_element(By.XPATH, '//a[@id="acceptAndDownload"]').click()
                        #sleep(1)
                        
                        for tab in driver.window_handles:
                            try:    
                                if tab != original_window:
                                    driver.switch_to.window(tab)
                                    driver.close()
                            except:
                                logging.error(f"Could not close other window for {prod.p_name} : {prod.url}")
                                pass
                        driver.switch_to.window(original_window)
                        sleep(1)
                        
                        el = driver.find_element(By.XPATH, '//a[@class="pull-xs-right"]')
                        action = webdriver.common.action_chains.ActionChains(driver)
                        action.move_to_element_with_offset(el, 5, 5)
                        action.click()
                        action.perform()
                        download_wait(new_down_path, 45)

                    # success with one current language, close window, move to another 
                    logging.info(f'Downloaded all files for {prod.p_name} to {new_down_path}')
                
                except Exception as e: ## something wrong while getting the files for a language: write the curent state to file, terminate
                    
                    with open(temporary_catalogue, 'w') as f:
                        f.write(str(catalogue))
                    driver.close()
                    logging.error(f"Exception---\n{e}\nThe issue was with {prod.p_name}, {lang}, {prod.url}")
                    quit()  #  and just quit, to continue on the next run
                    """
                    flist = [f for f in listdir(new_down_path) if isfile(join(new_down_path, f))]
                    for s in flist:
                        FILELIST.append(s)
                    """
                
                # sleep(10)  # to let everything finish downloading
            
            ## Success, no exceptons! -> remove the item from the list of products (for sure, with exception handling);
            ## and move on, no writing the state to disk
                if fNotDownload:
                    logging.info(f"We skip some of {prod.p_name} files at {prod.url}\n{lang} language is not available.")
                    break
            iter += 1
            catalogue.pop(0)
            with open(temporary_catalogue, 'w') as f:
                f.write(str(catalogue))
            
        except Exception as e: 
            # something wrong while moving to the next item in catalogue
            logging.error(f"Exception---\n{e}\nCould not open next item in the catalogue!! Iteration No {iter} !!")
            try:    # try to close the session and quit
                driver.close()
                   
                with open(temporary_catalogue, 'w') as f:
                    f.write(str(catalogue))
                              
                # quit()          
            except InvalidSessionIdException as e:
                ## invalid session (it happens somehow...) - we cannot close it
                with open(temporary_catalogue, 'w') as f:
                    f.write(str(catalogue))
                logging.error(f"Exception---\n{e}\nCould not close the driver properly after the exception! Iteration No {iter} !!")
                quit()  # write the state and quit      
            except NoSuchWindowException as e:
                logging.error(f"Exception---\n{e}\nCould not close the window, nosuchwindow excepton. Iteration No {iter} !!")
                  # the window is aready closed, no need to do anything
            except Exception as e:
                logging.error(f"Exception---\n{e}\nUnknown error")
            
        if iter >= ln:
            logging.info(f"ALL DONE!".center(100, '-'))#print("END of LIST")
            with open(temporary_catalogue, 'w') as f:
                        f.write(str(catalogue))
            quit()
            
    
def main():
    
    """
    with open('D:\Programming\Python\_AIT\CanonClicker\_linkset.txt', 'r') as f:
        dic = json.loads(f.read())
        
    catalogue = make_struct(dic)
    
    print(catalogue)
    """
    logging.basicConfig(filename='D:\Programming\Python\_AIT\CanonClicker\_clicker_.log', encoding='utf-8', format='%(levelname)s : %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    
    temporary_catalogue = 'D:\Programming\Python\_AIT\CanonClicker\_intermit.txt'

    catalogue = read_prod_from_file(temporary_catalogue)
    logging.info(f'Loaded the catalogue from file {temporary_catalogue}')  
    click_n_get(catalogue)
    #print(catalogue[0])

    #print("ALL DONE!".center(60, '='))
    """
    dic = {"Canon": {"Powershot": {"Powershot1": "https://www.google.com", "Powershot2": "https://www.microsoft.com"}, "PIXMA": {"PIXMA1": "https://whois.com", "PIXMA2": "https://www.facebook.com"}}}
    #click_n_get(dic)

    catal: canon_product = []
    catal.append(canon_product('Canon', 'Printer', 'PIXMA', "https://www.canon-europe.com/support/consumer_products/products/fax__multifunctionals/inkjet/pixma_mg_series/pixma_mg2550s.html"))
    catal.append(canon_product('Canon', 'Scaner', 'ScanPro', "https://www.canon-europe.com/support/consumer_products/products/fax__multifunctionals/inkjet/pixma_ts_series/pixma-ts705.html"))
    click_n_get(catal)
    #s: str = ''
    #input(s)
    """

if __name__ == '__main__':
    main()
