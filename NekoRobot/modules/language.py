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

from typing import Union, List, Dict, Callable, Generator, Any
import itertools
from collections.abc import Iterable
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton

from NekoRobot import dispatcher
import NekoRobot.modules.sql.language_sql as sql
from NekoRobot.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from NekoRobot.langs import get_string, get_languages, get_language



def paginate(
    iterable: Iterable, page_size: int
) -> Generator[List, None, None]:
    while True:
        i1, i2 = itertools.tee(iterable)
        iterable, page = (
            itertools.islice(i1, page_size, None),
            list(itertools.islice(i2, page_size)),
        )
        if not page:
            break
        yield page


def gs(chat_id: Union[int, str], string: str) -> str:
    lang = sql.get_chat_lang(chat_id)
    return get_string(lang, string)


@user_admin
def set_lang(update: Update, _) -> None:
    chat = update.effective_chat
    msg = update.effective_message

    msg_text = gs(chat.id, "curr_chat_lang").format(
        get_language(sql.get_chat_lang(chat.id))[:-3]
    )

    keyb = [InlineKeyboardButton(
                text=name,
                callback_data=f"setLang_{code}",
            ) for code, name in get_languages().items()]
    keyb = list(paginate(keyb, 2))
    keyb.append(
        [
            InlineKeyboardButton(
                text="Help us in translations",
                url="https://poeditor.com/join/project?hash=oJISpjNcEx",
            )
        ]
    )
    msg.reply_text(msg_text, reply_markup=InlineKeyboardMarkup(keyb))


@user_admin_no_reply
def lang_button(update: Update, _) -> None:
    query = update.callback_query
    chat = update.effective_chat

    query.answer()
    lang = query.data.split("_")[1]
    sql.set_lang(chat.id, lang)

    query.message.edit_text(
        gs(chat.id, "set_chat_lang").format(get_language(lang)[:-3])
    )


SETLANG_HANDLER = CommandHandler("language", set_lang)
SETLANG_BUTTON_HANDLER = CallbackQueryHandler(lang_button, pattern=r"setLang_")

dispatcher.add_handler(SETLANG_HANDLER)
dispatcher.add_handler(SETLANG_BUTTON_HANDLER)
