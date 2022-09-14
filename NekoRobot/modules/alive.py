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

import random
from platform import python_version

from pyrogram import __version__ as pyrover
from telethon import Button
from telethon import __version__ as tlhver

from NekoRobot import BOT_USERNAME, SUPPORT_CHAT, tbot
from NekoRobot.events import register

PRINCE = (
    "https://telegra.ph/file/cd7aad1ea310312886358.jpg",
    "https://telegra.ph/file/48a97320463caa61dba3d.jpg",
    "https://telegra.ph/file/2295a7207495eccbbe298.jpg",
    "https://telegra.ph/file/67e0bf231a97cd2e364ea.jpg",
    "https://telegra.ph/file/990684ecd3d119fa9fec6.jpg",
)


@register(pattern="^/alive$")
def alive(event):
    NEKO = f"** ♡ Hey [{event.sender.first_name}](tg://user?id={event.sender.id}) I,m NekoRobot **\n\n"
    NEKO += f"**♡ Python Version :** `{python_version}`\n\n"
    NEKO += f"**♡ Telethon Version :** `{tlhver}`\n\n"
    NEKO += f"**♡ Pyrogram Version :** `{pyrover}`\n\n"
    NEKO += "**♡ My Master :** [LovelyPrince](https://t.me/BlackLover_Prince) "
    BUTTON = [
        [
            Button.url("【► HELP ◄】", f"https://t.me/{BOT_USERNAME}?start=help"),
            Button.url("【► SUPPORT ◄】", f"https://t.me/{SUPPORT_CHAT}"),
        ]
    ]
    tbot.send_file(
        event.chat_id, random.choice(PRINCE), caption=NEKO, buttons=BUTTON
    )
