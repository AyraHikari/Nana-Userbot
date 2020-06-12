import time
import math
import random
import os

from nana import app, Command

from pyrogram import Filters
from gsearch.googlesearch import search


__MODULE__ = "Search"

@app.on_message(Filters.user("self") & Filters.command(["google"], Command))
async def google_search(client, message):
	if len(message.text.split()) == 1:
		await message.edit("Usage: `google how to search from google`")
		return
	text = message.text.split(None, 1)[1]
	results = search(text)
	teks = "<b>Search results from</b> <code>{}</code>\n".format(text)
	if results == []:
		await message.edit("Please try again later:\n`{}`".format(text), parse_mode="markdown")
		return
	for x in range(len(results)):
		teks += '<b>{}.</b> <a href="{}">{}</a>\n'.format(x+1, results[x][1], results[x][0])
	await message.edit(teks, parse_mode="html", disable_web_page_preview=True)

#@app.on_message(Filters.user("self") & Filters.command(["pic"], Command))
async def BingImages(client, message):
	if len(message.text.split()) == 1:
		await message.edit("Usage: `.pic name`")
		return
	photo = message.text.split(None, 1)[1]
	result = await client.get_inline_bot_results("@pic", photo)
	await message.edit("Random result of: " + photo)
	await client.send_inline_bot_result(message.chat.id, query_id=result.query_id, result_id=result.results[random.randint(0, len(result.results))].id, hide_via=True)
