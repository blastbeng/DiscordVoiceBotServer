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
import fakeyou
import time
import wave
import audioop
from uuid import uuid4
from chatterbot import ChatBot
from chatterbot.conversation import Statement
from custom_trainer import TranslatedListTrainer
from custom_trainer import CustomTrainer
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
from faker import Faker
from markovipy import MarkoviPy
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv
from fakeyou.objects import *

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TMP_DIR = os.environ.get("TMP_DIR")
TRANSLATOR_PROVIDER = os.environ.get("TRANSLATOR_PROVIDER")
TRANSLATOR_BASEURL = os.environ.get("TRANSLATOR_BASEURL")
MYMEMORY_TRANSLATOR_EMAIL = os.environ.get("MYMEMORY_TRANSLATOR_EMAIL")
FAKEYOU_USER = os.environ.get("FAKEYOU_USER")
FAKEYOU_PASS = os.environ.get("FAKEYOU_PASS")

fy=fakeyou.FakeYou()

fake = Faker()

EXCEPTION_WIKIPEDIA = 'Non ho trovato risultati per: '
EXCEPTION_YOUTUBE_AUDIO = 'Errore nella riproduzione da Youtube.'

wikipedia.set_lang("it")

class YoutubeVideo():
    def __init__(self):
        self.title = None
        self.link = None

class TrainJson():
  def __init__(self, info, language, sentences):
        self.info = info
        self.language = language
        self.sentences = sentences

class BaseClass(object):
    def __init__(self, classtype):
        self._type = classtype

def ClassFactory(name, argnames, BaseClass=BaseClass):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            # here, the argnames variable is the one passed to the
            # ClassFactory call
            if key not in argnames:
                raise TypeError("Argument %s not valid for %s" 
                    % (key, self.__class__.__name__))
            setattr(self, key, value)
        BaseClass.__init__(self, name[:-len("Class")])
    newclass = type(name, (BaseClass,),{"__init__": __init__})
    return newclass


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

def get_tts_google(text: str):    
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

def get_chatterbot(chatid: str, train: bool):

  dbfile=chatid+"-db.sqlite3"

  fle = Path('./config/'+dbfile)
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()

  nlp = spacy.load("it_core_news_lg")
  chatbot = ChatBot(
      'PezzenteCapo',
      storage_adapter='chatterbot.storage.SQLStorageAdapter',
      database_uri='sqlite:///config/'+dbfile,
      statement_comparison_function = LevenshteinDistance,
      response_selection_method = get_most_frequent_response,
      logic_adapters=[
          {
              'import_path': 'chatterbot.logic.BestMatch',
              'maximum_similarity_threshold': 0.90
          }
      ]
  )

  with sqlite3.connect("./config/"+dbfile) as db:
    cursor = db.cursor()
    cursor.execute('''SELECT COUNT(*) from STATEMENT ''')
    result=cursor.fetchall()
    if result == 0 :
      learn('ciao', 'ciao', chatbot)
      if train:
        trainer = CustomTrainer(chatbot, translator_provider=TRANSLATOR_PROVIDER, translator_baseurl=TRANSLATOR_BASEURL, translator_email=MYMEMORY_TRANSLATOR_EMAIL)
        trainer.train()      
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


def populate_new_sentences(chatbot: ChatBot, count: int, word: str, fromapi: bool, chatid: str):
  filename = ""
  try:
    out = ""
    #filename = ''
    #if word:
    #  filename = TMP_DIR + '/sentences_parsed.txt'
    #else:
    #filename = TMP_DIR + '/sentences.txt'

    filename = TMP_DIR + '/' + get_random_string(24) + ".txt"


    extract_sentences_from_chatbot(filename, word, False, chatbot, chatid)

    last = None
    
    if fromapi:
      out = out + "Processing...\n\n"

    if word is not None:
      with open(filename, 'a') as sentence_file:
        towrite = ""
        sanitized = word.strip()
        if sanitized[-1] in string.punctuation:
          if fromapi:
            out = out + " - " + sanitized +"\n"
          towrite = towrite + sanitized +"\n"
        else:
          if fromapi:
            out = out + " - " + sanitized +".\n"
          towrite = towrite + sanitized + ".\n"
        sentence_file.write(towrite)

    i=0
    while(i < count): 
      markov = MarkoviPy(filename, random.randint(3, 4)).generate_sentence()

      if last is None:
        with open(filename) as f:
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
      last = markov
      i=i+1
    if fromapi:
      return out
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    if fromapi:
      return "Errore!"
    else:
      print("Error populating sentences!")
  finally:
    try:
      os.remove(filename)
    except OSError:
      pass

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

def extract_sentences_from_chatbot(filename: str, word: str, distinct: bool, chatbot: ChatBot, chatid: str):
  #globalsanit = ""
  try:
    dbfile=chatid+"-db.sqlite3"
    sqliteConnection = sqlite3.connect('./config/'+dbfile)
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
        #if (word is not None and word.lower() in sentence.lower()) or word is None:
        sanitized = sentence.strip()
        if sanitized[-1] not in string.punctuation:
          sanitized = sanitized + "."
        if records.index(row) != records_len:
          sanitized = sanitized + "\n"
        sentence_file.write(sanitized)
        count = count + 1

    cursor.close()
    #if not distinct:
    #  lines = open(filename).readlines()
    #  random.shuffle(lines)
    #  open(filename, 'w').writelines(lines)
    
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

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def train_json(json_req, chatbot: ChatBot):
  try:
    if not json_req:
      print(empty_template_trainfile_json())
    else:
      content = json_req
      trainer = TranslatedListTrainer(chatbot, lang=content['language'], translator_provider=TRANSLATOR_PROVIDER, translator_baseurl=TRANSLATOR_BASEURL, translator_email=MYMEMORY_TRANSLATOR_EMAIL)
      i = 0
      while(i < len(content['sentences'])):
        trainarray=[]
        j = 0
        while (j < len(content['sentences'][i]["message"+str(i)])):
          trainarray.append(content['sentences'][i]["message"+str(i)][j])
          j = j + 1
        
        trainer.train(trainarray)
        i = i + 1

      print(TrainJson("Done.", content['language'], []).__dict__)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(empty_template_trainfile_json())

def empty_template_trainfile_json():
  trainJsonSentencesArray=[]

  message0=[]
  message0.append("Hello, How are you?")
  message0.append("I am fine, thanks.")

  Conversation0 = ClassFactory("ConversationClass", "message0")
  conversation0 = Conversation0(message0=message0)

  trainJsonSentencesArray.append(conversation0.__dict__)

  message1=[]
  message1.append("How was your day?")
  message1.append("It was good, thanks.")

  Conversation1 = ClassFactory("ConversationClass", "message1")
  conversation1 = Conversation1(message1=message1)

  trainJsonSentencesArray.append(conversation1.__dict__)

  trainJson = TrainJson("Error! Please use this format.", "en", trainJsonSentencesArray)

  return trainJson.__dict__

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in "txt"

def train_txt(trainfile, chatbot: ChatBot, lang: str):
  try:
      print("Loading: " + trainfile)
      trainer = TranslatedListTrainer(chatbot, lang=lang, translator_provider=TRANSLATOR_PROVIDER, translator_baseurl=TRANSLATOR_BASEURL, translator_email=MYMEMORY_TRANSLATOR_EMAIL)
      trainfile_array = []
      with open(trainfile) as file:
          for line in file:
              if line.split():
                trainfile_array.append(line.strip())
              else:
                trainer.train(trainfile_array)
                trainfile_array=[]
      if len(trainfile_array) > 0:
        trainer.train(trainfile_array)
      print("Done. Deleting: " + trainfile)
      os.remove(trainfile)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print("Error! Please upload a trainfile.txt")

def delete_by_text(dbpath: str, text: str):
  try:
    sqliteConnection = sqlite3.connect(dbpath)
    cursor = sqliteConnection.cursor()

    sqlite_delete_query = """DELETE FROM Statement 
                          WHERE text like ?
                          OR text like ?
                          OR text = ?"""

    data_tuple = (text+'%', 
                  '%'+text, 
                  text)

    cursor.execute(sqlite_delete_query, data_tuple)
    sqliteConnection.commit()
    cursor.close()

    return('Frasi con parola chiave "' + text + '" cancellate!')
  except sqlite3.Error as error:
    print("Failed to delete data from sqlite", error)
    return("Errore!")
  finally:
    if sqliteConnection:
        sqliteConnection.close()

def get_tts(text: str, voice=None):
  try:
    if voice is None or voice == "null":
      voice_to_use = get_random_voice()
    else:
      voice_to_use = voice
    if voice_to_use != "google":
      fy.login(FAKEYOU_USER,FAKEYOU_PASS)
      #newtext = text.translate(str.maketrans('', '', string.punctuation))
      ijt = generate_ijt(fy, text.strip(), voice_to_use)
      if ijt is not None:
        out = get_wav_fy(fy,ijt)
        if out is not None:
          return out
        else:
          return get_tts_google(text.strip())
      else:
        return get_tts_google(text.strip())
    else:
      return get_tts_google(text.strip())
  except fakeyou.exception.InvalidCredentials:
    return get_tts_google(text.strip())

def get_random_voice():
  voices = [ 
    "TM:nk1h2vqxhzdc", #caparezza 
    "TM:5ggf3m5w2mhq", #gerry scotti
    "TM:eb0rmkq6fxtj" #Goku
    "TM:7r48p42sbqej", #maria de filippi
    "TM:xd8srfb4v5w6", #mario giordano  
    "TM:zdag8n18q9ct", #paolo bonolis   
    "TM:8bqjb9x51vz3", #papa francesco               
    "TM:22e5sxvt2dvk"] #silvio berlusconi
  size = len(voices)
  n = random.randint(0,size-1)
  sentence = voices[n]
  return sentence

def generate_ijt(fy,text:str,ttsModelToken:str):
  if fy.v:
    print("getting job token")
  payload={"uuid_idempotency_token":str(uuid4()),"tts_model_token":ttsModelToken,"inference_text":text}
  handler=fy.session.post(url=fy.baseurl+"tts/inference",data=json.dumps(payload))
  if handler.status_code==200:
    ijt=handler.json()["inference_job_token"]
    return ijt
  elif handler.status_code==400:
    return None
  elif handler.status_code==429:
    return None


def get_wav_fy(fy,ijt:str):
  while True:
    handler=fy.session.get(url=fy.baseurl+f"tts/job/{ijt}")
    if handler.status_code==200:
      hjson=handler.json()
      wavo=wav(hjson)
      if fy.v:
        print("WAV STATUS :",wavo.status)
      if wavo.status=="started":
        continue
      elif "pending" in wavo.status:
        time.sleep(2)
        continue
      elif "attempt_failed" in wavo.status:
        return None
      elif "complete_success":
        content=fy.session.get("https://storage.googleapis.com/vocodes-public"+wavo.maybePublicWavPath).content
        fp = BytesIO(content)
        fp.seek(0)
        return fp
    elif handler.status_code==429:
      return None
