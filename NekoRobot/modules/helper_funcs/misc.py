import os
import cv2
from typing import Dict, List, Union
from html import escape
import ffmpeg

from math import ceil


from NekoRobot import NO_LOAD
from telegram import MAX_MESSAGE_LENGTH, Bot, InlineKeyboardButton, ParseMode
from telegram.error import TelegramError


class EqInlineKeyboardButton(InlineKeyboardButton):

    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def split_message(msg: str) -> List[str]:
    if len(msg) < MAX_MESSAGE_LENGTH:
        return [msg]

    else:
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

        return result


def paginate_modules(page_n: int, module_dict: Dict, prefix, chat=None) -> List:
    if not chat:
        modules = sorted([
            EqInlineKeyboardButton(
                x.__mod_name__,
                callback_data="{}_module({})".format(prefix,
                                                     x.__mod_name__.lower()))
            for x in module_dict.values()
        ])
    else:
        modules = sorted([
            EqInlineKeyboardButton(
                x.__mod_name__,
                callback_data="{}_module({},{})".format(prefix, chat,
                                                        x.__mod_name__.lower()))
            for x in module_dict.values()
        ])

    pairs = [
    modules[i * 3:(i + 1) * 3] for i in range((len(modules) + 3 - 1) // 3)
    ]

    round_num = len(modules) / 3
    calc = len(modules) - round(round_num)
    if calc == 1:
        pairs.append((modules[-1], ))
    elif calc == 2:
        pairs.append((modules[-1], ))

    max_num_pages = ceil(len(pairs) / 10)
    modulo_page = page_n % max_num_pages

    # can only have a certain amount of buttons side by side
    if len(pairs) > 8:
        pairs = pairs[modulo_page * 8:8 * (modulo_page + 1)] + [
            (EqInlineKeyboardButton("《", callback_data="{}_prev({})".format(prefix, modulo_page)),
                EqInlineKeyboardButton("Close", callback_data="neko_back"),
             EqInlineKeyboardButton("》", callback_data="{}_prev({})".format(prefix, modulo_page)))]

    else:
        pairs +=[[EqInlineKeyboardButton("Close", callback_data="neko_back")]]

    return pairs


def send_to_list(bot: Bot,
                 send_to: list,
                 message: str,
                 markdown=False,
                 html=False) -> None:
    if html and markdown:
        raise Exception("Can only send with either markdown or HTML!")
    for user_id in set(send_to):
        try:
            if markdown:
                bot.send_message(
                    user_id, message, parse_mode=ParseMode.MARKDOWN)
            elif html:
                bot.send_message(user_id, message, parse_mode=ParseMode.HTML)
            else:
                bot.send_message(user_id, message)
        except TelegramError:
            pass  # ignore users who fail


def build_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def revert_buttons(buttons):
    res = ""
    for btn in buttons:
        if btn.same_line:
            res += "\n[{}](buttonurl://{}:same)".format(btn.name, btn.url)
        else:
            res += "\n[{}](buttonurl://{})".format(btn.name, btn.url)

    return res


def build_keyboard_parser(bot, chat_id, buttons):
    keyb = []
    for btn in buttons:
        if btn.url == "{rules}":
            btn.url = "http://t.me/{}?start={}".format(bot.username, chat_id)
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb

def convert_gif(input):
    """Function to convert mp4 to webm(vp9)"""

    vid = cv2.VideoCapture(input)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)

    #check height and width to scale
    if width > height:
        width = 512
        height = -1
    elif height > width:
        height = 512
        width = -1
    elif width == height:
        width = 512
        height = 512


    converted_name = 'kangsticker.webm'

    (
        ffmpeg
            .input(input)
            .filter('fps', fps=30, round="up")
            .filter('scale', width=width, height=height)
            .trim(start="00:00:00", end="00:00:03", duration="3")
            .output(converted_name, vcodec="libvpx-vp9", 
                        **{
                            #'vf': 'scale=512:-1',
                            'crf': '30'
                            })
            .overwrite_output()
            .run()
    )

def is_module_loaded(name):
    return name not in NO_LOAD
