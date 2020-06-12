import os, requests, html, time

from bs4 import BeautifulSoup

from pyrogram import Filters, InlineKeyboardMarkup, InlineKeyboardButton

from nana import app, Owner, OwnerName, Command, DB_AVAIABLE
from nana.helpers.parser import mention_markdown, escape_markdown
from nana.helpers.msg_types import Types, get_message_type
if DB_AVAIABLE:
	from nana.modules.database.afk_db import set_afk, get_afk


__MODULE__ = "AFK"

# Set priority to 11 and 12
MENTIONED = []
AFK_RESTIRECT = {}
DELAY_TIME = 60 # seconds

@app.on_message(Filters.user("self") & (Filters.command(["afk"], Command) | Filters.regex("^brb ")))
async def afk(client, message):
	if not DB_AVAIABLE:
		await message.edit("Your database is not avaiable!")
		return
	if len(message.text.split()) >= 2:
		set_afk(True, message.text.split(None, 1)[1])
		await message.edit("{} is now AFK!\nBecause of {}".format(mention_markdown(message.from_user.id, message.from_user.first_name), message.text.split(None, 1)[1]))
		await client.send_message(Owner, "You are now AFK!\nBecause of {}".format(message.text.split(None, 1)[1]))
	else:
		set_afk(True, "")
		await message.edit("{} is now AFK!".format(mention_markdown(message.from_user.id, message.from_user.first_name)))
		await client.send_message(Owner, "You are now AFK!")
	await message.stop_propagation()


@app.on_message(Filters.mentioned & ~Filters.bot, group=12)
async def afk_mentioned(client, message):
	if not DB_AVAIABLE:
		return
	global MENTIONED
	get = get_afk()
	if get and get['afk']:
		if "-" in str(message.chat.id):
			cid = str(message.chat.id)[4:]
		else:
			cid = str(message.chat.id)

		if cid in list(AFK_RESTIRECT):
			if int(AFK_RESTIRECT[cid]) >= int(time.time()):
				return
		AFK_RESTIRECT[cid] = int(time.time()) + DELAY_TIME
		if get['reason']:
			await message.reply("Sorry, {} is AFK!\nBecause of {}".format(mention_markdown(Owner, OwnerName), get['reason']))
		else:
			await message.reply("Sorry, {} is AFK!".format(mention_markdown(Owner, OwnerName)))

		content, message_type = get_message_type(message)
		if message_type == Types.TEXT:
			if message.text:
				text = message.text
			else:
				text = message.caption
		else:
			text = message_type.name

		MENTIONED.append({"user": message.from_user.first_name, "user_id": message.from_user.id, "chat": message.chat.title, "chat_id": cid, "text": text, "message_id": message.message_id})
		await client.send_message(Owner, "{} mentioned you in {}\n\n{}\n\nTotal count: `{}`\n\n{}".format(mention_markdown(message.from_user.id, message.from_user.first_name), message.chat.title, text[:3500], len(MENTIONED), f"[Go to message](https://t.me/c/{cid}/{message.message_id})"))

@app.on_message(Filters.user("self") & Filters.group, group=13)
async def no_longer_afk(client, message):
	if not DB_AVAIABLE:
		return
	global MENTIONED
	get = get_afk()
	if get and get['afk']:
		await client.send_message(message.from_user.id, "You are no longer afk!")
		set_afk(False, "")
		text = "You are no longer afk!\n**Total {} mentioned you**\n".format(len(MENTIONED))
		for x in MENTIONED:
			msg_text = x["text"]
			if len(msg_text) >= 11:
				msg_text = "{}...".format(x["text"])
			text += "- [{}](https://t.me/c/{}/{}) ({}): {}\n".format(escape_markdown(x["user"]), x["chat_id"], x["message_id"], x["chat"], msg_text)
		await client.send_message(Owner, text)
		MENTIONED = []

