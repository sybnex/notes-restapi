#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

from flask import Flask
from flask_restful import Api, Resource, reqparse

import os
import sys
import pickle
import logging
import requests
from uuid import uuid4

from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.utils.helpers import escape_markdown

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)-5s: %(message)s")

logger = logging.getLogger(__name__)

class MyApi(Api):
    @property
    def specs_url(self):
        """Monkey patch for HTTPS"""
        scheme = 'http' if '5000' in self.base_url else 'https'
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)

app = Flask(__name__)
api = MyApi(app)

notes = [
    {
        "name": "light",
        "data": "false"
    },
    {
        "name": "healthz",
        "data": "true"
    }
]

class Note(Resource):
    def get(self, name):
        for note in notes:
            if(name == note["name"]):
                return note, 200
        return "Note not found", 404

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("data")
        args = parser.parse_args()

        for note in notes:
            if(name == note["name"]):
                return "Note with name {} already exists".format(name), 400

        note = {
            "name": name,
            "data": args["data"]
        }
        notes.append(note)
        return note, 201

    def put(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("data")
        args = parser.parse_args()

        for note in notes:
            if(name == note["name"]):
                note["data"] = args["data"]
                return note, 200
        
        note = {
            "name": name,
            "data": args["data"]
        }
        notes.append(note)
        return note, 201

    def delete(self, name):
        global notes
        notes = [note for note in notes if note["name"] != name]
        return "{} is deleted.".format(name), 200
      
api.add_resource(Note, "/note/<string:name>")

# --- BOT ---
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def lighton(update, context):
    r = requests.put("https://notes.julina.ch/note/light?data=true")

def lightoff(update, context):
    r = requests.put("https://notes.julina.ch/note/light?data=false")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

if __name__ == '__main__':
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    token = os.environ["TELEGRAM_TOKEN"]
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("lighton",  lighton))
    dp.add_handler(CommandHandler("lightoff", lightoff))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Start flask
    app.run(host='0.0.0.0', threaded=True, debug=True)

