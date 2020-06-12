import time
import math
import os
import pyrogram

from platform import python_version, uname
from nana import app, Command, DB_AVAIABLE, USERBOT_VERSION, BotUsername
from nana.helpers.parser import mention_markdown

from pyrogram import Filters


@app.on_message(Filters.user("self") & Filters.command(["me"], Command))
async def get_myself_client(client, message):
	try:
		me = await app.get_me()
	except ConnectionError:
		return
	getphoto = await client.get_profile_photos(me.id)
	if len(getphoto) == 0:
		getpp = None
	else:
		getpp = getphoto[0]
	text = "**ℹ️ Your profile:**\n"
	text += "First name: {}\n".format(me.first_name)
	if me.last_name:
		text += "Last name: {}\n".format(me.last_name)
	text += "User ID: `{}`\n".format(me.id)
	if me.username:
		text += "Username: @{}\n".format(me.username)
	text += "Phone number: `{}`\n".format("*" * len(me.phone_number))
	text += "`Nana Version    : v{}`\n".format(USERBOT_VERSION)
	if me.photo:
		await client.send_photo(message.chat.id, photo=getpp.file_id, file_ref=getpp.file_ref, caption=text, reply_to_message_id=message.message_id)
	else:
		await message.edit(text, reply_markup=button)

@app.on_message(Filters.user("self") & Filters.command(["mata"], Command))
async def sangmata_checker(client, message):
	if message.reply_to_message:
		await message.edit("__Checking...__")
		await client.forward_messages("@SangMataInfo_bot", message.chat.id, message.reply_to_message.message_id)
		is_no_record = False
		for x in range(8):
			time.sleep(1)
			msg = await app.get_history("@SangMataInfo_bot", limit=3)
			if msg[0].text == "No records found":
				await message.edit("No records found")
				is_no_record = True
				await client.read_history("@SangMataInfo_bot")
				break
			if msg[0].from_user.id == 461843263 and msg[1].from_user.id == 461843263 and msg[2].from_user.id == 461843263:
				await client.read_history("@SangMataInfo_bot")
				break
			else:
				print("Failed, try again ({})".format(x+1))
				continue
		if is_no_record:
			return
		history_name = "1. " + msg[2].text.split("\n\n1. ")[1]
		username_history = "1. " + msg[1].text.split("\n\n1. ")[1]
		text = "**Name History for** [{}](tg://user?id={}) (`{}`)\n\n".format(message.reply_to_message.from_user.first_name, message.reply_to_message.from_user.id, message.reply_to_message.from_user.id) + history_name
		if len(text) <= 4096 and len(text) + len("\n\n**Username History**\n\n") + len(username_history) <= 4906:
			text += "\n\n**Username History**\n\n" + username_history
			await message.edit(text)
		else:
			await message.edit(text)
			await message.reply("\n\n**Username History**\n\n" + username_history)
		return
	await message.edit("Error!")

@app.on_message(Filters.user("self") & (Filters.command(["alive"], Command)))
async def alive(client, message):
	try:
		me = await app.get_me()
	except ConnectionError:
		await message.edit("Failed!")
		return
	machine = uname()
	text = "Hello {}!\n\n".format(message.from_user.first_name)
	text += "**Your bot information:**\n"
	text += "-> Userbot: `Running (v{})`\n".format(USERBOT_VERSION)
	text += "-> Database: `{}`\n".format(DB_AVAIABLE)
	text += "-> Machine: `{} - {} {} {} {}`\n".format(machine.node, machine.system, machine.release, machine.version, machine.machine)
	text += "-> Python: `{}`\n".format(python_version())
	text += "-> Pyrogram: `{}`\n".format(pyrogram.__version__)
	text += "\nBot logged in as {} (`{}`)".format(me.first_name, me.id)
	await message.edit(text)

@app.on_message(Filters.user("self") & (Filters.command(["id"], Command)))
async def userid(client, message):
	chat = message.chat
	user = message.from_user
	if message.reply_to_message:
		if message.reply_to_message.forward_from:
			user_id = message.reply_to_message.from_user.id
			user = mention_markdown(message.reply_to_message.forward_from.id, message.reply_to_message.forward_from.first_name)
		else:
			user_id = message.reply_to_message.from_user.id
			user = mention_markdown(message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name)
	elif len(message.text.split()) >= 2:
		u = message.text.split()[1]
		u = await client.get_users(u)
		user_id = u.id
		user = mention_markdown(u.id, u.first_name)
	else:
		user_id = message.from_user.id
		user = mention_markdown(message.from_user.id, message.from_user.first_name)
	text = "{}'s ID is `{}`\nThis chat id is `{}`".format(user, user_id, message.chat.id)
	await message.edit(text)

@app.on_message(Filters.user("self") & (Filters.command(["ver", "version"], Command)))
async def version(client, message):
	text = "**Version**\n"
	text += "-> Userbot: `Running (v{})`\n".format(USERBOT_VERSION)
	text += "-> Python: `{}`\n".format(python_version())
	text += "-> Pyrogram: `{}`\n".format(pyrogram.__version__)
