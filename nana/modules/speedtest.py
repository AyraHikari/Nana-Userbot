import speedtest
import requests
import os
import ftplib

from urllib.parse import unquote
from datetime import datetime
from nana import app, Command
from nana.helpers import speed_convert
from pyrogram import Filters

__MODULE__ = "Speedtest"
__HELP__ = """
Check your server speed if it good or not for ping, download and upload.

──「 **Speed Test** 」──
-> `speedtest`
Check your server speed for ping, download and upload
"""

@app.on_message(Filters.user("self") & Filters.command(["speedtest"], Command))
async def ftpdel(client, message):
		await message.edit("__Testing speed...__")
		test = speedtest.Speedtest()
		test.get_best_server()
		test.download()
		test.upload()
		test.results.share()
		result = test.results.dict()
		teks = "**Speed test done!**\n\n"
		teks += "⬇️ `{}`\n".format(speed_convert(result['download']))
		teks += "⬆️ `{}`\n".format(speed_convert(result['upload']))
		teks += "🌐 `{} ms`\n".format(result['ping'])
		teks += "💠 `{}`\n".format(result['client']['isp'])
		teks += "📍 `{}, {}`".format(result['server']['name'], result['server']['country'])
		await message.edit(teks)
