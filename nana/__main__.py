import time
import logging
import importlib
import random
import sys
import traceback
import threading
import asyncio

import pyrogram
from pyrogram import Filters
from nana import app, Owner, log, Command, USERBOT_VERSION, get_self

from nana.modules import ALL_MODULES

try:
	from nana import TEST_DEVELOP
except ImportError:
	TEST_DEVELOP = False

BOT_RUNTIME = 0


loop = asyncio.get_event_loop()

async def get_runtime():
	return BOT_RUNTIME

async def reload_userbot():
	await app.start()
	for modul in ALL_MODULES:
		imported_module = importlib.import_module("nana.modules." + modul)
		importlib.reload(imported_module)

async def reinitial_restart():
	await get_self()

async def reboot():
	global BOT_RUNTIME
	importlib.reload(importlib.import_module("nana.modules"))
	from nana.modules import ALL_MODULES
	# await setbot.send_message(Owner, "Bot is restarting...")
	await app.restart()
	await reinitial_restart()
	# Reset global var
	BOT_RUNTIME = 0
	# Nana userbot
	for modul in ALL_MODULES:
		imported_module = importlib.import_module("nana.modules." + modul)
		if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
			imported_module.__MODULE__ = imported_module.__MODULE__
		importlib.reload(imported_module)
	# await setbot.send_message(Owner, "Restart successfully!")

async def restart_all():
	# Restarting and load all plugins
	asyncio.get_event_loop().create_task(reboot())

RANDOM_STICKERS = ["CAADAgAD6EoAAuCjggf4LTFlHEcvNAI", "CAADAgADf1AAAuCjggfqE-GQnopqyAI", "CAADAgADaV0AAuCjggfi51NV8GUiRwI"]

async def reinitial():
	await app.start()
	await get_self()
	await app.stop()

async def start_bot():
	# sys.excepthook = except_hook
	print("----- Checking user and bot... -----")
	await reinitial()
	print("----------- Check done! ------------")
	# Assistant bot
	# Nana userbot
	await app.start()
	for modul in ALL_MODULES:
		imported_module = importlib.import_module("nana.modules." + modul)
		if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
			imported_module.__MODULE__ = imported_module.__MODULE__
	log.info("-----------------------")
	log.info("Userbot modules: " + str(ALL_MODULES))
	log.info("-----------------------")
	log.info("Bot run successfully!")
	if TEST_DEVELOP:
		log.warning("Test is passed!")
	else:
		await app.idle()

if __name__ == '__main__':
	BOT_RUNTIME = int(time.time())
	loop.run_until_complete(start_bot())
