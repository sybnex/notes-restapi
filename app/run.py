#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, url_for
from flask_restplus import Api, Resource, reqparse

import os
import sys
import logging
import requests
import schedule

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

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


notes = [{"name": "light", "data": {"value": False}},
         {"name": "dinner", "data": {"value": False}},
         {"name": "vacation", "data": {"value": False}},
         {"name": "weather", "data": {}},
         {"name": "healthz", "data": {"value": True}}]


def getWeather():
    url = "http://api.openweathermap.org/data/2.5/"
    url += "weather?id=7286216&units=metric&appid=%s" % weather_token
    response = requests.get(url, timeout=15)
    logging.info("Got weather data with code: %s" % response.status_code)
    requests.put("http://localhost:5000/weather",
                 json={"data": response.json()})


@api.route("/<name>")
class Note(Resource):

    @api.doc(params={"name": "Name of the note"})
    @api.doc(responses={200: "Success",
                        404: "Not Found"})
    def get(self, name):
        schedule.run_pending()
        for note in notes:
            if(name == note["name"]):
                return note["data"], 200

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
        return note["data"], 200

    @api.doc(params={"name": "Name of the note",
                     "data": "Content of note"})
    @api.doc(responses={200: "Success",
                        201: "Note created"})
    def put(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("data", type=dict)
        args = parser.parse_args()

        for note in notes:
            if(name == note["name"]):
                note["data"] = args["data"]
                return note, 200

        note = {"name": name,
                "data": args["data"]}
        notes.append(note)
        return note["data"], 201

    @api.doc(params={"name": "Name of the note"})
    @api.doc(responses={200: "Success"})
    def delete(self, name):
        global notes
        notes = [note for note in notes if note["name"] != name]
        return {}, 200


# --- BOT ---
# Define few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error
def setStatus(update, obj, status):
    switch = True if status == "on" else False
    requests.put("http://localhost:5000/%s" % obj,
                 json={"data": {"value": switch}})
    update.message.reply_text('%s %s!' % (obj, status))


def button(update, context):
    query = update.callback_query
    query.edit_message_text(text="Selected option: {}".format(query.data))


def light(update, context):
    if len(context.args[0]) == 0:
        keyboard = [[InlineKeyboardButton("On", callback_data='on'),
                     InlineKeyboardButton("Off", callback_data='off')],
                    [InlineKeyboardButton("Unknown", callback_data='3')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose:', reply_markup=reply_markup)
    else:
        setStatus(update, "light", context.args[0])


def dinner(update, context):
    setStatus(update, "dinner", context.args[0])


def vacation(update, context):
    setStatus(update, "vacation", context.args[0])


def status(update, context):
    light = requests.get("http://localhost:5000/light").json()
    dinner = requests.get("http://localhost:5000/dinner").json()
    text = "Light: %s, Dinner %s" % (light["value"], dinner["value"])
    update.message.reply_text(text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    weather_token = os.environ["WEATHER_TOKEN"]
    telegram_token = os.environ["TELEGRAM_TOKEN"]
    if telegram_token != "":
        logger.info("Found telegram token! Starting Bot ...")
        updater = Updater(telegram_token, use_context=True)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CallbackQueryHandler(button))
        dp.add_handler(CommandHandler("light",  light, pass_args=True))
        dp.add_handler(CommandHandler("dinner",  dinner, pass_args=True))
        dp.add_handler(CommandHandler("vacation",  vacation, pass_args=True))
        dp.add_handler(CommandHandler("status", status))

        # log all errors
        dp.add_error_handler(error)

        # Start the Bot
        updater.start_polling()
    else:
        logger.error("Not token found to start Bot!")

    # Get weather every 5 min.
    if weather_token != "":
        logger.info("Found weather token. Starting scheduler ...")
        schedule.every(1).minutes.do(getWeather)

    # Start flask
    app.run(host='0.0.0.0', threaded=True, debug=True)
