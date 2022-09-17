import os.path
import sqlite3
import os
from os import environ
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

    print(u"Text: {}".format(result["input"]))
    print(result)
    return(result["translatedText"])

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'D:\Programming\Python\Text_Count\my-translation-sa-key.json'

project_id = environ.get("PROJECT_ID", "")
assert project_id
parent = f"projects/{project_id}"
word = 'roll'
# ruword = translate_text("ru", word)

data = pd.read_json('https://translate.google.com/?sl=en&tl=ru&text=composure&op=translate')

print(data)

