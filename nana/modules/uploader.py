import asyncio
import os
import requests
import shutil
import time

from nana import app, Command
from pyrogram import errors, Filters, InlineKeyboardMarkup, InputTextMessageContent, InlineKeyboardButton

from nana.helpers import download_url
from nana.alternative.send_sticker import send_sticker

__MODULE__ = "Uploader image"



async def time_parser(start, end):
	time_end = end - start
	month = time_end // 2678400
	days = time_end // 86400
	hours = time_end // 3600 % 24
	minutes = time_end // 60 % 60
	seconds = time_end % 60
	times = ""
	if month:
		times += "{} month, ".format(month)
	if days:
		times += "{} days, ".format(days)
	if hours:
		times += "{} hours, ".format(hours)
	if minutes:
		times += "{} minutes, ".format(minutes)
	if seconds:
		times += "{} seconds".format(seconds)
	if times == "":
		times = "{} miliseconds".format(time_end)
	return times

def convert_size(size_bytes):
	if size_bytes == 0:
		return "0B"
	size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
	i = int(math.floor(math.log(size_bytes, 1024)))
	p = math.pow(1024, i)
	s = round(size_bytes / p, 2)
	return "%s %s" % (s, size_name[i])

CURRENT_COUNTER = {}
async def callback_send(current, total, chat_id, message, client):
	global CURRENT_COUNTER
	if not CURRENT_COUNTER.get(chat_id + message.message_id):
		await message.edit("__[{}] Uploading...__".format("{:.1f}%".format(current * 100 / total)))
		CURRENT_COUNTER[chat_id + message.message_id] = 0
	CURRENT_COUNTER[chat_id + message.message_id] += 1
	if CURRENT_COUNTER[chat_id + message.message_id] % 100 == 0:
		try:
			await message.edit("__[{}] Uploading...__".format("{:.1f}%".format(current * 100 / total)))
		except Exception as err:
			print("Error: failed to edit message: " + str(err))
		print("{:.1f}%".format(current * 100 / total))
	else:
		print("{:.1f}%".format(current * 100 / total))



@app.on_message(Filters.user("self") & Filters.command(["stk"], Command))
async def StickerUploader(client, message):
	if len(message.text.split()) == 1:
		await message.edit("Usage: `.stk url`")
		return
	photo = message.text.split(None, 1)[1]
	await message.delete()
	if "http" in photo:
		r = requests.get(photo, stream=True)
		with open("nana/cache/stiker.png", "wb") as stk:
			shutil.copyfileobj(r.raw, stk)
		if message.reply_to_message:
			await send_sticker(message.chat.id, "nana/cache/stiker.png", reply_to_message_id=message.reply_to_message.message_id)
		else:
			await send_sticker(message.chat.id, "nana/cache/stiker.png")
		os.remove("nana/cache/stiker.png")
	else:
		if message.reply_to_message:
			await send_sticker(message.chat.id, photo, reply_to_message_id=message.reply_to_message.message_id)
		else:
			await send_sticker(message.chat.id, photo)

@app.on_message(Filters.user("self") & Filters.command(["pic"], Command))
async def PictureUploader(client, message):
	if len(message.text.split()) == 1:
		await message.edit("Usage: `.pic url`")
		return
	photo = message.text.split(None, 1)[1]
	await message.delete()
	if "http" in photo:
		r = requests.get(photo, stream=True)
		with open("nana/cache/pic.png", "wb") as stk:
			shutil.copyfileobj(r.raw, stk)
		if message.reply_to_message:
			await client.send_photo(message.chat.id, "nana/cache/pic.png", reply_to_message_id=message.reply_to_message.message_id)
		else:
			await client.send_photo(message.chat.id, "nana/cache/pic.png")
		os.remove("nana/cache/pic.png")
	else:
		if message.reply_to_message:
			await client.send_photo(message.chat.id, photo, caption, reply_to_message_id=message.reply_to_message.message_id)
		else:
			await client.send_photo(message.chat.id, photo, caption)

@app.on_message(Filters.user("self") & Filters.command(["send"], Command))
async def SendFiles(client, message):
	if len(message.text.split()) <= 2:
		await message.edit("Usage: `.send (type) (path)`")
		return
	# await message.edit("__Starting sending...__")
	p = message.text.split(None, 2)
	ftype = p[1]
	path = p[2]
	method = ["photo", "audio", "document", "sticker", "video", "animation", "voice", "vn"]
	global IMSGID, STOP_DOWNLOAD
	IMSGID = ""
	STOP_UPLOAD = False
	if ftype.lower() in method:
		await message.delete()
		await sendit(client, message, ftype, path)
		# await message.edit("File was sent successfully!")
	elif ftype.lower() == "url":
		await message.delete()
		file_name = None
		if "|" in path:
			file_name = path.split("|")[1]
			path = path.split("|")[0]
		await sendit(client, message, ftype, path, file_name=file_name)
	else:
		await message.edit("**Unknown type!**\nSupported type: photo, audio, document, sticker, video, animation, voice, vn")

async def sendit(client, message, ftype, path, file_name=False):
	await message.edit("__Uploading...__")
	start = int(time.time())

	if ftype.lower() == "photo":
		try:
			await app.send_photo(message.chat.id, path, reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None, progress=callback_send, progress_args=(message.chat.id, message, client))
		except Exception as err:
			await message.edit("Error: " + str(err))
			return
	elif ftype.lower() == "audio":
		try:
			await app.send_audio(message.chat.id, path, reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None, progress=callback_send, progress_args=(message.chat.id, message, client))
		except Exception as err:
			await message.edit("Error: " + str(err))
			return
	elif ftype.lower() == "document":
		try:
			await app.send_document(message.chat.id, path, reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None, progress=callback_send, progress_args=(message.chat.id, message, client))
		except Exception as err:
			await message.edit("Error: " + str(err))
			return
	elif ftype.lower() == "sticker":
		try:
			await app.send_sticker(message.chat.id, path, reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None, progress=callback_send, progress_args=(message.chat.id, message, client))
		except Exception as err:
			await message.edit("Error: " + str(err))
			return
	elif ftype.lower() == "video":
		try:
			await app.send_video(message.chat.id, path, reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None, progress=callback_send, progress_args=(message.chat.id, message, client))
		except Exception as err:
			await message.edit("Error: " + str(err))
			return
	elif ftype.lower() == "animation":
		try:
			await app.send_animation(message.chat.id, path, reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None, progress=callback_send, progress_args=(message.chat.id, message, client))
		except Exception as err:
			await message.edit("Error: " + str(err))
			return
	elif ftype.lower() == "voice":
		try:
			await app.send_voice(message.chat.id, path, reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None, progress=callback_send, progress_args=(message.chat.id, message, client))
		except Exception as err:
			await message.edit("Error: " + str(err))
			return
	elif ftype.lower() == "vn":
		try:
			await app.send_video_note(message.chat.id, path, reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None, progress=callback_send, progress_args=(message.chat.id, message, client))
		except Exception as err:
			await message.edit("Error: " + str(err))
			return
	elif ftype.lower() == "url":
		file_name = file_name if file_name else path.split("/")[-1].split("?")[0]
		await message.edit(f"__Downloading {file_name}...__")
		isdone, ret = await download_url(path, file_name)
		if not isdone:
			await message.edit("Error: " + str(err))
			return
		await message.edit(f"__Uploading {file_name}...__")
		try:
			await app.send_document(message.chat.id, "nana/downloads/" + file_name, reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None, progress=callback_send, progress_args=(message.chat.id, message, client))
		except Exception as err:
			await message.edit("Error: " + str(err))
			return
	else:
		await message.edit("Error: unknown type")
		return

	end = int(time.time())
	times = await time_parser(start, end)
	if STOP_UPLOAD:
		return

	text = f"**File was sent successfully for {times}!"
	await message.edit(text)
	if ftype.lower() == "url":
		os.remove("nana/downloads/" + file_name)
