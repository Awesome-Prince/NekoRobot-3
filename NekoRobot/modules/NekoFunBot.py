import random

import requests
from telegram.ext import Filters

from NekoRobot import dispatcher
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


def slap(update, context):
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


def blush(update, context):
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
        name1 = message.from_user.first_name
        msg.reply_video(blushme, caption="*Oh {}~kun I Luv You*~".format(name1))


def cute(update, context):
    msg = update.effective_message
    name = msg.from_user.first_name
    url = "https://nekos.best/api/v2/neko"
    r = requests.get(url)
    e = r.json()
    cuteme = e["results"][0]["url"]
    msg.reply_photo(
        cuteme, caption="Thank UwU {}-Kun  *smiles and hides ^~^*".format(name)
    )


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

dispatcher.add_handler(KISS_HANDLER)
dispatcher.add_handler(PAT_HANDLER)
dispatcher.add_handler(HUG_HANDLER)
dispatcher.add_handler(SLAP_HANDLER)
dispatcher.add_handler(CUTE_HANDLER)
dispatcher.add_handler(SLEEP_HANDLER)
