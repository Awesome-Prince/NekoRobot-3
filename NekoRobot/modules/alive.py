"""
BSD 2-Clause License
Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022-2023, Awesome-Prince, [ https://github.com/Awesome-Prince ]
Copyright (c) 2022-2023, BlackLover • Network, [ https://github.com/Awesome-Prince/NekoRobot-3 ]
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

import datetime
from datetime import datetime
from platform import python_version

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext

from NekoRobot import BOT_NAME, BOT_USERNAME, NEKO_PTB, SUPPORT_CHAT
from NekoRobot.modules.disable import DisableAbleCommandHandler

""" =======================Neko====================== """
NEKOX = (
    "https://telegra.ph/file/cd7aad1ea310312886358.png"
    "https://telegra.ph/file/48a97320463caa61dba3d.png"
    "https://telegra.ph/file/2295a7207495eccbbe298.png"
    "https://telegra.ph/file/67e0bf231a97cd2e364ea.png"
    "https://telegra.ph/file/990684ecd3d119fa9fec6.png"
)
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

    NEKO_ALIVE = f"""
    *♡ Hey [{user.first_name}](tg://user?id={user.id})
    I'm {BOT_NAME}*
    ➖➖➖➖➖➖➖➖➖➖➖➖➖
    *♡ My Uptime :* `{uptime}`
    *♡ Python Version :* `{python_version()}`
    *♡ My Master :* [LovelyPrince](https://t.me/BlackLover_Prince)
    ➖➖➖➖➖➖➖➖➖➖➖➖➖
    *Thanks For Adding Me In* {chat_name}
    """

    buttons = [
        [
            InlineKeyboardButton(
                "【► Help ◄】", f"https://t.me/{BOT_USERNAME}?start=help"
            ),
            InlineKeyboardButton("【► Support ◄】", f"https://t.me/{SUPPORT_CHAT}"),
        ]
    ]

    hmm = message.reply_photo(
        random.choice(NEKOX),
        caption=NEKO_ALIVE,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN,
    )


ALIVE_HANDLER = DisableAbleCommandHandler("alive", awake, run_async=True)
NEKO_PTB.add_handler(ALIVE_HANDLER)
__command_list__ = ["alive"]
__handlers__ = [
    ALIVE_HANDLER,
]
