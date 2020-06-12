import os
from typing import Union

import pyrogram
from pyrogram.api import functions, types
from pyrogram.client.ext import BaseClient, utils
from pyrogram.errors import FilePartMissing

from nana import app


async def send_sticker(
    chat_id: Union[int, str],
        sticker: str,
        file_ref: str = None,
        disable_notification: bool = None,
        reply_to_message_id: int = None,
        schedule_date: int = None,
        reply_markup: Union[
            "pyrogram.InlineKeyboardMarkup",
            "pyrogram.ReplyKeyboardMarkup",
            "pyrogram.ReplyKeyboardRemove",
            "pyrogram.ForceReply"
        ] = None,
        progress: callable = None,
        progress_args: tuple = ()
    ) -> Union["pyrogram.Message", None]:
    if True:
        file = None

        try:
            if os.path.exists(sticker):
                file = await app.save_file(sticker, progress=progress, progress_args=progress_args)
                media = types.InputMediaUploadedDocument(
                    mime_type="image/webp",
                    file=file,
                    attributes=[
                        types.DocumentAttributeFilename(file_name=os.path.basename(sticker))
                    ]
                )
            elif sticker.startswith("http"):
                media = types.InputMediaDocumentExternal(
                    url=sticker
                )
            else:
                media = utils.get_input_media_from_file_id(sticker, file_ref, 8)

            while True:
                try:
                    r = await app.send(
                        functions.messages.SendMedia(
                            peer=await app.resolve_peer(chat_id),
                            media=media,
                            silent=disable_notification or None,
                            reply_to_msg_id=reply_to_message_id,
                            random_id=app.rnd_id(),
                            schedule_date=schedule_date,
                            reply_markup=reply_markup.write() if reply_markup else None,
                            message=""
                        )
                    )
                except FilePartMissing as e:
                    await app.save_file(sticker, file_id=file.id, file_part=e.x)
                else:
                    for i in r.updates:
                        if isinstance(
                            i,
                            (types.UpdateNewMessage, types.UpdateNewChannelMessage, types.UpdateNewScheduledMessage)
                        ):
                            return await pyrogram.Message._parse(
                                app, i.message,
                                {i.id: i for i in r.users},
                                {i.id: i for i in r.chats},
                                is_scheduled=isinstance(i, types.UpdateNewScheduledMessage)
                            )
        except BaseClient.StopTransmission:
            return None
    app.send(functions.channels.DeleteUserHistory(app.resolve_peer(chat.id), app.resolve_peer(user_id)))
