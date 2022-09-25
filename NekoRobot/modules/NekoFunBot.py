import random

import requests
from telegram.ext import Filters

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


def kiss(update, context):
    url = "https://nekos.best/api/v2/kiss"
    r = requests.get(url)
    e = r.json()
    kissme = e["results"][0]["url"]
    msg = update.effective_message
    msg.reply_video(kissme, caption="*Kisses u with all my love*~")


def pat(update, context):
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


def hug(update, context):
    msg = update.effective_message
    url = "https://nekos.best/api/v2/hug"
    r = requests.get(url)
    e = r.json()
    hugme = e["results"][0]["url"]
    if msg.reply_to_message:
        msg = update.effective_message
        name1 = msg.from_user.first_name
        name2 = msg.reply_to_message.from_user.first_name
        msg.reply_video(hugme, caption=f"*{name1} hugs {name2}*")
    else:
        msg = update.effective_message
        msg.reply_video(hugme, caption="*Hugs u with all my love*~")


def slap(update, context):
    msg = update.effective_message
    url = "https://nekos.best/api/v2/slap"
    r = requests.get(url)
    e = r.json()
    slapme = e["results"][0]["url"]
    if msg.reply_to_message:
        msg = update.effective_message
        name1 = msg.from_user.first_name
        name2 = msg.reply_to_message.from_user.first_name
        msg.reply_video(slapme, caption=f"*{name1} slaps {name2}*")
    else:
        msg = update.effective_message
        msg.reply_video(slapme, caption="Here... Take this from me.")


def blush(update, context):
    msg = update.effective_message
    url = "https://nekos.best/api/v2/blush"
    r = requests.get(url)
    e = r.json()
    blushme = e["results"][0]["url"]
    if msg.reply_to_message:
        msg = update.effective_message
        name1 = msg.from_user.first_name
        name2 = msg.reply_to_message.from_user.first_name
        msg.reply_video(blushme, caption=f"*{name1} blushes by seeing {name2}*~")
    else:
        msg = update.effective_message
        msg.reply_video(blushme, caption=f"*Oh {name1}~kun I Luv You*~")


def cute(update, context):
    msg = update.effective_message
    name = msg.from_user.first_name
    url = "https://nekos.best/api/v2/neko"
    r = requests.get(url)
    e = r.json()
    cuteme = e["results"][0]["url"]
    msg.reply_photo(cuteme, caption=f"Thank UwU {name}-Kun  *smiles and hides ^~^*")


def sleep(update, context):
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


KISS_HANDLER = MessageHandler(Filters.regex("(?i)Neko kiss"), kiss, run_async=True)
BLUSH_HANDLER = MessageHandler(Filters.regex("(?i)Neko blush"), blush, run_async=True)
PAT_HANDLER = MessageHandler(Filters.regex("(?i)Neko pat"), pat, run_async=True)
HUG_HANDLER = MessageHandler(Filters.regex("(?i)Neko hug"), hug, run_async=True)
SLAP_HANDLER = MessageHandler(Filters.regex("(?i)Neko slap"), slap, run_async=True)
CUTE_HANDLER = MessageHandler(Filters.regex("(?i)Neko cute"), cute, run_async=True)
SLEEP_HANDLER = MessageHandler(
    Filters.regex("(Neko sleep|sleep)"), sleep, run_async=True
)

NEKO_PTB.add_handler(KISS_HANDLER)
NEKO_PTB.add_handler(PAT_HANDLER)
NEKO_PTB.add_handler(HUG_HANDLER)
NEKO_PTB.add_handler(SLAP_HANDLER)
NEKO_PTB.add_handler(CUTE_HANDLER)
NEKO_PTB.add_handler(SLEEP_HANDLER)
NEKO_PTB.add_handler(BLUSH_HANDLER)
