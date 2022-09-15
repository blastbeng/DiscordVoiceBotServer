import sys
import os
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_KEY = os.environ.get("REDDIT_API_KEY")
API_SECRET = os.environ.get("REDDIT_API_SECRET")
SUBREDDITS = os.environ.get("SUBREDDITS").split(",")

class Post():
  def __init__(self, text, content, content_type):
      self.text = text
      self.content = content
      self.content_type = content_type

reddit = praw.Reddit(
    client_id=API_KEY,
    client_secret=API_SECRET,
    user_agent="Udoo_docker_instance",
)

def search(words: str):
    try:
        for submission in reddit.subreddit("all").search(words):
            print(submission.title)
    except Esception as error:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Failed to scrape from reddit", error)
        print(exc_type, fname, exc_tb.tb_lineno)
    return Post("TODO", "TODO", "TODO")