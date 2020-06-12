import time
import datetime
import os
import math
import multiprocessing
import random
import re
import json

import asyncio
from asyncio import create_subprocess_shell as asyncSubprocess
from asyncio.subprocess import PIPE as asyncPIPE
from urllib.error import HTTPError

from nana import app, Command, log
from nana.helpers import time_formatter, time_parser_int, time_parser, convert_size
from pyrogram import errors, Filters, InlineKeyboardMarkup, InputTextMessageContent, InlineKeyboardButton
from pySmartDL import SmartDL

__MODULE__ = "Downloads"

MEGA_DL = "nana/downloads/mega/"


async def subprocess_run(message, cmd):
	subproc = await asyncSubprocess(cmd, stdout=asyncPIPE, stderr=asyncPIPE)
	stdout, stderr = await subproc.communicate()
	exitCode = subproc.returncode
	if exitCode != 0:
		await message.edit(
			'**An error was detected while running subprocess.**\n'
			f'exitCode : `{exitCode}`\n'
			f'stdout : `{stdout.decode().strip()}`\n'
			f'stderr : `{stderr.decode().strip()}`')
		return exitCode
	return stdout.decode().strip(), stderr.decode().strip(), exitCode

CURRENT_COUNTER = {}
async def callback_dl(current, total, chat_id, message, client, is_mirror=False, nama=None):
	global CURRENT_COUNTER
	if not CURRENT_COUNTER.get(chat_id + message.message_id):
		await message.edit("__[{}] Downloading...__".format("{:.1f}%".format(current * 100 / total)))
		CURRENT_COUNTER[chat_id + message.message_id] = 0
	CURRENT_COUNTER[chat_id + message.message_id] += 1
	if CURRENT_COUNTER[chat_id + message.message_id] % 20 == 0:
		try:
			await message.edit("__[{}] Downloading...__".format("{:.1f}%".format(current * 100 / total)))
		except Exception as err:
			print("Error: failed to edit message: " + str(err))
		print("{:.1f}%".format(current * 100 / total))
	else:
		print("{:.1f}%".format(current * 100 / total))

async def download_url(message, url, file_name, is_mirror=False):
	start = int(time.time())
	global CURRENT_COUNTER
	# downloader = Downloader(url=url)
	downloader = SmartDL(url, "nana/downloads/" + file_name, progress_bar=False)
	try:
		downloader.start(blocking=False)
	except HTTPError as e:
		return await message.edit(f"`Err: {str(e)}`")
	c_time = time.time()
	CURRENT_COUNTER[file_name] = 0
	while not downloader.isFinished() and downloader.get_status() == "downloading":
		status = downloader.get_status().capitalize()
		total_length = downloader.filesize if downloader.filesize else None
		downloaded = downloader.get_dl_size()
		diff = time.time() - c_time
		percentage = "{:.1f}%".format(downloader.get_progress() * 100)
		speed = downloader.get_speed()
		estimated_total_time = round(downloader.get_eta())
		try:
			if CURRENT_COUNTER[file_name] % 500000 == 0:
				text = "__[{}] {} **{}**__\n{} of {} | {}/s\n**ETA** {} | {}".format(percentage, status, file_name, convert_size(downloaded), convert_size(total_length), convert_size(speed), time_parser_int(estimated_total_time), time_parser_int(round(diff)))
				await message.edit(text)
		except Exception as e:
			print(e)
		CURRENT_COUNTER[file_name] += 1
		if status == "Combining":
			text = "__[DONE] {} **{}**__\n{} of {} | {}/s\n**ETA** {} | {}".format(status, file_name, convert_size(downloaded), convert_size(total_length), convert_size(speed), time_parser_int(estimated_total_time), time_parser_int(round(diff)))
			await message.edit(text)
			wait = round(downloader.get_eta())
			await asyncio.sleep(wait)
	if downloader.isSuccessful():
		download_time = round(downloader.get_dl_time() + wait)
		text = "__[DONE] Downloaded **{}**__\nDownload took: {}".format(file_name, time_parser_int(download_time))
		return await message.edit(text)
	else:
		await message.edit("Failed to download")
		for e in downloader.get_errors():
			log.error(str(e))


async def download_reply_nocall(client, message):
	if message.reply_to_message.photo:
		nama = "photo_{}_{}.png".format(message.reply_to_message.photo.file_id, message.reply_to_message.photo.date)
		await client.download_media(message.reply_to_message.photo, file_name="nana/downloads/" + nama)
	elif message.reply_to_message.animation:
		nama = "giphy_{}-{}.gif".format(message.reply_to_message.animation.date, message.reply_to_message.animation.file_size)
		await client.download_media(message.reply_to_message.animation, file_name="nana/downloads/" + nama)
	elif message.reply_to_message.video:
		nama = "video_{}-{}.mp4".format(message.reply_to_message.video.date, message.reply_to_message.video.file_size)
		await client.download_media(message.reply_to_message.video, file_name="nana/downloads/" + nama)
	elif message.reply_to_message.sticker:
		nama = "sticker_{}_{}.webp".format(message.reply_to_message.sticker.date, message.reply_to_message.sticker.set_name)
		await client.download_media(message.reply_to_message.sticker, file_name="nana/downloads/" + nama)
	elif message.reply_to_message.audio:
		nama = "{}".format(message.reply_to_message.audio.file_name)
		await client.download_media(message.reply_to_message.audio, file_name="nana/downloads/" + nama)
	elif message.reply_to_message.voice:
		nama = "audio_{}.ogg".format(message.reply_to_message.voice)
		await client.download_media(message.reply_to_message.voice, file_name="nana/downloads/" + nama)
	elif message.reply_to_message.document:
		nama = "{}".format(message.reply_to_message.document.file_name)
		await client.download_media(message.reply_to_message.document, file_name="nana/downloads/" + nama)
	else:
		return False
	return "nana/downloads/" + nama


@app.on_message(Filters.user("self") & Filters.command(["dl"], Command))
async def download_from_url(client, message):
	if len(message.text.split()) == 1:
		await message.edit("Usage: `dl url filename`")
		return
	if not os.path.isdir("nana/downloads"):
		os.makedirs("nana/downloads")
	if len(message.text.split()) == 2:
		URL = message.text.split(None, 1)[1]
		file_name = URL.split("/")[-1]
	elif len(message.text.split()) >= 3:
		URL = message.text.split(None, 2)[1]
		file_name = message.text.split(None, 2)[2]
	else:
		await message.edit("Invaild args given!")
		return
	try:
		os.listdir("nana/downloads/")
	except FileNotFoundError:
		await message.edit("Invalid download path in config!")
		return
	is_mega = re.findall(r'\bhttps?://.*mega.*\.nz\S+', URL)
	if is_mega:
		await mega_downlaoder(message, is_mega[0], file_name=file_name if len(message.text.split()) >= 3 else None)
		return
	download = await download_url(message, URL, file_name)
	# await message.edit(download)


@app.on_message(Filters.user("self") & Filters.command(["download"], Command))
async def download_from_telegram(client, message):
	if not os.path.isdir("nana/downloads"):
		os.makedirs("nana/downloads")
	if message.reply_to_message:
		await message.edit("__Starting download...__")

		start = int(time.time())
		msgid = message.message_id # result.updates[-1].message.id
		if message.reply_to_message.photo:
			nama = "photo_{}_{}.png".format(message.reply_to_message.photo.file_id, message.reply_to_message.photo.date)
			await client.download_media(message.reply_to_message.photo, file_name="nana/downloads/" + nama, progress=callback_dl, progress_args=(message.chat.id, msgid, client,))
		elif message.reply_to_message.animation:
			nama = "giphy_{}-{}.gif".format(message.reply_to_message.animation.date, message.reply_to_message.animation.file_size)
			await client.download_media(message.reply_to_message.animation, file_name="nana/downloads/" + nama, progress=callback_dl, progress_args=(message.chat.id, msgid, client,))
		elif message.reply_to_message.video:
			nama = "video_{}-{}.mp4".format(message.reply_to_message.video.date, message.reply_to_message.video.file_size)
			await client.download_media(message.reply_to_message.video, file_name="nana/downloads/" + nama, progress=callback_dl, progress_args=(message.chat.id, msgid, client,))
		elif message.reply_to_message.sticker:
			nama = "sticker_{}_{}.webp".format(message.reply_to_message.sticker.date, message.reply_to_message.sticker.set_name)
			await client.download_media(message.reply_to_message.sticker, file_name="nana/downloads/" + nama, progress=callback_dl, progress_args=(message.chat.id, msgid, client,))
		elif message.reply_to_message.audio:
			nama = "{}".format(message.reply_to_message.audio.file_name)
			await client.download_media(message.reply_to_message.audio, file_name="nana/downloads/" + nama, progress=callback_dl, progress_args=(message.chat.id, msgid, client,))
		elif message.reply_to_message.voice:
			nama = "audio_{}.ogg".format(message.reply_to_message.voice)
			await client.download_media(message.reply_to_message.voice, file_name="nana/downloads/" + nama, progress=callback_dl, progress_args=(message.chat.id, msgid, client,))
		elif message.reply_to_message.document:
			nama = "{}".format(message.reply_to_message.document.file_name)
			await client.download_media(message.reply_to_message.document, file_name="nana/downloads/" + nama, progress=callback_dl, progress_args=(message.chat.id, msgid, client,))
		else:
			await message.edit("Unknown file!")
			# await message.edit("Unknown file!")
			return
		end = int(time.time())
		times = time_parser(start, end)

		text = f"**⬇ Downloaded!**\n🗂 File name: `{nama}`\n🏷 Saved to: `nana/downloads/`\n⏲ Downloaded in: {times}"
		await message.edit(text)
	else:
		await message.edit("Reply document to download it")


async def decrypt_file(megadl, file_path, temp_file_path, hex_key, hex_raw_key):
	cmd = ("cat '{}' | openssl enc -d -aes-128-ctr -K {} -iv {} > '{}'".format(temp_file_path, hex_key, hex_raw_key, file_path))
	if await subprocess_run(megadl, cmd):
		os.remove(temp_file_path)
	else:
		raise FileNotFoundError(file_path)
	return
