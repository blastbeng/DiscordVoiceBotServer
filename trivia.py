import os
import requests
import sqlite3
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TMP_DIR = os.environ.get("SECRET_KEY")
TRIVIA_API = os.environ.get("TRIVIA_API")

def get_quiz(author, amount, category, difficulty, typeq):
  try:
    if amount and amount is not None and amount != "" and int(amount) <= 10:
      url = TRIVIA_API + "?amount=" + amount
    elif not amount or amount is None or amount == "":
      url = TRIVIA_API + "?amount=5"
    else:
      return "Error"
    if category and category is not None and category != "":
      url = url + "&category=" + category
    if difficulty and difficulty is not None and difficulty != "":
      url = url + "&difficulty=" + difficulty
    if typeq and typeq is not None and typeq != "":
      url = url + "&typeq=" + typeq
    response = requests.get(url)
    return insert_new_quiz(author, response.json())
  except:
    return "Error"

def insert_new_quiz(content):
  return 0



def check_temp_trivia_exists(): 
  fle = Path(TMP_DIR+'trivia.sqlite3')
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()

def create_empty_tables():
  check_temp_trivia_exists()
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'tournaments.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_create_quiz_query = """ CREATE TABLE IF NOT EXISTS Quiz(
            id INTEGER PRIMARY KEY,
            author VARCHAR(255) NOT NULL
        ); """

    cursor.execute(sqlite_create_quiz_query)    
    
    
    sqlite_create_questions_query = """ CREATE TABLE IF NOT EXISTS Questions(
            id INTEGER PRIMARY KEY,
            category VARCHAR(255) NOT NULL,
            type VARCHAR(255) NOT NULL,
            difficulty VARCHAR(255) NOT NULL,
            question INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            FOREIGN KEY (quiz_id)
              REFERENCES Quiz (id) 
        ); """

    cursor.execute(sqlite_create_questions_query)


    sqlite_create_answers_query = """ CREATE TABLE IF NOT EXISTS Answers(
            id INTEGER PRIMARY KEY,
            answers VARCHAR(255) NOT NULL,
            is_correct INTEGER NOT NULL,
            questions_id INTEGER NOT NULL,
            FOREIGN KEY (questions_id)
              REFERENCES Questions (id) 
        ); """

    cursor.execute(sqlite_create_answers_query)

    sqlite_create_user_answers_query = """ CREATE TABLE IF NOT EXISTS Answers(
            id INTEGER PRIMARY KEY,
            user VARCHAR(255) NOT NULL,
            user_id INTEGER NOT NULL,
            answer_id INTEGER NOT NULL,
            FOREIGN KEY (answer_id)
              REFERENCES Answers (id) 
        ); """

    cursor.execute(sqlite_create_user_answers_query)


  except sqlite3.Error as error:
    print("Failed to create tables", error)
  finally:
    if sqliteConnection:
        sqliteConnection.close()

def save_temp_quiz(author, content):  
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'tournaments.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_insert_quiz_query = """INSERT INTO Quiz
                          (author) 
                           VALUES 
                          (?)"""

    data_quiz_tuple = (content['author'])

    cursor.execute(sqlite_insert_quiz_query, data_quiz_tuple)

    quiz_id = cursor.lastrowid

    for result in content['results']:
      sqlite_insert_users_query = """INSERT INTO Questions
                            (category, type, difficulty, question, quiz_id) 
                            VALUES 
                            (?, ?, ?, ?)"""
      data_users_tuple = (result['category'], result['type'], result['difficulty'], result['question'], quiz_id)
      cursor.execute(sqlite_insert_users_query, data_users_tuple)


    sqliteConnection.commit()
    cursor.close()

  except sqlite3.Error as error:
    print("Failed to insert data into sqlite", error)
  finally:
    if sqliteConnection:
        sqliteConnection.close()
