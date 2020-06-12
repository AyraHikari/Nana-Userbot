import logging
import os
import sys
import re
import requests

from pyrogram import Client, errors
from pydrive.auth import GoogleAuth
from telegraph import Telegraph

# Postgresql
import threading

from sqlalchemy import create_engine, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import func, distinct, Column, String, UnicodeText, Integer

# logging
# 
# -> Advanced logging, for debugging purposes
# LOG_FORMAT = "[%(asctime)s.%(msecs)03d] %(filename)s:%(lineno)s %(levelname)s: %(message)s"
# logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
# 
ENV = bool(os.environ.get('ENV', False))
if ENV:
	TEST_DEVELOP = bool(os.environ.get('TEST_DEVELOP', False))
else:
	try:
		from nana.config import Development as Config
	except ModuleNotFoundError:
		logging.basicConfig(level=logging.INFO)
		log = logging.getLogger()
		log.error("You need to place config.py in nana dir!")
		quit(1)
	TEST_DEVELOP = Config.TEST_MODE

if TEST_DEVELOP:
	logging.basicConfig(level=logging.WARNING)
	log = logging.getLogger()
	log.warning("Testing mode activated!")
else:
	logging.basicConfig(level=logging.INFO)
	log = logging.getLogger()

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    log.error("You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting.")
    quit(1)

USERBOT_VERSION = "0.4.2 (Simple edition)"

OFFICIAL_BRANCH = ('master', 'dev')
REPOSITORY = "https://github.com/AyraHikari/Nana-Userbot"
RANDOM_STICKERS = ["CAADAgAD6EoAAuCjggf4LTFlHEcvNAI", "CAADAgADf1AAAuCjggfqE-GQnopqyAI", "CAADAgADaV0AAuCjggfi51NV8GUiRwI"]

APP_SESSION = "nana/session/Nana"

if ENV:
	# Version
	lang_code = os.environ.get('lang_code', "en")
	device_model = os.environ.get('device_model', "PC")
	app_version = "💝 Nana v{}".format(USERBOT_VERSION)
	system_version = os.environ.get('system_version', "Linux")

	# Must be filled
	api_id = os.environ.get('api_id', None)
	api_hash = os.environ.get('api_hash', None)

	# Session
	USERBOT_SESSION = os.environ.get('USERBOT_SESSION', None)

	# Required for some features
	# Set temp var for load later
	Owner = 0
	OwnerName = ""
	OwnerUsername = ""
	BotID = 0
	BotName = ""
	BotUsername = ""
	# From config
	Command = os.environ.get("Command", "! . - ^").split()
	NANA_WORKER = int(os.environ.get('NANA_WORKER', 8))

	# Write google api strings
	Drivestr = os.environ.get("GOOGLE_API_TEXT", "")
	if Drivestr:
		open("client_secrets.json", "w").write(str(Drivestr))

	# Bitly API
	BITLY_API = os.environ.get("BITLY_API", "")
	lydia_API = os.environ.get("lydia_API", "")

	try:
		TEST_DEVELOP = bool(os.environ.get('TEST_DEVELOP', False))
		if TEST_DEVELOP:
			APP_SESSION = os.environ.get('APP_SESSION', None)
		else:
			raise AttributeError
	except AttributeError:
		pass

	# APIs
	thumbnail_API = os.environ.get('thumbnail_API', None)
	screenshotlayer_API = os.environ.get('screenshotlayer_API', None)

	# LOADER
	USERBOT_LOAD = os.environ.get("USERBOT_LOAD", "").split()
	USERBOT_NOLOAD = os.environ.get("USERBOT_NOLOAD", "").split()

	DATABASE_URL = os.environ.get('DATABASE_URL', "postgres://username:password@localhost:5432/database")
	REMINDER_UPDATE = bool(os.environ.get('REMINDER_UPDATE', True))
	TEST_MODE = bool(os.environ.get('TEST_MODE', False))
else:

	# Version
	lang_code = Config.lang_code
	device_model = Config.device_model
	app_version = "💝 Nana v{}".format(USERBOT_VERSION)
	system_version = Config.system_version

	# Must be filled
	api_id = Config.api_id
	api_hash = Config.api_hash

	# Session
	USERBOT_SESSION = Config.USERBOT_SESSION

	# Required for some features
	# Set temp var for load later
	Owner = 0
	OwnerName = ""
	OwnerUsername = ""
	BotID = 0
	BotName = ""
	BotUsername = ""
	# From config
	Command = Config.Command
	NANA_WORKER = Config.NANA_WORKER

	# Write google api strings
	Drivestr = Config.GOOGLE_API_TEXT
	if Drivestr:
		open("client_secrets.json", "w").write(str(Drivestr))

	# Bitly API
	BITLY_API = Config.BITLY_API
	lydia_API = Config.lydia_API

	try:
		TEST_DEVELOP = Config.TEST_DEVELOP
		if TEST_DEVELOP:
			APP_SESSION = Config.APP_SESSION
		else:
			raise AttributeError
	except AttributeError:
		pass

	# APIs
	thumbnail_API = Config.thumbnail_API
	screenshotlayer_API = Config.screenshotlayer_API

	# LOADER
	USERBOT_LOAD = Config.USERBOT_LOAD
	USERBOT_NOLOAD = Config.USERBOT_NOLOAD

	DATABASE_URL = Config.DATABASE_URL
	REMINDER_UPDATE = Config.REMINDER_UPDATE
	TEST_MODE = Config.TEST_MODE

if USERBOT_SESSION:
	APP_SESSION = USERBOT_SESSION

gauth = GoogleAuth()

DB_AVAIABLE = False

# Postgresql
def mulaisql() -> scoped_session:
	global DB_AVAIABLE
	engine = create_engine(DATABASE_URL, client_encoding="utf8")
	BASE.metadata.bind = engine
	try:
		BASE.metadata.create_all(engine)
	except exc.OperationalError:
		DB_AVAIABLE = False
		return False
	DB_AVAIABLE = True
	return scoped_session(sessionmaker(bind=engine, autoflush=False))

async def get_self():
	global Owner, OwnerName, OwnerUsername, AdminSettings
	getself = await app.get_me()
	Owner = getself.id
	if getself.last_name:
		OwnerName = getself.first_name + " " + getself.last_name
	else:
		OwnerName = getself.first_name
	OwnerUsername = getself.username

BASE = declarative_base()
SESSION = mulaisql()

app = Client(APP_SESSION, api_id=api_id, api_hash=api_hash, app_version=app_version, device_model=device_model, system_version=system_version, lang_code=lang_code, workers=NANA_WORKER, test_mode=TEST_MODE)

telegraph = Telegraph()
telegraph.create_account(short_name='Nana Userbot')
