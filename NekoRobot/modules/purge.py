"""
BSD 2-Clause License
Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022-2023, Awesome-Prince, [ https://github.com/Awesome-Prince]
Copyright (c) 2022-2023, Programmer Network, [ https://github.com/Awesome-Prince/NekoRobot-3 ]
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import time

from telethon import events

from NekoRobot import tbot
from NekoRobot.modules.helper_funcs.telethn.chatstatus import (
    can_delete_messages,
    user_is_admin,
)


async def purge_messages(event):
    start = time.perf_counter()
    if event.from_id is None:
        return

    if not await user_is_admin(
        user_id=event.sender_id, message=event
    ) and event.from_id not in [1087968824]:
        await event.reply("Only Admins are allowed to use this command")
        return

    if not await can_delete_messages(message=event):
        await event.reply("Can't seem to purge the message")
        return

    reply_msg = await event.get_reply_message()
    if not reply_msg:
        await event.reply("Reply to a message to select where to start purging from.")
        return
    message_id = reply_msg.id
    delete_to = event.message.id

    messages = [event.reply_to_msg_id]
    for msg_id in range(message_id, delete_to + 1):
        messages.append(msg_id)
        if len(messages) == 100:
            await event.client.delete_messages(event.chat_id, messages)
            messages = []

    try:
        await event.client.delete_messages(event.chat_id, messages)
    except:
        pass
    time_ = time.perf_counter() - start
    text = f"Purged Successfully in {time_:0.2f} Second(s)"
    await event.respond(text, parse_mode="markdown")


async def delete_messages(event):
    if event.from_id is None:
        return

    if not await user_is_admin(
        user_id=event.sender_id, message=event
    ) and event.from_id not in [1087968824]:
        await event.reply("Only Admins are allowed to use this command")
        return

    if not await can_delete_messages(message=event):
        await event.reply("Can't seem to delete this?")
        return

    message = await event.get_reply_message()
    if not message:
        await event.reply("Whadya want to delete?")
        return
    chat = await event.get_input_chat()
    del_message = [message, event.message]
    await event.client.delete_messages(chat, del_message)


__help__ = """
*Admin only:*
 - /del: deletes the message you replied to
 - /purge: deletes all messages between this and the replied to message.
 - /purge <integer X>: deletes the replied message, and X messages following it if replied to a message.
"""

PURGE_HANDLER = purge_messages, events.NewMessage(pattern="^[!/]purge$")
DEL_HANDLER = delete_messages, events.NewMessage(pattern="^[!/]del$")

tbot.add_event_handler(*PURGE_HANDLER)
tbot.add_event_handler(*DEL_HANDLER)

__mod_name__ = "Purges"
__command_list__ = ["del", "purge"]
__handlers__ = [PURGE_HANDLER, DEL_HANDLER]
