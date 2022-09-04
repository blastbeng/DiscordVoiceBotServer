import tweepy
import utils
import os
import sqlite3
import requests
import threading
import sys
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TMP_DIR = os.environ.get("TMP_DIR")
TWITTER_CONSUMER_KEY = os.environ.get("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.environ.get("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_KEY = os.environ.get("TWITTER_ACCESS_KEY")
TWITTER_ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_KEY, TWITTER_ACCESS_SECRET)
api = tweepy.API(auth)


class Post():
  def __init__(self, text, content, content_type):
      self.text = text
      self.content = content
      self.content_type = content_type

def check_temp_twitter_exists(): 
  fle = Path(TMP_DIR+'/twitter.sqlite3')
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()

def check_persistent_twitter_exists(): 
  fle = Path(os.getcwd()+'/config/twitter.sqlite3')
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()

def create_empty_tables():
  create_empty_tables_cache()
  create_empty_tables_persistent()

def create_empty_tables_cache():
  check_temp_twitter_exists()
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'/twitter.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_create_posts_query = """ CREATE TABLE IF NOT EXISTS Posts(
            id INTEGER PRIMARY KEY,
            text VARCHAR(255) NOT NULL,
            content BLOB,
            content_type VARCHAR(10),
            UNIQUE(text, content, content_type)
        ); """

    cursor.execute(sqlite_create_posts_query)

  except sqlite3.Error as error:
    print("Failed to create tables", error)
  finally:
    if sqliteConnection:
        sqliteConnection.close()

  

def create_empty_tables_persistent():
  check_persistent_twitter_exists()
  try:
    #sqliteConnection = Path(os.getcwd()+'/config/twitter.sqlite3')
    path = r''+os.getcwd()+'/config/twitter.sqlite3'
    sqliteConnection = sqlite3.connect(path)
    cursor = sqliteConnection.cursor()

    sqlite_create_searches_query = """ CREATE TABLE IF NOT EXISTS Searches(
            id INTEGER PRIMARY KEY,
            text VARCHAR(255) NOT NULL,
            UNIQUE(text)
        ); """

    cursor.execute(sqlite_create_searches_query)

  except sqlite3.Error as error:
    print("Failed to create tables", error)
  finally:
    if sqliteConnection:
        sqliteConnection.close()

def scrape(words: str, count: int):
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'/twitter.sqlite3')
    cursor = sqliteConnection.cursor()
    #from_date = utils.get_random_date()

    words = "#"+words

    for tweet in tweepy.Cursor(api.search_tweets, 
                               words,
                               lang="en",
                               count=count,
                               tweet_mode='extended').items(count):
        

        sqlite_insert_posts_query = """INSERT OR IGNORE INTO Posts
                      (text, content, content_type) 
                      VALUES 
                      (?, ?, ?)"""

        if 'media' in tweet.entities and tweet.entities['media'] is not None and len(tweet.entities['media']) > 0 and tweet.entities['media'][0]['type'] and tweet.entities['media'][0]['type'] == 'photo':
            media = tweet.entities['media']

            content = media[0]['media_url']
            content_type = media[0]['type']

            data_posts_tuple = (tweet.full_text, content, content_type,)
            cursor.execute(sqlite_insert_posts_query, data_posts_tuple)

    sqliteConnection.commit()
    cursor.close()

  except Esception as error:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print("Failed to scrape from twitter", error)
    print(exc_type, fname, exc_tb.tb_lineno)
  finally:
    if sqliteConnection:
        sqliteConnection.close()


def insert_search(words: str):
  try:
    path = r''+os.getcwd()+'/config/twitter.sqlite3'
    sqliteConnection = sqlite3.connect(path)
    cursor = sqliteConnection.cursor()

    sqlite_insert_posts_query = """INSERT OR IGNORE INTO Searches
                      (text) 
                      VALUES 
                      (?, )"""

    data_posts_tuple = (tweet.full_text, content, content_type)
    cursor.execute(sqlite_insert_posts_query, data_posts_tuple)

    sqliteConnection.commit()
    cursor.close()

  except sqlite3.Error as error:
    print("Failed to insert data into sqlite", error)
  finally:
    if sqliteConnection:
        sqliteConnection.close()

def get_all_searches():
  searches = []
  try:
      path = r''+os.getcwd()+'/config/twitter.sqlite3'
      sqliteConnection = sqlite3.connect(path)
      cursor_users = sqliteConnection.cursor()

      sqlite_select_posts_query = """SELECT text from Searches ORDER BY RANDOM()"""
      cursor_users.execute(sqlite_select_posts_query, ())
      records = cursor_users.fetchall()

      for row in records:
        searches.append(row[0])

      cursor_users.close()
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    return []
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  return searches



def search_all_random():
  post = None
  try:
      sqliteConnection = sqlite3.connect(TMP_DIR+'/twitter.sqlite3')
      cursor_users = sqliteConnection.cursor()

      sqlite_select_posts_query = """SELECT text, content, content_type from Posts ORDER BY RANDOM() LIMIT 1"""
      cursor_users.execute(sqlite_select_posts_query, ())
      records = cursor_users.fetchall()

      if len(records)==0:
        post = Post("Nessun post trovato. Riprova tra qualche minuto...", "", "")
      else:
        for row in records:
          text = row[0]
          content = row[1]
          content_type = row[2]
          post = Post(text, content, content_type)

      cursor_users.close()
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    return Post("Error", "", "")
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  if post is not None:
    return post.__dict__
  else:
    return Post("Error", "", "")

def search_random(word: str, sched, callcount):
  post = None
  if (callcount >= 2):
    post = Post("Nessun post trovato. Riprova tra qualche minuto...", "", "")
  else:
    try:
        sqliteConnection = sqlite3.connect(TMP_DIR+'/twitter.sqlite3')
        cursor_users = sqliteConnection.cursor()

        sqlite_select_posts_query = """SELECT text, content, content_type from Posts WHERE text LIKE ? OR text LIKE ? OR text LIKE ? OR text = ? ORDER BY RANDOM() LIMIT 1"""
        cursor_users.execute(sqlite_select_posts_query, (
        '%'+word+'%',
          word+'%',
        '%'+word,
          word,
          ))
        records = cursor_users.fetchall()

        if len(records)==0:

          job = sched.get_job(word)

          if job is None:          
            sched.add_job(scrape, 'interval', args=[word,50], hours=2, id=word)

          #threading.Timer(0, scrape, args=[word, 50]).start()
          #post = Post("Nessun post trovato. Popolo il database. Riprova tra qualche secondo...", "", "")
          callcount = callcount + 1
          post = search_random(word, sched, callcount);
        else:
          for row in records:
            text = row[0]
            content = row[1]
            content_type = row[2]
            post = Post(text, content, content_type)

        cursor_users.close()
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      return Post("Error", "", "")
    finally:
      if sqliteConnection:
        sqliteConnection.close()
  if post is not None:
    return post
  else:
    return Post("Error", "", "")
