import requests

from nana import app, Command
from pyrogram import Filters

__MODULE__ = "Device"


DEVICE_LIST = "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json"

@app.on_message(Filters.user("self") & Filters.command(["device"], Command))
async def get_device_info(client, message):
	if len(message.text.split()) == 1:
		await message.edit("Usage: `device (codename)`")
		return
	getlist = requests.get(DEVICE_LIST).json()
	targetdevice = message.text.split()[1].lower()
	devicelist = []
	found = False
	if targetdevice in list(getlist):
		device = getlist.get(targetdevice)
		text = ""
		for x in device:
			text += "Brand: `{}`\nName: `{}`\nDevice: `{}`\nCodename: `{}`".format(x['brand'], x['name'], x['model'], targetdevice)
			text += "\n\n"
		await message.edit(text)
	else:
		await message.edit("Device {} was not found!".format(targetdevice))
