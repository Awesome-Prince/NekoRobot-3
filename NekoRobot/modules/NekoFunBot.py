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


import random

import requests

from telegram.ext import filters
from NekoRobot import NEKO_PTB
from NekoRobot.modules.disable import MessageHandler

OWO = (
    "*Neko pats {} on the head.",
    "*gently rubs {}'s head*.",
    "*Neko mofumofus {}'s head*",
    "*Neko messes up {}'s head*",
    "*Neko intensly rubs {}'s head*",
    "*{}'s waifu pats their head*",
    "*{}'s got free headpats*",
    "No pats for {}!",
)

K = "Vid" "Text" "Gif"

sleep_type = random.choice(K)


async def kiss(update, context):
    url = "https://nekos.best/api/v2/kiss"
    r = requests.get(url)
    e = r.json()
    kissme = e["results"][0]["url"]
    msg = update.effective_message
    msg.reply_video(kissme, caption="*Kisses u with all my love*~")


async def pat(update, context):
    msg = update.effective_message
    name = (
        msg.reply_to_message.from_user.first_name
        if msg.reply_to_message
        else msg.from_user.first_name
    )
    url = "https://nekos.best/api/v2/pat"
    r = requests.get(url)
    e = r.json()
    patme = e["results"][0]["url"]
    msg.reply_video(patme, caption=random.choice(OWO).format(name))


async def hug(update, context):
    msg = update.effective_message
    if msg.reply_to_message:
        url = "https://nekos.best/api/v2/hug"
        r = requests.get(url)
        e = r.json()
        hugme = e["results"][0]["url"]
        msg = update.effective_message
        name1 = msg.from_user.first_name
        name2 = msg.reply_to_message.from_user.first_name
        msg.reply_video(hugme, caption="*{} hugs {}*".format(name1, name2))
    else:
        url = "https://nekos.best/api/v2/hug"
        r = requests.get(url)
        e = r.json()
        hugme = e["results"][0]["url"]
        msg = update.effective_message
        msg.reply_video(hugme, caption="*Hugs u with all my love*~")


async def slap(update, context):
    msg = update.effective_message
    if msg.reply_to_message:
        url = "https://nekos.best/api/v2/slap"
        r = requests.get(url)
        e = r.json()
        slapme = e["results"][0]["url"]
        msg = update.effective_message
        name1 = msg.from_user.first_name
        name2 = msg.reply_to_message.from_user.first_name
        msg.reply_video(slapme, caption="*{} slaps {}*".format(name1, name2))
    else:
        url = "https://nekos.best/api/v2/slap"
        r = requests.get(url)
        e = r.json()
        slapme = e["results"][0]["url"]
        msg = update.effective_message
        msg.reply_video(slapme, caption="Here... Take this from me.")


async def blush(update, context):
    msg = update.effective_message
    if msg.reply_to_message:
        url = "https://nekos.best/api/v2/blush"
        r = requests.get(url)
        e = r.json()
        blushme = e["results"][0]["url"]
        msg = update.effective_message
        name1 = msg.from_user.first_name
        name2 = msg.reply_to_message.from_user.first_name
        msg.reply_video(
            blushme, caption="*{} blushes by seeing {}*~".format(name1, name2)
        )
    else:
        url = "https://nekos.best/api/v2/blush"
        r = requests.get(url)
        e = r.json()
        blushme = e["results"][0]["url"]
        msg = update.effective_message
        name1 = msg.from_user.first_name
        msg.reply_video(blushme, caption="*Oh {}~kun I Luv You*~".format(name1))


async def cute(update, context):
    msg = update.effective_message
    name = msg.from_user.first_name
    url = "https://nekos.best/api/v2/neko"
    r = requests.get(url)
    e = r.json()
    cuteme = e["results"][0]["url"]
    msg.reply_photo(
        cuteme, caption="Thank UwU {}-Kun  *smiles and hides ^~^*".format(name)
    )


async def sleep(update, context):
    if sleep_type == "Text":
        msg = update.effective_message
        msg.reply_text(". . . (∪｡∪)｡｡｡zzzZZ")
    if sleep_type == "Vid":
        msg = update.effective_message
        bed = "https://telegra.ph/file/f0fb71c72e059de34b565.mp4"
        msg.reply_video(bed)
    if sleep_type == "Gif":
        msg = update.effective_message
        url = "https://nekos.best/api/v2/sleep"
        r = requests.get(url)
        e = r.json()
        sleepme = e["results"][0]["url"]
        msg.reply_video(sleepme)


KISS_HANDLER = MessageHandler(filters.Regex("(?i)Neko kiss"), kiss, block=False)
BLUSH_HANDLER = MessageHandler(filters.Regex("(?i)Neko blush"), blush, block=False)
PAT_HANDLER = MessageHandler(filters.Regex("(?i)Neko pat"), pat, block=False)
HUG_HANDLER = MessageHandler(filters.Regex("(?i)Neko hug"), hug, block=False)
SLAP_HANDLER = MessageHandler(filters.Regex("(?i)Neko slap"), slap, block=False)
CUTE_HANDLER = MessageHandler(filters.Regex("(?i)Neko cute"), cute, block=False)
SLEEP_HANDLER = MessageHandler(filters.Regex("(Neko sleep|sleep)"), sleep, block=False)

NEKO_PTB.add_handler(KISS_HANDLER)
NEKO_PTB.add_handler(PAT_HANDLER)
NEKO_PTB.add_handler(HUG_HANDLER)
NEKO_PTB.add_handler(SLAP_HANDLER)
NEKO_PTB.add_handler(CUTE_HANDLER)
NEKO_PTB.add_handler(SLEEP_HANDLER)
NEKO_PTB.add_handler(BLUSH_HANDLER)
