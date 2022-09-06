import os
import sys
import requests
import enchant
from random import choice
from io import BytesIO
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv
from flask import send_file

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TMP_DIR = os.environ.get("TMP_DIR")

d = enchant.Dict("en_US")


def search(words: str):
    locale = "it_IT"
    ww = words.split()
    for w in ww:
        if d.check(w):
            locale = "en_US"
            break
    r = requests.get("https://api.qwant.com/v3/search/images",
        params={
            'count': 250,
            'q': words,
            't': 'images',
            'safesearch': 0,
            'locale': locale,
            'offset': 0,
            'device': 'desktop'
        },
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
    )
    if r.status_code != 200:
        raise Exception("API immagini non raggiungibile...")
    else:
        return get_image(r, words, 0, [])

def get_image(r, words: str, count: 0, searched: []):

    try:

        random_int = choice([i for i in range(0, 250) if i not in searched])
        searched.append(random_int)

        url = r.json().get('data').get('result').get('items')[random_int].get('media_fullsize')
        mimetype = r.json().get('data').get('result').get('items')[random_int].get('thumb_type')
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
        bytes_img = BytesIO(resp.raw.read())
        if mimetype == 'animatedgif':
            return bytes_img, 'image.gif', 'image/gif'
        elif mimetype == 'jpeg':
            return bytes_img, 'image.jpeg', 'image/jpeg'
        else:
            if count < 249:
                count = count + 1
                return get_image(r, words, count, searched)
            else:
                raise Exception("Nessun immagine trovata...")
    except:
        if count < 249:
            count = count + 1
            return get_image(r, words, count, searched)
        else:
            raise Exception("Nessun immagine trovata...")