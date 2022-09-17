
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import re
from time import sleep
from Libs.delempty import delete_empty_folders
from string import punctuation
import glob
from Classes.classes import TransSegment
from difflib import SequenceMatcher
from likescore import normalize_text
    

#from os import listdir, system, remove, mkdir, makedirs, rmdir
#from os.path import basename,isdir,isfile, join
#from os.path import isfile, join

#pathname = r"F:\TMP"
#print(f"Code = {delete_empty_folders(pathname, del_root=True)}")

#s = "eruih3443 54543huihgf.(44)656543 .54532 toigd 'df#%$%$# 432"
# print(re.findall(r'\b\d+\b', s))
# DNT = ['Canon', 'Windows', 'Macintosh', 'Easy-PhotoPrint', 'PowerShot', 'PIXMA', 'MP270', 'series', 'MP250', 'USB', 'FINE', 'PictBridge']
# a = TransSegment(segment_number = 10, segment_text = "Як помру, то поховайте", aligned_segment = 11, align_scores = {1: 14, 2: 66, 3: 76})
# b = TransSegment()
# a.prn()
# print(a.segment_text)

def findnumbers(st: str): # -> List[int]
    numbers = []
    numbers.append(re.findall(r'\b\d+\b', st))
    numbers.append(re.findall(r'^\d+', st))
    numbers.append(re.findall(r'.+\d+$', st))
    numbers.append(re.findall(r'\d+', st))
    return(numbers)

s1 = 'Describes. the sum. ma()ry of  .this  product\nTo check its availability:\n- go to www.product.com\n- look for the product\n- Enjoy!\n'
s2 = 'Детально описується робота цього продукту.'
ew = 'this'
uw = 'продукт'
# print(normalize_text(s1))

print('Keep this point in mind when using it.'.isalpha())


# quit()

with open(r'f:\CanonParallel\PDFTEXTEN.txt', 'r', encoding = 'utf-8') as f:
        stringsUK = normalize_text(f.read(), r'D:\Programming\Python\_AIT\StopWords\norm_en.txt')


"""
numbersEN = re.findall(r'\d+', s1)  # find numbers in one string and in the other 

numbersUK = re.findall(r'\d+', s2)

score = 0
if len(numbersEN) and len(numbersUK):
    for i in numbersEN:
        numbermatch: bool = False
        for k in numbersUK:
            if i == k: # number match found!
                score += 100
                numbermatch = True
        if not numbermatch: # found in source / target, but not found in target / source
            score -= 15        
    # if not numbermatch:
            # print(f"Found {numbersEN} in source, {numbersUK} in target, no matches.")
            # score -= 15 # there are numbers, but no matching numbers
elif len(numbersEN):
    score -= 150  # numbers are in source but are absent in target - should not be a match
elif len(numbersUK):        
    score -= 150 # no numbers in source but numbers are present in target - should not be a match

print(score)
"""

"""
print(findnumbers(s1))
# regex = fr'\b{s}\b'
#print(re.search(regex, s1).group(0))
"""
"""
from difflib import SequenceMatcher
s1 = 'Не кладіть жодні предмети на кришку для притиснення документів. Вони потраплять у задній лоток унаслідок відкривання кришки для притиснення документів, що призведе до збою в роботі апарата.'
max = 0
for st in re.split(r'\W', s1):
    sc = int(SequenceMatcher(None, st, 'документ').ratio()*100)
    print(sc)
    if sc > max:
        max = sc

print(max)        

#print(s1.find('product'))
#print(s2.find('продукт'))
"""
# print(int(SequenceMatcher(None, s1, s2).ratio()*100))

#print(punctuation)