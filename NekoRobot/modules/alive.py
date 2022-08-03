"""
MIT License
Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022 Hodacka
Copyright (c) 2022, Yūki • Black Knights Union, <https://github.com/Hodacka/NekoRobot-3>
This file is part of @NekoXRobot (Telegram Bot)
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the Software), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from telethon import Button

from NekoRobot import telethn as tbot
from NekoRobot.events import register

PHOTO = "https://telegra.ph/file/a21731c0c4c7f27a3ec16.jpg"


@register(pattern=("/alive"))
async def awake(event):
    NEKO = f"**♡ hey {event.sender.first_name} I,m Neko Robot** \n\n"
    NEKO += "**♡ I'm Working with Cuteness**\n\n"
    NEKO += "**♡ Neko: LATEST Version**\n\n"
    NEKO += "**♡ My Creator:** [LovelyPrince](t.me/DarlingPrince)\n\n"
    NEKO += "**♡ python-Telegram-Bot: 13.11**\n\n"
    BUTTON = [
        [
            Button.url("🚑 Support", "https://t.me/Koyuki_Support"),
            Button.url("📢 Updates", "https://t.me/Koyuki_Updates"),
        ]
    ]
    await tbot.send_file(event.chat_id, PHOTO, caption=NEKO, buttons=BUTTON)
