from .db import Session, Chats, Messages, Clars

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
contest_id = 0


def notify_all(message):
  session = Session()
  chats = session.query(Chats).filter(Chats.is_active == True).all()
  for chat in chats:
    bot.send_message(chat.tg_id, message, parse_mode="Markdown")
  session.close()


def signal_handler(sig, frame):
  notify_all('bot stopped')
  print("\nYou pressed Ctrl+C! Exiting.")
  sys.exit(0)


@bot.message_handler(commands=['secret', 's'])
def check_secret(message):
  if len(message.text.split(' ', 1)) > 1:
    if(message.text.split(' ', 1)[1] == config.secret):
      session = Session()
      chat = session.query(Chats).filter(
          Chats.tg_id == message.chat.id).first()
      if chat == None:
        chat = Chats(message.chat.id)
        session.add(chat)
      else:
        chat.is_active = True
      session.commit()
      session.close()
      bot.delete_message(message.chat.id, message.message_id)
    else:
      bot.reply_to(message, "wrong secret")


# @bot.message_handler(commands=['announcement', 'a'])
# def announcement(message):
#   if message.chat.id not in users:
#     bot.reply_to(message, "please enter secret")
#     return
#   if len(message.text.split("\n")) < 2 or len(message.text.split("\n")[0].split(' ')) < 2:
#     bot.reply_to(
#         message, "please use the following format of announcement:\n/announcement subject\ntext")
#     return
#   subject = " ".join(message.text.split("\n")[0].split(' ')[1:])
#   text = "\n".join(message.text.split("\n")[1:])

#   link = "http://{}/".format(config.hosts[0]["ip"])
#   sess.auth = (config.awsaclogin, config.awsacpass)
#   auth = sess.post(link+"aws")
#   xsrf = sess.cookies["_xsrf"]
#   login = sess.post(
#       link+"aws/login", {"username": config.awslogin, "password": config.awspass, "_xsrf": xsrf})
#   print(login)
#   a = sess.post(link+"aws/contest/{}/announcements/add".format(contest_id),
#                 {"subject": subject, "text": text, "_xsrf": xsrf})
#   bot.reply_to(message, "done")


@bot.message_handler(func=lambda message: message.reply_to_message)
def answer_clar(message):
  session = Session()
  message_ = session.query(Messages).filter(
      Messages.tg_id == message.reply_to_message.message_id, Messages.chat_id == message.chat.id).first()
  chat = session.query(Chats).filter(
      Chats.tg_id == message.chat.id).first()
  print(message_, chat)
  if message_ == None or chat == None:
    return
  clar_id = message_.clar_id
  clar = session.query(Clars).filter(Clars.id == clar_id).one()

  link = "http://{}/".format(config.hosts[0]["ip"])
  sess.auth = (config.awsaclogin, config.awsacpass)
  auth = sess.post(link+"aws")
  xsrf = sess.cookies["_xsrf"]
  login = sess.post(
      link+"aws/login", {"username": config.awslogin, "password": config.awspass, "_xsrf": xsrf})

  ans_link = link + \
      "aws/contest/{}/question/{}/reply".format(contest_id, clar.cms_id)
  ref = "{}aws/contest/{}/questions".format(link, contest_id)
  reply_question_quick_answer = "other"
  reply_question_text = message.text

  sess.post(ans_link, {"reply_question_quick_answer": reply_question_quick_answer,
                       "reply_question_text": reply_question_text,
                       "_xsrf": xsrf}, headers={'Referer': ref})

  clar.needs_answer = False
  clar.answer = message.text
  clar.answered = True
  clar.answered_username = message.from_user.username

  session.add(clar)
  session.commit()
  session.close()
  update_messages(clar_id)

  bot.delete_message(message.chat.id, message.message_id)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
  session = Session()
  message = session.query(Messages).filter(
      Messages.tg_id == call.message.message_id, Messages.chat_id == call.message.chat.id).first()
  chat = session.query(Chats).filter(
      Chats.tg_id == call.message.chat.id).first()
  if message == None or chat == None:
    return
  clar_id = message.clar_id
  clar = session.query(Clars).filter(Clars.id == clar_id).one()

  if call.data == 'reanswer':
    clar.needs_answer = True
    session.add(clar)
    session.commit()
    session.close()
    update_messages(clar_id)
    return

  link = "http://{}/".format(config.hosts[0]["ip"])
  sess.auth = (config.awsaclogin, config.awsacpass)
  auth = sess.post(link+"aws")
  xsrf = sess.cookies["_xsrf"]
  login = sess.post(
      link+"aws/login", {"username": config.awslogin, "password": config.awspass, "_xsrf": xsrf})

  ans_link = link + \
      "aws/contest/{}/question/{}/reply".format(contest_id, clar.cms_id)
  ref = "/contest/{}/questions".format(contest_id)
  reply_question_quick_answer = ""
  reply_question_text = ""
  clar.needs_answer = False
  if call.data == 'answer_yes':
    clar.answer = "Yes"
    reply_question_quick_answer = "yes"
  if call.data == 'answer_no':
    clar.answer = "No"
    reply_question_quick_answer = "no"
  if call.data == 'answer_aitd':
    clar.answer = "Answered in task description"
    reply_question_quick_answer = "answered"
  if call.data == 'answer_iq':
    clar.answer = "Invalid question"
    reply_question_quick_answer = "invalid"
  if call.data == 'answer_nc':
    clar.answer = "No comment"
    reply_question_quick_answer = "nocomment"
  clar.answered = True
  clar.answered_username = call.from_user.username

  sess.post(ans_link, {"reply_question_quick_answer": reply_question_quick_answer,
                       "reply_question_text": reply_question_text,
                       "_xsrf": xsrf}, headers={'Referer': ref})

  session.add(clar)
  session.commit()
  session.close()
  update_messages(clar_id)


def get_messages():
  updates = bot.get_updates(offset=(bot.last_update_id + 1), timeout=60)
  bot.process_new_updates(updates)


def update_messages(id):
  session = Session()
  clar = session.query(Clars).filter(Clars.id == id).one()
  messages = session.query(Messages).filter(Messages.clar_id == id).all()
  markup = build_markup(clar)
  for message in messages:
    try:
      bot.edit_message_text(chat_id=message.chat_id, message_id=message.tg_id, text="*{}* - {}\n{}\n\n`@{}\n{}`\n".format(
          clar.subject, clar.user, clar.text, clar.answered_username, clar.answer), reply_markup=markup, parse_mode="Markdown")
    except:
      pass
  session.commit()
  session.close()


def build_markup(clar):
  markup = telebot.types.InlineKeyboardMarkup(row_width=2)
  if clar.needs_answer:
    markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data='answer_yes'),
               telebot.types.InlineKeyboardButton(text='No', callback_data='answer_no'))
    markup.add(telebot.types.InlineKeyboardButton(
        text='Answered in task description', callback_data='answer_aitd'))
    markup.add(telebot.types.InlineKeyboardButton(text='Invalid question', callback_data='answer_iq'),
               telebot.types.InlineKeyboardButton(text='No comment', callback_data='answer_nc'))
  else:
    markup.add(telebot.types.InlineKeyboardButton(
        text='Reanswer', callback_data='reanswer'))
  return markup


def send_clar(id):
  session = Session()
  clar = session.query(Clars).filter(Clars.id == id).one()
  chats = session.query(Chats).filter(Chats.is_active == True).all()
  markup = build_markup(clar)
  for chat in chats:
    message = bot.send_message(chat.tg_id, "*{}* - {}\n{}\n".format(
        clar.subject, clar.user, clar.text), parse_mode="Markdown", reply_markup=markup)
    session.add(Messages(chat.tg_id, message.message_id, id))
  session.commit()
  session.close()


def parse_cms():
  link = "http://{}/".format(config.hosts[0]["ip"])
  sess.auth = (config.awsaclogin, config.awsacpass)
  auth = sess.post(link+"aws")
  xsrf = sess.cookies["_xsrf"]
  login = sess.post(
      link+"aws/login", {"username": config.awslogin, "password": config.awspass, "_xsrf": xsrf})

  contest_questions = sess.get(
      link+"aws/contest/{}/questions".format(contest_id))
  soup = Soup(contest_questions.content, features="html.parser")

  for notif in soup.select("div.notification"):
    q_id = int(notif.select_one(
        "form.reply_question_form").attrs['action'].split("/")[-2])
    user = notif.select_one("div.notification_timestamp").a.text
    subject = notif.select_one("div.notification_subject").text
    text = notif.select_one("div.notification_text").text
    answered = 'answered' in notif.attrs['class']
    pre_answer = ("" if not answered else notif.select(
        "div.notification_subject")[1].text.strip())

    answer = ("" if not answered else notif.select(
        "div.notification_text")[1].text.strip())
    if pre_answer != "Not yet replied." and pre_answer != "Reply:":
      answer = pre_answer[7:]
    ignored = 'ignored' in notif.attrs['class']

    session = Session()
    clar = session.query(Clars).filter(Clars.cms_id == q_id).first()
    if clar != None:
      changed = False
      if clar.answer != answer or clar.answered != answered or clar.ignored != ignored:
        clar.answer = answer
        clar.answered = answered
        clar.ignored = ignored
        clar.needs_answer = False
        clar.answered_username = "aws"
        session.add(clar)
        changed = True
      session.commit()
      clar_id = clar.id
      session.close()
      if changed:
        update_messages(clar_id)
      continue
    clar = Clars(q_id, user, subject, text, answered, answer,
                 ignored, True if not answered and not ignored else False)
    session.add(clar)
    session.commit()
    clar_id = clar.id
    session.close()
    send_clar(clar_id)


def send_all_error():
  notify_all('*some error occured. please check!*')


def start(id):
  signal.signal(signal.SIGINT, signal_handler)
  print("Press Ctrl+C to exit")

  global contest_id
  contest_id = id

  notify_all('bot started')

  latest_update_milis = int(round(time.time() * 1000))
  update_delay_milis = 5 * 1000

  while True:

    current_milis = int(round(time.time() * 1000))
    if latest_update_milis + update_delay_milis > current_milis:
      time.sleep(1)
      continue
    latest_update_milis = current_milis

    try:
      print("u0")
      parse_cms()
      print("u1")
      get_messages()
      print("u2")

    except SystemExit:
      raise
    except Exception:
      traceback.print_exc()
      try:
        send_all_error()
      except:
        pass
      pass
    except:
      pass
