import os
import requests
import sqlite3
import traceback
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TMP_DIR = os.environ.get("TMP_DIR")
TRIVIA_API = os.environ.get("TRIVIA_API")

def get_quiz(author, amount, category, difficulty, typeq):
  try:
    if not author:
      return "Error"
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
    print(traceback.format_exc())
    return "Error"

def check_temp_trivia_exists(): 
  fle = Path(TMP_DIR+'trivia.sqlite3')
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()

def create_empty_tables():
  check_temp_trivia_exists()
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')
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
            answer VARCHAR(255) NOT NULL,
            is_correct INTEGER NOT NULL,
            questions_id INTEGER NOT NULL,
            FOREIGN KEY (questions_id)
              REFERENCES Questions (id) 
        ); """

    cursor.execute(sqlite_create_answers_query)

    sqlite_create_user_answers_query = """ CREATE TABLE IF NOT EXISTS UserAnswers(
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

def insert_new_quiz(author, content): 
  quiz_id = 0 
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_insert_quiz_query = """INSERT INTO Quiz
                          (author) 
                           VALUES 
                          (?)"""

    data_quiz_tuple = (author,)

    cursor.execute(sqlite_insert_quiz_query, data_quiz_tuple)

    quiz_id = cursor.lastrowid

    for result in content['results']:
      sqlite_insert_questions_query = """INSERT INTO Questions
                            (category, type, difficulty, question, quiz_id) 
                            VALUES 
                            (?, ?, ?, ?, ?)"""
      data_questions_tuple = (result['category'], result['type'], result['difficulty'], result['question'], quiz_id)
      cursor.execute(sqlite_insert_questions_query, data_questions_tuple)

      question_id = cursor.lastrowid

      sqlite_insert_answers_query = """INSERT INTO Answers
                            (answer, is_correct, questions_id) 
                            VALUES 
                            (?, ?, ?)"""
      data_correct_answer_tuple = (result['correct_answer'], 1, question_id)
      cursor.execute(sqlite_insert_answers_query, data_correct_answer_tuple)

      for incorrect_answer in result['incorrect_answers']:
        data_incorrect_answer_tuple = (incorrect_answer, 0, question_id)
        cursor.execute(sqlite_insert_answers_query, data_incorrect_answer_tuple)

    sqliteConnection.commit()
    cursor.close()

  except sqlite3.Error as error:
    print("Failed to insert data into sqlite", error)
  finally:
    if sqliteConnection:
        sqliteConnection.close()
  if quiz_id != 0:
    return get_quiz_json(quiz_id)
  else:
    return "Error"

def get_quiz_json(quiz_id):
  quiz_data_set = None
  try:

    author = None
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')
    cursor_quiz = sqliteConnection.cursor()

    sqlite_select_quiz_query = """SELECT author from Quiz WHERE id = ? ORDER BY ID DESC"""
    cursor_quiz.execute(sqlite_select_quiz_query, (quiz_id,))
    records_quiz = cursor_quiz.fetchall()
    for row in records_quiz:
      author = row[0]

    
    cursor_quiz.close()

    if not author:
      return "Error"

    cursor_questions = sqliteConnection.cursor()

    sqlite_select_questions_query = """SELECT * from Questions WHERE quiz_id = ? ORDER BY ID DESC"""
    cursor_questions.execute(sqlite_select_questions_query, (quiz_id,))
    records_questions = cursor_questions.fetchall()

    json_question_list = []

    for row in records_questions:
      idquestion =   row[0]
      category =     row[1]
      typeq =        row[2]
      difficulty =   row[3]
      question =     row[4]

      cursor_answers = sqliteConnection.cursor()

      sqlite_select_answers_query = """SELECT * from Answers WHERE questions_id = ? ORDER BY ID DESC"""
      cursor_answers.execute(sqlite_select_answers_query, (idquestion,))
      records_answers = cursor_answers.fetchall()

      json_answers_list = []

      for row in records_answers:
        idanswer =     row[0]
        answer =       row[1]
        is_correct =   row[2]
        
        answers_data_set = {
          "id":           idanswer, 
          "answer":       answer, 
          "is_correct":   is_correct
        }

        json_answers_list.append(answers_data_set)



      question_data_set = {
        "id":           idquestion, 
        "category":     category, 
        "type":         typeq, 
        "difficulty":   difficulty, 
        "question":     question,
        "answers":      json_answers_list
      }
      json_question_list.append(question_data_set)

      cursor_answers.close()

    cursor_questions.close()

    quiz_data_set = {
        "id":           quiz_id, 
        "author":       author, 
        "questions":    json_question_list
    }

  except sqlite3.Error as error:
    print("Failed to read data from sqlite table", error)
  finally:
    if sqliteConnection:
      sqliteConnection.close()

  return quiz_data_set

  
