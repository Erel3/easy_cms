from multiprocessing import Process
from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel

from bs4 import BeautifulSoup as Soup

import config

import telebot
import requests
import time

import signal
import sys

from .dbhelper import DBHelper
db = DBHelper()
db.setup()

bot = telebot.TeleBot(config.token, threaded=False)
sess = requests.session()
users = {}
clars = {}
messages = {}
contest_id = 0

def signal_handler(sig, frame):
        for user, _ in users.items():
            bot.send_message(user, "bot stopped")
        print("\nYou pressed Ctrl+C! Exiting.")
        sys.exit(0)

@bot.message_handler(commands=['secret', 's'])
def check_secret(message):
    if len(message.text.split(' ', 1)) > 1:
        if(message.text.split(' ', 1)[1] == config.secret):
            db.add_user(message.chat.id)
            bot.reply_to(message, "correct")
        else:
            bot.reply_to(message, "wrong secret")

def send_all(id):
    for user, _ in users.items():
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data='answer_yes'),
                   telebot.types.InlineKeyboardButton(text='No', callback_data='answer_no'))
        markup.add(telebot.types.InlineKeyboardButton(text='Answered in task description', callback_data='answer_aitd'))
        markup.add(telebot.types.InlineKeyboardButton(text='Invalid question', callback_data='answer_iq'),
                   telebot.types.InlineKeyboardButton(text='No comment', callback_data='answer_nc'))
        message = bot.send_message(user, "*{}* - {}\n{}\n".format(clars[id]["subject"], clars[id]["user"], clars[id]["text"]), parse_mode="Markdown", reply_markup=markup)
        messages[message.message_id] = id


def parse_cms():
    link = "http://{}/".format(config.hosts[0]["ip"])
    sess.auth = (config.awsaclogin, config.awsacpass)
    auth = sess.post(link+"aws")
    xsrf = sess.cookies["_xsrf"]
    login = sess.post(link+"aws/login", {"username": config.awslogin, "password": config.awspass, "_xsrf": xsrf})

    contest_questions = sess.get(link+"aws/contest/{}/questions".format(contest_id))
    soup = Soup(contest_questions.content, features="html.parser")
    for notif in soup.select("div.notification"):
        q_id = int(notif.select_one("form.reply_question_form").attrs['action'].split("/")[-2])
        if q_id in clars:
            continue
        user = notif.select_one("div.notification_timestamp").a.text
        subject = notif.select_one("div.notification_subject").text
        text = notif.select_one("div.notification_text").text
        answered = 'answered' in notif.attrs['class']
        answer = "" if not answered else notif.select("div.notification_text")[1].text
        ignored = 'ignored' in notif.attrs['class']
        clars[q_id] = {
            "id": q_id,
            "user": user,
            "subject": subject,
            "text": text,
            "answered": answered,
            "answer": answer,
            "ignored": ignored,
        }
        if not (answered or ignored):
            send_all(q_id)


def get_messages():
    updates = bot.get_updates(offset=(bot.last_update_id + 1), timeout=2)
    bot.process_new_updates(updates)


def start(id):
    global contest_id
    contest_id = id
    signal.signal(signal.SIGINT, signal_handler)
    print("Press Ctrl+C to exit")
    while True:
        try:
            get_messages()
        except SystemExit:
            raise
        except:
            pass
