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

from functools import wraps
from threading import RLock
from time import perf_counter

from cachetools import TTLCache
from pyrogram import filters
from telegram import Chat, ChatMember, Update, User
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from NekoRobot import (
    DEL_CMDS,
    DEV_USERS,
    NEKO_PTB,
    SUDO_USERS,
    SUPPORT_CHAT,
    SUPPORT_USERS,
    TIGERS,
    WHITELIST_USERS,
)

# stores admemes in memory for 10 min.
ADMIN_CACHE = TTLCache(maxsize=512, ttl=60 * 10, timer=perf_counter)
THREAD_LOCK = RLock()


async def is_whitelist_plus(
    chat: Chat, user_id: int, member: ChatMember = None
) -> bool:
    return any(
        user_id in user
        for user in [WHITELIST_USERS, TIGERS, SUPPORT_USERS, SUDO_USERS, DEV_USERS]
    )


async def is_support_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return user_id in SUPPORT_USERS or user_id in SUDO_USERS or user_id in DEV_USERS


async def is_sudo_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return user_id in SUDO_USERS or user_id in DEV_USERS


async def is_stats_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return user_id in DEV_USERS


async def user_can_changeinfo(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_change_info


async def user_can_promote(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_promote_members


async def user_can_pin(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_pin_messages


async def is_user_admin(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    if (
        chat.type == "private"
        or user_id in SUDO_USERS
        or user_id in DEV_USERS
        or chat.all_members_are_administrators
        or user_id in {777000, 1087968824}
    ):  # Count telegram and Group Anonymous as admin
        return True
    if member:
        return member.status in ("administrator", "creator")

    with THREAD_LOCK:
        # try to fetch from cache first.
        try:
            return user_id in ADMIN_CACHE[chat.id]
        except (KeyError, IndexError):
            # keyerror happend means cache is deleted,
            # so query bot api again and return user status
            # while saving it in cache for future useage...
            chat_admins = NEKO_PTB.bot.getChatAdministrators(chat.id)
            admin_list = [x.user.id for x in chat_admins]
            ADMIN_CACHE[chat.id] = admin_list

            return user_id in admin_list


async def is_bot_admin(chat: Chat, bot_id: int, bot_member: ChatMember = None) -> bool:
    if chat.type == "private" or chat.all_members_are_administrators:
        return True

    if not bot_member:
        bot_member = chat.get_member(bot_id)

    return bot_member.status in ("administrator", "creator")


async def can_delete(chat: Chat, bot_id: int) -> bool:
    return chat.get_member(bot_id).can_delete_messages


async def is_user_ban_protected(
    chat: Chat, user_id: int, member: ChatMember = None
) -> bool:
    if (
        chat.type == "private"
        or user_id in SUDO_USERS
        or user_id in DEV_USERS
        or user_id in WHITELIST_USERS
        or user_id in TIGERS
        or chat.all_members_are_administrators
        or user_id in {777000, 1087968824}
    ):  # Count telegram and Group Anonymous as admin
        return True

    if not member:
        member = chat.get_member(user_id)

    return member.status in ("administrator", "creator")


async def is_user_in_chat(chat: Chat, user_id: int) -> bool:
    member = chat.get_member(user_id)
    return member.status not in ("left", "kicked")


async def dev_plus(func):
    @wraps(func)
    async def is_dev_plus_func(
        update: Update, context: CallbackContext, *args, **kwargs
    ):
        context.bot
        user = update.effective_user

        if user.id in DEV_USERS:
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass
        else:
            update.effective_message.reply_text(
                "This is a developer restricted command."
                "You do not have permissions to run this.",
            )

    return is_dev_plus_func


async def sudo_plus(func):
    @wraps(func)
    async def is_sudo_plus_func(
        update: Update, context: CallbackContext, *args, **kwargs
    ):
        context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_sudo_plus(chat, user.id):
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass
        else:
            update.effective_message.reply_text(
                "At Least be an Admin to use these all Commands",
            )

    return is_sudo_plus_func


async def stats_plus(func):
    @wraps(func)
    async def is_stats_plus_func(
        update: Update, context: CallbackContext, *args, **kwargs
    ):
        context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_stats_plus(chat, user.id):
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass
        else:
            update.effective_message.reply_text(
                "Neko stats is just for Dev User",
            )

    return is_sudo_plus_func


async def support_plus(func):
    @wraps(func)
    async def is_support_plus_func(
        update: Update, context: CallbackContext, *args, **kwargs
    ):
        context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_support_plus(chat, user.id):
            return func(update, context, *args, **kwargs)
        if DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass

    return is_support_plus_func


async def whitelist_plus(func):
    @wraps(func)
    async def is_whitelist_plus_func(
        update: Update,
        context: CallbackContext,
        *args,
        **kwargs,
    ):
        context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_whitelist_plus(chat, user.id):
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(
            f"You don't have access to use this.\nVisit @{SUPPORT_CHAT}",
        )

    return is_whitelist_plus_func


async def user_admin(func):
    @wraps(func)
    async def is_admin(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_user_admin(chat, user.id):
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass
        else:
            update.effective_message.reply_text(
                "At Least be an Admin to use these all Commands",
            )

    return is_admin


async def user_admin_no_reply(func):
    @wraps(func)
    async def is_not_admin_no_reply(
        update: Update,
        context: CallbackContext,
        *args,
        **kwargs,
    ):
        context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_user_admin(chat, user.id):
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass

    return is_not_admin_no_reply


async def user_not_admin(func):
    @wraps(func)
    async def is_not_admin(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and not is_user_admin(chat, user.id):
            return func(update, context, *args, **kwargs)

    return is_not_admin


async def bot_admin(func):
    @wraps(func)
    async def is_admin(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            not_admin = "I'm not admin!"
        else:
            not_admin = f"I'm not admin in <b>{update_chat_title}</b>! "

        if is_bot_admin(chat, bot.id):
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(not_admin, parse_mode=ParseMode.HTML)

    return is_admin


async def bot_can_delete(func):
    @wraps(func)
    async def delete_rights(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            cant_delete = "I can't delete messages here!\nMake sure I'm admin and can delete other user's messages."
        else:
            cant_delete = f"I can't delete messages in <b>{update_chat_title}</b>!\nMake sure I'm admin and can delete other user's messages there."

        if can_delete(chat, bot.id):
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(cant_delete, parse_mode=ParseMode.HTML)

    return delete_rights


async def can_pin(func):
    @wraps(func)
    async def pin_rights(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            cant_pin = (
                "I can't pin messages here!\nMake sure I'm admin and can pin messages."
            )
        else:
            cant_pin = f"I can't pin messages in <b>{update_chat_title}</b>!\nMake sure I'm admin and can pin messages there."

        if chat.get_member(bot.id).can_pin_messages:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(cant_pin, parse_mode=ParseMode.HTML)

    return pin_rights


async def can_promote(func):
    @wraps(func)
    async def promote_rights(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            cant_promote = "I can't promote/demote people here!\nMake sure I'm admin and can appoint new admins."
        else:
            cant_promote = (
                f"I can't promote/demote people in <b>{update_chat_title}</b>!\n"
                f"Make sure I'm admin there and have the permission to appoint new admins."
            )

        if chat.get_member(bot.id).can_promote_members:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(cant_promote, parse_mode=ParseMode.HTML)

    return promote_rights


async def can_restrict(func):
    @wraps(func)
    async def restrict_rights(
        update: Update, context: CallbackContext, *args, **kwargs
    ):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            cant_restrict = "I can't restrict people here!\nMake sure I'm admin and can restrict users."
        else:
            cant_restrict = f"I can't restrict people in <b>{update_chat_title}</b>!\nMake sure I'm admin there and can restrict users."

        if chat.get_member(bot.id).can_restrict_members:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(
            cant_restrict,
            parse_mode=ParseMode.HTML,
        )

    return restrict_rights


async def user_can_ban(func):
    @wraps(func)
    async def user_is_banhammer(
        update: Update, context: CallbackContext, *args, **kwargs
    ):
        context.bot
        user = update.effective_user.id
        member = update.effective_chat.get_member(user)
        if (
            not member.can_restrict_members
            and member.status != "creator"
            and user not in SUDO_USERS
            and user not in [777000, 1087968824]
        ):
            update.effective_message.reply_text(
                "Sorry son, but you're not worthy to wield the banhammer.",
            )
            return ""
        return func(update, context, *args, **kwargs)

    return user_is_banhammer


async def connection_status(func):
    @wraps(func)
    async def connected_status(
        update: Update, context: CallbackContext, *args, **kwargs
    ):
        conn = connected(
            context.bot,
            update,
            update.effective_chat,
            update.effective_user.id,
            need_admin=False,
        )

        if conn:
            chat = NEKO_PTB.bot.getChat(conn)
            update.__setattr__("_effective_chat", chat)
        elif update.effective_message.chat.type == "private":
            update.effective_message.reply_text(
                "Send /connect in a group that you and I have in common first.",
            )
            return connected_status

        return func(update, context, *args, **kwargs)

    return connected_status


from NekoRobot.modules import connection

connected = connection.connected


async def callbacks_in_filters(data):
    return filters.create(lambda flt, _, query: flt.data in query.data, data=data)
