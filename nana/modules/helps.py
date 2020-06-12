import time
import math
import os
import pyrogram

from platform import python_version, uname
from nana import app, Command, DB_AVAIABLE, USERBOT_VERSION, BotUsername
from nana.helpers.parser import mention_markdown

from pyrogram import Filters


@app.on_message(Filters.user("self") & Filters.command(["help"], Command))
async def get_help(client, message):
	await message.edit("To get help, ask @NanaAssistantBot")

# @app.on_message(Filters.user("self") & Filters.command(["update"], Command))
async def get_update(client, message):
	await message.edit("Wut")
