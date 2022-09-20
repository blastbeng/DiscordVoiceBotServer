import re
import shutil
import chatterbot
import spacy
import random
import wikipedia
import sqlite3
import json
import insults
import requests
import sys
import os
import datetime
import string
from chatterbot import ChatBot
from chatterbot.conversation import Statement
from chatterbot.trainers import ListTrainer
from chatterbot.comparisons import LevenshteinDistance
#from chatterbot.comparisons import SpacySimilarity
#from chatterbot.comparisons import JaccardSimilarity
#from chatterbot.response_selection import get_random_response
from chatterbot.response_selection import get_most_frequent_response
from gtts import gTTS
from io import BytesIO
from pytube import YouTube
from pytube import Search
from pathlib import Path
from google_translate_py import Translator
from faker import Faker
from markovipy import MarkoviPy
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TMP_DIR = os.environ.get("TMP_DIR")

fake = Faker()

EXCEPTION_WIKIPEDIA = 'Non ho trovato risultati per: '
EXCEPTION_YOUTUBE_AUDIO = 'Errore nella riproduzione da Youtube.'

wikipedia.set_lang("it")

class YoutubeVideo():
    def __init__(self):
        self.title = None
        self.link = None

def wiki_summary(testo: str):
  try:
    definition = wikipedia.summary(testo, sentences=1, auto_suggest=True, redirect=True)
    return testo + ": " + definition
  except:
    return EXCEPTION_WIKIPEDIA + testo


def generate(filename: str):
  with open(filename, "rb") as fmp3:
      data = fmp3.read(1024)
      while data:
          yield data
          data = fmp3.read(1024)

def get_tts(text: str):    
  tts = gTTS(text=text, lang="it", slow=False)
  fp = BytesIO()
  tts.write_to_fp(fp)
  fp.seek(0)
  return fp

def clean_input(testo: str):
  re_equ = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
  ck_url = re.findall(re_equ, testo)
  if(ck_url):
    return False
  else:
    return True

def get_chatterbot(trainfile: str):
  fle = Path('./config/db.sqlite3')
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()

  nlp = spacy.load("it_core_news_lg")
  chatbot = ChatBot(
      'PezzenteCapo',
      storage_adapter='chatterbot.storage.SQLStorageAdapter',
      database_uri='sqlite:///config/db.sqlite3',
      statement_comparison_function = LevenshteinDistance,
      response_selection_method = get_most_frequent_response,
      logic_adapters=[
          {
              'import_path': 'chatterbot.logic.BestMatch',
              'maximum_similarity_threshold': 0.90
          }
      ]
  )

  if os.path.isfile(trainfile):
    print("Loading: " + trainfile)
    trainer = ListTrainer(chatbot)
    trainfile_array = []
    with open(trainfile) as file:
        for line in file:
            trainfile_array.append(line.strip())
    trainer.train(trainfile_array)
    print("Done. Deleting: " + trainfile)
    os.remove(trainfile)
  with sqlite3.connect("./config/db.sqlite3") as db:
    cursor = db.cursor()
    cursor.execute('''SELECT COUNT(*) from STATEMENT ''')
    result=cursor.fetchall()
    if result == 0 :
      learn('ciao', 'ciao', chatbot)    
  return chatbot

def learn(testo: str, risposta: str, chatbot: ChatBot):
  input_statement = Statement(text=testo)
  correct_response = Statement(text=risposta)
  chatbot.learn_response(correct_response, previous_statement=input_statement)

def recreate_file(filename: str):
  if os.path.exists(filename):
    os.remove(filename)
    fle = Path(filename)
    fle.touch(exist_ok=True)  


def populate_new_sentences(chatbot: ChatBot, count: int, word: str, fromapi: bool):
  try:
    out = ""
    filename = ''
    if word:
      filename = TMP_DIR + '/sentences_parsed.txt'
    else:
      filename = TMP_DIR + '/sentences.txt'


    extract_sentences_from_chatbot(filename, word, False, chatbot)

    
    if fromapi:
      out = out + "Processing...\n\n"

    i=0
    while(i < count): 
      markov = MarkoviPy(filename, random.randint(3, 4)).generate_sentence()

      with open(filename) as f:
        last = None
        for line in (line for line in f if line.rstrip('\n')):
          last = line
      
      with open(filename, 'a') as sentence_file:
        towrite = ""
        sanitized = markov.strip()
        if sanitized[-1] in string.punctuation:
          if fromapi:
            out = out + " - " + sanitized +"\n"
          towrite = towrite + sanitized
        else:
          if fromapi:
            out = out + " - " + sanitized +".\n"
          towrite = towrite + sanitized + "."
        sentence_file.write(towrite)

      learn(last, markov, chatbot)
      i=i+1
    if fromapi:
      return out
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    if fromapi:
      return "Parola o frase non trovata nel database del bot."
    else:
      print("Error populating sentences!")

def get_youtube_audio(link: str):
  try:
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    fp = BytesIO()
    video.stream_to_buffer(fp)
    fp.seek(0)
    return fp    
  except:
    return get_tts(EXCEPTION_YOUTUBE_AUDIO)

def search_youtube_audio(text: str, onevideo: bool):
  try:
    s = Search(text)
    if not s.results or len(s.results) == 0:
      videos = []
      return videos
    else:
      if onevideo:
        videos = []
        size = len(s.results)-1
        n = random.randint(0,size)
        video = s.results[n]
        youtubeVideo = YoutubeVideo()
        youtubeVideo.title=video.title
        youtubeVideo.link=video.watch_url
        videos.append(youtubeVideo.__dict__)
        return videos
      else:
        videos = []
        for video in s.results:
          youtubeVideo = YoutubeVideo()
          youtubeVideo.title=video.title
          youtubeVideo.link=video.watch_url
          videos.append(youtubeVideo.__dict__)
        return videos
  except:
    videos = []
    return videos  

def get_youtube_info(link: str):
  try:
    videos = []
    video = YouTube(link)
    youtubeVideo = YoutubeVideo()
    youtubeVideo.title=video.title
    youtubeVideo.link=video.watch_url
    videos.append(youtubeVideo.__dict__)
    return videos    
  except:
    videos = []
    return videos

def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    htmlCodes = (
            ("'", '&#39;'),
            ('"', '&quot;'),
            ('>', '&gt;'),
            ('<', '&lt;'),
            ('&', '&amp;'),
            ('', '“'),
            ('', '"'),
        )
    for code in htmlCodes:
        s = s.replace(code[1], code[0])
    return s.strip()

def get_joke(cat: str):
  try:
    url="http://192.168.1.160:3050/v1/jokes"
    if cat != "":
      params="category="+cat
      url=url+"?"+params
    r = requests.get(url)
    if r.status_code != 200:
      return "API barzellette non raggiungibile..."
    else:
#      full_json = r.text
      full = json.loads(r.text)
      text = html_decode(full['data']['text'])
      return text
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    return "Riprova tra qualche secondo..."


def scrape_jokes():
  print("--- START : JOKES SCRAPER ---")
  #print("-----------------------------")
  #scrape_internal("LAPECORASCLERA", "1")
  #print("-----------------------------")
  #scrape_internal("FUORIDITESTA", "1")
  print("-----------------------------")
  scrape_internal("LAPECORASCLERA", "0")
  print("-----------------------------")
  scrape_internal("FUORIDITESTA", "0")
  print("-----------------------------")
  print("---- END : JOKES SCRAPER ----")

def scrape_internal(scraper: str, page: str):
  try:
    url="http://192.168.1.160:3050/v1/mngmnt/scrape"
    params="scraper="+scraper
    if page != 0:
      params = params+"&pageNum="+page
    url=url+"?"+params
    r = requests.get(url)
    if r.status_code != 200:
      print(scraper + ": Error scraping jokes!")
      pass
    else:
      full_json = r.text
      full = json.loads(full_json)
      print(scraper + ": Jokes scraper result")
      print("status:"+ str(full['status']))
      print("numberTotal:"+ str(full['numberTotal']))
      print("numberDone:"+ str(full['numberDone']))
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print("Error scraping jokes!")

def get_random_date():
  offset = '-' + str(random.randint(1, 4)) + 'y'
  date = fake.date_time_between(start_date=offset, end_date='now').strftime("%Y-%m-%d")
  return date

def extract_sentences_from_chatbot(filename: str, word: str, distinct: bool, chatbot: ChatBot):
  #globalsanit = ""
  try:
    sqliteConnection = sqlite3.connect('./config/db.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_select_sentences_query = ""
    if distinct:
      sqlite_select_sentences_query = """SELECT DISTINCT text FROM statement ORDER BY text"""
    else:
      sqlite_select_sentences_query = """SELECT text FROM statement"""

    data = ()

    cursor.execute(sqlite_select_sentences_query, data)
    records = cursor.fetchall()

    
    records_len = len(records)-1


    try:
      os.remove(filename)
    except OSError:
      pass
      
    globalsanit = ""

    count = 0

    with open(filename, 'a') as sentence_file:
      for row in records:
        sentence = row[0]
        if (word is not None and word.lower() in sentence.lower()) or word is None:
          sanitized = sentence.strip()
          if sanitized[-1] not in string.punctuation:
            sanitized = sanitized + "."
          if records.index(row) != records_len:
            sanitized = sanitized + "\n"
          sentence_file.write(sanitized)
          count = count + 1

    cursor.close()
    if not distinct:
      lines = open(filename).readlines()
      random.shuffle(lines)
      open(filename, 'w').writelines(lines)
    
    #if count < 5 and word is not None and chatbot is not None:
    #  extract_sentences_from_chatbot(TMP_DIR + '/sentences.txt', None, False, chatbot)
    #  lines = open(TMP_DIR + '/sentences.txt').read().splitlines()
    #  z=0
    #  word_internal = word;
    #  while(z<100):
    #    myline = random.choice(lines)
    #    sanitized = word_internal.strip()
    #    if sanitized[-1] not in string.punctuation:
    #      word_internal = word_internal + "."
    #    learn(word_internal, myline, chatbot)  
    #    learn(myline, word_internal, chatbot)
    #    z = z + 1
    #  extract_sentences_from_chatbot(filename, word, distinct, None)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    return "Error extracting sentences!"
  finally:
    if sqliteConnection:
        sqliteConnection.close()
  #if distinct:
  #  return globalsanit


def check_sentences_file_exists(): 
  fle = Path('./config/sentences.txt')
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()
