"""
BSD 2-Clause License
Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022-2023, Awesome-Prince, [ https://github.com/Awesome-Prince]
Copyright (c) 2022-2023,Programmer Network, [ https://github.com/Awesome-Prince/NekoRobot-3 ]
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

import ast
import asyncio
import contextlib
import html

from alphabet_detector import AlphabetDetector
from telegram import ChatPermissions, MessageEntity, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters
from telegram.helpers import mention_html

import NekoRobot.modules.sql.locks_sql as sql
from NekoRobot import LOGGER, NEKO_PTB
from NekoRobot.modules.disable import DisableAbleCommandHandler
from NekoRobot.modules.helper_funcs.admin_status import (
    AdminPerms,
    bot_admin_check,
    bot_is_admin,
    user_admin_check,
    user_is_admin,
    user_not_admin_check,
)
from NekoRobot.modules.helper_funcs.alternate import send_message
from NekoRobot.modules.helper_funcs.anonymous import user_admin
from NekoRobot.modules.helper_funcs.chat_status import connection_status
from NekoRobot.modules.log_channel import loggable
from NekoRobot.modules.sql.approve_sql import is_approved

ad = AlphabetDetector()

LOCK_TYPES = {
    "audio": filters.AUDIO,
    "voice": filters.VOICE,
    "document": filters.Document.ALL,
    "video": filters.VIDEO,
    "contact": filters.CONTACT,
    "photo": filters.PHOTO,
    "url": filters.Entity(MessageEntity.URL) | filters.CaptionEntity(MessageEntity.URL),
    "bots": filters.StatusUpdate.NEW_CHAT_MEMBERS,
    "forward": filters.FORWARDED & (~filters.IS_AUTOMATIC_FORWARD),
    "game": filters.GAME,
    "location": filters.LOCATION,
    "egame": filters.Dice.ALL,
    "rtl": "rtl",
    "button": "button",
    "inline": "inline",
    "apk": filters.Document.MimeType("application/vnd.android.package-archive"),
    "doc": filters.Document.MimeType("application/msword"),
    "exe": filters.Document.MimeType("application/x-ms-dos-executable"),
    "gif": filters.Document.MimeType("video/mp4"),
    "jpg": filters.Document.MimeType("image/jpeg"),
    "mp3": filters.Document.MimeType("audio/mpeg"),
    "pdf": filters.Document.MimeType("application/pdf"),
    "txt": filters.Document.MimeType("text/plain"),
    "xml": filters.Document.MimeType("application/xml"),
    "zip": filters.Document.MimeType("application/zip"),
}

LOCK_CHAT_RESTRICTION = {
    "all": {
        "can_send_messages": False,
        "can_send_media_messages": False,
        "can_send_polls": False,
        "can_send_other_messages": False,
        "can_add_web_page_previews": False,
        "can_change_info": False,
        "can_invite_users": False,
        "can_pin_messages": False,
    },
    "messages": {"can_send_messages": False},
    "media": {"can_send_media_messages": False},
    "sticker": {"can_send_other_messages": False},
    "gif": {"can_send_other_messages": False},
    "poll": {"can_send_polls": False},
    "other": {"can_send_other_messages": False},
    "previews": {"can_add_web_page_previews": False},
    "info": {"can_change_info": False},
    "invite": {"can_invite_users": False},
    "pin": {"can_pin_messages": False},
}

UNLOCK_CHAT_RESTRICTION = {
    "all": {
        "can_send_messages": True,
        "can_send_media_messages": True,
        "can_send_polls": True,
        "can_send_other_messages": True,
        "can_add_web_page_previews": True,
        "can_invite_users": True,
    },
    "messages": {"can_send_messages": True},
    "media": {"can_send_media_messages": True},
    "sticker": {"can_send_other_messages": True},
    "gif": {"can_send_other_messages": True},
    "poll": {"can_send_polls": True},
    "other": {"can_send_other_messages": True},
    "previews": {"can_add_web_page_previews": True},
    "info": {"can_change_info": True},
    "invite": {"can_invite_users": True},
    "pin": {"can_pin_messages": True},
}

PERM_GROUP = -8
REST_GROUP = -12


# NOT ASYNC
async def restr_members(
    bot, chat_id, members, messages=False, media=False, other=False, previews=False
):
    for mem in members:
        with contextlib.suppress(TelegramError):
            await bot.restrict_chat_member(
                chat_id,
                mem.user,
                can_send_messages=messages,
                can_send_media_messages=media,
                can_send_other_messages=other,
                can_add_web_page_previews=previews,
            )


# NOT ASYNC
async def unrestr_members(
    bot, chat_id, members, messages=True, media=True, other=True, previews=True
):
    for mem in members:
        with contextlib.suppress(TelegramError):
            await bot.restrict_chat_member(
                chat_id,
                mem.user,
                can_send_messages=messages,
                can_send_media_messages=media,
                can_send_other_messages=other,
                can_add_web_page_previews=previews,
            )


async def locktypes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "\n ➛ ".join(
            ["Locks available: "]
            + sorted(list(LOCK_TYPES) + list(LOCK_CHAT_RESTRICTION))
        )
    )


@connection_status
@bot_admin_check()
@user_admin_check(AdminPerms.CAN_CHANGE_INFO)
@loggable
async def lock(update, context) -> str:  # sourcery no-metrics
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    if bot_is_admin(chat, AdminPerms.CAN_DELETE_MESSAGES):
        if len(args) >= 1:
            ltype = args[0].lower()
            if ltype == "anonchannel":
                text = "`anonchannel` is not a lock, please use `/antichannel on` to restrict channels"
                send_message(update.effective_message, text, parse_mode="markdown")
            elif ltype in LOCK_TYPES:

                text = f"Locked {ltype} for non-admins!"
                sql.update_lock(chat.id, ltype, locked=True)
                send_message(update.effective_message, text, parse_mode="markdown")

                return f"<b>{html.escape(chat.title)}:</b>\n#LOCK\n<b>Admin:</b> {mention_html(user.id, user.first_name)}\nLocked <code>{ltype}</code>."

            if ltype in LOCK_CHAT_RESTRICTION:
                text = f"Locked {ltype} for all non-admins!"
                current_permission = context.bot.getChat(chat.id).permissions
                context.bot.set_chat_permissions(
                    chat_id=chat.id,
                    permissions=get_permission_list(
                        ast.literal_eval(str(current_permission)),
                        LOCK_CHAT_RESTRICTION[ltype.lower()],
                    ),
                )

                send_message(update.effective_message, text, parse_mode="markdown")
                return f"<b>{html.escape(chat.title)}:</b>\n#Permission_LOCK\n<b>Admin:</b> {mention_html(user.id, user.first_name)}\nLocked <code>{ltype}</code>."

            send_message(
                update.effective_message,
                "What are you trying to lock...? Try /locktypes for the list of lockables",
            )
        else:
            send_message(update.effective_message, "What are you trying to lock...?")

    else:
        send_message(
            update.effective_message,
            "I am not administrator or haven't got enough rights.",
        )

    return ""


@bot_admin_check()
@user_admin
@loggable
def unlock(update, context) -> str:  # sourcery no-metrics
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    if user_is_admin(update, user.id, allow_moderators=True):
        if len(args) >= 1:
            ltype = args[0].lower()
            if ltype == "anonchannel":
                text = "`anonchannel` is not a lock, please use `/antichannel on` to restrict channels"
                send_message(update.effective_message, text, parse_mode="markdown")
            elif ltype in LOCK_TYPES:
                text = f"Unlocked {ltype} for everyone!"
                sql.update_lock(chat.id, ltype, locked=False)
                send_message(update.effective_message, text, parse_mode="markdown")
                return f"<b>{html.escape(chat.title)}:</b>\n#UNLOCK\n<b>Admin:</b> {mention_html(user.id, user.first_name)}\nUnlocked <code>{ltype}</code>."

            if ltype in UNLOCK_CHAT_RESTRICTION:
                text = f"Unlocked {ltype} for everyone!"

                current_permission = context.bot.getChat(chat.id).permissions
                context.bot.set_chat_permissions(
                    chat_id=chat.id,
                    permissions=get_permission_list(
                        ast.literal_eval(str(current_permission)),
                        UNLOCK_CHAT_RESTRICTION[ltype.lower()],
                    ),
                )

                send_message(update.effective_message, text, parse_mode="markdown")

                return f"<b>{html.escape(chat.title)}:</b>\n#UNLOCK\n<b>Admin:</b> {mention_html(user.id, user.first_name)}\nUnlocked <code>{ltype}</code>."

            send_message(
                update.effective_message,
                "What are you trying to unlock...? Try /locktypes for the list of lockables.",
            )

        else:
            send_message(update.effective_message, "What are you trying to unlock...?")

    return ""


@user_not_admin_check
async def del_lockables(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:  # sourcery no-metrics
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]
    user = message.sender_chat or update.effective_user
    if is_approved(chat.id, user.id):
        return
    for lockable, filter in LOCK_TYPES.items():
        if lockable == "rtl":
            if sql.is_locked(chat.id, lockable) and bot_is_admin(
                chat, AdminPerms.CAN_DELETE_MESSAGES
            ):
                if message.caption:
                    check = ad.detect_alphabet(f"{message.caption}")
                    if "ARABIC" in check:
                        try:
                            # replyyy = "This action is restricted to admins only!"
                            # await message.reply_text(replyyy)
                            await message.delete()
                        except BadRequest as excp:
                            if excp.message != "Message to delete not found":
                                LOGGER.exception("ERROR in lockables")
                        break
                if message.text:
                    check = ad.detect_alphabet(f"{message.text}")
                    if "ARABIC" in check:
                        try:
                            # replyyy = "This action is restricted to admins only!"
                            # await message.reply_text(replyyy)
                            await message.delete()
                        except BadRequest as excp:
                            if excp.message != "Message to delete not found":
                                LOGGER.exception("ERROR in lockables")
                        break
            continue
        if lockable == "button":
            if (
                sql.is_locked(chat.id, lockable)
                and bot_is_admin(chat, AdminPerms.CAN_DELETE_MESSAGES)
                and message.reply_markup
                and message.reply_markup.inline_keyboard
            ):
                try:
                    # replyyy = "This action is restricted to admins only!"
                    # await message.reply_text(replyyy)
                    await message.delete()
                except BadRequest as excp:
                    if excp.message != "Message to delete not found":
                        LOGGER.exception("ERROR in lockables")
                break
            continue
        if lockable == "inline":
            if (
                sql.is_locked(chat.id, lockable)
                and bot_is_admin(chat, AdminPerms.CAN_DELETE_MESSAGES)
                and message
                and message.via_bot
            ):
                try:
                    # replyyy = "This action is restricted to admins only!"
                    # await message.reply_text(replyyy)
                    await message.delete()
                except BadRequest as excp:
                    if excp.message != "Message to delete not found":
                        LOGGER.exception("ERROR in lockables")
                break
            continue
        if (
            filter(update)
            and sql.is_locked(chat.id, lockable)
            and bot_is_admin(chat, AdminPerms.CAN_DELETE_MESSAGES)
        ):
            if lockable == "bots":
                new_members = update.effective_message.new_chat_members
                for new_mem in new_members:
                    if new_mem.is_bot:
                        if not bot_is_admin(chat, AdminPerms.CAN_RESTRICT_MEMBERS):
                            send_message(
                                update.effective_message,
                                "I see a bot and I've been told to stop them from joining..."
                                "but I'm not admin!",
                            )
                            return

                        chat.ban_member(new_mem.id)
                        send_message(
                            update.effective_message,
                            "Only admins are allowed to add bots in this chat! Get outta here.",
                        )
                        break
            else:
                try:
                    # replyyy = "This action is restricted to admins only!"
                    # await message.reply_text(replyyy)
                    await message.delete()
                except BadRequest as excp:
                    if excp.message != "Message to delete not found":
                        LOGGER.exception("ERROR in lockables")

                break


async def build_lock_message(chat_id):
    locks = sql.get_locks(chat_id)
    res = ""
    locklist = []
    permslist = []
    if locks:
        res += "*" + "These are the current locks in this Chat:" + "*"
        locklist.extend(
            (
                f"sticker = `{locks.sticker}`",
                f"audio = `{locks.audio}`",
                f"voice = `{locks.voice}`",
                f"document = `{locks.document}`",
                f"video = `{locks.video}`",
                f"contact = `{locks.contact}`",
                f"photo = `{locks.photo}`",
                f"gif = `{locks.gif}`",
                f"url = `{locks.url}`",
                f"bots = `{locks.bots}`",
                f"forward = `{locks.forward}`",
                f"game = `{locks.game}`",
                f"location = `{locks.location}`",
                f"rtl = `{locks.rtl}`",
                f"button = `{locks.button}`",
                f"egame = `{locks.egame}`",
                f"inline = `{locks.inline}`",
                "apk = f`{locks.apk}`",
                "doc = f`{locks.doc}`",
                "exe = f`{locks.exe}`",
                "jpg = f`{locks.jpg}`",
                "mp3 = f`{locks.mp3}`",
                "pdf = f`{locks.pdf}`",
                "txt = f`{locks.txt}`",
                "xml = f`{locks.xml}`",
                "zip = f`{locks.zip}`",
            )
        )

    permissions = await NEKO_PTB.bot.get_chat(chat_id).permissions
    permslist = [
        f"messages = `{permissions.can_send_messages}`",
        f"media = `{permissions.can_send_media_messages}`",
        f"poll = `{permissions.can_send_polls}`",
        f"other = `{permissions.can_send_other_messages}`",
        f"previews = `{permissions.can_add_web_page_previews}`",
        f"info = `{permissions.can_change_info}`",
        f"invite = `{permissions.can_invite_users}`",
        f"pin = `{permissions.can_pin_messages}`",
    ]

    if locklist:
        # Ordering lock list
        locklist.sort()
        # Building lock list string
        for x in locklist:
            res += f"\n ➛ {x}"
    res += "\n\n*" + "These are the current chat permissions:" + "*"
    for x in permslist:
        res += f"\n ➛ {x}"
    return res


@connection_status
@user_admin_check(AdminPerms.CAN_CHANGE_INFO)
def list_locks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user

    # Connection check
    conn = await connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = await NEKO_PTB.bot.getChat(conn)
        chat_name = chat.title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "This command is meant to use in group not in PM",
            )
            return ""
        chat = update.effective_chat
        chat_name = update.effective_message.chat.title

    res = await build_lock_message(chat.id)
    if conn:
        res = res.replace("Locks in", f"*{chat_name}*")

    send_message(update.effective_message, res, parse_mode=ParseMode.MARKDOWN_V2)


def get_permission_list(current, new):
    permissions = {
        "can_send_messages": None,
        "can_send_media_messages": None,
        "can_send_polls": None,
        "can_send_other_messages": None,
        "can_add_web_page_previews": None,
        "can_change_info": None,
        "can_invite_users": None,
        "can_pin_messages": None,
    }
    permissions |= current
    permissions |= new
    return ChatPermissions(**permissions)


def __import_data__(chat_id, data):
    # set chat locks
    locks = data.get("locks", {})
    for itemlock in locks:
        if itemlock in LOCK_TYPES:
            sql.update_lock(chat_id, itemlock, locked=True)
        elif itemlock in LOCK_CHAT_RESTRICTION:
            sql.update_restriction(chat_id, itemlock, locked=True)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return asyncio.get_running_loop().run_until_complete(build_lock_message(chat_id))


__help__ = """
Do stickers annoy you? or want to avoid people sharing links? or pictures? \
You're in the right place!
The locks module allows you to lock away some common items in the \
telegram world; the bot will automatically delete them!
➛ /locktypes*:* Lists all possible locktypes
*Admins only:*
➛ /lock <type>*:* Lock items of a certain type (not available in private)
➛ /unlock <type>*:* Unlock items of a certain type (not available in private)
➛ /locks*:* The current list of locks in this chat.
Locks can be used to restrict a group's users.
eg:
Locking urls will auto-delete all messages with urls, locking stickers will restrict all \
non-admin users from sending stickers, etc.
Locking bots will stop non-admins from adding bots to the chat.
*Note:*
 ➛ Unlocking permission *info* will allow members (non-admins) to change the group information, such as the description or the group name
 ➛ Unlocking permission *pin* will allow members (non-admins) to pinned a message in a group
"""

__mod_name__ = "Locks"

NEKO_PTB.add_handler(DisableAbleCommandHandler("locktypes", locktypes))
NEKO_PTB.add_handler(CommandHandler("lock", lock))  # , filters=Filters.group)
NEKO_PTB.add_handler(CommandHandler("unlock", unlock))  # , filters=Filters.group)
NEKO_PTB.add_handler(CommandHandler("locks", list_locks))  # , filters=Filters.group)
NEKO_PTB.add_handler(
    MessageHandler(filters.ALL & filters.ChatType.GROUPS, del_lockables), PERM_GROUP
)
