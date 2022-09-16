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
from chatterbot.trainers import ChatterBotCorpusTrainer
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

def get_chatterbot(outfile: str, infile: str):
  fle = Path('./config/db.sqlite3')
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()

  nlp = spacy.load("it_core_news_lg")
  chatbot = ChatBot(
      'PezzenteCapo',
      storage_adapter='chatterbot.storage.SQLStorageAdapter',
      database_uri='sqlite:///config/db.sqlite3',
      logic_adapters=[
          'chatterbot.logic.BestMatch'
      ],
      statement_comparison_function = LevenshteinDistance,
      #statement_comparison_function = SpacySimilarity,
      #statement_comparison_function = JaccardSimilarity,
      #response_selection_method = get_random_response,
      response_selection_method = get_most_frequent_response
  )
  if infile is not None or outfile is not None:
    trainer = ChatterBotCorpusTrainer(chatbot)
    if outfile is not None:
      trainer.export_for_training(outfile)
      if infile is not None and not os.path.exists(infile):
        shutil.copyfile(outfile, infile)
    if infile is not None and os.path.exists(infile):
      trainer = ChatterBotCorpusTrainer(chatbot)
      trainer.train(infile)
      
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
  chatbot.learn_response(correct_response, input_statement)

def recreate_file(filename: str):
  if os.path.exists(filename):
    os.remove(filename)
    fle = Path(filename)
    fle.touch(exist_ok=True)  


def populate_new_sentences(chatbot: ChatBot, count: int, word: str):
  try:
    filename = ''
    if word:
      filename = TMP_DIR + '/sentences_parsed.txt'
    else:
      filename = TMP_DIR + '/sentences.txt'


    extract_sentences_from_chatbot(filename, word, False)

    i=0
    out=""
    while(i < count): 
      sent_num = i + 1;
      out = out + "Processing n. " + str(sent_num) + "\n";
      markov = MarkoviPy(filename, random.randint(3, 4)).generate_sentence()

      with open(filename) as f:
        last = None
        for line in (line for line in f if line.rstrip('\n')):
          last = line


      out = out + " - Sentence : " + last +"\n"

      learn(last, markov, chatbot)
      
      with open(filename, 'a') as sentence_file:
        towrite = "\n"
        sanitized = markov.strip()
        if sanitized[-1] in string.punctuation:
          out = out + " - Generated: " + sanitized +"\n"
          towrite = towrite + sanitized
        else:
          out = out  + " - Generated: " + sanitized +".\n"        
          towrite = towrite + sanitized + "."
        sentence_file.write(towrite)

      out = out + "\n\n"
      i=i+1
    return out
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    return "Error populating sentences!"

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

def extract_sentences_from_chatbot(filename: str, word: str, distinct: bool):
  globalsanit = ""
  try:
    sqliteConnection = sqlite3.connect('./config/db.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_select_sentences_query = ""
    if distinct:
      sqlite_select_sentences_query = """SELECT DISTINCT text FROM statement"""
    else:
      sqlite_select_sentences_query = """SELECT text FROM statement"""

    data = ()

    cursor.execute(sqlite_select_sentences_query, data)
    records = cursor.fetchall()


    try:
      os.remove(filename)
    except OSError:
      pass
      
    globalsanit = ""

    count = 1

    with open(filename, 'a') as sentence_file:
      records_len = len(records)-1
      for row in records:
        sentence = row[0]
        if (word is not None and word.lower() in sentence.lower()) or word is None:
          sanitized = sentence.strip()
          if sanitized[-1] not in string.punctuation:
            sanitized = sanitized + "."
          if records.index(row) != records_len:
            sanitized = sanitized + "\n"

          if distinct:
            globalsanit = globalsanit + str(count) + ". "+ sanitized
            count = count + 1

          sentence_file.write(sanitized)

    cursor.close()
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    return "Error extracting sentences!"
  finally:
    if sqliteConnection:
        sqliteConnection.close()
  if distinct:
    return globalsanit


def check_sentences_file_exists(): 
  fle = Path('./config/sentences.txt')
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()
