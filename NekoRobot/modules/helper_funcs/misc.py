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

import contextlib
from asyncio import sleep
from typing import Dict, List

from telegram import Bot, InlineKeyboardButton
from telegram.constants import MessageLimit, ParseMode
from telegram.error import TelegramError

from NekoRobot import NO_LOAD


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def delete(delmsg, timer):
    sleep(timer)
    try:
        delmsg.delete()
    except:
        return


def split_message(msg: str) -> List[str]:
    if len(msg) < MessageLimit.TEXT_LENGTH:
        return [msg]

    lines = msg.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < MessageLimit.TEXT_LENGTH:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line
    # Else statement at the end of the for loop, so append the leftover string.
    result.append(small_msg)

    return result


def paginate_modules(
    _: int, module_dict: Dict, prefix, chat=None
) -> List[List[EqInlineKeyboardButton]]:
    modules = (
        sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data=f"{prefix}_module({x.__mod_name__.lower()})",
                )
                for x in module_dict.values()
            ]
        )
        if chat
        else sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data=f"{prefix}_module({chat},{x.__mod_name__.lower()})",
                )
                for x in module_dict.values()
            ]
        )
    )

    pairs = [list(a) for a in zip(modules[::3], modules[1::3], modules[2::3])]

    round_num = len(modules) / 3
    calc = len(modules) - round(round_num)
    if calc in [1, 2]:
        pairs.append((modules[-1],))
    else:
        pairs += [[EqInlineKeyboardButton("[► Back ◄]", callback_data="neko_back")]]

    return pairs


async def send_to_list(
    bot: Bot, send_to: list, message: str, markdown=False, html=False
) -> None:  # sourcery skip: raise-specific-error
    if html and markdown:
        raise Exception("Can only send with either markdown or HTML!")
    for user_id in set(send_to):
        with contextlib.suppress(TelegramError):
            if markdown:
                await bot.send_message(
                    user_id, message, parse_mode=ParseMode.MARKDOWN_V2
                )
            elif html:
                await bot.send_message(user_id, message, parse_mode=ParseMode.HTML)
            else:
                await bot.send_message(user_id, message)


def build_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def revert_buttons(buttons):
    return "".join(
        f"\n[{btn.name}](buttonurl://{btn.url}:same)"
        if btn.same_line
        else f"\n[{btn.name}](buttonurl://{btn.url})"
        for btn in buttons
    )


def build_keyboard_parser(bot, chat_id, buttons):
    keyb = []
    for btn in buttons:
        if btn.url == "{rules}":
            btn.url = f"http://https://telegram.dog/{bot.username}?start={chat_id}"
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def is_module_loaded(name):
    return name not in NO_LOAD
