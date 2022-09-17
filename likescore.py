from typing import List
import Classes.classes
from difflib import SequenceMatcher
from string import punctuation
import re

from time import sleep



def normalize_text(raw_text: str, savefile) -> List[str]:
    
    strings = []
    result_strings = []
    # print(raw_text.replace(' .', '.').replace(' ,', ',').replace(' ’', '’').replace('. ', '.\n'))
    res_strings = raw_text.replace(' .', '.').replace(' ,', ',').replace(' ’', '’').replace('. ', '.\n').split('\n')
    
    
    # print(strings)
    strings = [line for line in res_strings if line.strip() != ""]
    """for line in res_strings:
        if line.isalpha():
            strings.append(line)
        else:
            print(line + '----\n')
    
    for line in r_strings:
        if line.strip('\n') != '':
            strings.append(line)
    """
    """
    with open(r'D:\Programming\Python\_AIT\CanonClicker\DataFiles\temp.txt', 'w', encoding = 'utf-8') as f:
        for st in strings:
            f.write(st + '\n')        
    """
    # print(strings)
    
    length = len(strings)
    #print(f"length = {length}")
    iter = 0
    segment = ''
    
    while iter < length:
        line = strings[iter]
        #print(f"Line: {line}")
        #print(f"iter_beg = {iter}")
        
        if iter + 1 < length:
            
            line_next = strings[iter+1] 
            
            if line_next[0].islower(): #  (line_next.find('. ') or line_next.find(', ')) and   or line.strip()[-1] in ['’',"'"]   and line_next.strip()[2:] == ' )'):
            #result_strings.append(' '.join((line, line_next)))
                segment = segment.strip('\n') + ' ' + line
            #print(f"Current semgent : {segment}")
            # iter += 1
            else: 
                segment = segment.strip() + ' ' + line.strip()
                result_strings.append(segment.strip())
                # print(f"Merged : {segment.strip() + ' ' + line.strip()}")
                segment = ''
                # else: segment = ''    
            #print(f"Added segment: {segment}")
            
        else: 
            result_strings.append(segment.strip('\n').strip())
            #print(f"Added last segment: {line}")
            segment = ''
            break
        iter += 1
        #print(f"iter_end = {iter}")
    
    with open(savefile, 'w', encoding = 'utf-8') as f:
        for st in result_strings:
            f.write(st+ '\n')
    
    return(result_strings)    



def create_staging_dic(string: str, dic: List[Classes.classes.dic_article], *, STAGING_DIC_RATIO = 0.95) -> List[Classes.classes.dic_article]:
    staging_dic: List[Classes.classes.dic_article] = []
    
    for art in dic: ## build the temporary dic out of the words available in source using pre-buit dictionary
        for word in [lst for lst in re.split(r'\W', string.lower()) if len(lst) > 1]:
            if SequenceMatcher(None, word, art.eng_word).ratio() > STAGING_DIC_RATIO:
                double = False
                for w in staging_dic: 
                    if art.eng_word == w.eng_word and art.ukr_word == w.ukr_word:
                        double = True
                if not double:
                    staging_dic.append(art)
    return(staging_dic)

def count_likescore(s1: str, s2: str, dic: List[Classes.classes.dic_article]) -> int: ## returns likescore of 2 strings (En, Ukr) using pre-built dictionary
    # 
    # 
    

    # some words are never translated ans must appear as is in the translation :
    DNT = ['Canon', 'SCAN', 'Windows', 'Macintosh', 'Easy-PhotoPrint', 'PowerShot', 'PIXMA', 'MP270', 'series', 'MP250', 'USB', 'FINE', 'PictBridge']
    DIC_RATIO = 0.60
    STAGING_DIC_RATIO = 0.90
    NUMBERPLUS_SCORE = 100
    NUMBERMINUS_SCORE = -25

    score = 0
   
    if len(s1) == 0 or len(s2) == 0 and len(s1) != len(s2):
        return(-500) ## one string is empty, the other is not. Definitely it's not match
    
    if s1[-1] in punctuation and s1[-1] == s2[-1]:  # both end with the same punctuation mark
        score +=15
    else:
        score -= 5
        
    if abs(len(s1) - len(s2))/len(s1) * 100 < 45: # lengths differs less than 45%
        score +=30
    else:
        score -=100  # one string is too short
        # print(f"Length does not match, {score}")
    
    #print(f"Length : {score}")
    

    numbersEN = re.findall(r'\d+', s1)  # find numbers in one string  
    numbersUK = re.findall(r'\d+', s2)  # and in the other
    
    if len(numbersEN) and len(numbersUK):
        for i in numbersEN:
            numbermatch: bool = False
            for k in numbersUK:
                if i == k: # number match found!
                    score += NUMBERPLUS_SCORE
                    numbermatch = True
            if not numbermatch: # found in source / target, but not found in target / source
                score += NUMBERMINUS_SCORE        
        
    elif len(numbersEN):
        score -= 150  # numbers are in source but are absent in target - should not be a match
    elif len(numbersUK):        
        score -= 150 # no numbers in source but numbers are present in target - should not be a match

    #print(f"Numbers : {score}")

    if s1[0].isupper() and s2[0].isupper:
        score += 10
    else:
        score -= 50

    #print(f"First letter upper : {score}")

    for name in DNT:
        if s1.lower().find(name.lower()) != -1:
            if s2.lower().find(name.lower()) != -1:
                #print(f"{name} found in both!")
                score += 100
            else:
                score -= 50    
        else:
            if s2.lower().find(name.lower()) != -1:    
                score -= 50
    
    #print(f"DNT List : {score}")
    с = ''
    for c in [char for char in punctuation if char != '-']: # - is sometimes used in both languages legally, but not always translated as - (tinkie-winke -> якесь одоробло)
        if s1.find(c) != -1:
            if s2.find(c) != -1:
                score += 25
            else:
                score -= 25
        else:
            if s2.find(c) != -1:
                score -= 25
    
    
    staging_dic: List[Classes.classes.dic_article] = dic.copy()
    #staging_dic: List[classes.dic_article] = []
    
    #for art in edic: ## build the temporary dic out of the words available in source using pre-buit dictionary
    #    for word in [lst for lst in re.split(r'\W', s1.lower()) if len(lst) > 1]:
    #        if SequenceMatcher(None, word, art.eng_word).ratio() > STAGING_DIC_RATIO:
    #            double = False
    #            for w in staging_dic: 
    #                if art.eng_word == w.eng_word and art.ukr_word == w.ukr_word:
    #                    double = True
    #            if not double:
    #                #print(f"Adding article for {art.eng_word} to staging dic, word is {word}")
    #                staging_dic.append(art)

    
    for art in staging_dic:
        found_match: bool = False
        for ukrword in [lst for lst in re.split(r'\W', s2.lower()) if len(lst) > 1]: 
            if SequenceMatcher(None, ukrword, art.ukr_word).ratio() > DIC_RATIO:
                score += 100
                found_match = True
                #print(f"Match: {art.eng_word} - {ukrword}")
                break  # we've found the matching word, no need to check for the rest of the translated sentence
        if not found_match:
            score -= 25
            
    
    """
    # logging.info(f'{s1} : {staging_dic}')
    for art in staging_dic:
        ew = art.eng_word
        uw = art.ukr_word
        # print(ew)
        if re.search(fr'[ ]{ew}[. ;:"]', s1.lower()):
                        
            if re.search(fr'[ ]{uw}([А-я. ;:"])', s2.lower()) != None:
                score += 100
                logging.info(f"Found {ew} : {uw}")
            else:
                score -= 25
                logging.info(f'Found {ew}, but not found {uw}')
        
        else:
            if re.search(fr'[ ]{uw}([А-я. ;:"])', s2.lower()) != None:
                score -= 25
                logging.info(f'No {ew}, but found {uw}')
            
    logging.info((f"{s1} -> {s2}: Dictionary score {score}"))
    """
    return(score)


def main():
    pass

if __name__ == '__main__':
    main()