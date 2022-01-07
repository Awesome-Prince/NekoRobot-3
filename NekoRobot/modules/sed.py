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

import sre_constants

import regex
import telegram
from NekoRobot import LOGGER, dispatcher
from NekoRobot.modules.disable import DisableAbleMessageHandler
from NekoRobot.modules.helper_funcs.regex_helper import (infinite_loop_check)
from telegram import Update
from telegram.ext import CallbackContext, Filters, run_async

DELIMITERS = ("/", ":", "|", "_")


def separate_sed(sed_string):
    if len(sed_string) >= 3 and sed_string[
            1] in DELIMITERS and sed_string.count(sed_string[1]) >= 2:
        delim = sed_string[1]
        start = counter = 2
        while counter < len(sed_string):
            if sed_string[counter] == "\\":
                counter += 1

            elif sed_string[counter] == delim:
                replace = sed_string[start:counter]
                counter += 1
                start = counter
                break

            counter += 1

        else:
            return None

        while counter < len(sed_string):
            if sed_string[counter] == "\\" and counter + 1 < len(
                    sed_string) and sed_string[counter + 1] == delim:
                sed_string = sed_string[:counter] + sed_string[counter + 1:]

            elif sed_string[counter] == delim:
                replace_with = sed_string[start:counter]
                counter += 1
                break

            counter += 1
        else:
            return replace, sed_string[start:], ""

        flags = ""
        if counter < len(sed_string):
            flags = sed_string[counter:]
        return replace, replace_with, flags.lower()


@run_async
def sed(update: Update, context: CallbackContext):
    sed_result = separate_sed(update.effective_message.text)
    if sed_result and update.effective_message.reply_to_message:
        if update.effective_message.reply_to_message.text:
            to_fix = update.effective_message.reply_to_message.text
        elif update.effective_message.reply_to_message.caption:
            to_fix = update.effective_message.reply_to_message.caption
        else:
            return

        repl, repl_with, flags = sed_result
        if not repl:
            update.effective_message.reply_to_message.reply_text(
                "You're trying to replace... "
                "nothing with something?")
            return

        try:
            try:
                check = regex.match(
                    repl, to_fix, flags=regex.IGNORECASE, timeout=5)
            except TimeoutError:
                return
            if check and check.group(0).lower() == to_fix.lower():
                update.effective_message.reply_to_message.reply_text(
                    "Hey everyone, {} is trying to make "
                    "me say stuff I don't wanna "
                    "say!".format(update.effective_user.first_name))
                return
            if infinite_loop_check(repl):
                update.effective_message.reply_text(
                    "I'm afraid I can't run that regex.")
                return
            if 'i' in flags and 'g' in flags:
                text = regex.sub(
                    repl, repl_with, to_fix, flags=regex.I, timeout=3).strip()
            elif 'i' in flags:
                text = regex.sub(
                    repl, repl_with, to_fix, count=1, flags=regex.I,
                    timeout=3).strip()
            elif 'g' in flags:
                text = regex.sub(repl, repl_with, to_fix, timeout=3).strip()
            else:
                text = regex.sub(
                    repl, repl_with, to_fix, count=1, timeout=3).strip()
        except TimeoutError:
            update.effective_message.reply_text('Timeout')
            return
        except sre_constants.error:
            LOGGER.warning(update.effective_message.text)
            LOGGER.exception("SRE constant error")
            update.effective_message.reply_text(
                "Do you even sed? Apparently not.")
            return

        # empty string errors -_-
        if len(text) >= telegram.MAX_MESSAGE_LENGTH:
            update.effective_message.reply_text(
                "The result of the sed command was too long for \
                                                 telegram!")
        elif text:
            update.effective_message.reply_to_message.reply_text(text)


__help__ = """
 • `s/<text1>/<text2>(/<flag>)`*:* Reply to a message with this to perform a sed operation on that message, replacing all \
occurrences of 'text1' with 'text2'. Flags are optional, and currently include 'i' for ignore case, 'g' for global, \
or nothing. Delimiters include `/`, `_`, `|`, and `:`. Text grouping is supported. The resulting message cannot be \
larger than {}.
*Reminder:* Sed uses some special characters to make matching easier, such as these: `+*.?\\`
If you want to use these characters, make sure you escape them!
*Example:* \\?.
""".format(telegram.MAX_MESSAGE_LENGTH)

__mod_name__ = "Sed/Regex"

SED_HANDLER = DisableAbleMessageHandler(
    Filters.regex(r's([{}]).*?\1.*'.format("".join(DELIMITERS))),
    sed,
    friendly="sed")

dispatcher.add_handler(SED_HANDLER)
