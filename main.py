import os
import logging
import utils
import insults
import tournament
import requests
import json
from flask import Flask, request, send_file, Response, jsonify
from flask_restx import Api, Resource, reqparse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from chatterbot.conversation import Statement
from flask_caching import Cache
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(level=logging.ERROR)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

chatbot = utils.get_chatterbot(None, False)
tournament.create_empty_tables()

executors = {
    'default': ThreadPoolExecutor(16),
    'processpool': ProcessPoolExecutor(4)
}

sched = BackgroundScheduler(timezone='Europe/Rome', executors=executors)


app = Flask(__name__)
config = {    
    "CACHE_TYPE" : os.environ['CACHE_TYPE'],
    "CACHE_REDIS_HOST" : os.environ['CACHE_REDIS_HOST'],
    "CACHE_REDIS_PORT" : os.environ['CACHE_REDIS_PORT'],
    "CACHE_REDIS_DB" : os.environ['CACHE_REDIS_DB'],
    "CACHE_REDIS_URL" : os.environ['CACHE_REDIS_URL'],
    "CACHE_DEFAULT_TIMEOUT" : os.environ['CACHE_DEFAULT_TIMEOUT']
}

app.config.from_mapping(config)
cache = Cache(app)
api = Api(app)

nstext = api.namespace('chatbot_text', 'Accumulators Chatbot Text APIs')

parserinsult = reqparse.RequestParser()
parserinsult.add_argument("text", type=str)

def get_response_str(text: str):
    r = Response(response=text, status=200, mimetype="text/xml")
    r.headers["Content-Type"] = "text/xml; charset=utf-8"
    return r

def get_response_json(text: str):
    r = Response(response=text, status=200, mimetype="application/json")
    r.headers["Content-Type"] = "application/json; charset=utf-8"
    return r

@nstext.route('/repeat/<string:text>')
class TextRepeatClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, text: str):
    return text

@nstext.route('/repeat/learn/<string:text>')
class TextRepeatLearnClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, text: str):
    chatbot.get_response(text)
    return get_response_str(text)

@nstext.route('/ask/<string:text>')
class TextAskClass(Resource):
  @cache.cached(timeout=1, query_string=True)
  def get (self, text: str):
    return get_response_str(chatbot.get_response(text).text)

@nstext.route('/search/<string:text>')
class TextSearchClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, text: str):
    return get_response_str(utils.wiki_summary(text))

@nstext.route('/learn/<string:text>/<string:response>')
class TextLearnClass(Resource):
  @cache.cached(timeout=10, query_string=True)
  def get (self, text: str, response: str):
    return get_response_str(utils.learn(text, response, chatbot))

@nstext.route('/insult')
class TextInsultClass(Resource):
  @api.expect(parserinsult)
  @cache.cached(timeout=1, query_string=True)
  def get (self):
    sentence = insults.get_insults()
    chatbot.get_response(sentence)
    text = request.args.get("text")
    if text and text != '' and text != 'none':
      sentence = text + " " + sentence
    return sentence


@nstext.route('/tournament')
class TextTournamentClass(Resource): 
  def post (self):
    return jsonify(tournament.generate_tournament(request.get_json()));

@nstext.route('/tournament/regen')
class TextTournamentRegenClass(Resource): 
  def post (self):
    content = request.get_json()
    return jsonify(tournament.regen_tournament(content['author'], content['name'], content['description']));


nsaudio = api.namespace('chatbot_audio', 'Accumulators Chatbot TTS audio APIs')

@nsaudio.route('/repeat/<string:text>')
class AudioRepeatClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, text: str):
    return send_file(utils.get_tts(text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/repeat/learn/<string:text>')
class AudioRepeatLearnClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, text: str):
    chatbot.get_response(text)
    return send_file(utils.get_tts(text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/ask/<string:text>')
class AudioAskClass(Resource):
  @cache.cached(timeout=1, query_string=True)
  def get (self, text: str):
    return send_file(utils.get_tts(chatbot.get_response(text).text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/search/<string:text>')
class AudioSearchClass(Resource):
  @cache.cached(timeout=10, query_string=True)
  def get (self, text: str):
    return send_file(utils.get_tts(utils.wiki_summary(text)), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/insult')
class AudioInsultClass(Resource):
  @api.expect(parserinsult)
  @cache.cached(timeout=10, query_string=True)
  def get (self):
    sentence = insults.get_insults()
    chatbot.get_response(sentence)
    text = request.args.get("text")
    if text and text != '' and text != 'none':
      sentence = text + " " + sentence
    return send_file(utils.get_tts(sentence), attachment_filename='audio.wav', mimetype='audio/x-wav')


nsmusic = api.namespace('chatbot_music', 'Accumulators Chatbot Music APIs')

parserurl = reqparse.RequestParser()
parserurl.add_argument("url", type=str)

@nsmusic.route('/youtube/get')
class YoutubeGetClass(Resource):
  @api.expect(parserurl)
  def get(self):
    url = request.args.get("url")
    audio = utils.get_youtube_audio(url)
    return send_file(audio, attachment_filename='audio.mp3', mimetype='audio/mp3')

@nsmusic.route('/youtube/info')
class YoutubeInfoClass(Resource):
  @api.expect(parserurl)
  def get(self):
    url = request.args.get("url")
    return utils.get_youtube_info(url)

parsersearch = reqparse.RequestParser()
parsersearch.add_argument("text", type=str)
parsersearch.add_argument("onevideo", type=str)

@nsmusic.route('/youtube/search')
class YoutubeSearchClass(Resource):
  @api.expect(parsersearch)
  def get(self):
    text = request.args.get("text")
    onevideo = request.args.get("onevideo")
    return utils.search_youtube_audio(text, bool(onevideo))

nsjokestext = api.namespace('jokes_text', 'Accumulators Jokes APIs')

@nsjokestext.route('/chuck')
class TextChuckClass(Resource):
  @cache.cached(timeout=1)
  def get(self):
    return get_response_str(utils.get_joke("CHUCK_NORRIS"))

@nsjokestext.route('/random')
class TextRandomJokeClass(Resource):
  @cache.cached(timeout=1)
  def get(self):
    return get_response_str(utils.get_joke(""))

nsjokesaudio = api.namespace('jokes_audio', 'Accumulators Jokes Audio APIs')

@nsjokesaudio.route('/chuck')
class AudioChuckClass(Resource):
  @cache.cached(timeout=1)
  def get(self):
    try:
      text = utils.get_joke("CHUCK_NORRIS")
      tts = utils.get_tts(text)
      return send_file(tts, attachment_filename='audio.wav', mimetype='audio/x-wav')
    except:
      return send_file(utils.get_tts("Riprova tra qualche secondo..."), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsjokesaudio.route('/random')
class AudioRandomJokeClass(Resource):
  @cache.cached(timeout=1)
  def get(self):
    try:
      text = utils.get_joke("")
      tts = utils.get_tts(text)
      return send_file(tts, attachment_filename='audio.wav', mimetype='audio/x-wav')
    except:
      return send_file(utils.get_tts("Riprova tra qualche secondo..."), attachment_filename='audio.wav', mimetype='audio/x-wav')

def scrape_jokes():
  utils.scrape_jokes()

sched.add_job(scrape_jokes, 'interval', hours=12)

if __name__ == '__main__':
  sched.start()
  cache.init_app(app)
  app.run()
