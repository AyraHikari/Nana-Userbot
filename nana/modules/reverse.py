import requests

from nana import app, Command
from pyrogram import Filters

__MODULE__ = "Reverse Image"


@app.on_message(Filters.user("self") & Filters.command(["reverse"], Command))
async def check_image(client, message):
	if message.reply_to_message.photo:
		nama = "photo_{}_{}.png".format(message.reply_to_message.photo.file_id, message.reply_to_message.photo.date)
		await client.download_media(message.reply_to_message.photo, file_name="nana/downloads/" + nama)
	elif message.reply_to_message.animation:
		nama = "giphy_{}-{}.gif".format(message.reply_to_message.animation.date, message.reply_to_message.animation.file_size)
		await client.download_media(message.reply_to_message.animation, file_name="nana/downloads/" + nama)
	else:
		await message.edit("File doesn't support!")
		return
	searchUrl = 'http://www.google.co.id/searchbyimage/upload'
	filePath = 'nana/downloads/{}'.format(nama)
	multipart = {'encoded_image': (filePath, open(filePath, 'rb')), 'image_content': ''}
	response = requests.post(searchUrl, files=multipart, allow_redirects=False)
	fetchUrl = response.headers['Location']
	await message.edit("🖼 Image was found!\n\n[Check from google here]({})".format(fetchUrl))
