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

import html
from typing import Optional, Union

from telegram import (
    Bot,
    Chat,
    ChatMember,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
)
from telegram.error import BadRequest, TelegramError
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, filters
from telegram import mention_html

from NekoRobot import (
    BAN_STICKER,
    DEV_USERS,
    ERROR_LOGS,
    LOGGER,
    NEKO_PTB,
    OWNER_ID,
    SUDO_USERS,
    WHITELIST_USERS,
)
from NekoRobot.modules.disable import DisableAbleCommandHandler
from NekoRobot.modules.helper_funcs.chat_status import (
    connection_status,
    dev_plus,
    is_user_admin,
)
from NekoRobot.modules.helper_funcs.extraction import extract_user_and_text
from NekoRobot.modules.helper_funcs.string_handling import extract_time
from NekoRobot.modules.log_channel import gloggable, loggable


def cannot_ban(banner_id, user_id, message) -> bool:
    if banner_id in DEV_USERS:
        if user_id not in DEV_USERS:
            return False
        else:
            message.reply_text("Why are you trying to ban another dev?")
            return True
    else:
        if user_id == OWNER_ID:
            message.reply_text("I'd never ban my owner.")
            return True
        elif user_id in DEV_USERS:
            message.reply_text(
                "This user is one of my Devs, I can't act against our own."
            )
            return True
        elif user_id in SUDO_USERS:
            message.reply_text("My sudos are ban immune")
            return True
        elif user_id in WHITELIST_USERS:
            message.reply_text("Let one of my Devs fight a Whitelist user.")
            return True
        return False


ban_myself = "Oh yeah, ban myself, noob!"

from Cutiepii_Robot.modules.helper_funcs.admin_status import (
    AdminPerms,
    bot_admin_check,
    bot_is_admin,
    user_admin_check,
    user_is_admin,
)


async def ban_chat(bot: Bot, who: Chat, where_chat_id, reason=None) -> Union[str, bool]:
    try:
        await bot.banChatSenderChat(where_chat_id, who.id)
    except BadRequest as excp:
        if excp.message != "Reply message not found":
            LOGGER.warning(
                f"error banning channel {who.title}:{who.id} in {where_chat_id} because: {excp.message}"
            )

            return False

    return (
        f'<b>Channel:</b> <a href="t.me/{who.username}">{html.escape(who.title)}</a>'
        f"<b>Channel ID:</b> {who.id}"
        ""
        if reason is None
        else f"<b>Reason:</b> {reason}"
    )


async def ban_user(
    bot: Bot, who: ChatMember, where_chat_id, reason=None
) -> Union[str, bool]:
    try:
        await bot.banChatMember(where_chat_id, who.user.id)
    except BadRequest as excp:
        if excp.message != "Reply message not found":
            LOGGER.warning(
                f"error banning user {who.user.first_name}:{who.user.id} in {where_chat_id} because: {excp.message}"
            )

            return False

    return (
        f'<b>User:</b> <a href="tg://user?id={who.user.id}">{html.escape(who.user.first_name)}</a>'
        f"<b>User ID:</b> {who.user.id}"
        ""
        if reason is None
        else f"<b>Reason:</b> {reason}"
    )


async def unban_chat(
    bot: Bot, who: Chat, where_chat_id, reason=None
) -> Union[str, bool]:
    try:
        await bot.unbanChatSenderChat(where_chat_id, who.id)
    except BadRequest as excp:
        if excp.message != "Reply message not found":
            LOGGER.warning(
                f"error banning channel {who.title}:{who.id} in {where_chat_id} because: {excp.message}"
            )

            return False

    return (
        f'<b>Channel:</b> <a href="t.me/{who.username}">{html.escape(who.title)}</a>'
        f"<b>Channel ID:</b> {who.id}"
        ""
        if reason is None
        else f"<b>Reason:</b> {reason}"
    )


async def unban_user(
    bot: Bot, who: ChatMember, where_chat_id, reason=None
) -> Union[str, bool]:
    try:
        await bot.unbanChatMember(where_chat_id, who.user.id)
    except BadRequest as excp:
        if excp.message != "Reply message not found":
            LOGGER.warning(
                f"error banning user {who.user.first_name}:{who.user.id} in {where_chat_id} because: {excp.message}"
            )

            return False

    return (
        f'<b>User:</b> <a href="tg://user?id={who.user.id}">{html.escape(who.user.first_name)}</a>'
        f"<b>User ID:</b> {who.user.id}"
        ""
        if reason is None
        else f"<b>Reason:</b> {reason}"
    )


@connection_status
@bot_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@user_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
async def ban(
    update: Update, context: CallbackContext
) -> Optional[str]:  # sourcery no-metrics
    global delsilent
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args
    bot = context.bot

    if message.text.startswith(("/s", "!s", ">s")):
        silent = True
        if not bot_is_admin(chat, AdminPerms.CAN_DELETE_MESSAGES):
            await message.reply_text("I don't have permission to delete messages here!")
            return
    else:
        silent = False
    if message.text.startswith(("/d", "!d", ">d")):
        delban = True
        if not bot_is_admin(chat, AdminPerms.CAN_DELETE_MESSAGES):
            await message.reply_text("I don't have permission to delete messages here!")
            return
        if not user_is_admin(update, user.id, perm=AdminPerms.CAN_DELETE_MESSAGES):
            await message.reply_text(
                "You don't have permission to delete messages here!"
            )
            return
    else:
        delban = False
    if message.text.startswith(("/ds", "!ds", ">ds")):
        delsilent = True
        if not bot_is_admin(chat, AdminPerms.CAN_DELETE_MESSAGES):
            await message.reply_text("I don't have permission to delete messages here!")
            return
        if not user_is_admin(update, user.id, perm=AdminPerms.CAN_DELETE_MESSAGES):
            await message.reply_text(
                "You don't have permission to delete messages here!"
            )
            return

    if message.reply_to_message and message.reply_to_message.sender_chat:
        if message.reply_to_message.is_automatic_forward:
            await message.reply_text("This is a pretty bad idea, isn't it?")
            return

        if did_ban := ban_chat(
            bot,
            message.reply_to_message.sender_chat,
            chat.id,
            reason=" ".join(args) or None,
        ):
            logmsg = (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#BANNED\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            )
            logmsg += did_ban

            await message.reply_text(
                f"Channel {html.escape(message.reply_to_message.sender_chat.title)} was banned successfully from {html.escape(chat.title)}",
                parse_mode=ParseMode.HTML,
            )

        else:
            await message.reply_text("Failed to ban channel")
            return ""

    user_id, reason = await extract_user_and_text(message, args)

    if not user_id:
        await message.reply_text("I doubt that's a user.")
        return ""

    member = None
    chan = None
    try:
        member = await chat.get_member(user_id)
    except BadRequest:
        try:
            chan = await bot.get_chat(user_id)
        except BadRequest as excp:
            if excp.message != "Chat not found":
                raise
            await message.reply_text("Can't seem to find this person.")
            return ""

    if chan:
        if did_ban := ban_chat(bot, chan, chat.id, reason=" ".join(args) or None):
            logmsg = (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#BANNED\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            )
            logmsg += did_ban

            await message.reply_text(
                f"Channel {html.escape(chan.title)} was banned successfully from {html.escape(chat.title)}",
                parse_mode=ParseMode.HTML,
            )

        else:
            await message.reply_text("Failed to ban channel")
            return ""

    elif user_id == context.bot.id:
        await message.reply_text(ban_myself)
        return ""

    elif await is_user_admin(update, user_id, member) and user.id not in DEV_USERS:
        message.reply_text("This user has immunity and cannot be banned.")
        return ""

    elif did_ban := ban_user(bot, member, chat.id, reason=" ".join(args) or None):
        logmsg = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#BANNED\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        )
        logmsg += did_ban

        reply = (
            f"<b>╔━「 Ban Event</b>\n"
            f"<b>➛ Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>➛ User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            reply += f"\n<b>➛ Reason:</b> \n{html.escape(reason)}"

        await bot.sendMessage(
            chat.id,
            reply,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔄 Unban", callback_data=f"unbanb_unban={user_id}"
                        ),
                        InlineKeyboardButton(
                            text="🗑️ Delete", callback_data="unbanb_del"
                        ),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return logmsg

    else:
        await message.reply_text("Failed to ban user")
        return ""

    if silent:
        if delsilent and message.reply_to_message:
            await message.reply_to_message.delete()
        await message.delete()
    elif delban and message.reply_to_message:
        await message.reply_to_message.delete()
    context.bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker

    return logmsg


@connection_status
@bot_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@user_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
async def temp_ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args

    user_id, reason = await extract_user_and_text(message, args)

    if not user_id:
        await message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        await message.reply_text("I can't seem to find this user.")
        return log_message
    if user_id == bot.id:
        await message.reply_text(ban_myself)
        return log_message

    elif cannot_ban(user.id, user_id, message):
        return ""

    elif is_user_admin(update, user_id, member) and user.id not in DEV_USERS:
        message.reply_text("This user has immunity and cannot be banned.")
        return ""

    if not reason:
        await message.reply_text("You haven't specified a time to ban this user for!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    bantime = await extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "#TEMP_BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}\n"
        f"<b>Time:</b> {time_val}"
    )
    if reason:
        log += f"\n<b>Reason:</b> {reason}"

    try:
        chat.ban_member(user_id, until_date=bantime)
        await bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker

        reply_msg = (
            f"<b>╔━「 ❕ Temp Banned</b>\n"
            f"<b>➛ Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>➛ User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
            f"<b>➛ Time: {time_val}</b>"
        )

        if reason:
            reply_msg += f"\n<b>➛ Reason:</b> {html.escape(reason)}"

        await bot.sendMessage(
            chat.id,
            reply_msg,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔄 Unban", callback_data=f"unbanb_unban={user_id}"
                        ),
                        InlineKeyboardButton(
                            text="🗑️ Delete", callback_data="unbanb_del"
                        ),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            await message.reply_text(
                f"Banned! User will be banned for {time_val}.", quote=False
            )
            return log
        await bot.sendMessage(ERROR_LOGS, str(update))
        await bot.sendMessage(
            ERROR_LOGS,
            f"ERROR banning user {user_id} in chat {chat.title} ({chat.id}) due to {excp.message}",
        )

        await message.reply_text("Well damn, I can't ban that user.")

    return log_message


@connection_status
@bot_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@user_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
async def kick(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args

    if message.reply_to_message and message.reply_to_message.sender_chat:
        await message.reply_text(
            "This command doesn't work on channels, but I can ban them if u want."
        )
        return log_message

    user_id, reason = await extract_user_and_text(message, args)

    if not user_id:
        await message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        await message.reply_text("I can't seem to find this user.")
        return log_message
    if user_id == bot.id:
        await message.reply_text("Yeahhh I'm not gonna do that.")
        return log_message

    if await is_user_admin(update, user_id, member) and user not in DEV_USERS:
        cannot_ban(user_id, message)
        return log_message

    if chat.unban_member(user_id):
        await bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker

        if reason:

            await bot.sendMessage(
                chat.id,
                f"{mention_html(member.user.id, member.user.first_name)} was kicked by {mention_html(user.id, user.first_name)} in {message.chat.title}\n<b>Reason</b>: <code>{reason}</code>",
                parse_mode=ParseMode.HTML,
            )

        else:

            await bot.sendMessage(
                chat.id,
                f"{mention_html(member.user.id, member.user.first_name)} was kicked by {mention_html(user.id, user.first_name)} in {message.chat.title}",
                parse_mode=ParseMode.HTML,
            )

        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#KICKED\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
        )
        if reason:
            log += f"\n<b>Reason:</b> {reason}"

        return log
    await message.reply_text("Well damn, I can't kick that user.")

    return log_message


@bot_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
async def kickme(update: Update) -> Optional[str]:
    user_id = update.effective_message.from_user.id
    user = update.effective_message.from_user
    chat = update.effective_chat
    if await is_user_admin(update, user_id, member):
        await update.effective_message.reply_text("Haha you're stuck with us here.")
        return ""

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        await update.effective_message.reply_text("*kicks you out of the group*")

        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#KICKED\n"
            "self kick"
            f"<b>User:</b> {mention_html(user.id, user.first_name)}\n"
        )

        return log
    await update.effective_message.reply_text("Huh? I can't :/")


@connection_status
@bot_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@user_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
async def unban(
    update: Update, context: CallbackContext
) -> Optional[str]:  # sourcery no-metrics
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args
    bot = context.bot

    if message.reply_to_message and message.reply_to_message.sender_chat:
        if message.reply_to_message.is_automatic_forward:
            await message.reply_text("This command doesn't work like this!")
            return

        if did_ban := unban_chat(
            bot,
            message.reply_to_message.sender_chat,
            chat.id,
            reason=" ".join(args) or None,
        ):
            logmsg = (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#UNBANNED\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            )
            logmsg += did_ban

            await message.reply_text(
                f"Channel {html.escape(message.reply_to_message.sender_chat.title)} was unbanned successfully from {html.escape(chat.title)}",
                parse_mode=ParseMode.HTML,
            )

        else:
            await message.reply_text("Failed to unban channel")
            return ""

    user_id, reason = await extract_user_and_text(message, args)

    if not user_id:
        await message.reply_text("I doubt that's a user.")
        return ""

    member = None
    chan = None
    try:
        member = await chat.get_member(user_id)
    except BadRequest:
        try:
            chan = await bot.get_chat(user_id)
        except BadRequest as excp:
            if excp.message != "Chat not found":
                raise
            await message.reply_text("Can't seem to find this person.")
            return ""

    if chan:
        if did_ban := unban_chat(bot, chan, chat.id, reason=" ".join(args) or None):
            logmsg = (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#UNBANNED\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            )
            logmsg += did_ban

            await message.reply_text(
                f"Channel {html.escape(chan.title)} was unbanned successfully from {html.escape(chat.title)}",
                parse_mode=ParseMode.HTML,
            )

        else:
            await message.reply_text("Failed to unban channel")
            return ""

    elif user_id == context.bot.id:
        await message.reply_text(ban_myself)
        return ""

    elif await is_user_admin(update, user_id, member) and user.id not in DEV_USERS:
        cannot_ban(user_id, message)
        return ""

    elif member.status not in ["banned", "kicked"]:
        await message.reply_text("This user isn't banned!")
        return ""

    elif did_ban := unban_user(bot, member, chat.id, reason=" ".join(args) or None):
        logmsg = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#UNBANNED\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        )
        logmsg += did_ban

        await message.reply_text(
            f"{mention_html(member.user.id, member.user.first_name)} was unbanned by {mention_html(user.id, user.first_name)} in <b>{message.chat.title}</b>",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.reply_text("Failed to unban user")
        return ""

    return logmsg


WHITELISTED_USERS = [OWNER_ID] + DEV_USERS + SUDO_USERS + WHITELIST_USERS


@connection_status
@bot_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@gloggable
async def selfunban(update: Update, context: CallbackContext) -> Optional[str]:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    if user.id not in WHITELISTED_USERS:
        return

    try:
        chat_id = int(args[0])
    except:
        await message.reply_text("Give a valid chat ID.")
        return

    chat = bot.getChat(chat_id)

    try:
        member = chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "User not found":
            await message.reply_text("I can't seem to find this user.")
            return
        raise

    if member.status not in ("left", "kicked"):
        await message.reply_text("Aren't you already in the chat??")
        return

    chat.unban_member(user.id)
    await message.reply_text("Yep, I have unbanned you.")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNBANNED\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log


@connection_status
@bot_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@user_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
async def unbanb_btn(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user
    if query.data != "unbanb_del":
        splitter = query.data.split("=")
        query_match = splitter[0]
        if query_match == "unbanb_unban":
            user_id = splitter[1]
            try:
                member = await chat.get_member(user_id)
            except BadRequest:
                pass
            chat.unban_member(user_id)
            await query.message.edit_text(
                f"{member.user.first_name} [{member.user.id}] Unbanned."
            )
            await bot.answer_callback_query(query.id, text="Unbanned!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#UNBANNED\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
            )

    else:
        await query.message.delete()
        await bot.answer_callback_query(query.id, text="Deleted!")
        return ""


@connection_status
@bot_admin_check(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
async def banme(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_message.from_user.id
    chat = update.effective_chat
    user = update.effective_user
    if res := update.effective_chat.ban_member(user_id):
        await update.effective_message.reply_text("Yes, you're right! GTFO..")
        return f"<b>{html.escape(chat.title)}:</b>\n#BANME\n<b>User:</b> {mention_html(user.id, user.first_name)}\n<b>ID:</b> <code>{user_id}</code>"

    await update.effective_message.reply_text("Huh? I can't :/")


@dev_plus
async def snipe(update: Update, context: CallbackContext) -> None:
    args = context.args
    bot = context.bot
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError:
        await update.effective_message.reply_text("Please give me a chat to echo to!")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            await bot.sendMessage(int(chat_id), to_send)
        except TelegramError:
            LOGGER.warning("Couldn't send to group %s", chat_id)
            await update.effective_message.reply_text(
                "Couldn't send the message. Perhaps I'm not part of that group?"
            )


__help__ = """
*User Commands*:
➛ /kickme*:* kicks the user who issued the command
➛ /banme*:*  Bot Will Bans you from the group.
➛ /roar*:*  Self Unban
*Ban Commands are Admins only*:
➛ /ban <userhandle>*:* bans a user. (via handle, or reply)
➛ /sban <userhandle>*:* Silently ban a user. Deletes command, Replied message and doesn't reply. (via handle, or reply)
➛ /tban <userhandle> x(m/h/d)*:* bans a user for `x` time. (via handle, or reply). `m` = `minutes`, `h` = `hours`, `d` = `days`.
➛ /dban <userhandle>*:* bans a user deleting the replied to message. (via handle, or reply)
➛ /unban <userhandle>*:* unbans a user. (via handle, or reply)
➛ /kick <userhandle>*:* kicks a user out of the group, (via handle, or reply)
*Mute Commands are Admins only*:
➛ /mute <userhandle>*:* silences a user. Can also be used as a reply, muting the replied to user.
➛ /tmute <userhandle> x(m/h/d)*:* mutes a user for x time. (via handle, or reply). `m` = `minutes`, `h` = `hours`, `d` = `days`.
➛ /unmute <userhandle>*:* unmutes a user. Can also be used as a reply, muting the replied to user.
"""

NEKO_PTB.add_handler(CommandHandler(["ban", "dban", "sban", "dsban"], ban))
NEKO_PTB.add_handler(CommandHandler(["tban"], temp_ban))
NEKO_PTB.add_handler(CommandHandler(["kick", "punch"], kick))
NEKO_PTB.add_handler(CommandHandler("unban", unban))
NEKO_PTB.add_handler(CommandHandler(["selfunban", "roar"], selfunban))
NEKO_PTB.add_handler(CallbackQueryHandler(unbanb_btn, pattern=r"unbanb_"))
NEKO_PTB.add_handler(
    DisableAbleCommandHandler(
        ["kickme", "punchme"], kickme, filters=filters.ChatType.GROUPS
    )
)
NEKO_PTB.add_handler(CommandHandler("snipe", snipe, filters=filters.User(SUDO_USERS)))
NEKO_PTB.add_handler(CommandHandler("banme", banme))

__mod_name__ = "Bans/Mutes"
