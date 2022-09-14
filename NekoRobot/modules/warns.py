"""
BSD 2-Clause License
Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022-2023, Awesome-Prince, [ https://github.com/Awesome-Prince]
Copyright (c) 2022-2023, Programmer Network, [ https://github.com/Awesome-Prince/NekoRobot-3 ]
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

import html
import re
import NekoRobot.modules.sql.rules_sql as rules_sql

from typing import Optional

from NekoRobot import BAN_STICKER, BOT_USERNAME, DEV_USERS, OWNER_ID, SUDO_USERS, WHITELIST_USERS, NEKO_PTB
from NekoRobot.modules.disable import DisableAbleCommandHandler

from NekoRobot.modules.helper_funcs.extraction import (
    extract_text,
    extract_user,
    extract_user_and_text,
)
from NekoRobot.modules.helper_funcs.misc import split_message
from NekoRobot.modules.helper_funcs.string_handling import split_quotes
from NekoRobot.modules.log_channel import loggable
from NekoRobot.modules.sql import warns_sql as sql
from NekoRobot.modules.sql.approve_sql import is_approved
from NekoRobot.modules.helper_funcs.admin_status import user_admin_check, bot_admin_check, AdminPerms, bot_is_admin, user_is_admin
from NekoRobot.modules.helper_funcs.chat_status import is_user_admin
from telegram import (
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
    User,
)
from telegram.error import BadRequest
from telegram.constants import ParseMode, MessageLimit
from telegram.ext import (
    ContextTypes,
    filters,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler
)
from telegram.helpers import mention_html

WARN_HANDLER_GROUP = 9
CURRENT_WARNING_FILTER_STRING = "<b>Current warning filters in this chat:</b>\n"
WARNS_GROUP = 2
MAX_MESSAGE_LENGTH = MessageLimit.TEXT_LENGTH

async def warn_immune(message, update, uid, warner):

    if user_is_admin(update, uid):
        if uid is OWNER_ID:
            await message.reply_text("NThis is my CREATOR, how dare you!")
            return True
        if uid in DEV_USERS:
            await message.reply_text("NThis user is one of my Devs, go cry somewhere else.")
            return True
        if uid in SUDO_USERS:
            await message.reply_text("NThis user is a SUDO user, i'm not gonna warn him!")
            return True
        await message.reply_text("NDamn admins, They are too far to be warned!")
        return True

    if uid not in WHITELIST_USERS:
        return False
    if warner:
        await message.reply_text("NWhitelisted users are warn immune.")
        return True
    await message.reply_text(
        "A whitelisted user triggered an auto warn filter!\nI can't warn them users but they should avoid abusing this."
    )
    return True

# Not async
async def warn(
    user: User, update: Update, reason: str, message: Message, warner: User = None
) -> Optional[str]:  # sourcery no-metrics
    chat = update.effective_chat
    if warn_immune(message=message, update=update, uid=user.id, warner=warner):
        return

    if warner:
        warner_tag = mention_html(warner.id, warner.first_name)
    else:
        warner_tag = "Automated warn filter."

    limit, soft_warn = sql.get_warn_setting(chat.id)
    num_warns, reasons = sql.warn_user(user.id, chat.id, reason)
    if num_warns >= limit:
        sql.reset_warns(user.id, chat.id)
        if soft_warn:  # kick
            chat.unban_member(user.id)
            reply = (
                f"<b>╔━「 Kick Event 」</b>\n"
                f"<b>➛ User:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>➛ Count:</b> {limit}"
            )

        else:  # ban
            chat.ban_member(user.id)
            reply = (
                f"<b>╔━「 Ban Event 」</b>\n"
                f"<b>➛ User:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>➛ Count:</b> {limit}"
            )

        for warn_reason in reasons:
            reply += f"\n - {html.escape(warn_reason)}"

        message.bot.send_sticker(chat.id, BAN_STICKER)  # Saitama's sticker
        keyboard = None
        log_reason = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#WARN_BAN\n"
            f"<b>Admin:</b> {warner_tag}\n"
            f"<b>User:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Counts:</b> <code>{num_warns}/{limit}</code>"
        )

    else:
        keyboard = [
            [
                InlineKeyboardButton(
                    "🚨 Remove Warn", callback_data=f"rm_warn({user.id})"
                )
            ]
        ]

        if rules := rules_sql.get_rules(chat.id):
            keyboard[0].append(
                InlineKeyboardButton(
                    "📝 Rules",
                    url=f"t.me/{BOT_USERNAME}?start={chat.id}",
                )
            )


        reply = (
            f"<b>╔━「 Warn Event 」</b>\n"
            f"<b>➛ User:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>➛ Count:</b> {num_warns}/{limit}"
        )
        if reason:
            reply += f"\n<b>➛ Reason:</b> {html.escape(reason)}"
        reply += '\nPlease take some of your precious time to read the rules!'

        log_reason = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#WARN\n"
            f"<b>Admin:</b> {warner_tag}\n"
            f"<b>User:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Counts:</b> <code>{num_warns}/{limit}</code>"
        )

    try:
        await message.reply_text(reply, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML,
        )
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            await message.reply_text(
                reply, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML, quote=False
            )
        else:
            raise
    return log_reason

# Not async
async def swarn(
    user: User, update: Update, reason: str, message: Message, dels, warner: User = None,
) -> str:  # sourcery no-metrics
    if warn_immune(message=message, update=update, uid=user.id, warner=warner):
        return
    chat = update.effective_chat

    if warner:
        warner_tag = mention_html(warner.id, warner.first_name)
    else:
        warner_tag = "Automated warn filter."

    limit, soft_warn = sql.get_warn_setting(chat.id)
    num_warns, reasons = sql.warn_user(user.id, chat.id, reason)
    if num_warns >= limit:
        sql.reset_warns(user.id, chat.id)
        if soft_warn:  # kick
            chat.unban_member(user.id)
            reply = (
                f"<b>╔━「Kick Event 」</b>\n"
                f"<b>➛ User:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>➛ Count:</b> {limit}"
            )

        else:  # ban
            chat.ban_member(user.id)
            reply = (
                f"><b>╔━「 Ban Event 」</b>\n"
                f"<b>➛ User:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>➛ Count:</b> {limit}"
            )

        for warn_reason in reasons:
            reply += f"\n - {html.escape(warn_reason)}"

        message.bot.send_sticker(chat.id, BAN_STICKER)  # Saitama's sticker
        keyboard = None
        log_reason = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#WARN_BAN\n"
            f"<b>Admin:</b> {warner_tag}\n"
            f"<b>User:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User ID:</b> <code>{user.id}</code>\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Counts:</b> <code>{num_warns}/{limit}</code>"
        )

    else:
        keyboard = [
            [
                InlineKeyboardButton(
                    "🚨 Remove Warn", callback_data=f"rm_warn({user.id})"
                )
            ]
        ]

        if rules := rules_sql.get_rules(chat.id):
            keyboard[0].append(
                InlineKeyboardButton(
                    "📝 Rules",
                    url=f"t.me/{BOT_USERNAME}?start={chat.id}",
                )
            )


        reply = (
            f"<b>╔━「 Warn Event 」</b>\n"
            f"<b>➛ User:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>➛ Count:</b> {num_warns}/{limit}\n"

        )
        if reason:
            reply += f"\n<code> </code><b>➛ Reason:</b> {html.escape(reason)}"

        reply += f"\nPlease take some of your precious time to read the rules!"

        log_reason = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#WARN\n"
            f"<b>Admin:</b> {warner_tag}\n"
            f"<b>User:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User ID:</b> <code>{user.id}</code>\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Counts:</b> <code>{num_warns}/{limit}</code>"
        )

    try:
        if dels and message.reply_to_message:
            await message.reply_to_message.delete()
        await message.reply_text(reply, InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML,
        )
        await message.delete()
    except BadRequest as excp:
        if excp.message != "Reply message not found":
            raise
        # Do not reply
        if message.reply_to_message:
            await message.reply_to_message.delete()
        await message.reply_text(
            reply, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML, quote=False
        )
        await message.delete()
    return log_reason

# Not async
async def dwarn(
    user: User, update: Update, reason: str, message: Message, warner: User = None
) -> str:  # sourcery no-metrics
    if warn_immune(message=message, update=update, uid=user.id, warner=warner):
        return
    chat = update.effective_chat
    if warner:
        warner_tag = mention_html(warner.id, warner.first_name)
    else:
        warner_tag = "Automated warn filter."

    limit, soft_warn = sql.get_warn_setting(chat.id)
    num_warns, reasons = sql.warn_user(user.id, chat.id, reason)
    if num_warns >= limit:
        sql.reset_warns(user.id, chat.id)
        if soft_warn:  # kick
            chat.unban_member(user.id)
            reply = (
                f"<b>╔━「 Kick Event 」</b>\n"
                f"<b>➛ User:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>➛ Count:</b> {limit}"
            )
        else:  # ban
            chat.ban_member(user.id)
            reply = (
                f"><b>╔━「 Ban Event 」</b>\n"
                f"<b>➛ User:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>➛ Count:</b> {limit}"
            )

        for warn_reason in reasons:
            reply += f"\n - {html.escape(warn_reason)}"

        message.bot.send_sticker(chat.id, BAN_STICKER)  # Saitama's sticker
        keyboard = None
        log_reason = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#WARN_BAN\n"
            f"<b>Admin:</b> {warner_tag}\n"
            f"<b>User:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Counts:</b> <code>{num_warns}/{limit}</code>"
        )

    else:
        keyboard = [
            [
                InlineKeyboardButton(
                    "🚨 Remove Warn", callback_data=f"rm_warn({user.id})"
                )
            ]
        ]

        if rules := rules_sql.get_rules(chat.id):
            keyboard[0].append(
                InlineKeyboardButton(
                    "📝 Rules",
                    url=f"t.me/{BOT_USERNAME}?start={chat.id}",
                )
            )


        reply = (
            f"<b>╔━「 Warn Event 」</b>\n"
            f"<b>➛ User:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>➛ Count:</b> {num_warns}/{limit}"
        )
        if reason:
            reply += f"\n<code> </code><b>➛ Reason:</b> {html.escape(reason)}"
        reply += f"\nPlease take some of your precious time to read the rules!"

        log_reason = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#WARN\n"
            f"<b>Admin:</b> {warner_tag}\n"
            f"<b>User:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Counts:</b> <code>{num_warns}/{limit}</code>"
        )

    try:
        if message.reply_to_message:
            await message.reply_to_message.delete()
        await message.reply_text(reply, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML,
        )
    except BadRequest as excp:
        if excp.message != "Reply message not found":
            raise
        # Do not reply
        if message.reply_to_message:
            await message.reply_to_message.delete()
        await message.reply_text(reply,
                                 reply_markup=InlineKeyboardMarkup(keyboard),
                                 parse_mode = ParseMode.HTML,
                                 quote=False)
    return log_reason

@bot_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@user_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query  # type: Optional[CallbackQuery]
    user = update.effective_user  # type: Optional[User]
    if match := re.match(r"rm_warn\((.+?)\)", query.data):
        user_id = match[1]
        chat = update.effective_chat  # type: Optional[Chat]
        if not is_user_admin(update, int(user.id)):
            await query.answer(text="You are not authorized to remove this warn! Only administrators may remove warns.", show_alert=True)
            return ""
        if res := sql.remove_warn(user_id, chat.id):
            await update.effective_message.edit_text(
                f"Warn removed by {mention_html(user.id, user.first_name)}." if not is_anon(user, chat) else "anon admin")

            user_member = await chat.get_member(user_id)
            return "<b>{}:</b>" \
                   "\n#UNWARN" \
                   "\n<b>Admin:</b> {}" \
                   "\n<b>User:</b> {} (<code>{}</code>)".format(html.escape(chat.title),
                                                                mention_html(user.id, user.first_name),
                                                                mention_html(user_member.user.id, user_member.user.first_name),
                                                                user_member.user.id)
        await update.effective_message.edit_text(
            "User has already has no warns.".format(mention_html(user.id, user.first_name)),
            parse_mode=ParseMode.HTML,
            )
            return ""


@bot_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@user_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    warner: Optional[User] = update.effective_user

    user_id, reason = await extract_user_and_text(message, args)

    if (message.reply_to_message and message.reply_to_message.sender_chat) or user_id < 0:
        message.reply_text("This command can't be used on channels, however you can ban them instead.")
        return ""
    
    if message.text.startswith('/s') or message.text.startswith('!s') or message.text.startswith('>s'):
        silent = True
        if not bot_is_admin(chat, AdminPerms.CAN_DELETE_MESSAGES):
            return ""
    else:
        silent = False
    if message.text.startswith('/d') or message.text.startswith('!d') or message.text.startswith('>d'):
        delban = True
        if not bot_is_admin(chat, AdminPerms.CAN_DELETE_MESSAGES):
            return ""
    else:
        delban = False
    if message.text.startswith('/ds') or message.text.startswith('!ds') or message.text.startswith('>ds'):
        delsilent = True
        if not bot_is_admin(chat, AdminPerms.CAN_DELETE_MESSAGES):
            return ""
    else:
        delsilent = False
    if silent:
        dels = False
        if user_id:
            if (
                message.reply_to_message
                and message.reply_to_message.from_user.id == user_id
            ):
                return swarn(
                    message.reply_to_message.from_user,
                    update,
                    reason,
                    message,
                    dels,
                    warner,
                )
            return swarn(chat.get_member(user_id).user, update, reason, message, dels, warner)
        else:
            await message.reply_text("NThat looks like an invalid User ID to me.")
    if not delsilent and delban and user_id:
        if (
            message.reply_to_message
            and message.reply_to_message.from_user.id == user_id
        ):
            return dwarn(
                message.reply_to_message.from_user,
                update,
                reason,
                message,
                warner,
            )
        return dwarn(chat.get_member(user_id).user, update, reason, message, warner)
    elif not delsilent and delban or not delsilent and not user_id:
        await message.reply_text("NThat looks like an invalid User ID to me.")
    elif not delsilent:
        if (
            message.reply_to_message
            and message.reply_to_message.from_user.id == user_id
        ):
            return await warn(
                message.reply_to_message.from_user,
                update,
                reason,
                message.reply_to_message,
                warner,
            )
        return await warn(chat.get_member(user_id).user, update, reason, message, warner)
    else:
        dels = True
        if user_id:
            if (
                message.reply_to_message
                and message.reply_to_message.from_user.id == user_id
            ):
                return swarn(
                    message.reply_to_message.from_user,
                    update,
                    reason,
                    message,
                    dels,
                    warner,
                )
            return swarn(chat.get_member(user_id).user, update, reason, message, dels, warner)
        else:
            await message.reply_text("NThat looks like an invalid User ID to me.")
    return ""

@bot_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@user_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
async def reset_warns(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user

    if user_id:= extract_user(message, args):
        sql.reset_warns(user_id, chat.id)
        await message.reply_text("NWarns have been reset!")
        warned = await chat.get_member(user_id).user
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#RESETWARNS\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(warned.id, warned.first_name)}\n"
            f"<b>User ID:</b> <code>{warned.id}</code>"
        )
    await message.reply_text("NNo user has been designated!")
    return ""

async def warns(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    user_id = extract_user(message, args) or update.effective_user.id
    result = sql.get_warns(user_id, chat.id)

    if result and result[0] != 0:
        num_warns, reasons = result
        limit, soft_warn = sql.get_warn_setting(chat.id)

        if reasons:
            text = (
                f"This user has {num_warns}/{limit} warns, for the following reasons:"
            )
            for reason in reasons:
                text += f"\n ➛ {reason}"

            msgs = split_message(text)
            for msg in msgs:
                await update.effective_message.reply_text(msg)
        else:
            await update.effective_message.reply_text(
                f"User has {num_warns}/{limit} warns, but no reasons for any of them."
            )
    else:
        await update.effective_message.reply_text("This user doesn't have any warns!")

@bot_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
# NEKO_PTB handler stop - do not async
@user_admin_check(AdminPerms.CAN_CHANGE_INFO)
async def add_warn_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat: Optional[Chat] = update.effective_chat
    msg: Optional[Message] = update.effective_message
    user = update.effective_user

    args = msg.text.split(
        None, 1
    )  # use python's maxsplit to separate Cmd, keyword, and reply_text

    if len(args) < 2:
        return

    extracted = split_quotes(args[1])

    if len(extracted) < 2:
        return

    # set trigger -> lower, so as to avoid adding duplicate filters with different cases
    keyword = extracted[0].lower()
    content = extracted[1]

    # Note: perhaps handlers can be removed somehow using sql.get_chat_filters
    for handler in NEKO_PTB.handlers.get(WARN_HANDLER_GROUP, []):
        if handler.filters == (keyword, chat.id):
            NEKO_PTB.remove_handler(handler, WARN_HANDLER_GROUP)

    sql.add_warn_filter(chat.id, keyword, content)

    await update.effective_message.reply_text(f"Warn handler added for '{keyword}'!")

@bot_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@user_admin_check(AdminPerms.CAN_CHANGE_INFO)
async def remove_warn_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat: Optional[Chat] = update.effective_chat
    msg: Optional[Message] = update.effective_message
    user = update.effective_user

    args = msg.text.split(
        None, 1
    )  # use python's maxsplit to separate Cmd, keyword, and reply_text

    if len(args) < 2:
        return

    extracted = split_quotes(args[1])

    if len(extracted) < 1:
        return

    to_remove = extracted[0]

    chat_filters = sql.get_chat_warn_triggers(chat.id)

    if not chat_filters:
        await msg.reply_text("No warning filters are active here!")
        return

    for filt in chat_filters:
        if filt == to_remove:
            sql.remove_warn_filter(chat.id, to_remove)
            await msg.reply_text("Okay, I'll stop warning people for that.")

    await msg.reply_text(
        "That's not a current warning filter - run /warnlist for all active warning filters."
    )

async def list_warn_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat: Optional[Chat] = update.effective_chat
    all_handlers = sql.get_chat_warn_triggers(chat.id)

    if not all_handlers:
        await update.effective_message.reply_text("No warning filters are active here!")
        return

    filter_list = CURRENT_WARNING_FILTER_STRING
    for keyword in all_handlers:
        entry = f" - {html.escape(keyword)}\n"
        if len(entry) + len(filter_list) > MAX_MESSAGE_LENGTH:
            await update.effective_message.reply_text(filter_list, parse_mode=ParseMode.HTML,
            )
            filter_list = entry
        else:
            filter_list += entry

    if filter_list != CURRENT_WARNING_FILTER_STRING:
        await update.effective_message.reply_text(filter_list, parse_mode=ParseMode.HTML,
        )


@loggable
async def reply_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    chat: Optional[Chat] = update.effective_chat
    message: Optional[Message] = update.effective_message
    user: Optional[User] = update.effective_user

    if not user:  # Ignore channel
        return

    if user.id == 777000:
        return
    if is_approved(chat.id, user.id):
        return

    chat_warn_filters = sql.get_chat_warn_triggers(chat.id)
    to_match = extract_text(message)
    if not to_match:
        return ""

    for keyword in chat_warn_filters:
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            user: Optional[User] = update.effective_user
            warn_filter = sql.get_warn_filter(chat.id, keyword)
            return await warn(user, update, warn_filter.reply, message)
    return ""

@user_admin_check(AdminPerms.CAN_CHANGE_INFO)
@loggable
async def set_warn_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat: Optional[Chat] = update.effective_chat
    user = update.effective_user
    msg: Optional[Message] = update.effective_message
    if args:
        if args[0].isdigit():
            if int(args[0]) < 3:
                await msg.reply_text("The minimum warn limit is 3!")
            else:
                sql.set_warn_limit(chat.id, int(args[0]))
                await msg.reply_text(f"Updated the warn limit to {args[0]}")
                return (
                    f"<b>{html.escape(chat.title)}:</b>\n"
                    f"#SET_WARN_LIMIT\n"
                    f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                    f"Set the warn limit to <code>{args[0]}</code>"
                )
        else:
            await msg.reply_text("Give me a number as an arg!")
    else:
        limit, _ = sql.get_warn_setting(chat.id)

        await msg.reply_text(f"The current warn limit is {limit}")
    return ""


@user_admin_check(AdminPerms.CAN_CHANGE_INFO)
async def set_warn_strength(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user
    msg: Optional[Message] = update.effective_message


    if args:
        if args[0].lower() in ("on", "yes"):
            sql.set_warn_strength(chat.id, False)
            await msg.reply_text("Too many warns will now result in a Ban!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has enabled strong warns. Users will be banned"
            )

        if args[0].lower() in ("off", "no"):
            sql.set_warn_strength(chat.id, True)
            await msg.reply_text(
                "Too many warns will now result in a kick! Users will be able to join again after."
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has disabled bans. I will just kick users."
            )
        await msg.reply_text("I only understand on/yes/no/off!")
    else:
        limit, soft_warn = sql.get_warn_setting(chat.id)
        if soft_warn:
            await msg.reply_text(
                "Warns are currently set to *kick* users when they exceed the limits.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        else:
            await msg.reply_text(
                "Warns are currently set to *Ban* users when they exceed the limits.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
    return ""


def __stats__():
    return (
        f"➛ {sql.num_warns()} overall warns, across {sql.num_warn_chats()} chats.\n"
        f"➛ {sql.num_warn_filters()} warn filters, across {sql.num_warn_filter_chats()} chats."
    )


def __import_data__(chat_id, data):
    for user_id, count in data.get("warns", {}).items():
        for _ in range(int(count)):
            sql.warn_user(user_id, chat_id)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    num_warn_filters = sql.num_warn_chat_filters(chat_id)
    limit, soft_warn = sql.get_warn_setting(chat_id)
    return (
        f"This chat has `{num_warn_filters}` warn filters. "
        f"It takes `{limit}` warns before the user gets *{'kicked' if soft_warn else 'banned'}*."
    )

__help__ = """
➛ /warns <userhandle>*:* get a user's number, and reason, of warnings.
➛ /warnlist*:* list of all current warning filters
*Admin only:*
➛ /warn <userhandle>*:* warn a user. After 3 warns, the user will be banned from the group. Can also be used as a reply.
➛ /resetwarn <userhandle>*:* reset the warnings for a user. Can also be used as a reply.
➛ /addwarn <keyword> <reply message>*:* set a warning filter on a certain keyword. If you want your keyword to \
be a sentence, encompass it with quotes, as such*:* `/addwarn "very angry" This is an angry user`. 
➛ /nowarn <keyword>*:* stop a warning filter
➛ /warnlimit <num>*:* set the warning limit
➛ /strongwarn <on/yes/off/no>*:* If set to on, exceeding the warn limit will result in a ban. Else, will just kick.
  """

__mod_name__ = "Warnings"

NEKO_PTB.add_handler(CommandHandler(["swarn", "dwarn",  "dswarn", "warn"], warn_user, filters=filters.ChatType.GROUPS, block=False))
NEKO_PTB.add_handler(CommandHandler(["resetwarn", "resetwarns"], reset_warns, filters=filters.ChatType.GROUPS, block=False))
NEKO_PTB.add_handler(CommandHandler(["rmwarn", "unwarn"], remove_warns, filters=filters.ChatType.GROUPS, block=False))
NEKO_PTB.add_handler(CallbackQueryHandler(button, pattern=r"rm_warn"))
NEKO_PTB.add_handler(DisableAbleCommandHandler("warns", warns, filters=filters.ChatType.GROUPS))
NEKO_PTB.add_handler(CommandHandler("addwarn", add_warn_filter, filters=filters.ChatType.GROUPS, block=False))
NEKO_PTB.add_handler(CommandHandler(["nowarn", "stopwarn"], remove_warn_filter, filters=filters.ChatType.GROUPS, block=False))
NEKO_PTB.add_handler(DisableAbleCommandHandler(["warnlist", "warnfilters"], list_warn_filters, filters=filters.ChatType.GROUPS,admin_ok=True))
NEKO_PTB.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & (~filters.UpdateType.EDITED_MESSAGE), reply_filter))
NEKO_PTB.add_handler(CommandHandler("warnlimit", set_warn_limit, filters=filters.ChatType.GROUPS,block=False))
NEKO_PTB.add_handler(CommandHandler("strongwarn", set_warn_strength, filters=filters.ChatType.GROUPS, block=False))
