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

import asyncio
import datetime
from datetime import datetime

from pyrogram import __version__ as pyrover
from telegram import __version__ as ptb
from telethon import Button
from telethon import __version__ as tlhver

from NekoRobot import BOT_NAME, BOT_USERNAME, SUPPORT_CHAT
from NekoRobot import tbot as neko
from NekoRobot.events import register

edit_time = 5
""" =======================Neko====================== """
file1 = "https://telegra.ph/file/cd7aad1ea310312886358.png"
file2 = "https://telegra.ph/file/48a97320463caa61dba3d.png"
file3 = "https://telegra.ph/file/2295a7207495eccbbe298.png"
file4 = "https://telegra.ph/file/67e0bf231a97cd2e364ea.png"
file5 = "https://telegra.ph/file/990684ecd3d119fa9fec6.png"
""" =======================Neko====================== """

START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60 * 60 * 24),
    ("hour", 60 * 60),
    ("min", 60),
    ("sec", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append(f'{amount} {unit}{"" if amount == 1 else "s"}')
    return ", ".join(parts)


@register(pattern=("/alive"))
async def hmm(yes):
    await yes.get_chat()
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    NekoX = f"** ♡ Hey [{yes.sender.first_name}](tg://user?id={yes.sender.id}) I'm {BOT_NAME} **\n\n"
    NekoX += f"**♡ My Uptime :** `{uptime}`\n\n"
    NekoX += f"**♡ Python-telegram-bot Version :** `{ptb}`\n\n"
    NekoX += f"**♡ Telethon Version :** `{tlhver}`\n\n"
    NekoX += f"**♡ Pyrogram Version :** `{pyrover}`\n\n"
    NekoX += "**♡ My Master :** [LovelyPrince](https://t.me/Its_IZ_PRINCE_xD) "
    NekoX += f"Thanks For Adding Me In {yes.chat.title}"
    BUTTON = [
        [
            Button.url("【► Help ◄】", f"https://t.me/{BOT_USERNAME}?start=help"),
            Button.url("【► Support ◄】", f"https://t.me/{SUPPORT_CHAT}"),
        ]
    ]
    on = await neko.send_file(yes.chat_id, file=file2, caption=NekoX, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok = await neko.edit_message(yes.chat_id, on, file=file3, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok2 = await neko.edit_message(yes.chat_id, ok, file=file4, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok3 = await neko.edit_message(yes.chat_id, ok2, file=file1, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok4 = await neko.edit_message(yes.chat_id, ok3, file=file2, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok5 = await neko.edit_message(yes.chat_id, ok4, file=file1, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok6 = await neko.edit_message(yes.chat_id, ok5, file=file3, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok7 = await neko.edit_message(yes.chat_id, ok6, file=file4, buttons=BUTTON)
