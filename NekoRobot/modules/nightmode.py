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


from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import *
from telethon import functions
from telethon.tl.types import ChatBannedRights

from NekoRobot import OWNER_ID, tbot
from NekoRobot.events import register
from NekoRobot.modules.sql_extended.night_mode_sql import (
    add_nightmode,
    get_all_chat_id,
    is_nightmode_indb,
    rmnightmode,
)

hehes = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    send_polls=True,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)

openhehe = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    send_polls=False,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


async def can_change_info(message):
    result = await tbot(
        functions.channels.GetParticipantRequest(
            channel=message.chat_id,
            user_id=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.change_info
    )


@register(pattern="^/(nimode|Nightmode|NightMode) ?(.*)")
async def profanity(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    input = event.pattern_match.group(2)
    if event.sender_id != OWNER_ID:
        if not await is_register_admin(event.input_chat, event.sender_id):
            await event.reply("Only admins can execute this command!")
            return
        else:
            if not await can_change_info(message=event):
                await event.reply(
                    "You are missing the following rights to use this command:CanChangeinfo"
                )
                return
    if not input:
        if is_nightmode_indb(str(event.chat_id)):
            await event.reply("Currently NightMode is Enabled for this Chat")
            return
        await event.reply("Currently NightMode is Disabled for this Chat")
        return
    if "on" in input and event.is_group:
        if is_nightmode_indb(str(event.chat_id)):
            await event.reply("Night Mode is Already Turned ON for this Chat")
            return
        add_nightmode(str(event.chat_id))
        await event.reply("NightMode turned on for this chat.")
    if "off" in input:
        if event.is_group and not is_nightmode_indb(str(event.chat_id)):
            await event.reply("Night Mode is Already Off for this Chat")
            return
        rmnightmode(str(event.chat_id))
        await event.reply("NightMode Disabled!")
    if "off" not in input and "on" not in input:
        await event.reply("Please Specify On or Off!")
        return


async def job_close():
    chats = get_all_chat_id()
    if len(chats) == 0:
        return
    for pro in chats:
        try:
            await tbot.send_message(
                int(pro.chat_id),
                "12:00 Am, Group Is Closing Till 6 Am. Night Mode Started !",
            )
            await tbot(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(pro.chat_id), banned_rights=hehes
                )
            )
        except Exception as e:
            logger.info(f"Unable To Close Group {chat} - {e}")


# Run everyday at 12am
scheduler = AsyncIOScheduler(timezone="Asia/Colombo")
scheduler.add_job(job_close, trigger="cron", hour=23, minute=59)
scheduler.start()


async def job_open():
    chats = get_all_chat_id()
    if len(chats) == 0:
        return
    for pro in chats:
        try:
            await tbot.send_message(int(pro.chat_id), "06:00 Am, Group Is Opening.")
            await tbot(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(pro.chat_id), banned_rights=openhehe
                )
            )
        except Exception as e:
            logger.info(f"Unable To Open Group {pro.chat_id} - {e}")


# Run everyday at 06
scheduler = AsyncIOScheduler(timezone="Asia/Colombo")
scheduler.add_job(job_open, trigger="cron", hour=5, minute=58)
scheduler.start()


__help__ = """
 • `/nimode` on/off
 
**Note:** Night Mode chats get Automatically closed at 12pm(IST)
and Automatically openned at 6am(IST) To Prevent Night Spams.
"""


__mod_name__ = "Night Mode"
