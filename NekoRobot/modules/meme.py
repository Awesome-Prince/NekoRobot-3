import html
import random
import time

import requests
from telegram import ChatPermissions, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import CallbackContext

import NekoRobot.modules.helper_funcs.string_store as fun
import NekoRobot.modules.NekoFunBot_Strings as fun_strings
from NekoRobot import NEKO_PTB, SUPPORT_CHAT
from NekoRobot.events import register
from NekoRobot.modules.disable import (
    DisableAbleCommandHandler,
    DisableAbleMessageHandler,
)
from NekoRobot.modules.helper_funcs.alternate import typing_action
from NekoRobot.modules.helper_funcs.chat_status import is_user_admin
from NekoRobot.modules.helper_funcs.extraction import extract_user

GIF_ID = "CgACAgQAAx0CSVUvGgAC7KpfWxMrgGyQs-GUUJgt-TSO8cOIDgACaAgAAlZD0VHT3Zynpr5nGxsE"


@register(pattern="^/truth ?(.*)")
async def _(td):
    try:
        resp = requests.get("https://api.safone.tech/truth").json()
        results = f"{resp['truth']}"
        return await td.reply(results)
    except Exception:
        await td.reply(f"Error Report @{SUPPORT_CHAT}")


@register(pattern="^/dare ?(.*)")
async def _(dr):
    try:
        resp = requests.get("https://api.safone.tech/dare").json()
        results = f"{resp['dare']}"
        return await dr.reply(results)
    except Exception:
        await dr.reply(f"Error Report @{SUPPORT_CHAT}")


@register(pattern="^/fact ?(.*)")
async def _(dr):
    try:
        resp = requests.get("https://api.safone.tech/fact").json()
        results = f"{resp['fact']}"
        return await dr.reply(results)
    except Exception:
        await dr.reply(f"Error Report @{SUPPORT_CHAT}")


@register(pattern="^/quotes ?(.*)")
async def _(dr):
    try:
        resp = requests.get("https://api.safone.tech/quote").json()
        results = f"{resp['quote']}"
        return await dr.reply(results)
    except Exception:
        await dr.reply(f"Error Report @{SUPPORT_CHAT}")


@register(pattern="^/joke ?(.*)")
async def _(dr):
    try:
        resp = requests.get("https://api.safone.tech/joke").json()
        results = f"{resp['joke']}"
        return await dr.reply(results)
    except Exception:
        await dr.reply(f"Error Report @{SUPPORT_CHAT}")


@register(pattern="^/bully ?(.*)")
async def _(dr):
    try:
        resp = requests.get("https://api.safone.tech/bully").json()
        results = f"{resp['bully']}"
        return await dr.reply(results)
    except Exception:
        await dr.reply(f"Error Report @{SUPPORT_CHAT}")


@register(pattern="^/advice ?(.*)")
async def _(dr):
    try:
        resp = requests.get("https://api.safone.tech/advice").json()
        results = f"{resp['advice']}"
        return await dr.reply(results)
    except Exception:
        await dr.reply(f"Error Report @{SUPPORT_CHAT}")


async def runs(update: Update, context: CallbackContext):
    update.effective_message.reply_text(random.choice(fun_strings.RUN_STRINGS))


async def sanitize(update: Update, context: CallbackContext):
    message = update.effective_message
    name = (
        message.reply_to_message.from_user.first_name
        if message.reply_to_message
        else message.from_user.first_name
    )
    reply_animation = (
        message.reply_to_message.reply_animation
        if message.reply_to_message
        else message.reply_animation
    )
    reply_animation(GIF_ID, caption=f"*Sanitizes {name}*")


async def sanitize(update: Update, context: CallbackContext):
    message = update.effective_message
    name = (
        message.reply_to_message.from_user.first_name
        if message.reply_to_message
        else message.from_user.first_name
    )
    reply_animation = (
        message.reply_to_message.reply_animation
        if message.reply_to_message
        else message.reply_animation
    )
    reply_animation(random.choice(fun_strings.GIFS), caption=f"*Sanitizes {name}*")


async def slap(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    chat = update.effective_chat

    reply_text = (
        message.reply_to_message.reply_text
        if message.reply_to_message
        else message.reply_text
    )

    curr_user = html.escape(message.from_user.first_name)
    user_id = extract_user(message, args)

    if user_id == bot.id:
        temp = random.choice(fun_strings.SLAP_YONE_TEMPLATES)

        if isinstance(temp, list):
            if temp[2] == "tmute":
                if is_user_admin(chat, message.from_user.id):
                    reply_text(temp[1])
                    return

                mutetime = int(time.time() + 60)
                bot.restrict_chat_member(
                    chat.id,
                    message.from_user.id,
                    until_date=mutetime,
                    permissions=ChatPermissions(can_send_messages=False),
                )
            reply_text(temp[0])
        else:
            reply_text(temp)
        return

    if user_id:

        slapped_user = bot.get_chat(user_id)
        user1 = curr_user
        user2 = html.escape(slapped_user.first_name)

    else:
        user1 = bot.first_name
        user2 = curr_user

    temp = random.choice(fun_strings.SLAP_TEMPLATES)
    item = random.choice(fun_strings.ITEMS)
    hit = random.choice(fun_strings.HIT)
    throw = random.choice(fun_strings.THROW)

    if update.effective_user.id == 1107959621:
        temp = "@ashenwalk scratches {user2}"

    reply = temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw)

    reply_text(reply, parse_mode=ParseMode.HTML)


async def pat(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args
    message = update.effective_message

    reply_to = message.reply_to_message if message.reply_to_message else message

    curr_user = html.escape(message.from_user.first_name)
    user_id = extract_user(message, args)

    if user_id:
        patted_user = bot.get_chat(user_id)
        user1 = curr_user
        user2 = html.escape(patted_user.first_name)

    else:
        user1 = bot.first_name
        user2 = curr_user

    pat_type = random.choice(("Text", "Gif", "Sticker"))
    if pat_type == "Gif":
        try:
            temp = random.choice(fun_strings.PAT_GIFS)
            reply_to.reply_animation(temp)
        except BadRequest:
            pat_type = "Text"

    if pat_type == "Sticker":
        try:
            temp = random.choice(fun_strings.PAT_STICKERS)
            reply_to.reply_sticker(temp)
        except BadRequest:
            pat_type = "Text"

    if pat_type == "Text":
        temp = random.choice(fun_strings.PAT_TEMPLATES)
        reply = temp.format(user1=user1, user2=user2)
        reply_to.reply_text(reply, parse_mode=ParseMode.HTML)


async def roll(update: Update, context: CallbackContext):
    update.message.reply_text(random.choice(range(1, 7)))


async def shout(update: Update, context: CallbackContext):
    args = context.args
    text = " ".join(args)
    result = []
    result.append(" ".join(list(text)))
    for pos, symbol in enumerate(text[1:]):
        result.append(symbol + " " + "  " * pos + symbol)
    result = list("\n".join(result))
    result[0] = text[0]
    result = "".join(result)
    msg = "```\n" + result + "```"
    return update.effective_message.reply_text(msg, parse_mode="MARKDOWN")


async def toss(update: Update, context: CallbackContext):
    update.message.reply_text(random.choice(fun_strings.TOSS))


async def shrug(update: Update, context: CallbackContext):
    msg = update.effective_message
    reply_text = (
        msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text
    )
    reply_text(r"¯\_(ツ)_/¯")


async def bluetext(update: Update, context: CallbackContext):
    msg = update.effective_message
    reply_text = (
        msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text
    )
    reply_text(
        "/BLUE /TEXT\n/MUST /CLICK\n/I /AM /A /STUPID /ANIMAL /THAT /IS /ATTRACTED /TO /COLORS"
    )


async def rlg(update: Update, context: CallbackContext):
    eyes = random.choice(fun_strings.EYES)
    mouth = random.choice(fun_strings.MOUTHS)
    ears = random.choice(fun_strings.EARS)

    if len(eyes) == 2:
        repl = ears[0] + eyes[0] + mouth[0] + eyes[1] + ears[1]
    else:
        repl = ears[0] + eyes[0] + mouth[0] + eyes[0] + ears[1]
    update.message.reply_text(repl)


async def decide(update: Update, context: CallbackContext):
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun_strings.DECIDE))


async def eightball(update: Update, context: CallbackContext):
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun_strings.EIGHTBALL))


async def table(update: Update, context: CallbackContext):
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun_strings.TABLE))


normiefont = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
]
weebyfont = [
    "卂",
    "乃",
    "匚",
    "刀",
    "乇",
    "下",
    "厶",
    "卄",
    "工",
    "丁",
    "长",
    "乚",
    "从",
    "𠘨",
    "口",
    "尸",
    "㔿",
    "尺",
    "丂",
    "丅",
    "凵",
    "リ",
    "山",
    "乂",
    "丫",
    "乙",
]


async def weebify(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    string = ""

    if message.reply_to_message:
        string = message.reply_to_message.text.lower().replace(" ", "  ")

    if args:
        string = "  ".join(args).lower()

    if not string:
        message.reply_text(
            "Usage is `/weebify <text>`", parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    for normiecharacter in string:
        if normiecharacter in normiefont:
            weebycharacter = weebyfont[normiefont.index(normiecharacter)]
            string = string.replace(normiecharacter, weebycharacter)

    if message.reply_to_message:
        message.reply_to_message.reply_text(string)
    else:
        message.reply_text(string)


@typing_action
async def goodnight(update, context):
    message = update.effective_message
    reply = random.choice(fun.GDNIGHT)
    message.reply_text(reply, parse_mode=ParseMode.MARKDOWN_V2)


@typing_action
async def goodmorning(update, context):
    message = update.effective_message
    reply = random.choice(fun.GDMORNING)
    message.reply_text(reply, parse_mode=ParseMode.MARKDOWN_V2)


__help__ = """
 🔹 `/runs`*:* reply a random string from an array of replies
 🔹 `/slap`*:* slap a user, or get slapped if not a reply
 🔹 `/shrug`*:* get shrug XD
 🔹 `/table`*:* get flip/unflip :v
 🔹 `/decide*:* Randomly answers yes/no/maybe
 🔹 `/toss`*:* Tosses A coin
 🔹 `/bluetext`*:* check urself :V
 🔹 `/roll*:* Roll a dice
 🔹 `/rlg`*:* Join ears,nose,mouth and create an emo ;-;
 🔹 `/weebify` <text>*:* returns a weebified text
 🔹 `/pat`*:* pats a user, or get patted
 🔹 `/8ball`*:* predicts using 8ball method 
 🔹 `/decide` can be also used with regex like: `Liza? <question>: randomly answer "Yes, No" etc.`
 🔹 `/hitler` *:* Quote a message and type this command to make a caption of hitler
"""

SANITIZE_HANDLER = DisableAbleCommandHandler("sanitize", sanitize, block=False)
RUNS_HANDLER = DisableAbleCommandHandler("runs", runs, block=False)
SLAP_HANDLER = DisableAbleCommandHandler("slap", slap, block=False)
PAT_HANDLER = DisableAbleCommandHandler("pat", pat, block=False)
ROLL_HANDLER = DisableAbleCommandHandler("roll", roll, block=False)
TOSS_HANDLER = DisableAbleCommandHandler("toss", toss, block=False)
SHRUG_HANDLER = DisableAbleCommandHandler("shrug", shrug, block=False)
BLUETEXT_HANDLER = DisableAbleCommandHandler("bluetext", bluetext, block=False)
RLG_HANDLER = DisableAbleCommandHandler("rlg", rlg, block=False)
DECIDE_HANDLER = DisableAbleCommandHandler("decide", decide, block=False)
EIGHTBALL_HANDLER = DisableAbleCommandHandler("8ball", eightball, block=False)
TABLE_HANDLER = DisableAbleCommandHandler("table", table, block=False)
SHOUT_HANDLER = DisableAbleCommandHandler("shout", shout, block=False)
WEEBIFY_HANDLER = DisableAbleCommandHandler("weebify", weebify, block=False)
GDMORNING_HANDLER = DisableAbleMessageHandler(
    Filters.regex(r"(?i)(gm|good morning)"),
    goodmorning,
    friendly="goodmorning",
    block=False,
)
GDNIGHT_HANDLER = DisableAbleMessageHandler(
    Filters.regex(r"(?i)(gn|good night)"),
    goodnight,
    friendly="goodnight",
    block=False,
)

NEKO_PTB.add_handler(WEEBIFY_HANDLER)
NEKO_PTB.add_handler(SHOUT_HANDLER)
NEKO_PTB.add_handler(SANITIZE_HANDLER)
NEKO_PTB.add_handler(RUNS_HANDLER)
NEKO_PTB.add_handler(SLAP_HANDLER)
NEKO_PTB.add_handler(PAT_HANDLER)
NEKO_PTB.add_handler(ROLL_HANDLER)
NEKO_PTB.add_handler(TOSS_HANDLER)
NEKO_PTB.add_handler(SHRUG_HANDLER)
NEKO_PTB.add_handler(BLUETEXT_HANDLER)
NEKO_PTB.add_handler(RLG_HANDLER)
NEKO_PTB.add_handler(DECIDE_HANDLER)
NEKO_PTB.add_handler(EIGHTBALL_HANDLER)
NEKO_PTB.add_handler(TABLE_HANDLER)
NEKO_PTB.add_handler(GDMORNING_HANDLER)
NEKO_PTB.add_handler(GDNIGHT_HANDLER)

__mod_name__ = "Fun"
__command_list__ = [
    "runs",
    "slap",
    "roll",
    "toss",
    "shrug",
    "bluetext",
    "rlg",
    "decide",
    "table",
    "pat",
    "sanitize",
    "shout",
    "weebify",
    "8ball",
]
__handlers__ = [
    RUNS_HANDLER,
    SLAP_HANDLER,
    PAT_HANDLER,
    ROLL_HANDLER,
    TOSS_HANDLER,
    SHRUG_HANDLER,
    BLUETEXT_HANDLER,
    RLG_HANDLER,
    DECIDE_HANDLER,
    TABLE_HANDLER,
    SANITIZE_HANDLER,
    SHOUT_HANDLER,
    WEEBIFY_HANDLER,
    EIGHTBALL_HANDLER,
    GDMORNING_HANDLER,
    GDNIGHT_HANDLER,
]
