"""
STATUS: Code is working. ✅
"""

"""
GNU General Public License v3.0

Copyright (C) 2022, SOME-1HING [https://github.com/SOME-1HING]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
import datetime
from datetime import datetime
from platform import python_version

from NekoRobot import BOT_NAME, BOT_USERNAME, NEKO_PTB, SUPPORT_CHAT
from NekoRobot.modules.disable import DisableAbleCommandHandler
from telegram import ParseMode, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

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

def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append("{} {}{}".format(amount, unit, "" if amount == 1 else "s"))
    return ", ".join(parts)

def awake(update: Update, context: CallbackContext):
    message = update.effective_message

    user = message.from_user
    chat_name = update.effective_message.chat.title

    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = _human_time_duration(int(uptime_sec))
    NekoX = f"** ♡ Hey [{user.first_name}](tg://user?id={user.id}) I'm {BOT_NAME} **\n\n"
    NekoX += f"**♡ My Uptime :** `{uptime}`\n\n"
    NekoX += f"**♡ Python Version :** `{python_version()}`\n\n"
    NekoX += "**♡ My Master :** [LovelyPrince](https://t.me/BlackLover_Prince) "
    NekoX += f"Thanks For Adding Me In {chat_name}"
    buttons = [
        [
           InlineKeyboardButton("【► Help ◄】", f"https://t.me/{BOT_USERNAME}?start=help"),
           InlineKeyboardButton("【► Support ◄】", f"https://t.me/{SUPPORT_CHAT}"),
        ]
    ]

    hmm = message.reply_photo(file2, caption=NekoX, reply_markup=InlineKeyboardMarkup(buttons),parse_mode=ParseMode.MARKDOWN)

    asyncio.sleep(edit_time)
    hmm1 = hmm.edit_photo(file3, reply_markup=InlineKeyboardMarkup(buttons),parse_mode=ParseMode.MARKDOWN)

    asyncio.sleep(edit_time)
    hmm2 = hmm1.edit_photo(file4, reply_markup=InlineKeyboardMarkup(buttons),parse_mode=ParseMode.MARKDOWN)

    asyncio.sleep(edit_time)
    hmm3 = hmm2.edit_photo(file1, reply_markup=InlineKeyboardMarkup(buttons),parse_mode=ParseMode.MARKDOWN)

    asyncio.sleep(edit_time)
    hmm4 = hmm3.edit_photo(file2, reply_markup=InlineKeyboardMarkup(buttons),parse_mode=ParseMode.MARKDOWN)

    asyncio.sleep(edit_time)
    hmm5 = hmm4.edit_photo(file1, reply_markup=InlineKeyboardMarkup(buttons),parse_mode=ParseMode.MARKDOWN)

    asyncio.sleep(edit_time)
    hmm6 = hmm5.edit_photo(file3, reply_markup=InlineKeyboardMarkup(buttons),parse_mode=ParseMode.MARKDOWN)

    asyncio.sleep(edit_time)
    hmm6.edit_photo(file4, reply_markup=InlineKeyboardMarkup(buttons),parse_mode=ParseMode.MARKDOWN)

ALIVE_HANDLER = DisableAbleCommandHandler("alive", awake, run_async=True)
NEKO_PTB.add_handler(ALIVE_HANDLER)
__command_list__ = ["alive"]
__handlers__ = [
    ALIVE_HANDLER,
]
