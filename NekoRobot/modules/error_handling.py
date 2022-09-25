"""
BSD 2-Clause License
Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022-2023, Awesome-Prince, [ https://github.com/Awesome-Prince ]
Copyright (c) 2022-2023, Programmer • Network, [ https://github.com/Awesome-Prince/NekoRobot-3 ]
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
import html
import io
import random
import sys
import traceback

import pretty_errors
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler

from NekoRobot import DEV_USERS, ERROR_LOGS, NEKO_PTB

from ..utils.pastebin import paste

pretty_errors.mono()


class ErrorsDict(dict):
    """A custom dict to store errors and their count"""

    def __init__(self, *args, **kwargs):
        self.raw = []
        super().__init__(*args, **kwargs)

    def __contains__(self, error):
        self.raw.append(error)
        error.identifier = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5))
        for e in self:
            if type(e) is type(error) and e.args == error.args:
                self[e] += 1
                return True
        self[error] = 0
        return False

    def __len__(self):
        return len(self.raw)


errors = ErrorsDict()


def error_callback(update: Update, context: CallbackContext):
    if not update:
        return
    if context.error not in errors:
        try:
            stringio = io.StringIO()
            pretty_errors.output_stderr = stringio
            output = pretty_errors.excepthook(
                type(context.error),
                context.error,
                context.error.__traceback__,
            )
            pretty_errors.output_stderr = sys.stderr
            pretty_error = stringio.getvalue()
            stringio.close()
        except:
            pretty_error = "Failed to create pretty error."
        tb_list = traceback.format_exception(
            None,
            context.error,
            context.error.__traceback__,
        )
        tb = "".join(tb_list)
        pretty_message = f'{pretty_error}\n-------------------------------------------------------------------------------\nAn exception was raised while handling an update\nUser: {update.effective_user.id}\nChat: {update.effective_chat.title if update.effective_chat else ""} {update.effective_chat.id if update.effective_chat else ""}\nCallback data: {update.callback_query.data if update.callback_query else "None"}\nMessage: {update.effective_message.text if update.effective_message else "No message"}\n\nFull Traceback: {tb}'

        e = html.escape(f"{context.error}")
        link = asyncio.run(paste(pretty_message))
        context.bot.send_message(
            ERROR_LOGS,
            text=f"#{context.error.identifier}\n<b>An Error has occurred:"
            f"</b>\n<code>{e}</code>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("See Errors", url=link)]],
            ),
            parse_mode="html",
        )


def list_errors(update: Update, context: CallbackContext):
    if update.effective_user.id not in DEV_USERS:
        return
    e = dict(sorted(errors.items(), key=lambda item: item[1], reverse=True))
    msg = "<b>Errors List:</b>\n"
    for x, value in e.items():
        msg += f"• <code>{x}:</code> <b>{value}</b> #{x.identifier}\n"
    msg += f"{len(errors)} have occurred since startup."
    if len(msg) > 4096:
        with open("errors_msg.txt", "w+") as f:
            f.write(msg)
        context.bot.send_document(
            update.effective_chat.id,
            open("errors_msg.txt", "rb"),
            caption="Too many errors have occured..",
            parse_mode="html",
        )
        return
    update.effective_message.reply_text(msg, parse_mode="html")


NEKO_PTB.add_error_handler(error_callback)
NEKO_PTB.add_handler(CommandHandler("errors", list_errors))
