import time

from pyrogram import Filters, errors, InlineKeyboardMarkup, InlineKeyboardButton

from nana import app, Command, Owner, BotUsername, DB_AVAIABLE, Owner
from nana.helpers.string import parse_button, build_keyboard
from nana.helpers.msg_types import Types, get_note_type, fetch_note_type

if DB_AVAIABLE:
	from nana.modules.database import notes_db as db

# TODO: Add buttons support in some types
# TODO: Add group notes, but whats for? since only you can get notes

__MODULE__ = "Notes"

GET_FORMAT = {
	Types.TEXT.value: app.send_message,
	Types.DOCUMENT.value: app.send_document,
	Types.PHOTO.value: app.send_photo,
	Types.VIDEO.value: app.send_video,
	Types.STICKER.value: app.send_sticker,
	Types.AUDIO.value: app.send_audio,
	Types.VOICE.value: app.send_voice,
	Types.VIDEO_NOTE.value: app.send_video_note,
	Types.ANIMATION.value: app.send_animation,
	Types.ANIMATED_STICKER.value: app.send_sticker,
	Types.CONTACT: app.send_contact
}


@app.on_message(Filters.user(Owner) & Filters.command(["save"], Command))
async def save_note(client, message):
	if not DB_AVAIABLE:
		await message.edit("Your database is not avaiable!")
		return
	note_name, text, data_type, content, file_ref = get_note_type(message)

	if not note_name:
		await message.edit("```" + message.text + '```\n\nError: You must give a name for this note!')
		return

	if data_type == Types.TEXT:
		file_id = None
		teks, button = parse_button(text)
		if not teks:
			await message.edit("```" + message.text + '```\n\nError: There is no text in here!')
			return
	else:
		file_id = await client.forward_messages(Owner, message.chat.id, message.reply_to_message.message_id, as_copy=True)

	db.save_selfnote(message.from_user.id, note_name, text, data_type, content, file_ref, file_id.message_id if file_id else None)
	await message.edit('Saved note `{}`!'.format(note_name))


@app.on_message(Filters.user(Owner) & Filters.command(["get"], Command))
async def get_note(client, message):
	if not DB_AVAIABLE:
		await message.edit("Your database is not avaiable!")
		return
	is_hash = False
	if len(message.text.split()) >= 2:
		note = message.text.split()[1]
	else:
		await message.edit("Give me a note tag!")

	getnotes = db.get_selfnote(message.from_user.id, note)
	if not getnotes:
		await message.edit("This note does not exist!")
		return

	replyid = None # message.message_id
	if message.reply_to_message:
		replyid = message.reply_to_message.message_id

	if getnotes['type'] == Types.TEXT:
		teks, button = parse_button(getnotes.get('value'))
		button = build_keyboard(button)
		if button:
			button = InlineKeyboardMarkup(button)
		else:
			button = None
		if button:
			await message.edit("Inline button not supported in this userbot version :(\nSee @AyraSupport for more information")
			return
		else:
			await message.edit(teks)
	elif getnotes['type'] in (Types.STICKER, Types.VOICE, Types.VIDEO_NOTE, Types.CONTACT, Types.ANIMATED_STICKER):
		await message.delete()
		try:
			if replyid:
				await GET_FORMAT[getnotes['type']](message.chat.id, getnotes['file'], file_ref=getnotes['file_ref'], reply_to_message_id=replyid)
			else:
				await GET_FORMAT[getnotes['type']](message.chat.id, getnotes['file'], file_ref=getnotes['file_ref'])
		except errors.exceptions.bad_request_400.BadRequest:
			msg = await client.get_messages(Owner, getnotes['message_id'])
			note_name, text, data_type, content, file_ref = fetch_note_type(msg)
			db.save_selfnote(Owner, note, "", getnotes['type'], content, file_ref, getnotes['message_id'])
			if replyid:
				await GET_FORMAT[getnotes['type']](message.chat.id, content, file_ref=file_ref, reply_to_message_id=replyid)
			else:
				await GET_FORMAT[getnotes['type']](message.chat.id, content, file_ref=file_ref)
	else:
		await message.delete()
		if getnotes.get('value'):
			teks, button = parse_button(getnotes.get('value'))
			button = build_keyboard(button)
			if button:
				button = InlineKeyboardMarkup(button)
			else:
				button = None
		else:
			teks = None
			button = None
		if button:
			await message.edit("Inline button not supported in this userbot version :(\nSee @AyraSupport for more information")
			return
		else:
			try:
				if replyid:
					await GET_FORMAT[getnotes['type']](message.chat.id, getnotes['file'], file_ref=getnotes['file_ref'], caption=teks, reply_to_message_id=replyid)
				else:
					await GET_FORMAT[getnotes['type']](message.chat.id, getnotes['file'], file_ref=getnotes['file_ref'], caption=teks)
			except errors.exceptions.bad_request_400.BadRequest:
				msg = await client.get_messages(Owner, getnotes['message_id'])
				note_name, text, data_type, content, file_ref = fetch_note_type(msg)
				db.save_selfnote(Owner, note, teks, getnotes['type'], content, file_ref, getnotes['message_id'])
				if replyid:
					await GET_FORMAT[getnotes['type']](message.chat.id, getnotes['file'], file_ref=getnotes['file_ref'], caption=teks, reply_to_message_id=replyid)
				else:
					await GET_FORMAT[getnotes['type']](message.chat.id, getnotes['file'], file_ref=getnotes['file_ref'], caption=teks)

@app.on_message(Filters.user(Owner) & Filters.command(["notes", "saved"], Command))
async def local_notes(client, message):
	if not DB_AVAIABLE:
		await message.edit("Your database is not avaiable!")
		return
	getnotes = db.get_all_selfnotes(message.from_user.id)
	if not getnotes:
		await message.edit("There are no notes in local notes!")
		return
	rply = "**Local notes:**\n"
	for x in getnotes:
		if len(rply) >= 1800:
			await message.reply(rply)
			rply = "**Local notes:**\n"
		rply += "- `{}`\n".format(x)

	await message.edit(rply)

@app.on_message(Filters.user(Owner) & Filters.command(["clear"], Command))
async def clear_note(client, message):
	if not DB_AVAIABLE:
		await message.edit("Your database is not avaiable!")
		return
	if len(message.text.split()) <= 1:
		await message.edit("What do you want to clear?")
		return

	note = message.text.split()[1]
	getnote = db.rm_selfnote(message.from_user.id, note)
	if not getnote:
		await message.edit("This note does not exist!")
		return

	await message.edit("Deleted note `{}`!".format(note))
