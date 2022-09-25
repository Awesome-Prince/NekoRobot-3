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

from gpytranslate import SyncTranslator
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from NekoRobot import NEKO_PTB
from NekoRobot.modules.disable import DisableAbleCommandHandler

trans = SyncTranslator()


def translate(update: Update, context: CallbackContext) -> None:
    bot = context.bot
    message = update.effective_message
    reply_msg = message.reply_to_message
    if not reply_msg:
        message.reply_text("Reply to a message to translate it!")
        return
    if reply_msg.caption:
        to_translate = reply_msg.caption
    elif reply_msg.text:
        to_translate = reply_msg.text
    try:
        args = message.text.split()[1].lower()
        if "//" in args:
            source = args.split("//")[0]
            dest = args.split("//")[1]
        else:
            source = trans.detect(to_translate)
            dest = args
    except IndexError:
        source = trans.detect(to_translate)
        dest = "en"
    translation = trans(to_translate, sourcelang=source, targetlang=dest)
    reply = (
        f"<b>Translated from {source} to {dest}</b>:\n"
        f"<code>{translation.text}</code>"
    )

    bot.send_message(text=reply, chat_id=message.chat.id, parse_mode=ParseMode.HTML)


def languages(update: Update, context: CallbackContext) -> None:
    message = update.effective_message
    bot = context.bot
    bot.send_message(
        text="Click [here](https://telegra.ph/Lang-Codes-03-19-3) to see the list of supported language codes!",
        chat_id=message.chat.id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )


__help__ = """ 
Use this module to translate stuff!
*Commands:*
• /tl (or /tr ): as a reply to a message, translates it to English.
• /tl <lang>: translates to <lang>
eg: `/tl ja`: translates to Japanese.
• /tl <source>//<dest>: translates from <source> to <lang>.
eg: `/tl ja//en`: translates from Japanese to English.
• [List of supported languages for translation](https://telegra.ph/Lang-Codes-03-19-3)
"""

TRANSLATE_HANDLER = DisableAbleCommandHandler(["tr", "tl"], translate, run_async=True)
TRANSLATE_LANG_HANDLER = DisableAbleCommandHandler(
    ["lang", "languages"], languages, run_async=True
)

NEKO_PTB.add_handler(TRANSLATE_HANDLER)
NEKO_PTB.add_handler(TRANSLATE_LANG_HANDLER)

__mod_name__ = "Translator"
__command_list__ = ["tr", "tl", "lang", "languages"]
__handlers__ = [TRANSLATE_HANDLER, TRANSLATE_LANG_HANDLER]
