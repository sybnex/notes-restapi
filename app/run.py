#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

from flask import Flask, url_for
from flask_restplus import Api, Resource, reqparse

import os
import sys
import logging
import requests

from telegram.ext import Updater, CommandHandler

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
api = MyApi(app, version="1.0", title="Noteservice API",
            description="A simple API")

notes = [{"name": "light", "data": "false"},
         {"name": "dinner", "data": "false"},
         {"name": "vacation", "data": "false"},
         {"name": "healthz", "data": "true"}]


@api.route("/<name>")
class Note(Resource):

    @api.doc(params={"name": "Name of the note"})
    @api.doc(responses={200: "Success",
                        404: "Not Found"})
    def get(self, name):
        for note in notes:
            if(name == note["name"]):
                return note, 200

        api.abort(404)

    @api.doc(params={"name": "Name of the note",
                     "data": "Content of note"})
    @api.doc(responses={200: "Success",
                        405: "Note already exist"})
    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("data")
        args = parser.parse_args()

        for note in notes:
            if(name == note["name"]):
                api.abort(405)

        note = {"name": name,
                "data": args["data"]}
        notes.append(note)
        return note, 200

    @api.doc(params={"name": "Name of the note",
                     "data": "Content of note"})
    @api.doc(responses={200: "Success",
                        201: "Note created"})
    def put(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("data")
        args = parser.parse_args()

        for note in notes:
            if(name == note["name"]):
                note["data"] = args["data"]
                return note, 200

        note = {"name": name,
                "data": args["data"]}
        notes.append(note)
        return note, 201

    @api.doc(params={"name": "Name of the note"})
    @api.doc(responses={200: "Success"})
    def delete(self, name):
        global notes
        notes = [note for note in notes if note["name"] != name]
        return {}, 200


# --- BOT ---
# Define few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error
def lighton(update, context):
    requests.put("https://notes.julina.ch/light?data=true")
    update.message.reply_text('Light on!')


def lightoff(update, context):
    requests.put("https://notes.julina.ch/light?data=false")
    update.message.reply_text('Light off!')


def dinneron(update, context):
    requests.put("https://notes.julina.ch/dinner?data=true")
    update.message.reply_text('Dinner on!')


def dinneroff(update, context):
    requests.put("https://notes.julina.ch/dinner?data=false")
    update.message.reply_text('Dinner off!')


def vacationon(update, context):
    requests.put("https://notes.julina.ch/vacation?data=true")
    update.message.reply_text('Dinner off!')


def vacationoff(update, context):
    requests.put("https://notes.julina.ch/vacation?data=false")
    update.message.reply_text('Dinner off!')


def status(update, context):
    light = requests.get("https://notes.julina.ch/light")
    dinner = requests.get("https://notes.julina.ch/dinner")
    text = "Light: %s, Dinner %s", light, dinner
    update.message.reply_text(text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    token = os.environ["TELEGRAM_TOKEN"]
    if token != "":
        logger.info("Starting Bot")
        updater = Updater(token, use_context=True)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("lighton",  lighton))
        dp.add_handler(CommandHandler("lightoff", lightoff))
        dp.add_handler(CommandHandler("dinneron",  dinneron))
        dp.add_handler(CommandHandler("dinneroff", dinneroff))
        dp.add_handler(CommandHandler("status", status))

        # log all errors
        dp.add_error_handler(error)

        # Start the Bot
        updater.start_polling()
    else:
        logger.error("Not token found to start Bot!")

    # Start flask
    app.run(host='0.0.0.0', threaded=True, debug=True)
