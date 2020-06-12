import time
import datetime
import os
import pydrive
import requests
from pydrive.drive import GoogleDrive

from bs4 import BeautifulSoup
from nana import app, Command, gauth
from nana.helpers.parser import cleanhtml
from nana.modules.downloads import download_url
from pyrogram import Filters

__MODULE__ = "Google Drive"


async def get_drivedir(drive):
	file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
	for drivefolders in file_list:
		if drivefolders['title'] == 'Nana Drive':
			return drivefolders['id']
	mkdir = drive.CreateFile({'title': 'Nana Drive', "mimeType": "application/vnd.google-apps.folder"})
	mkdir.Upload()

async def get_driveid(driveid):
	if "http" in driveid or "https" in driveid:
		drivesplit = driveid.split('drive.google.com')[1]
		if '/d/' in drivesplit:
			driveid = drivesplit.split('/d/')[1].split('/')[0]
		elif 'id=' in drivesplit:
			driveid = drivesplit.split('id=')[1].split('&')[0]
		else:
			return False
	return driveid

async def get_driveinfo(driveid):
	getdrivename = BeautifulSoup(requests.get('https://drive.google.com/file/d/{}/view'.format(driveid), allow_redirects=False).content)
	filename = cleanhtml(str(getdrivename.find('title'))).split(" - ")[0]
	return filename

CURRENT_COUNTER = {}
async def callback_dl(current, total, message):
	global CURRENT_COUNTER
	if not CURRENT_COUNTER.get(message.chat.id + message.message_id):
		await message.edit("__[{}] Downloading...__".format("{:.1f}%".format(current * 100 / total)))
		CURRENT_COUNTER[message.chat.id + message.message_id] = 0
	CURRENT_COUNTER[message.chat.id + message.message_id] += 1
	if CURRENT_COUNTER[message.chat.id + message.message_id] % 20 == 0:
		try:
			await message.edit("__[{}] Downloading...__".format("{:.1f}%".format(current * 100 / total)))
		except Exception as err:
			print("Error: failed to edit message: " + str(err))
		print("{:.1f}%".format(current * 100 / total))
	else:
		print("{:.1f}%".format(current * 100 / total))


@app.on_message(Filters.user("self") & Filters.command(["gdrive"], Command))
async def gdrive_stuff(client, message):
	gauth.LoadCredentialsFile("nana/session/drive")
	if gauth.credentials is None:
		await message.edit("You are not logged in to your google drive account!\nCheck your saved messages for more information!")
		gdriveclient = os.path.isfile("client_secrets.json")
		if not gdriveclient:
			await message.send_message(Owner, "Hello, look like you're not logged in to google drive 🙂\nI can help you to login.\n\nFirst of all, you need to activate your google drive API\n1. [Go here](https://developers.google.com/drive/api/v3/quickstart/python), click **Enable the drive API**\n2. Login to your google account (skip this if you're already logged in)\n3. After logged in, click **Enable the drive API** again, and click **Download Client Configuration** button, download that.\n4. After downloaded that file, rename `credentials.json` to `client_secrets.json`, and upload to your bot dir (not in nana dir)\nor if you're using heroku, read this alternate guide\n4a. Open `credentials.json`, copy all text from that file, then paste **GOOGLE_API_TEXT** with that text\n\nAfter that, you can go next guide by type `/gdrive`")
		else:
			await message.send_message(Owner, "Hello, look like you're not logged in to google drive :)\nI can help you to login.\n\n**To login Google Drive**\n1. `/gdrive` to get login URL\n2. After you're logged in, copy your Token.\n3. `/gdrive (token)` without `(` or `)` to login, and your session will saved to `nana/session/drive`.\n\nDon't share your session to someone, else they will hack your google drive account!")
		return
	elif gauth.access_token_expired:
		# Refresh them if expired
		gauth.Refresh()
	else:
		# Initialize the saved creds
		gauth.Authorize()

	drive = GoogleDrive(gauth)
	drive_dir = await get_drivedir(drive)

	if len(message.text.split()) == 3 and message.text.split()[1] == "download":
		await message.edit("Downloading...")
		driveid = await get_driveid(message.text.split()[2])
		if not driveid:
			await message.edit("Invaild URL!\nIf you think this is bug, please go to your Assistant bot and type `/reportbug`")
			return
		filename = await get_driveinfo(driveid)
		if not filename:
			await message.edit("Invaild URL!\nIf you think this is bug, please go to your Assistant bot and type `/reportbug`")
			return
		await message.edit("Downloading for `{}`\nPlease wait...".format(filename))
		download = drive.CreateFile({'id': driveid})
		download.GetContentFile(filename)
		try:
			os.rename(filename, "nana/downloads/" + filename)
		except FileExistsError:
			os.rename(filename, "nana/downloads/" + filename + ".2")
		await message.edit("Downloaded!\nFile saved to `{}`".format("nana/downloads/" + filename))
	elif len(message.text.split()) == 3 and message.text.split()[1] == "upload":
		filename = message.text.split()[2].split(None, 1)[0]
		real_file_name = filename.split("/")[-1]
		checkfile = os.path.isfile(filename)
		if not checkfile:
			await message.edit("File `{}` was not found!".format(filename))
			return
		await message.edit("Uploading `{}`...".format(real_file_name))
		upload = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": drive_dir}], 'title': real_file_name})
		upload.SetContentFile(filename)
		upload.Upload()
		upload.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
		await message.edit("Uploaded!\nDownload link: [{}]({})\nDirect download link: [{}]({})".format(real_file_name, upload['alternateLink'], real_file_name, upload['downloadUrl']))
	elif len(message.text.split()) == 3 and message.text.split()[1] == "mirror":
		message.edit("Mirroring...")
		driveid = await get_driveid(message.text.split()[2])
		if not driveid:
			await message.edit("Invaild URL!\nIf you think this is bug, please go to your Assistant bot and type `/reportbug`")
			return
		filename = await get_driveinfo(driveid)
		if not filename:
			await message.edit("Invaild URL!\nIf you think this is bug, please go to your Assistant bot and type `/reportbug`")
			return
		mirror = drive.auth.service.files().copy(fileId=driveid, body={"parents": [{"kind": "drive#fileLink", "id": drive_dir}], 'title': filename}).execute()
		new_permission = {'type': 'anyone', 'value': 'anyone', 'role': 'reader'}
		drive.auth.service.permissions().insert(fileId=mirror['id'], body=new_permission).execute()
		await message.edit("Done!\nDownload link: [{}]({})\nDirect download link: [{}]({})".format(filename, mirror['alternateLink'], filename, mirror['downloadUrl']))
	elif len(message.text.split()) == 2 and message.text.split()[1] == "tgmirror":
		if message.reply_to_message:
			await message.edit("__Downloading...__")
			if message.reply_to_message.photo:
				nama = "photo_{}_{}.png".format(message.reply_to_message.photo.file_id, message.reply_to_message.photo.date)
				await client.download_media(message.reply_to_message.photo, file_name="nana/downloads/" + nama, progress=callback_dl, progress_args=(message,))
			elif message.reply_to_message.animation:
				nama = "giphy_{}-{}.gif".format(message.reply_to_message.animation.date, message.reply_to_message.animation.file_size)
				await client.download_media(message.reply_to_message.animation, file_name="nana/downloads/" + nama, progress=callback_dl, progress_args=(message,))
			elif message.reply_to_message.video:
				nama = "video_{}-{}.mp4".format(message.reply_to_message.video.date, message.reply_to_message.video.file_size)
				await client.download_media(message.reply_to_message.video, file_name="nana/downloads/" + nama, progress=callback_dl, progress_args=(message,))
			elif message.reply_to_message.sticker:
				nama = "sticker_{}_{}.webp".format(message.reply_to_message.sticker.date, message.reply_to_message.sticker.set_name)
				await client.download_media(message.reply_to_message.sticker, file_name="nana/downloads/" + nama, progress=callback_dl, progress_args=(message,))
			elif message.reply_to_message.audio:
				nama = "{}".format(message.reply_to_message.audio.file_name)
				await client.download_media(message.reply_to_message.audio, file_name="nana/downloads/" + nama, progress=callback_dl, progress_args=(message,))
			elif message.reply_to_message.voice:
				nama = "audio_{}.ogg".format(message.reply_to_message.voice)
				await client.download_media(message.reply_to_message.voice, file_name="nana/downloads/" + nama, progress=callback_dl, progress_args=(message,))
			elif message.reply_to_message.document:
				nama = "{}".format(message.reply_to_message.document.file_name)
				await client.download_media(message.reply_to_message.document, file_name="nana/downloads/" + nama, progress=callback_dl, progress_args=(message,))
			else:
				message.edit("Unknown file!")
				return
			await message.edit("__Uploading...__")
			upload = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": drive_dir}], 'title': nama})
			upload.SetContentFile("nana/downloads/" + nama)
			upload.Upload()
			upload.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
			await message.edit("Done!\nDownload link: [{}]({})\nDirect download link: [{}]({})".format(nama, upload['alternateLink'], nama, upload['downloadUrl']))
			os.remove("nana/downloads/" + nama)
		else:
			await message.edit("Reply document to mirror it to gdrive")
	elif len(message.text.split()) == 3 and message.text.split()[1] == "urlmirror":
		await message.edit("Downloading...")
		URL = message.text.split()[2]
		nama = URL.split("/")[-1]
		time_dl = await download_url(URL, nama)
		if "Downloaded" not in time_dl:
			await message.edit("Failed to download file, invaild url!")
			return
		await message.edit(f"Downloaded with {time_dl}.\nNow uploading...")
		upload = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": drive_dir}], 'title': nama})
		upload.SetContentFile("nana/downloads/" + nama)
		upload.Upload()
		upload.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
		await message.edit("Done!\nDownload link: [{}]({})\nDirect download link: [{}]({})".format(nama, upload['alternateLink'], nama, upload['downloadUrl']))
		os.remove("nana/downloads/" + nama)
	else:
		await message.edit("Usage:\n-> `gdrive download <url/gid>`\n-> `gdrive upload <file>`\n-> `gdrive mirror <url/gid>`\n\nFor more information about this, go to your assistant.")
