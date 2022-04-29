import re
import chatterbot
import spacy
import random
import wikipedia
import sqlite3
import json
import insults
from chatterbot import ChatBot
from chatterbot.conversation import Statement
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.comparisons import LevenshteinDistance
from chatterbot.response_selection import get_random_response
from gtts import gTTS
from io import BytesIO
from pytube import YouTube
from pytube import Search
from pathlib import Path

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

def get_chatterbot(outfile: str, train: bool):
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
      response_selection_method = get_random_response
  )
  if train:
    trainer = ChatterBotCorpusTrainer(chatbot)
    trainer.train("chatterbot.corpus.italian")
  if outfile is not None:
    trainer.export_for_training(outfile)  

  with sqlite3.connect("./config/db.sqlite3") as db:
    cursor = db.cursor()
    cursor.execute('''SELECT COUNT(*) from STATEMENT ''')
    result=cursor.fetchall()
    if result == 0 :
      print("The db file is empty, learning ciao - ciao")
      utils.learn('ciao', 'ciao', chatbot)
    else :
      print("The db file is not empty")
  return chatbot


def learn(testo: str, risposta: str, chatbot: ChatBot):
  input_statement = Statement(text=testo)
  correct_response = Statement(text=risposta)
  chatbot.learn_response(correct_response, input_statement)
  return "Ho imparato: " + testo + " => " + risposta

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



class TournamentUsers():
  def __init__(self, id, username, image, title):
      self.id = id
      self.username = username
      self.image = image
      self.title = title

class TournamentTeams():
  def __init__(self, name, users):
      self.name = name
      self.users = users

class TournamentRounds():
  def __init__(self, round, teams):
      self.round = round
      self.teams = teams

class TournamentInfo():
  def __init__(self, author, author_image, guild_image, name, description, image, rounds):
      self.author       = author
      self.author_image = author_image
      self.guild_image  = guild_image
      self.name         = name
      self.description  = description
      self.image        = image
      self.rounds       = rounds

def generate_tournament(content):

  user_titles = insults.names_single_base
  team_names = insults.names_plural

  tournamentUsersArray = []
  for user in content['users']:
    user_title = random.choice(user_titles)
    user_titles.remove(user_title)
    tournamentUser = TournamentUsers(user['id'], user['username'], user['image'], user_title)
    tournamentUsersArray.append(tournamentUser.__dict__)

  tournamentTeamsArray = []
  team_name = random.choice(team_names)
  team_names.remove(team_name)
  tournamentTeam = TournamentTeams(team_name, tournamentUsersArray)
  tournamentTeamsArray.append(tournamentTeam.__dict__)

  tournamentRoundsArray = []
  tournamentRounds = TournamentRounds("round 1", tournamentTeamsArray)
  tournamentRoundsArray.append(tournamentRounds.__dict__)

  tournament = TournamentInfo(content['author'],
                          content['author_image'],
                          content['guild_image'],
                          content['name'],
                          content['description'],
                          content['image'],
                          tournamentRoundsArray.__dict__)
  return tournament.__dict__