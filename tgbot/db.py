from sqlalchemy import Table, Column, Integer, Boolean, Float, String, MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///sqlite.db', echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Chats(Base):
  __tablename__ = 'chats'
  id = Column(Integer, primary_key=True)
  tg_id = Column(Integer)
  is_active = Column(Boolean)

  def __init__(self, id):
    self.tg_id = id
    self.is_active = True


class Messages(Base):
  __tablename__ = 'messages'
  id = Column(Integer, primary_key=True)
  chat_id = Column(Integer)
  tg_id = Column(Integer)
  clar_id = Column(Integer)

  def __init__(self, chat_id, id, clar_id):
    self.chat_id = chat_id
    self.tg_id = id
    self.clar_id = clar_id


class Clars(Base):
  __tablename__ = 'clars'
  id = Column(Integer, primary_key=True)
  cms_id = Column(Integer)
  user = Column(String)
  subject = Column(String)
  text = Column(String)
  answered = Column(Boolean)
  answer = Column(String)
  ignored = Column(Boolean)
  needs_answer = Column(Boolean)
  answered_username = Column(String)

  def __init__(self, id, user, subject, text, answered, answer, ignored, needs_answer):
    self.cms_id = id
    self.user = user
    self.subject = subject
    self.text = text
    self.answered = answered
    self.answer = answer
    self.ignored = ignored
    self.needs_answer = needs_answer
    self.answered_username = "aws"


Base.metadata.create_all(engine)

session = Session()
