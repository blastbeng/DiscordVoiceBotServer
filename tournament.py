import random
import sqlite3
import os
from decimal import Decimal
from itertools import combinations
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TMP_DIR = os.environ.get("TMP_DIR")

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
  def __init__(self, author, author_image, guild_image, teamsize, name, description, image, users, teams, rounds):
      self.author       = author
      self.author_image = author_image
      self.guild_image  = guild_image
      self.teamsize     = teamsize
      self.name         = name
      self.description  = description
      self.image        = image
      self.users        = users
      self.teams        = teams
      self.rounds       = rounds

def generate_teams(tournamentUsersArray, team_size: int, user_size: int):
  
  team_names = [ "I Cessi",
          "Gli Stronzi",
          "I Brutti",
          "Le Merde",
          "Le Minchie",
          "Le Troie",
          "I Cazzi",
          "Le Pucchiacche",
          "I Pazzi Mentali",
          "I Luridi",
          "I Pezzenti",
          "Gli Analfabeti",
          "Gli Incapaci",
          "I Putridi",
          "Le Puttane",
          "I Piglianculo",
          "I Coglioni",
          "I Drogati",
          "I Masochisti",
          "I Sadici",
          "I Sadomasochisti",
          "Le Vulve",
          "I Laidi",
          "Gli Eunuchi",
          "I Succhiapalle",
          "Gli Eroinomani",
          "Le Guerriere Sailor",
          "Le Bestie di Satana",
          "I Buchi Spanati",
          "Gli incompetenti"]

  random.shuffle(tournamentUsersArray)

  tournamentTeamsArray = []

  index = 0
  while index < len(tournamentUsersArray):
    index_team = 0
    internalTournamentUsersArray = []
    while index_team < team_size:
      internalTournamentUsersArray.append(tournamentUsersArray[index])
      #if index < len(tournamentUsersArray):
      #else:      
      #  tournamentBot = TournamentUsers('0', 'Bot', '', 'Un bot stronzo')
      #  internalTournamentUsersArray.append(tournamentBot.__dict__)

      index_team += 1
      index += 1
    
    if team_size == 1:
      team_name = 0
    else:
      team_name = random.choice(team_names)
      team_names.remove(team_name)

    tournamentTeam = TournamentTeams(team_name, internalTournamentUsersArray)
    tournamentTeamsArray.append(tournamentTeam.__dict__) 
  return tournamentTeamsArray

def rSubset(arr, r):
  return list(combinations(arr, r))

def generate_rounds(tournamentTeamsArray):
  generated_teams_rounds = rSubset(tournamentTeamsArray, 2)

  tournamentRoundsArray = []

  index = 0
  while index < len(generated_teams_rounds):
    team_round = generated_teams_rounds[index]
    roundName = "Round " + str(index + 1)
    tournamentRounds = TournamentRounds(roundName, team_round)
    tournamentRoundsArray.append(tournamentRounds.__dict__)
    index += 1
  
  random.shuffle(tournamentRoundsArray)
  return tournamentRoundsArray

def populate_users(users_input, team_size: int, user_size: int):

  user_titles = [ "Cesso",
          "Stronzo",
          "Brutto",
          "Merda",
          "Minchia",
          "Troia",
          "Cazzo",
          "Pucchiacca",
          "Pazzo Mentale",
          "Lurido",
          "Pezzente",
          "Analfabeta",
          "Incapace",
          "Putrido",
          "Puttana",
          "Piglianculo",
          "Coglione",
          "Drogato",
          "Masochista",
          "Sadico",
          "Sadomasochista",
          "Vulva",
          "Laido",
          "Eunuco",
          "Succhiapalle",
          "Eroinomane",
          "Guerriera Sailor",
          "Bestia di Satana",
          "Buco Spanato",
          "Incompetente"]

  index = 0;
  bot_number = 0;

  index = 0
  while index < user_size:
    index += team_size
  
  bot_number = index - user_size

  tournamentUsersArray = []
  for user in users_input:
    user_title = random.choice(user_titles)
    user_titles.remove(user_title)
    tournamentUser = TournamentUsers(user['id'], user['username'], user['image'], user_title)
    tournamentUsersArray.append(tournamentUser.__dict__)

  index_bot = 0
  while index_bot < bot_number:
    tournamentBot = TournamentUsers('0', 'Bot', '', 'Un bot stronzo')
    tournamentUsersArray.append(tournamentBot.__dict__)
    index_bot += 1

  return tournamentUsersArray

def check_temp_tournament_exists(): 
  fle = Path(TMP_DIR+'/tournaments.sqlite3')
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()

def create_empty_tables():
  check_temp_tournament_exists()
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'/tournaments.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_create_tournaments_query = """ CREATE TABLE IF NOT EXISTS Tournaments(
            id INTEGER PRIMARY KEY,
            author VARCHAR(255) NOT NULL,
            author_image VARCHAR(255) NOT NULL,
            guild_image VARCHAR(255) NOT NULL,
            teamsize INTEGER NOT NULL,
            name VARCHAR(255) NOT NULL,
            description VARCHAR(255) NOT NULL,
            image VARCHAR(255) NOT NULL
        ); """

    cursor.execute(sqlite_create_tournaments_query)


    sqlite_create_users_query = """ CREATE TABLE IF NOT EXISTS Users(
            id INTEGER PRIMARY KEY,
            userid INTEGER NOT NULL,
            username VARCHAR(255) NOT NULL,
            image VARCHAR(255) NOT NULL,
            tournament_id INTEGER NOT NULL,
            FOREIGN KEY (tournament_id)
              REFERENCES Tournaments (id) 
        ); """

    cursor.execute(sqlite_create_users_query)

  except sqlite3.Error as error:
    print("Failed to create tables", error)
  finally:
    if sqliteConnection:
        sqliteConnection.close()


def save_temp_tournament(content):  
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'/tournaments.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_insert_tournaments_query = """INSERT INTO Tournaments
                          (author, author_image, guild_image, teamsize, name, description, image) 
                           VALUES 
                          (?, ?, ?, ?, ?, ?, ?)"""

    data_tournaments_tuple = (content['author'], 
                              content['author_image'], 
                              content['guild_image'], 
                              content['teamsize'],
                              content['name'],
                              content['description'],
                              content['image'])

    cursor.execute(sqlite_insert_tournaments_query, data_tournaments_tuple)

    tournament_id = cursor.lastrowid

    for user in content['users']:
      sqlite_insert_users_query = """INSERT INTO Users
                            (userid, username, image, tournament_id) 
                            VALUES 
                            (?, ?, ?, ?)"""
      data_users_tuple = (user['id'], user['username'], user['image'], tournament_id)
      cursor.execute(sqlite_insert_users_query, data_users_tuple)


    sqliteConnection.commit()
    cursor.close()

  except sqlite3.Error as error:
    print("Failed to insert data into sqlite", error)
  finally:
    if sqliteConnection:
        sqliteConnection.close()

def regen_tournament(author: str, name: str, description: str):
  tournament_data_set = None
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'/tournaments.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_select_query = """SELECT * from Tournaments WHERE author = ? AND name = ? AND description = ? ORDER BY ID DESC"""
    cursor.execute(sqlite_select_query, (author, name, description))
    records = cursor.fetchall()

    idtournament = 0

    for row in records:
      idtournament = row[0]
      author =       row[1]
      author_image = row[2]
      guild_image =  row[3]
      teamsize =     row[4]
      name =         row[5]
      description =  row[6]
      image =        row[7]

      if idtournament != 0:
        break

    cursor.close()


    if idtournament == 0:
      if sqliteConnection:
        sqliteConnection.close()
      return "Error"
    else:
      cursor_users = sqliteConnection.cursor()

      sqlite_select_users_query = """SELECT * from Users WHERE tournament_id = ?"""
      cursor_users.execute(sqlite_select_users_query, (idtournament,))
      records = cursor_users.fetchall()

      json_user_list = []

      for row in records:
        userid =         row[1]
        username =       row[2]
        image_user =     row[3]

        user_data_set = {
          "id":       userid, 
          "username":     username, 
          "image":        image_user
        }
        json_user_list.append(user_data_set)

      cursor_users.close()


      tournament_data_set = {
        "author":       author, 
        "author_image": author_image, 
        "guild_image":  guild_image, 
        "teamsize":     teamsize, 
        "name":         name, 
        "description":  description, 
        "image":        image,
        "users":        json_user_list
      }
  except sqlite3.Error as error:
    print("Failed to read data from sqlite table", error)
  finally:
    if sqliteConnection:
      sqliteConnection.close()

  if tournament_data_set is not None:
    return generate_tournament(tournament_data_set)
  else:
    return "Error"

def generate_tournament(content):
  
  save_temp_tournament(content)

  team_size = int(content['teamsize'])

  user_size = len(content['users'])

  tournamentUsersArray = populate_users(content['users'], team_size, user_size)

  tournamentTeamsArray = generate_teams(tournamentUsersArray, team_size, user_size)

  tournamentRoundsArray = generate_rounds(tournamentTeamsArray)

  tournament = TournamentInfo(content['author'],
                          content['author_image'],
                          content['guild_image'],
                          content['teamsize'],
                          content['name'],
                          content['description'],
                          content['image'],
                          tournamentUsersArray,
                          tournamentTeamsArray,
                          tournamentRoundsArray)

  dicted = tournament.__dict__

  return dicted