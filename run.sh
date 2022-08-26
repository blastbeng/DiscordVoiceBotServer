#/bin/sh
source .venv/bin/activate
FLASK_APP=./chatbot.py flask run --host=0.0.0.0
