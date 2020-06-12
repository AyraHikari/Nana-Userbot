import math
from datetime import datetime

from pyrogram import Filters

from nana import Owner, app, Command

__MODULE__ = "Purges"


@app.on_message(Filters.me & Filters.command(["purge"], Command))
async def purge(client, message):
    if message.reply_to_message:
        start_t = datetime.now()
        user_id = None
        from_user = None
        start_message = message.reply_to_message.message_id
        end_message = message.message_id
        list_of_messages = await client.get_messages(chat_id=message.chat.id,
                                                    message_ids=range(start_message, end_message),
                                                    replies=0)
        list_of_messages_to_delete = []
        purged_messages_count = 0
        for a_message in list_of_messages:
            if len(list_of_messages_to_delete) == 100:
                await client.delete_messages(chat_id=message.chat.id,
                                            message_ids=list_of_messages_to_delete,
                                            revoke=True)
                purged_messages_count += len(list_of_messages_to_delete)
                list_of_messages_to_delete = []
            if from_user is not None:
                if a_message.from_user == from_user:
                    list_of_messages_to_delete.append(a_message.message_id)
            else:
                list_of_messages_to_delete.append(a_message.message_id)
        await client.delete_messages(chat_id=message.chat.id,
                                    message_ids=list_of_messages_to_delete,
                                    revoke=True)
        purged_messages_count += len(list_of_messages_to_delete)
        end_t = datetime.now()
        time_taken_s = (end_t - start_t).seconds
        await message.delete()
    else:
        out = "Reply to a message to to start purge."
        await message.delete()


@app.on_message(Filters.me & Filters.command(["purgeme"], Command))
async def purge_myself(client, message):
    if len(message.text.split()) >= 2 and message.text.split()[1].isdigit():
        target = int(message.text.split()[1])
    else:
        await message.edit("Give me a number for a range!")
    get_msg = await client.get_history(message.chat.id)
    listall = []
    counter = 0
    for x in get_msg:
        if counter == target + 1:
            break
        if x.from_user.id == int(Owner):
            listall.append(x.message_id)
            counter += 1
    if len(listall) >= 101:
        total = len(listall)
        semua = listall
        jarak = 0
        jarak2 = 0
        for x in range(math.ceil(len(listall) / 100)):
            if total >= 101:
                jarak2 += 100
                await client.delete_messages(message.chat.id, message_ids=semua[jarak:jarak2])
                jarak += 100
                total -= 100
            else:
                jarak2 += total
                await client.delete_messages(message.chat.id, message_ids=semua[jarak:jarak2])
                jarak += total
                total -= total
    else:
        await client.delete_messages(message.chat.id, message_ids=listall)


@app.on_message(Filters.me & Filters.command(["del"], Command))
async def delete_replied(client, message):
    msg_ids = [message.message_id]
    if message.reply_to_message:
        msg_ids.append(message.reply_to_message.message_id)
    await client.delete_messages(message.chat.id, msg_ids)
