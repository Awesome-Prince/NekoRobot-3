import random

from telegram import ParseMode
from telethon import Button

from NekoRobot import OWNER_ID, SUPPORT_CHAT
from NekoRobot import telethn as tbot

from ..events import register


@register(pattern="/feedback ?(.*)")
async def feedback(e):
    quew = e.pattern_match.group(1)
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    NEKO = (
        "https://telegra.ph/file/e5c3bbe019bcf1b9ae5f2.jpg",
        "https://telegra.ph/file/0ba843f671d4a1a0a85bc.jpg",
        "https://telegra.ph/file/a41b6429a30efb83eec1b.jpg",
        "https://telegra.ph/file/43800df04a77f0c6283b8.jpg",
        "https://telegra.ph/file/6e44ad8e4a2a1a9bafa5e.jpg",
    )
    UNFEED = ("https://telegra.ph/file/80eaba068d71e0715b425.jpg",)
    BUTTON = [[Button.url("View Feedback✨", f"https://t.me/NekoXRobot")]]
    TEXT = "Thanks For Your Feedback, I Hope You Enjoy Our Service"
    GIVE = "Give Some Text For Feedback✨"
    logger_text = f"""
**New Feedback**

**From User:** {mention}
**Username:** @{e.sender.username}
**User ID:** `{e.sender.id}`
**Feedback:** `{e.text}`
"""
    if e.sender_id != OWNER_ID and not quew:
        await e.reply(
            GIVE,
            parse_mode=ParseMode.MARKDOWN,
            buttons=BUTTON,
            file=random.choice(UNFEED),
        ),
        return

    await tbot.send_message(
        SUPPORT_CHAT,
        f"{logger_text}",
        file=random.choice(NEKO),
        link_preview=False,
    )
    await e.reply(TEXT, file=random.choice(NEKO), buttons=BUTTON)
