import logging
import utils
import insults
import tournament
from flask import Flask, request, send_file, Response, jsonify
from flask_restx import Api, Resource, reqparse
from chatterbot.conversation import Statement
logging.basicConfig(level=logging.ERROR)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

chatbot = utils.get_chatterbot(None, False)
tournament.create_empty_tables()

app = Flask(__name__)
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
  def get (self, text: str):
    return text

@nstext.route('/repeat/learn/<string:text>')
class TextRepeatLearnClass(Resource):
  def get (self, text: str):
    chatbot.get_response(text)
    return get_response_str(text)

@nstext.route('/ask/<string:text>')
class TextAskClass(Resource):
  def get (self, text: str):
    return get_response_str(chatbot.get_response(text).text)

@nstext.route('/search/<string:text>')
class TextSearchClass(Resource):
  def get (self, text: str):
    return get_response_str(utils.wiki_summary(text))

@nstext.route('/learn/<string:text>/<string:response>')
class TextLearnClass(Resource):
  def get (self, text: str, response: str):
    return get_response_str(utils.learn(text, response, chatbot))

@nstext.route('/insult')
class TextInsultClass(Resource):
  @api.expect(parserinsult)
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
class TextTournamentRegebClass(Resource): 
  def post (self):
    content = request.get_json()
    return jsonify(tournament.regen_tournament(content['author'], content['name'], content['description']));


nsaudio = api.namespace('chatbot_audio', 'Accumulators Chatbot TTS audio APIs')

@nsaudio.route('/repeat/<string:text>')
class AudioRepeatClass(Resource):
  def get (self, text: str):
    return send_file(utils.get_tts(text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/repeat/learn/<string:text>')
class AudioRepeatLearnClass(Resource):
  def get (self, text: str):
    chatbot.get_response(text)
    return send_file(utils.get_tts(text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/ask/<string:text>')
class AudioAskClass(Resource):
  def get (self, text: str):
    return send_file(utils.get_tts(chatbot.get_response(text).text), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/search/<string:text>')
class AudioSearchClass(Resource):
  def get (self, text: str):
    return send_file(utils.get_tts(utils.wiki_summary(text)), attachment_filename='audio.wav', mimetype='audio/x-wav')

@nsaudio.route('/insult')
class AudioInsultClass(Resource):
  @api.expect(parserinsult)
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

if __name__ == '__main__':
  app.run()
