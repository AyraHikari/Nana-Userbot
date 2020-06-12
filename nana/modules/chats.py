import os

from nana import app, Command, DB_AVAIABLE, Owner
from pyrogram import Filters
if DB_AVAIABLE:
	from nana.modules.database.chats_db import update_chat, get_all_chats, update_chat_admin, update_me_restirected, delete_my_chat_admin, get_all_chats_admin


MESSAGE_RECOUNTER = 0

__MODULE__ = "Chats"

def get_msgc():
	return MESSAGE_RECOUNTER

@app.on_message(Filters.group, group=10)
async def UpdateMyChats(client, message):
	global MESSAGE_RECOUNTER
	if DB_AVAIABLE:
		update_chat(message.chat)
	MESSAGE_RECOUNTER += 1

COUNTER_DELAY = {}
@app.on_message(Filters.group | Filters.channel, group=11)
async def UpdateMyChatsAdmin(client, message):
	if not COUNTER_DELAY.get(message.chat.id):
		COUNTER_DELAY[message.chat.id] = 0
	COUNTER_DELAY[message.chat.id] += 1
	if COUNTER_DELAY[message.chat.id] % 25 == 0:
		get_user = await client.get_chat_member(message.chat.id, Owner)
		if get_user['status'] != 'member' and get_user['status'] != 'restricted':
			if DB_AVAIABLE:
				update_chat_admin(message.chat, get_user['status'])
		if get_user['status'] == 'restricted':
			update_me_restirected(message.chat)
			delete_my_chat_admin(message.chat, get_user['status'])
		if get_user['status'] == 'member':
			delete_my_chat_admin(message.chat, get_user['status'])


@app.on_message(Filters.user("self") & Filters.command(["chatlist"], Command))
async def get_chat(client, message):
	if not DB_AVAIABLE:
		await message.edit("Your database is not avaiable!")
		return
	all_chats = get_all_chats()
	chatfile = 'List of chats that I joined.\n'
	for chat in all_chats:
		if str(chat.chat_username) != "None":
			chatfile += "{} - ({}): @{}\n".format(chat.chat_name, chat.chat_id, chat.chat_username)
		else:
			chatfile += "{} - ({})\n".format(chat.chat_name, chat.chat_id)

	with open("nana/cache/chatlist.txt", "w", encoding="utf-8") as writing:
		writing.write(str(chatfile))
		writing.close()

	await client.send_document("self", document="nana/cache/chatlist.txt", caption="Here is the chat list that I joined.")
	await message.edit("My chat list exported to my saved messages.")
	os.remove("nana/cache/chatlist.txt")


@app.on_message(Filters.user("self") & Filters.command(["myadminchats"], Command))
async def get_chats_admin(client, message):
	if not DB_AVAIABLE:
		await message.edit("Your database is not avaiable!")
		return
	all_chats = get_all_chats_admin()
	chatfile = 'List of chats that I am became creator/admin.\n'
	for chat in all_chats:
		if str(chat.chat_username) != "None":
			chatfile += "[{}] {} - ({}): @{}\n".format(chat.chat_status, chat.chat_name, chat.chat_id, chat.chat_username)
		else:
			chatfile += "[{}] {} - ({})\n".format(chat.chat_status, chat.chat_name, chat.chat_id)

	with open("nana/cache/adminchats.txt", "w", encoding="utf-8") as writing:
		writing.write(str(chatfile))
		writing.close()

	await client.send_document("self", document="nana/cache/adminchats.txt", caption="List of chats that I am became creator/admin.")
	await message.edit("My admin chat list exported to my saved messages.")
	os.remove("nana/cache/adminchats.txt")
