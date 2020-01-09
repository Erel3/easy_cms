from multiprocessing import Process
from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel

from bs4 import BeautifulSoup as Soup

import config

import telebot
import requests
import time
import traceback

import signal
import sys

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
            users[message.chat.id] = {}
            bot.delete_message(message.chat.id, message.message_id)
        else:
            bot.reply_to(message, "wrong secret")


@bot.message_handler(commands=['announcement', 'a'])
def announcement(message):
    if message.chat.id not in users:
        bot.reply_to(message, "please enter secret")
        return
    if len(message.text.split("\n")) < 2 or len(message.text.split("\n")[0].split(' ')) < 2:
        bot.reply_to(message, "please use the following format of announcement:\n/announcement subject\ntext")
        return
    subject = " ".join(message.text.split("\n")[0].split(' ')[1:])
    text = "\n".join(message.text.split("\n")[1:])

    link = "http://{}/".format(config.hosts[0]["ip"])
    sess.auth = (config.awsaclogin, config.awsacpass)
    auth = sess.post(link+"aws")
    xsrf = sess.cookies["_xsrf"]
    login = sess.post(link+"aws/login", {"username": config.awslogin, "password": config.awspass, "_xsrf": xsrf})
    print(login)
    a = sess.post(link+"aws/contest/{}/announcements/add".format(contest_id), {"subject": subject, "text": text, "_xsrf": xsrf})
    bot.reply_to(message, "done")


@bot.message_handler(func=lambda message: message.reply_to_message)
def answer_clar(message):
    if message.chat.id not in users:
        bot.reply_to(message, "please enter secret")
        return
    if message.reply_to_message.message_id not in messages:
        return
    clar_id = messages[message.reply_to_message.message_id]
    link = "http://{}/".format(config.hosts[0]["ip"])
    sess.auth = (config.awsaclogin, config.awsacpass)
    auth = sess.post(link+"aws")
    xsrf = sess.cookies["_xsrf"]
    login = sess.post(link+"aws/login", {"username": config.awslogin, "password": config.awspass, "_xsrf": xsrf})

    ans_link = link+"aws/contest/{}/question/{}/reply".format(contest_id, clar_id)
    ref = "/contest/{}/questions".format(contest_id)
    reply_question_quick_answer = "other"
    reply_question_text = message.text
    sess.post(ans_link, {"ref": ref,
                         "reply_question_quick_answer": reply_question_quick_answer,
                         "reply_question_text": reply_question_text,
                         "_xsrf": xsrf})

    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data='answer_yes'),
            telebot.types.InlineKeyboardButton(text='No', callback_data='answer_no'))
    markup.add(telebot.types.InlineKeyboardButton(text='Answered in task description', callback_data='answer_aitd'))
    markup.add(telebot.types.InlineKeyboardButton(text='Invalid question', callback_data='answer_iq'),
            telebot.types.InlineKeyboardButton(text='No comment', callback_data='answer_nc'))
    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.reply_to_message.message_id, text="*{}* - {}\n{}\n\n`@{}\n{}`\n".format(clars[clar_id]["subject"], clars[clar_id]["user"], clars[clar_id]["text"], message.from_user.username, message.text), reply_markup=markup, parse_mode="Markdown")
    except:
        pass
    bot.delete_message(message.chat.id, message.message_id)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.message.message_id not in messages:
        return
    if call.message.chat.id not in users:
        return
    clar_id = messages[call.message.message_id]
    try:
        link = "http://{}/".format(config.hosts[0]["ip"])
        sess.auth = (config.awsaclogin, config.awsacpass)
        auth = sess.post(link+"aws")
        xsrf = sess.cookies["_xsrf"]
        login = sess.post(link+"aws/login", {"username": config.awslogin, "password": config.awspass, "_xsrf": xsrf})

        ans_link = link+"aws/contest/{}/question/{}/reply".format(contest_id, clar_id)
        ref = "/contest/{}/questions".format(contest_id)
        reply_question_quick_answer = ""
        reply_question_text = ""

        if call.data == 'answer_yes':
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            markup.add(telebot.types.InlineKeyboardButton(text='☑️Yes', callback_data='answer_yes'),
                       telebot.types.InlineKeyboardButton(text='No', callback_data='answer_no'))
            markup.add(telebot.types.InlineKeyboardButton(text='Answered in task description', callback_data='answer_aitd'))
            markup.add(telebot.types.InlineKeyboardButton(text='Invalid question', callback_data='answer_iq'),
                       telebot.types.InlineKeyboardButton(text='No comment', callback_data='answer_nc'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="*{}* - {}\n{}\n\n`@{}`".format(clars[clar_id]["subject"], clars[clar_id]["user"], clars[clar_id]["text"], call.message.from_user.username), reply_markup=markup, parse_mode="Markdown")
            reply_question_quick_answer = "yes"
        if call.data == 'answer_no':
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data='answer_yes'),
                       telebot.types.InlineKeyboardButton(text='☑️No', callback_data='answer_no'))
            markup.add(telebot.types.InlineKeyboardButton(text='Answered in task description', callback_data='answer_aitd'))
            markup.add(telebot.types.InlineKeyboardButton(text='Invalid question', callback_data='answer_iq'),
                       telebot.types.InlineKeyboardButton(text='No comment', callback_data='answer_nc'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="*{}* - {}\n{}\n\n`@{}`".format(clars[clar_id]["subject"], clars[clar_id]["user"], clars[clar_id]["text"], call.message.from_user.username), reply_markup=markup, parse_mode="Markdown")
            reply_question_quick_answer = "no"
        if call.data == 'answer_aitd':
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data='answer_yes'),
                       telebot.types.InlineKeyboardButton(text='No', callback_data='answer_no'))
            markup.add(telebot.types.InlineKeyboardButton(text='☑️Answered in task description', callback_data='answer_aitd'))
            markup.add(telebot.types.InlineKeyboardButton(text='Invalid question', callback_data='answer_iq'),
                       telebot.types.InlineKeyboardButton(text='No comment', callback_data='answer_nc'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="*{}* - {}\n{}\n\n`@{}`".format(clars[clar_id]["subject"], clars[clar_id]["user"], clars[clar_id]["text"], call.message.from_user.username), reply_markup=markup, parse_mode="Markdown")
            reply_question_quick_answer = "answered"
        if call.data == 'answer_iq':
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data='answer_yes'),
                       telebot.types.InlineKeyboardButton(text='No', callback_data='answer_no'))
            markup.add(telebot.types.InlineKeyboardButton(text='Answered in task description', callback_data='answer_aitd'))
            markup.add(telebot.types.InlineKeyboardButton(text='☑️Invalid question', callback_data='answer_iq'),
                       telebot.types.InlineKeyboardButton(text='No comment', callback_data='answer_nc'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="*{}* - {}\n{}\n\n`@{}`".format(clars[clar_id]["subject"], clars[clar_id]["user"], clars[clar_id]["text"], call.message.from_user.username), reply_markup=markup, parse_mode="Markdown")
            reply_question_quick_answer = "invalid"
        if call.data == 'answer_nc':
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data='answer_yes'),
                       telebot.types.InlineKeyboardButton(text='No', callback_data='answer_no'))
            markup.add(telebot.types.InlineKeyboardButton(text='Answered in task description', callback_data='answer_aitd'))
            markup.add(telebot.types.InlineKeyboardButton(text='Invalid question', callback_data='answer_iq'),
                       telebot.types.InlineKeyboardButton(text='☑️No comment', callback_data='answer_nc'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="*{}* - {}\n{}\n\n`@{}`".format(clars[clar_id]["subject"], clars[clar_id]["user"], clars[clar_id]["text"], call.message.from_user.username), reply_markup=markup, parse_mode="Markdown")
            reply_question_quick_answer = "nocomment"
        sess.post(ans_link, {"ref": ref,
                             "reply_question_quick_answer": reply_question_quick_answer,
                             "reply_question_text": reply_question_text,
                             "_xsrf": xsrf})
    except:
        pass


def get_messages():
    updates = bot.get_updates(offset=(bot.last_update_id + 1), timeout=2)
    bot.process_new_updates(updates)


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


def send_all_error():
    for user, _ in users.items():
        bot.send_message(user, "*some error occured. please check!*", parse_mode="Markdown")



def start(id):
    global users
    global contest_id
    contest_id = id
    signal.signal(signal.SIGINT, signal_handler)
    print("Press Ctrl+C to exit")
    cycle = 0
    while True:
        try:
            if users and cycle % 10 == 0:
                parse_cms()
            get_messages()
        except SystemExit:
            raise
        except Exception:
            traceback.print_exc()
            send_all_error()
            pass
        except:
            pass
        cycle += 1
