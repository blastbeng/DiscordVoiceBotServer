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
import sys
from flask import Flask, request, send_file, Response, jsonify, render_template
from flask_restx import Api, Resource, reqparse
from flask_apscheduler import APScheduler
from chatterbot.conversation import Statement
from flask_caching import Cache
from markovipy import MarkoviPy
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TMP_DIR = os.environ.get("TMP_DIR")

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
parserinsult.add_argument("chatid", type=str)

def get_response_str(text: str):
    r = Response(response=text, status=200, mimetype="text/xml")
    r.headers["Content-Type"] = "text/xml; charset=utf-8"
    return r

def get_response_json(text: str):
    r = Response(response=text, status=200, mimetype="application/json")
    r.headers["Content-Type"] = "application/json; charset=utf-8"
    return r

@nstext.route('/repeat/<string:text>/<string:chatid>')
class TextRepeatClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, text: str, chatid: str):
    return text

@nstext.route('/repeat/learn/<string:text>/<string:chatid>')
class TextRepeatLearnClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, text: str, chatid: str):
    #get_chatbot_by_id(chatid).get_response(text)
    threading.Timer(0, get_chatbot_by_id(chatid).get_response, args=[text]).start()
    return get_response_str(text)

@nstext.route('/repeat/learn/user/<string:user>/<string:text>/<string:chatid>')
class AudioRepeatLearnUserClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, user: str, text: str, chatid: str):
    if user in previousMessages:
      utils.learn(previousMessages[user], text, get_chatbot_by_id(chatid))
    previousMessages[user] = text
    return send_file(utils.get_tts(text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nstext.route('/ask/<string:text>/<string:chatid>')
class TextAskClass(Resource):
  def get (self, text: str, chatid: str):
    return get_response_str(get_chatbot_by_id(chatid).get_response(text).text)

@nstext.route('/ask/user/<string:user>/<string:text>/<string:chatid>')
class TextAskUserClass(Resource):
  def get (self, user: str, text: str, chatid: str):
    dolearn = False;
    if user not in previousMessages:
      dolearn=True
    chatbot_response = get_chatbot_by_id(chatid).get_response(text, learn=dolearn).text
    if user in previousMessages:
      utils.learn(previousMessages[user], text, get_chatbot_by_id(chatid))
    previousMessages[user] = chatbot_response
    return get_response_str(chatbot_response)

@nstext.route('/search/<string:text>/<string:chatid>')
class TextSearchClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, text: str, chatid: str):
    return get_response_str(utils.wiki_summary(text))

@nstext.route('/learn/<string:text>/<string:response>/<string:chatid>')
class TextLearnClass(Resource):
  @cache.cached(timeout=10, query_string=True)
  def get (self, text: str, response: str, chatid: str):
    utils.learn(text, response, get_chatbot_by_id(chatid))
    return "Ho imparato: " + text + " => " + response

@nstext.route('/insult')
class TextInsultClass(Resource):
  @api.expect(parserinsult)
  def get (self):
    sentence = insults.get_insults()
    #get_chatbot_by_id(chatid).get_response(sentence)
    chatid = request.args.get("chatid")
    threading.Timer(0, get_chatbot_by_id(chatid).get_response, args=[sentence]).start()
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

@nsaudio.route('/repeat/<string:text>/<string:chatid>')
class AudioRepeatClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, text: str, chatid: str):
    return send_file(utils.get_tts(text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/repeat/learn/<string:text>/<string:chatid>')
class AudioRepeatLearnClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, text: str, chatid: str):
    #get_chatbot_by_id(chatid).get_response(text)
    threading.Timer(0, get_chatbot_by_id(chatid).get_response, args=[text]).start()
    return send_file(utils.get_tts(text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/repeat/learn/user/<string:user>/<string:text>/<string:chatid>')
class AudioRepeatLearnUserClass(Resource):
  @cache.cached(timeout=3000, query_string=True)
  def get (self, user: str, text: str, chatid: str):
    if user in previousMessages:
      utils.learn(previousMessages[user], text, get_chatbot_by_id(chatid))
    previousMessages[user] = text
    return send_file(utils.get_tts(text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/ask/<string:text>/<string:chatid>')
class AudioAskClass(Resource):
  def get (self, text: str, chatid: str):
    return send_file(utils.get_tts(get_chatbot_by_id(chatid).get_response(text).text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/ask/user/<string:user>/<string:text>/<string:chatid>')
class AudioAskUserClass(Resource):
  def get (self, user: str, text: str, chatid: str):
    dolearn = False;
    if user not in previousMessages:
      dolearn=True
    chatbot_response = get_chatbot_by_id(chatid).get_response(text, learn=dolearn).text
    if user in previousMessages:
      utils.learn(previousMessages[user], text, get_chatbot_by_id(chatid))
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
#      return send_file(utils.get_tts(get_chatbot_by_id(chatid).get_response(text).text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/search/<string:text>/<string:chatid>')
class AudioSearchClass(Resource):
  @cache.cached(timeout=10, query_string=True)
  def get (self, text: str, chatid: str):
    return send_file(utils.get_tts(utils.wiki_summary(text)), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/insult')
class AudioInsultClass(Resource):
  @api.expect(parserinsult)
  def get (self):
    sentence = insults.get_insults()
    #get_chatbot_by_id(chatid).get_response(sentence)
    chatid = request.args.get("chatid")
    threading.Timer(0, get_chatbot_by_id(chatid).get_response, args=[sentence]).start()
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
    #threading.Timer(0, get_chatbot_by_id(chatid).get_response, args=[words]).start()
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


#nswebhook = api.namespace('webhooks', 'Accumulators Webhooks APIs')

#@nswebhook.route('/test', methods=['POST'])
#class WebhookTest(Resource):
#  def webhook():
#    if request.method == 'POST':
#      print("Data received from Webhook is: ", request.json)
#    return "Webhook received!"



nsutils = api.namespace('utils', 'AccumulatorsUtils APIs')

@nsutils.route('/sentence/populate/<int:count>/<string:chatid>')
class UtilsPopulateSentences(Resource):
  def get (self, count: int, chatid: str):
    threading.Timer(0, utils.populate_new_sentences, args=[get_chatbot_by_id(chatid), count, None, False]).start()
    return "Starting thread populate_new_sentences with parameters: " + str(count) + ", None. Watch the logs."

@nsutils.route('/sentence/populate/parsed/<int:count>/<string:word>/<string:chatid>')
class UtilsPopulateSentencesParsed(Resource):
  def get (self, count: int, word: str, chatid: str):
    threading.Timer(0, utils.populate_new_sentences, args=[get_chatbot_by_id(chatid), count, word, False]).start()
    return "Starting thread populate_new_sentences with parameters: " + str(count) + ", " + word + ". Watch the logs."

@nsutils.route('/sentence/populate/parsed/api/<string:word>/<string:chatid>')
class UtilsPopulateSentencesParsedApi(Resource):
  def get (self, word: str, chatid: str):
    return get_response_str(utils.populate_new_sentences(get_chatbot_by_id(chatid), 5, word, True))

@nsutils.route('/sentence/populate/api/<string:chatid>')
class UtilsPopulateSentencesApi(Resource):
  def get (self, chatid: str):
    return get_response_str(utils.populate_new_sentences(get_chatbot_by_id(chatid), 5, None, True))
	
@nsutils.route('/upload/trainfile/json')
class UtilsTrainFile(Resource):
  def post (self):    
    try:
      chatid = request.form.get("chatid")
      threading.Timer(0, utils.train_json, args=[request.get_json(), get_chatbot_by_id(chatid)]).start()
      return get_response_str("Done. Watch the logs for errors.")
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      return utils.empty_template_trainfile_json()
	
@nsutils.route('/upload/trainfile/txt')
class UtilsTrainFile(Resource):
  def post (self):
    try:
      chatid = request.form.get("chatid")
      trf=request.files['trainfile']
      if not trf and allowed_file(trf):
        return get_response_str("Error! Please upload a trainfile.txt")
      else:
        trainfile=TMP_DIR + '/' + utils.get_random_string(24) + ".txt"
        trf.save(trainfile)
        threading.Timer(0, utils.train_txt, args=[trainfile, get_chatbot_by_id(chatid), request.form.get("language")]).start()
        return get_response_str("Done. Watch the logs for errors.")
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      return get_response_str("Error! Please upload a trainfile.txt")

@app.route('/upload')
def upload_file():
   return render_template('upload.html')

def get_chatbot_by_id(chatid: str):
  if chatid not in chatbots_dict:
    chatbots_dict[chatid] = utils.get_chatterbot(chatid, os.environ['TRAIN'] == "True")
  return chatbots_dict[chatid]

if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
  previousMessages = {}
  chatbots_dict = {}
  #chatbot = utils.get_chatterbot(os.environ['TRAIN'] == "True")
  #twitter.create_empty_tables()
  tournament.create_empty_tables()
  cache.init_app(app)
  scheduler.init_app(app)
  scheduler.start()
  
  
  
@scheduler.task('interval', id='scrape_jokes', hours=72, misfire_grace_time=900)
def scrape_jokes():
  utils.scrape_jokes()
  
#@scheduler.task('cron', id='populate_sentences', hour=4, minute=10, second=0, misfire_grace_time=900)
#def populate_sentences():
#  print(utils.populate_new_sentences(chatbot, 1000, None, False))

if __name__ == '__main__':
  app.run()
