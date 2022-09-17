import sqlite3
import os.path
from typing import List
from os import environ
from time import sleep

import pandas as pd

def translate_text(target, text):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    import six
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    #print(u"Text: {}".format(result["input"]))
    #print(type(result))
    if type(result) is list:
        return(result[0]["translatedText"])
    if type(result) is dict:
        return(result["translatedText"])

def normalize_text(raw_text: str) -> list[str]:
    text: str = ''
    strings = []
    result_strings = []
    
    text = raw_text.replace('\n\n\n', '\n')
    text = text.replace('\n\n', '\n')
    strings = text.replace(' .', '.').replace(' ,', ',').replace(' ’', '’').split('\n')
    
    res_strings = []
    
    for line in strings:
        if len(line):
            res_strings.append(line)
    strings = res_strings.copy()    
    
    length = len(strings)
    iter = 0
    while iter < length:
        line = strings[iter]
        if iter + 1 < length:
            line_next = strings[iter+1] 
            
            if ((line_next.find('.') or line_next.find(',')) and not line_next[0].isupper()) or line_next.strip()[0].islower(): #  or line.strip()[-1] in ['’',"'"]   and line_next.strip()[2:] == ' )'):
                result_strings.append(' '.join((line.strip(), line_next.strip())))
                #print(f"Punctuation mark in the next line, merged, added : {' '.join((line, strings[i+1]))}")
                iter += 1
            else: 
                result_strings.append(line.strip())
                #print(f"Nothing special, just added : {line}")
        iter += 1
    
    return(result_strings)

def ReadPDF(PDFPath: str, start: int, end: int):
    import fitz
    strlist = []
    with fitz.open(PDFPath) as doc:
        for page in doc.pages(start, end, 1):
            strlist.append(page.get_text())

    return(strlist)

def create_word_list(PDFPath) -> List[str]:
    text = ReadPDF(PDFPath, 4, 41)
    lst = []
    
    for st in text:
        lines = st.split('\n')
        for str in lines:
            lst.append(str.strip())

    iter: int = 0
    length = len(lst)
    
    while iter < length:
        
        ind: int = lst[iter].find('(')    
        if lst[iter].find('Page ') != -1 and lst[iter].find(' of ') != -1:
            lst.pop(iter)
            length = len(lst)
            #print(f'iter = {iter}, length = {length}')
        elif lst[iter].find('Cambridge English: ') != -1:
            lst.pop(iter)
            length = len(lst)    
        
        elif lst[iter].find('Vocabulary List: ') != -1:
            lst.pop(iter)
            length = len(lst) 

        elif lst[iter].find('201') != -1:
            lst.pop(iter)
            length = len(lst) 
        
        elif lst[iter].find('•') != -1:
            #print(lst[iter])
            lst.pop(iter)
            length = len(lst)
            
        
        elif len(lst[iter]) <2:
            lst.pop(iter)
            length = len(lst)
            
        
        elif ind != -1:
            lst[iter] = lst[iter][:ind-1]
            iter += 1
        else:
            iter += 1     
        # lst[iter] = lst[iter].strip()

    
def main():

    #db_is_new: bool = False
    from __mylibs.uk_stemmer import UkStemmer

    db_filename = 'D:\\Programming\\Python\\_AIT\\StopWords\\stopwordsUKR.db'
    db_stem = 'D:\\Programming\\Python\\_AIT\\StopWords\\stemwordsUKR.db'
    db_comp = 'D:\\Programming\\Python\\_AIT\\StopWords\\stagingUKR.db'       
    
    stemmer = UkStemmer()
    
        
    with sqlite3.connect(db_comp) as conn_stem:
        c = conn_stem.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS Dictionary
        ([word_id] INTEGER PRIMARY KEY AUTOINCREMENT, [word_eng] TEXT, [word_ukr] TEXT)
        ''')
        conn_stem.commit()
    
    
    #if os.path.exists(db_filename):
    #    db_is_new = False
    #if db_is_new:
    #    with sqlite3.connect(db_filename) as conn:
    #        c = conn.cursor()
    #        c.execute('''
    #        CREATE TABLE IF NOT EXISTS Dictionary
    #        ([word_id] INTEGER PRIMARY KEY AUTOINCREMENT, [word_en] TEXT, [word_ukr] TEXT)
    #        ''')
    #        conn.commit()
    

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'D:\Programming\Python\Text_Count\my-translation-sa-key.json'

    project_id = environ.get("PROJECT_ID", "")
    assert project_id
    parent = f"projects/{project_id}"

    st = ''
    i = 0
    with open(r'D:\Programming\Python\_AIT\StopWords\staging.txt', 'r', encoding = 'utf-8') as f:
        with sqlite3.connect(db_comp) as conn_dic:
            cdic = conn_dic.cursor()
            for st in f.read().split('\n'):
                print(i)
                i += 1
                try:   
                    query = f"INSERT INTO Dictionary(word_eng, word_ukr) values ('{st}', '{stemmer.stem_word(translate_text('uk', st))}');"
                    #print(query)
                    cdic.execute(query)
                except Exception as e:
                    conn_dic.commit() ## max id 2920 
                    print(e)
                    print(f"Error, the last inserted index is {i} : {st}")
                    quit()
            conn_dic.commit()     
    """
    with sqlite3.connect('D:\\Programming\\Python\\Text_Count\\words.db') as conn:
            c = conn.cursor()
            with sqlite3.connect(db_stem) as conn_dic:
                cdic = conn_dic.cursor()
                for a in gloss[3][1]:
        
                for st in c.execute('SELECT english FROM dict order by english asc;'):
                    print(i)
                    i += 1
                    try:   
                        query = f"INSERT INTO Dictionary(word_eng, word_ukr) values ('{st[0]}', '{stemmer.stem_word(translate_text('uk', st))}');"
                        #print(query)
                        cdic.execute(query)
                    except Exception as e:
                        conn_dic.commit() ## max id 2920 
                        print(e)
                        print(f"Error, the last inserted index is {i + 2921}, dict record num {i}")
                        quit()
                conn_dic.commit()                
    conn.commit()  ## max id 2920 
    """ 
    """
    gloss = pd.read_html('https://www.eapfoundation.com/vocab/academic/other/csavl/') # , usecols=1)
    with sqlite3.connect(db_comp) as conn_dic:
        cdic = conn_dic.cursor()
        for k, a in enumerate(gloss[3][1]):
            if k > 433 and k != 581:
                try:   
                    query = f"INSERT INTO Dictionary(word_en, word_ukr) values ('{a}', '{stemmer.stem_word(translate_text('uk', a))}');"
                            #print(query)
                    cdic.execute(query)
                except Exception as e:
                    conn_dic.commit() ## max id 2920 
                    print(e)
                    print(f"Error, the error with dict word {a}")
                    quit()
        conn_dic.commit()                
    """


    #print(stemmer.stem_word(translate_text('uk', 'ability')))

    #for st in list:
    #    print(st)

if __name__ == '__main__':
    main()