"""
BSD 2-Clause License
Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022-2023, Awesome-Prince, [ https://github.com/Awesome-Prince]
Copyright (c) 2022-2023, BlackLover Network, [ https://github.com/Awesome-Prince/NekoRobot-3 ]
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
from platform import python_version

from pyrogram import __version__ as pyrover
from telethon import Button
from telethon import __version__ as tlhver

from NekoRobot import BOT_NAME, BOT_USERNAME, SUPPORT_CHAT, telethn
from NekoRobot.events import register

edit_time = 5
""" =======================Neko====================== """
file1 = ""
file2 = ""
file3 = ""
file4 = ""
file5 = ""
""" =======================Neko====================== """

BUTTON = [
    [
        Button.url("【► HELP ◄】", f"https://t.me/{BOT_USERNAME}?start=help"),
        Button.url("【► SUPPORT ◄】", f"https://t.me/{SUPPORT_CHAT}"),
    ]
]

START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60 * 60 * 24),
    ("hour", 60 * 60),
    ("min", 60),
    ("sec", 1),
)


def _human_time_duration(seconds):
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
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    pm_caption = f"** ♡ Hey [{yes.sender.first_name}](tg://user?id={yes.sender.id}) I'm {BOT_NAME} **\n\n"
    pm_caption += f"**♡ My Uptime :** `{uptime}`\n\n"
    pm_caption += f"**♡ Python Version :** `{python_version}`\n\n"
    pm_caption += f"**♡ Telethon Version :** `{tlhver}`\n\n"
    pm_caption += f"**♡ Pyrogram Version :** `{pyrover}`\n\n"
    pm_caption += "**♡ My Master :** [LovelyPrince](https://t.me/BlackLover_Prince) "
    BUTTON = [
        [
            Button.url("【► Help ◄】", f"https://t.me/{BOT_USERNAME}?start=help"),
            Button.url("【► Support ◄】", f"https://t.me/{SUPPORT_CHAT}"),
        ]
    ]
    on = await telethn.send_file(
        yes.chat_id, file=file1, caption=pm_caption, buttons=BUTTON, reply_to=yes
    )

    await asyncio.sleep(edit_time)
    ok = await telethn.edit_message(yes.chat_id, on, file=file2, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok2 = await telethn.edit_message(yes.chat_id, ok, file=file3, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok3 = await telethn.edit_message(yes.chat_id, ok2, file=file4, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok4 = await telethn.edit_message(yes.chat_id, ok3, file=file5, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok5 = await telethn.edit_message(yes.chat_id, ok4, file=file1, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok6 = await telethn.edit_message(yes.chat_id, ok5, file=file2, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok7 = await telethn.edit_message(yes.chat_id, ok6, file=file3, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok8 = await telethn.edit_message(yes.chat_id, ok7, file=file4, buttons=BUTTON)

    await asyncio.sleep(edit_time)
    ok9 = await telethn.edit_message(yes.chat_id, ok8, file=file5, buttons=BUTTON)
