from dataclasses import dataclass, field
import re

from typing import Dict, List, Tuple
from typing_extensions import Self

import fitz

from time import sleep

import logging

from Libs.delempty import progressbar

from likescore import count_likescore, create_staging_dic, normalize_text

import Classes.classes ## TransSegment (segment_number: int, segment_text: str, aligned_segment: int, align_scores: Dict[int,int])
from Classes.classes import dic_article, Segment, TransSegment, UsedItem
from Libs.uk_stemmer import UkStemmer  ## https://github.com/Desklop/Uk_Stemmer


#reader = PdfFileReader(open('D:\\Programming\\Python\\_AIT\\CanonClicker\\test.pdf', "rb"))
#st:str = pdf2text('D:\\Programming\\Python\\_AIT\\CanonClicker\\test.pdf')



Roots_dict_EN_UKR = {'usage': 'корист', 'compon': 'компон', 'orig': 'оріг'}

DECENT_SCORE = 400 ## threshold score for aligning texts

scoretable: dict = {} # global 2x-dim dictionary
                        # {eng_seg_number_1: {ukr_seg_number_1: score, ukr_seg_number_2: score, ....},
                        #  eng_seg_number_2: {ukr_seg_number_1: score, ukr_seg_number_2: score, ....},
                        #  ...
                        # }

@dataclass
class segmentUK:
    segment_number: int
    segment_text: str

def keywithmaxval(d: Dict): # -> Dict.key:
     """ a) create a list of the dict's keys and values; 
         b) return the key with the max value"""  
     v = list(d.values())
     k = list(d.keys())
     return k[v.index(max(v))]


# engdic = []

def make_eng_dic() -> List[dic_article]:
    engdic = []

    import sqlite3
    DBPATH = 'D:\\Programming\\Python\\_AIT\\CanonClicker\\DataFiles\\stagingUKR.db'
    with sqlite3.connect(DBPATH) as conn:
        #engdic = []
        c = conn.cursor()
        for row in c.execute('SELECT * FROM Dictionary'):
            if len(row[1]) > 1 and len(row[2]) > 1:
                engdic.append(dic_article(row[0], row[1], row[2]))
    return(engdic)

def build_custom_glossary(filelink) -> List[str]:  ## finds all words in english text; used to make staging dic with gtranslate.
    res = []
    with open(filelink, 'r', encoding = 'utf=8') as f:
        for str in re.split(r'\W', f.read().lower()):
            if len(str) >1 and not str.isdigit(): 
                if not str in res:
                    res.append(str)
    return(res)



def align_texts(sourcetext: List[Segment], targettext: List[Segment], i: int, align_score_threshold = DECENT_SCORE) -> Tuple[List[Segment], List[TransSegment], int]:
    textENG = sourcetext.copy()
    textUKR = targettext.copy()
        
    offset = textENG[i].segment_number - textENG[i].aligned_segment
    UKsegnum = textENG[i].aligned_segment
    
    if offset < 0: ## source is aligned with a segment lower
        #print(f"Need to move ENG {i} to {i-offset}")
        for ind in range(0, offset, -1):
            # print(ind, end='')
            textENG.insert(i, Segment(i - ind, '', -1, -10001, True))  ## wrong order, need to insert the highest first
            #print(f"Inserting empty ENG to {i} number {i-ind}")
            if i-ind in scoretable.keys():
                tempdic = scoretable[i-ind].copy()
                #print(F"copying scoretable record {i-ind} to {i-ind-offset}") 
                scoretable[i-ind].clear()
                scoretable.pop(i-ind)   ##            on adding the element record to the scoretable
                scoretable[i-ind-offset] = tempdic.copy()
            
        #print(f"Scoretable\n{i} : {tempdic}\n ->\n{i-offset} : {scoretable[i-offset]}")

        for iter in range(i, len(textENG)):
            textENG[iter].segment_number = iter
        
        
        
       
        ######  ---- adjust scoretable!!! if iter == i
         ## we work with the last segment in scoretable (???), as we've just found the high score 
        """
        for iter in range(i, max(scoretable.keys())):
            print(scoretable[iter])
            print(f"Moving scoretable for ENG: {iter} -> {iter - offset}")
            tempdic = scoretable[iter].copy() ## we work with the last segment in scoretable (???), as we've just found the high score 
            scoretable[iter].clear()
            scoretable.pop(iter)   ##            on adding the element record to the scoretable
            scoretable[iter-offset] = tempdic.copy()
        """
        
    
    elif offset > 0:
        
        for ind in range(offset, 0, -1):
            # print(ind, end='')
            textUKR.insert(i - offset, Segment(i - offset -1 + ind, '', -1, -10001, False))
        
        textUKR[i].segment_number = i
        textUKR[i].aligned_segment = i
        for iter in range(i+1, len(textUKR)):
            textUKR[iter].segment_number = iter
        
        textENG[i].aligned_segment = i
        
        for k in scoretable.keys():  ## now we need to adjust the scoretable to reflect the changes
            found = False
            for n in scoretable[k].keys(): 
                if n >=  UKsegnum:  # found the affected ukr segment for particular eng segment in the scoretable  
                    found = True
                    break 
            if found: ## so we need to adjust the score dictionary for the english segment 
                #print(f"Moving scoretable for UKR: {k}")
                tempdic = scoretable[k].copy()  # make a copy of the scores
                scoretable[k].clear() # clear the scores
                for key in tempdic.keys():  # loop through the segnumbers in the copy
                    if key < UKsegnum:  # for ukr segments unaffected 
                        scoretable[k][key] = tempdic[key] # simply create the same key with the same score
                    else:  # for others
                        scoretable[k][key+offset] = tempdic[key]  # create new key with new ukr segment number but with the same score
            
       
    return(textENG.copy(), textUKR.copy(), max(scoretable.keys()))

"""
def dump_to_file(i:int):
    with open(rf"D:\Programming\Python\_AIT\StopWords\Chunks\Chunk{{i}}.txt", 'w', encoding = 'utf-8') as f:
        f.write(scoretable)
    
"""

def count_max_score(seg:Segment, seglist: List[Segment], dic: List[dic_article], *, SCOPE = 7): #
    # lookup +- SCOPE segments to shorten the list to evaluate the scores
    
    if seg.segment_number not in scoretable.keys():
        scoretable[seg.segment_number] = {}
    
    
    max_score = -10000
    max_segment = -1
    
    for segUK in seglist: # loop through translated segments
        add = True
        if abs(segUK.segment_number - seg.segment_number) <= SCOPE:
            
            score = count_likescore(seg.segment_text, segUK.segment_text, dic) ## 135
            i: int = 0
            
                   
            scoretable[seg.segment_number][segUK.segment_number] = score
                    
            if score > max_score: 
                max_score = score
                seg.max_score = max_score
                segUK.max_score = max_score
                max_segment = segUK.segment_number

    return(seg, max_segment, max_score)
    


def ReadPDF(PDFPath: str, start: int, end: int) -> List[str]:
    strlist = []
    with fitz.open(PDFPath) as doc:
        for page in doc.pages(start, end, 1):
            strlist.append(page.get_text())

    return(strlist)

def deduplicate():  ## scoretable{key : {ukey: uscore} }
                    ## scoretable{scoretable.keys():  {scoretable[key].keys() : scoretable[key].values()}}
                    ## scoretable(scoretable.keys(): scoretable.values())
    scores = {}
    for key in scoretable.keys():
        # print(scoretable[key])
        segUK = list(scoretable[key])[0]
        if segUK not in scores.values():
            scores.update({key: segUK})    
        else:
            lst = [l for l in scores.items() if l[1] == segUK][0]
            #print(f"{key} : {segUK} new score {scoretable[key][segUK]}, in table: {lst[0]} : {lst[1]}, oldscore: {scoretable[lst[0]][lst[1]]}")
            try:
                if scoretable[key][segUK] < scoretable[lst[0]][lst[1]]:
                    #print(f"removed {key}:{segUK}")
                    #print(f"{key}:{segUK} score {scoretable[key][segUK]}, in table: {lst[0]}, {lst[1]}, score: {scoretable[lst[0]][lst[1]]}, new score is lower")
                    scoretable[key].pop(segUK)
                                
                else:
                
                    #print(f"removed {lst[0]} : {lst[1]}")
                    scoretable[lst[0]].pop(lst[1])
            except Exception as e:
                pass            
    # print(scores)

def main():
    
    logging.basicConfig(filename=r'D:\Programming\Python\_AIT\CanonClicker\Logs\log.txt', encoding='utf-8', level=logging.INFO)
    
    textUK = []
    textEN = []
    with open(r"f:\CanonParallel\PDFTEXTEN.txt", 'r', encoding = 'utf-8') as f:  # read text from file; originally obtained with readPDF()
        strings = normalize_text(f.read(), r'D:\Programming\Python\_AIT\CanonClicker\DataFiles\norm_en.txt')   # and 'normalize' it
    for i, seg in enumerate(strings):
        textEN.append(Segment(i, seg, -1, -1, True))  # build segment list for English

    with open(r'f:\CanonParallel\PDFTEXT.txt', 'r', encoding = 'utf-8') as f:
        stringsUK = normalize_text(f.read(), r'D:\Programming\Python\_AIT\CanonClicker\DataFiles\norm_ukr.txt')  # read and normalize the text
        
    for i, seg in enumerate(stringsUK):  # build segment list for Ukrainian
        textUK.append(Segment(i, seg, -1, -1, False))
    
    
    used = []  ## not used so far.. probably later
    edic = make_eng_dic()
        
    i = 0 
    length = len(textEN)
    mx = 0
    while i < length:  ## textEN changes in process hence cannot iterate using a generator
        
        staging_dic: List[Classes.classes.dic_article] = create_staging_dic(textEN[i].segment_text, edic) # build a dic for this segment
    
        # progressbar(i, length) 
        print (f"   {i} of {length}", end = '\r')
        seg, segUK_number, segUK_score = count_max_score(textEN[i], textUK, staging_dic) # filling the table
        
        seg.max_score = segUK_score
        seg.aligned_segment = segUK_number
         
        if segUK_score >= DECENT_SCORE:
            # print('Align ' + str(seg.segment_number))
            textEN, textUK, mx = align_texts(textEN, textUK, seg.segment_number) ## align text lists by segments with high score
            #dump_to_file() ## надо написать.. или нет

        length = len(textEN)    
        if mx > i:
            i = mx + 1
        else: i += 1

        if i > 10:
            break
    
    for i in scoretable.keys():  ## sort the score table values, descending
        scoretable[i] = {k: v for k, v in sorted(scoretable[i].items(), key=lambda item: item[1], reverse=True)} ## https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value

    deduplicate()
    
    with open(r'D:\Programming\Python\_AIT\CanonClicker\DataFiles\aligned.csv', 'w', encoding = 'utf-8') as f:
        for i in scoretable.keys():
        ## i - eng segment number
        ## u - ukr segment number = list(scoretable[i].keys())[0]
        ## sc - max(scoretable[i].values())
        ## textEN[i].segment_text - eng segment text
        ## textUK[u].segment_text - ukr segment text
            try:
                u = list(scoretable[i].keys())[0]
            except:
                u = 0
            try:
                u1 = list(scoretable[i].keys())[1]
            except Exception as e:
                u1 = u
            sc = max(scoretable[i].values()) if len(scoretable[i].values()) > 0 else -10000
            #if sc > 10:
            f.write(f"{i}\t{textEN[i].segment_text}\t{u}\t{textUK[u].segment_text}\t{sc}\t{u1}\t{textUK[u1].segment_text}\tscoretable key: {i}\t{scoretable[i]}\n") # write to file segments with "normal" score

if __name__ == '__main__':
    main()