import os
import logging
import image
import utils
import insults
import tournament
import requests
import json
import threading
import random
from flask import Flask, request, send_file, Response, jsonify
from flask_restx import Api, Resource, reqparse
from flask_apscheduler import APScheduler
from chatterbot.conversation import Statement
from flask_caching import Cache
from markovipy import MarkoviPy

logging.basicConfig(level=logging.INFO)

log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)


app = Flask(__name__)
class Config:    
    CACHE_TYPE = os.environ['CACHE_TYPE']
    CACHE_REDIS_HOST = os.environ['CACHE_REDIS_HOST']
    CACHE_REDIS_PORT = os.environ['CACHE_REDIS_PORT']
    CACHE_REDIS_DB = os.environ['CACHE_REDIS_DB']
    CACHE_REDIS_URL = os.environ['CACHE_REDIS_URL']
    CACHE_DEFAULT_TIMEOUT = os.environ['CACHE_DEFAULT_TIMEOUT']
    SCHEDULER_API_ENABLED = True

scheduler = APScheduler()

app.config.from_object(Config())
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
    #chatbot.get_response(text)
    threading.Timer(0, chatbot.get_response, args=[text]).start()
    return get_response_str(text)

@nstext.route('/repeat/learn/user/<string:user>/<string:text>')
class AudioRepeatLearnUserClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, user: str, text: str):
    if user in previousMessages:
      utils.learn(previousMessages[user], text, chatbot)
    previousMessages[user] = text
    return send_file(utils.get_tts(text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nstext.route('/ask/<string:text>')
class TextAskClass(Resource):
  def get (self, text: str):
    return get_response_str(chatbot.get_response(text).text)

@nstext.route('/ask/user/<string:user>/<string:text>')
class TextAskUserClass(Resource):
  def get (self, user: str, text: str):
    dolearn = False;
    if user not in previousMessages:
      dolearn=True
    chatbot_response = chatbot.get_response(text, learn=dolearn).text
    if user in previousMessages:
      utils.learn(previousMessages[user], text, chatbot)
    previousMessages[user] = chatbot_response
    return get_response_str(chatbot_response)

@nstext.route('/search/<string:text>')
class TextSearchClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, text: str):
    return get_response_str(utils.wiki_summary(text))

@nstext.route('/learn/<string:text>/<string:response>')
class TextLearnClass(Resource):
  @cache.cached(timeout=10, query_string=True)
  def get (self, text: str, response: str):
    utils.learn(text, response, chatbot)
    return "Ho imparato: " + text + " => " + response

@nstext.route('/insult')
class TextInsultClass(Resource):
  @api.expect(parserinsult)
  def get (self):
    sentence = insults.get_insults()
    #chatbot.get_response(sentence)
    threading.Timer(0, chatbot.get_response, args=[sentence]).start()
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
    #chatbot.get_response(text)
    threading.Timer(0, chatbot.get_response, args=[text]).start()
    return send_file(utils.get_tts(text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/repeat/learn/user/<string:user>/<string:text>')
class AudioRepeatLearnUserClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, user: str, text: str):
    if user in previousMessages:
      utils.learn(previousMessages[user], text, chatbot)
    previousMessages[user] = text
    return send_file(utils.get_tts(text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/ask/<string:text>')
class AudioAskClass(Resource):
  def get (self, text: str):
    return send_file(utils.get_tts(chatbot.get_response(text).text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/ask/user/<string:user>/<string:text>')
class AudioAskUserClass(Resource):
  def get (self, user: str, text: str):
    dolearn = False;
    if user not in previousMessages:
      dolearn=True
    chatbot_response = chatbot.get_response(text, learn=dolearn).text
    if user in previousMessages:
      utils.learn(previousMessages[user], text, chatbot)
    previousMessages[user] = chatbot_response
    return send_file(utils.get_tts(chatbot_response), attachment_filename='audio.wav', mimetype='audio/x-wav')

#def thread_wait(i):
#    time.sleep(i)

#@nsaudio.route('/ask/<int:countdown>/<string:text>')
#class AudioAskTimedClass(Resource):
#  def get (self, countdown: int, text: str):
#    if thread_wait and thread_wait.is_alive():
#      None
#    else:
#      thread_wait = threading.Thread(target=thread_wait, args=(countdown,))
#      thread_wait.start()
#      return send_file(utils.get_tts(chatbot.get_response(text).text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/search/<string:text>')
class AudioSearchClass(Resource):
  @cache.cached(timeout=10, query_string=True)
  def get (self, text: str):
    return send_file(utils.get_tts(utils.wiki_summary(text)), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/insult')
class AudioInsultClass(Resource):
  @api.expect(parserinsult)
  def get (self):
    sentence = insults.get_insults()
    #chatbot.get_response(sentence)
    threading.Timer(0, chatbot.get_response, args=[sentence]).start()
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
  def get(self):
    return get_response_str(utils.get_joke(""))

nsjokesaudio = api.namespace('jokes_audio', 'Accumulators Jokes Audio APIs')

@nsjokesaudio.route('/chuck')
class AudioChuckClass(Resource):
  def get(self):
    try:
      text = utils.get_joke("CHUCK_NORRIS")
      tts = utils.get_tts(text)
      return send_file(tts, attachment_filename='audio.wav', mimetype='audio/x-wav')
    except:
      return send_file(utils.get_tts("Riprova tra qualche secondo..."), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsjokesaudio.route('/random')
class AudioRandomJokeClass(Resource):
  def get(self):
    try:
      text = utils.get_joke("")
      tts = utils.get_tts(text)
      return send_file(tts, attachment_filename='audio.wav', mimetype='audio/x-wav')
    except:
      return send_file(utils.get_tts("Riprova tra qualche secondo..."), attachment_filename='audio.wav', mimetype='audio/x-wav')


nswebtext = api.namespace('reddit', 'Accumulators Reddit APIs')

@nswebtext.route('/search/<string:word>')
class TextRedditSearchClass(Resource):
  def get(self, word: str):
    return jsonify(reddit.search(word).__dict__)



nsimages = api.namespace('images', 'Accumulators Images APIs')

@nsimages.route('/search/<string:words>')
class AudioSearchClass(Resource):
  def get (self, words: str):
    threading.Timer(0, chatbot.get_response, args=[words]).start()
    bytes_img, attachment_filename, mimetype = image.search(words)
    return send_file(bytes_img, attachment_filename=attachment_filename, mimetype=mimetype)

#nswebtext = api.namespace('twitter', 'Accumulators Twitter APIs')

#@nswebtext.route('/search/random/byhashtag/<string:word>')
#class TextTwitterLocalSearchClass(Resource):
#  @cache.cached(timeout=1, query_string=True)
#  def get(self, word: str):
#    return jsonify(twitter.search_random(word, sched, 0).__dict__)

#@nswebtext.route('/search/random')
#class TextTwitterRandomSearchClass(Resource):
#  @cache.cached(timeout=1, query_string=True)
#  def get(self):
#    return jsonify(twitter.search_all_random())

#for tw_search in twitter.get_all_searches():
#  sched.add_job(twitter.scrape, 'interval', args=[tw_search,50], hours=2, id=tw_search)


nswebhook = api.namespace('webhooks', 'Accumulators Webhooks APIs')

@nswebhook.route('/test', methods=['POST'])
class WebhookTest(Resource):
  def webhook():
    if request.method == 'POST':
      print("Data received from Webhook is: ", request.json)
    return "Webhook received!"



nsutils = api.namespace('utils', 'AccumulatorsUtils APIs')

@nsutils.route('/sentence/extract')
class UtilsExtractSentences(Resource):
  def get (self):
    #return get_response_str(utils.extract_sentences_from_chatbot('./config/sentences.txt', None, True))
    utils.extract_sentences_from_chatbot('./config/sentences.txt', None, True, None)
    return send_file('./config/sentences.txt', attachment_filename='sentences.txt', mimetype='text/plain')

@nsutils.route('/sentence/random')
class UtilsRandomSentences(Resource):
  def get (self):
    return get_response_str(MarkoviPy('./config/sentences.txt', random.randint(2, 3)).generate_sentence())

@nsutils.route('/sentence/populate/<int:count>')
class UtilsPopulateSentences(Resource):
  def get (self, count: int):
    threading.Timer(0, utils.populate_new_sentences, args=[chatbot, count, None, False]).start()
    return "Starting thread populate_new_sentences with parameters: " + str(count) + ", None. Watch the logs."

@nsutils.route('/sentence/populate/parsed/<int:count>/<string:word>')
class UtilsPopulateSentencesParsed(Resource):
  def get (self, count: int, word: str):
    threading.Timer(0, utils.populate_new_sentences, args=[chatbot, count, word, False]).start()
    return "Starting thread populate_new_sentences with parameters: " + str(count) + ", " + word + ". Watch the logs."

@nsutils.route('/sentence/populate/parsed/api/<string:word>')
class UtilsPopulateSentencesParsedApi(Resource):
  def get (self, word: str):
    return get_response_str(utils.populate_new_sentences(chatbot, 5, word, True))

@nsutils.route('/sentence/populate/api')
class UtilsPopulateSentencesApi(Resource):
  def get (self):
    return get_response_str(utils.populate_new_sentences(chatbot, 5, None, True))

if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
  previousMessages = {}
  chatbot = utils.get_chatterbot('./config/trainfile.txt')
  utils.check_sentences_file_exists()
  utils.extract_sentences_from_chatbot('./config/sentences.txt', None, True, None)
  #twitter.create_empty_tables()
  tournament.create_empty_tables()
  cache.init_app(app)
  scheduler.init_app(app)
  scheduler.start()
  
  
  
@scheduler.task('interval', id='scrape_jokes', hours=72, misfire_grace_time=900)
def scrape_jokes():
  utils.scrape_jokes()
  
@scheduler.task('interval', id='extract_sentences', hours=24, misfire_grace_time=900)
def extract_sentences():
  utils.extract_sentences_from_chatbot('./config/sentences.txt', None, True, None)
  
@scheduler.task('cron', id='populate_sentences', hour=4, minute=10, second=0, misfire_grace_time=900)
def populate_sentences():
  print(utils.populate_new_sentences(chatbot, 1000, None, False))

if __name__ == '__main__':
  app.run()
