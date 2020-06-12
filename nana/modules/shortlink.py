import pyrogram
import requests
from datetime import datetime

from nana import app, Command, BITLY_API
from pyrogram import Filters

__MODULE__ = "Shortlink"
__HELP__ = """
Just make it short for link

──「 **Bitly** 」──
-> `bitly google.com`
Do shortlink for google

──「 **Bitly check link** 」──
-> `bitstats bit.ly/sH0RtL1Nk`
Check original link from bitly link

──「 **S.ID Short Link** 」──
-> `st http://google.com`
Shortlink but with s.id, must fill http or https!
"""

@app.on_message(Filters.user("self") & Filters.command(["bitly"], Command))
async def bitly_shortlink(client, message):
	if len(message.text.split()) == 1:
		await message.edit("Usage: `bitly google.com`")
		return
	if not BITLY_API:
		await message.edit("You must fill **BITLY_API** in config before use this.\nRegister at [here](https://dev.bitly.com/my_apps.html)", parse_mode="markdown")
		return
	target_url = message.text.split(None, 1)[1]
	url = "https://api-ssl.bitly.com/v4/bitlinks"
	data = {"long_url": target_url}
	headers = {'Authorization': 'Bearer {}'.format(BITLY_API), 'Content-type': 'application/json'}
	get = requests.post(url, json=data, headers=headers)
	get_json = get.json()
	if get.status_code == 200:
		await message.edit("**Shortlink created!**\n**Original link:** {}\n**Shorted link:** {}\n\n**To get stats:** `bitstats {}`".format(get_json['long_url'], get_json['link'], get_json['id']))
	else:
		await message.edit("**Error:**\n{}\n\n{}".format(get_json['message'], get_json['description']))

@app.on_message(Filters.user("self") & Filters.command(["bitstats"], Command))
async def bitly_shortlink(client, message):
	if len(message.text.split()) == 1:
		await message.edit("Usage: `bitstats bit.ly/sH0RtL1Nk`")
		return
	if not BITLY_API:
		await message.edit("You must fill BITLY_API in config before use this.\nRegister at [here](https://dev.bitly.com/my_apps.html)", parse_mode="markdown")
		return
	target_url = message.text.split(None, 1)[1]
	url = "https://api-ssl.bitly.com/v4/bitlinks/{}".format(target_url)
	headers = {'Authorization': 'Bearer {}'.format(BITLY_API), 'Content-type': 'application/json'}
	get = requests.get(url, headers=headers)
	get_json = get.json()
	if get.status_code == 200:
		parse_time = datetime.strptime(get_json['created_at'], "%Y-%m-%dT%H:%M:%S+0000").strftime("%H:%M:%S %d-%m-%Y")
		await message.edit("**Shortlink Info**\n**Original link:** {}\n**Shorted link:** {}\n\n**Created at** `{}`".format(get_json['long_url'], get_json['link'], parse_time))
	else:
		await message.edit("**Error:**\n{}\n\n{}".format(get_json['message'], get_json['description']))


@app.on_message(Filters.user("self") & Filters.command(["st"], Command))
async def sid_shortlink(client, message):
	if len(message.text.split()) == 1:
		await message.edit("Usage: `st https://google.com`")
		return
	target_url = message.text.split(None, 1)[1]
	await message.edit("__Please wait...__")
	get = requests.post("https://s.id/api/public/link/shorten", data={'url': target_url})
	get_json = get.json()
	if get.status_code == 200:
		await message.edit("**Shortlink created!**\n**Original link:** {}\n**Shorted link:** https://s.id/{}".format(target_url, get_json['short']))
	elif get.status_code == 200 and not get_json['success']:
		await message.edit("**Error!**\n{}".format(", ".join(get_json['errors']['url'])))
	else:
		await message.edit("**Error:**\n{}\n\n{}".format(get_json['message'], get_json['description']))