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

import sre_constants

import regex
import telegram
from telegram import Update
from telegram.ext import CallbackContext, Filters

from NekoRobot import LOGGER, NEKO_PTB
from NekoRobot.modules.disable import DisableAbleMessageHandler
from NekoRobot.modules.helper_funcs.regex_helper import infinite_loop_check

DELIMITERS = ("/", ":", "|", "_")


def separate_sed(sed_string):
    if (
        len(sed_string) >= 3
        and sed_string[1] in DELIMITERS
        and sed_string.count(sed_string[1]) >= 2
    ):
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
            if (
                sed_string[counter] == "\\"
                and counter + 1 < len(sed_string)
                and sed_string[counter + 1] == delim
            ):
                sed_string = sed_string[:counter] + sed_string[counter + 1 :]

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
                "You're trying to replace... " "nothing with something?"
            )
            return

        try:
            try:
                check = regex.match(repl, to_fix, flags=regex.IGNORECASE, timeout=5)
            except TimeoutError:
                return
            if check and check.group(0).lower() == to_fix.lower():
                update.effective_message.reply_to_message.reply_text(
                    "Hey everyone, {} is trying to make "
                    "me say stuff I don't wanna "
                    "say!".format(update.effective_user.first_name)
                )
                return
            if infinite_loop_check(repl):
                update.effective_message.reply_text(
                    "I'm afraid I can't run that regex."
                )
                return
            if "i" in flags and "g" in flags:
                text = regex.sub(
                    repl, repl_with, to_fix, flags=regex.I, timeout=3
                ).strip()
            elif "i" in flags:
                text = regex.sub(
                    repl, repl_with, to_fix, count=1, flags=regex.I, timeout=3
                ).strip()
            elif "g" in flags:
                text = regex.sub(repl, repl_with, to_fix, timeout=3).strip()
            else:
                text = regex.sub(repl, repl_with, to_fix, count=1, timeout=3).strip()
        except TimeoutError:
            update.effective_message.reply_text("Timeout")
            return
        except sre_constants.error:
            LOGGER.warning(update.effective_message.text)
            LOGGER.exception("SRE constant error")
            update.effective_message.reply_text("Do you even sed? Apparently not.")
            return

        # empty string errors -_-
        if len(text) >= telegram.MAX_MESSAGE_LENGTH:
            update.effective_message.reply_text(
                "The result of the sed command was too long for \
                                                 telegram!"
            )
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
""".format(
    telegram.MAX_MESSAGE_LENGTH
)

__mod_name__ = "Sed/Regex"

SED_HANDLER = DisableAbleMessageHandler(
    Filters.regex(r"s([{}]).*?\1.*".format("".join(DELIMITERS))),
    sed,
    friendly="sed",
    run_async=True,
)

NEKO_PTB.add_handler(SED_HANDLER)
