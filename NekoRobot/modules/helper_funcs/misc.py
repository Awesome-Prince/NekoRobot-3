"""
MIT License

Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022 Awesome-Prince
Copyright (c) 2022, BlackLover • Network, <https://github.com/Awesome-Prince/NekoRobot-3>

This file is part of @NekoXRobot (Telegram Bot)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is

furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import base64
import contextlib
import json
import zlib
from asyncio import sleep
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse, urlunparse

import base58
import requests
from Crypto import Hash, Protocol, Random
from Crypto.Cipher import AES
from telegram import MAX_MESSAGE_LENGTH, Bot, InlineKeyboardButton, ParseMode
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
    if len(msg) < MAX_MESSAGE_LENGTH:
        return [msg]

    lines = msg.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < MAX_MESSAGE_LENGTH:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line
    # Else statement at the end of the for loop, so append the leftover string.
    result.append(small_msg)

    return


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
                await bot.send_message(user_id, message, parse_mode=ParseMode.MARKDOWN)
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


def upload_text(data: str) -> Optional[str]:
    passphrase = Random.get_random_bytes(32)
    salt = Random.get_random_bytes(8)
    key = Protocol.KDF.PBKDF2(
        passphrase, salt, 32, 100000, hmac_hash_module=Hash.SHA256
    )
    compress = zlib.compressobj(wbits=-15)
    paste_blob = (
        compress.compress(json.dumps({"paste": data}, separators=(",", ":")).encode())
        + compress.flush()
    )
    cipher = AES.new(key, AES.MODE_GCM)
    paste_meta = [
        [
            base64.b64encode(cipher.nonce).decode(),
            base64.b64encode(salt).decode(),
            100000,
            256,
            128,
            "aes",
            "gcm",
            "zlib",
        ],
        "syntaxhighlighting",
        0,
        0,
    ]
    cipher.update(json.dumps(paste_meta, separators=(",", ":")).encode())
    ct, tag = cipher.encrypt_and_digest(paste_blob)
    resp = requests.post(
        "https://bin.nixnet.services",
        headers={"X-Requested-With": "JSONHttpRequest"},
        data=json.dumps(
            {
                "v": 2,
                "adata": paste_meta,
                "ct": base64.b64encode(ct + tag).decode(),
                "meta": {"expire": "1week"},
            },
            separators=(",", ":"),
        ),
    )
    data = resp.json()
    url = list(urlparse(urljoin("https://bin.nixnet.services", data["url"])))
    url[5] = base58.b58encode(passphrase).decode()
    return urlunparse(url)
