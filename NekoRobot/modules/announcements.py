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
import contextlib

from typing import Optional
from telegram.error import TelegramError
from NekoRobot.modules.helper_funcs.admin_status import A_CACHE, B_CACHE
from telegram import Update, ChatMemberUpdated
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ChatMemberHandler

import NekoRobot.modules.sql.log_channel_sql as logsql
from NekoRobot import OWNER_ID, NEKO_PTB
from NekoRobot.modules.log_channel import loggable

import NekoRobot.modules.sql.logger_sql as sql

# Module to extract and log (optional: send to chat) status changes in chat members using ChatMemberUpdated
# https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/chatmemberbot.py


def extract_status_change(chat_member_update: ChatMemberUpdated):
    try:
        status_change = chat_member_update.difference().get("status")
    except AttributeError:  # no change in status
        status_change = None

    try:
        title_change = chat_member_update.difference().get("custom_title")
    except AttributeError:  # no change in title
        title_change = None

    return status_change, title_change


def do_announce(chat):  # announce to chat or only to log channel?
    return bool(chat.type != "channel" and sql.does_chat_log(chat.id))


@loggable
async def chatmemberupdates(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    bot = context.bot
    chat = update.effective_chat
    message = update.effective_message
    log_setting = logsql.get_chat_setting(chat.id)
    if not log_setting:
        logsql.set_chat_setting(
            logsql.LogChannelSettings(chat.id, True, True, True, True, True))
        log_setting = logsql.get_chat_setting(chat.id)

    result = extract_status_change(update.chat_member)
    status_change, title_change = result

    if title_change is not None and status_change is None:  # extract title changes for admins
        oldtitle, newtitle = title_change
        cause_name = await update.chat_member.from_user.mention_html()
        member_name = await update.chat_member.new_chat_member.user.mention_html(
        )
        if oldtitle != newtitle:

            if str(update.chat_member.from_user.id) == str(
                    bot.id):  # bot action
                return ''  # we handle these in their respective modules

            if oldtitle is None:
                if do_announce(chat):
                    await update.effective_chat.send_message(
                        f"{member_name}'s title was set by {cause_name}.\nold title: {oldtitle}\nnew title: '<code>{newtitle}</code>'",
                        parse_mode=ParseMode.HTML,
                    )
                log_message = (f"<b>{html.escape(chat.title)}:</b>\n"
                               f"#ADMIN\nTitle set\n"
                               f"<b>By Admin:</b> {cause_name}\n"
                               f"<b>To Admin:</b> {member_name}\n"
                               f"<b>Old Title:</b> {oldtitle}\n"
                               f"<b>New Title:</b> '<code>{newtitle}</code>'")
                return log_message

            if newtitle is None:
                if do_announce(chat):
                    await update.effective_chat.send_message(
                        f"{member_name}'s title was removed by {cause_name}.\nold title: '<code>{oldtitle}</code"
                        f">'\nnew title: {newtitle}",
                        parse_mode=ParseMode.HTML,
                    )
                log_message = (f"<b>{html.escape(chat.title)}:</b>\n"
                               f"#ADMIN\nTitle removed\n"
                               f"<b>By Admin:</b> {cause_name}\n"
                               f"<b>To Admin:</b> {member_name}\n"
                               f"<b>Old Title:</b> '<code>{oldtitle}</code>'\n"
                               f"<b>New Title:</b> {newtitle}")
                return log_message
            if do_announce(chat):
                await update.effective_chat.send_message(
                    f"{member_name}'s title was changed by {cause_name}.\nold title: '<code>{oldtitle}</code"
                    f">'\nnew title: '<code>{newtitle}</code>'",
                    parse_mode=ParseMode.HTML,
                )
            log_message = (f"<b>{html.escape(chat.title)}:</b>\n"
                           f"#ADMIN\nTitle changed\n"
                           f"<b>By Admin:</b> {cause_name}\n"
                           f"<b>To Admin:</b> {member_name}\n"
                           f"<b>Old Title:</b> '<code>{oldtitle}</code>'\n"
                           f"<b>New Title:</b> '<code>{newtitle}</code>'")
            return log_message

    if status_change is not None:  # exctract chat changes
        status = ','.join(status_change)
        oldstat = str(status.split(",")[0])
        newstat = str(status.split(",")[1])

        if str(update.chat_member.from_user.id) == str(bot.id):
            return ''  # we handle these in their respective modules same as before

        cause_name = await update.chat_member.from_user.mention_html()
        member_name = await update.chat_member.new_chat_member.user.mention_html(
        )

        if oldstat == "administrator":
            if newstat == "member":
                if do_announce(chat):
                    await update.effective_chat.send_message(
                        f"{member_name} was demoted by {cause_name}.",
                        parse_mode=ParseMode.HTML,
                    )

                if not log_setting.log_action:
                    return ""

                log_message = (f"<b>{html.escape(chat.title)}:</b>\n"
                               f"#ADMIN\n<b>Demoted</b>\n"
                               f"<b>Admin:</b> {cause_name}\n"
                               f"<b>User:</b> {member_name}")
                return log_message

            if newstat == "kicked":
                if do_announce(chat):
                    await update.effective_chat.send_message(
                        f"{member_name} was demoted and removed by {cause_name}.",
                        parse_mode=ParseMode.HTML,
                    )

                if not log_setting.log_action:
                    return ""

                log_message = (f"<b>{html.escape(chat.title)}:</b>\n"
                               f"#BANNED\n"
                               f"#ADMIN\n<b>Demoted</b>\n"
                               f"<b>Admin:</b> {cause_name}\n"
                               f"<b>User:</b> {member_name}")
                return log_message

            if newstat == "left":
                if not log_setting.log_action:
                    return ""

                log_message = (f"<b>{html.escape(chat.title)}:</b>\n"
                               f"#ADMIN\n<b>Left</b>\n"
                               f"<b>Admin:</b> {cause_name}\n"
                               f"<b>User:</b> {member_name}")
                return log_message

        if oldstat != "administrator" and newstat == "administrator":
            if title_change is not None:
                oldtitle, newtitle = title_change
                if oldtitle != newtitle:
                    if do_announce(chat):
                        await update.effective_chat.send_message(
                            f"{member_name} was promoted by {cause_name} with the title <code>{newtitle}</code>.",
                            parse_mode=ParseMode.HTML,
                        )

                    if not log_setting.log_action:
                        return ""

                    log_message = (f"<b>{html.escape(chat.title)}:</b>\n"
                                   f"#ADMIN\n<b>Promoted</b>\n"
                                   f"<b>Admin:</b> {cause_name}\n"
                                   f"<b>User:</b> {member_name}\n"
                                   f"<b>Title:</b> '<code>{newtitle}</code>'")
                    return log_message

            else:
                if do_announce(chat):
                    await update.effective_chat.send_message(
                        f"{member_name} was promoted by {cause_name}.",
                        parse_mode=ParseMode.HTML,
                    )

                if not log_setting.log_action:
                    return ""

                log_message = (f"<b>{html.escape(chat.title)}:</b>\n"
                               f"#ADMIN\n<b>Promoted</b>\n"
                               f"<b>Admin:</b> {cause_name}\n"
                               f"<b>User:</b> {member_name}")
                return log_message

        if oldstat != "restricted" and newstat == "restricted":
            if do_announce(chat):
                await update.effective_chat.send_message(
                    f"{member_name} was muted by {cause_name}.",
                    parse_mode=ParseMode.HTML,
                )

            if not log_setting.log_action:
                return ""

            log_message = (f"<b>{html.escape(chat.title)}:</b>\n"
                           f"#MUTED\n"
                           f"<b>Admin:</b> {cause_name}\n"
                           f"<b>User:</b> {member_name}")
            return log_message

        if oldstat == "restricted" and newstat != "restricted":
            if do_announce(chat):
                await update.effective_chat.send_message(
                    f"{member_name} was unmuted by {cause_name}.",
                    parse_mode=ParseMode.HTML,
                )

            if not log_setting.log_action:
                return ""

            log_message = (f"<b>{html.escape(chat.title)}:</b>\n"
                           f"#UNMUTED\n"
                           f"<b>Admin:</b> {cause_name}\n"
                           f"<b>User:</b> {member_name}")
            return log_message

        if str(update.chat_member.from_user.id) == str(bot.id):
            cause_name = await message.from_user.mention_html()
        else:
            cause_name = await update.chat_member.from_user.mention_html()

        if oldstat != "kicked" and newstat == "kicked":
            if do_announce(chat):
                await update.effective_chat.send_message(
                    f"{member_name} was banned by {cause_name}.",
                    parse_mode=ParseMode.HTML,
                )

            if not log_setting.log_action:
                return ""

            log_message = (f"<b>{html.escape(chat.title)}:</b>\n"
                           f"#BANNED\n"
                           f"<b>Admin:</b> {cause_name}\n"
                           f"<b>User:</b> {member_name}")
            return log_message

        if oldstat == "kicked" and newstat != "kicked":
            if do_announce(chat):
                await update.effective_chat.send_message(
                    f"{member_name} was unbanned by {cause_name}.",
                    parse_mode=ParseMode.HTML,
                )

            if not log_setting.log_action:
                return ""

            log_message = (f"<b>{html.escape(chat.title)}:</b>\n"
                           f"#UNBANNED\n"
                           f"<b>Admin:</b> {cause_name}\n"
                           f"<b>User:</b> {member_name}")
            return log_message

        if oldstat == ("left" or "kicked") and newstat == "member":
            if member_name == cause_name:

                if not log_setting.log_joins:
                    return ""

                log_message = (
                    f"<b>{html.escape(chat.title)}:</b>\n"
                    f"#WELCOME\n"
                    f"<b>User:</b> {member_name}\n"
                    f"<b>ID</b>: <code>{update.chat_member.new_chat_member.user.id}</code>"
                )
                return log_message
            if not log_setting.log_joins:
                return ""

            log_message = (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME\n"
                f"<b>User:</b> {member_name}\n"
                f"<b>Added by:</b> {cause_name}\n"
                f"<b>ID</b>: <code>{update.chat_member.new_chat_member.user.id}</code>"
            )
            return log_message

        if oldstat == ("member" or "administrator") and newstat == "left":
            if member_name == cause_name:

                if not log_setting.log_leave:
                    return ""

                log_message = (
                    f"<b>{html.escape(chat.title)}:</b>\n"
                    f"#GOODBYE\n"
                    f"<b>User:</b> {member_name}\n"
                    f"<b>ID</b>: <code>{update.chat_member.new_chat_member.user.id}</code>"
                )
                return log_message

            if not log_setting.log_leave:
                return ""

            log_message = (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#REMOVED\n"
                f"<b>User:</b> {member_name}\n"
                f"<b>Removed by:</b> {cause_name}\n"
                f"<b>ID</b>: <code>{update.chat_member.new_chat_member.user.id}</code>"
            )
            return log_message


async def mychatmemberupdates(update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> None:
    result = extract_status_change(update.my_chat_member)
    status_change, _1 = result
    chat = update.effective_chat
    chatname = chat.title or chat.first_name or 'None'
    cause_name = update.effective_user.mention_html(
    ) if update.effective_user else "Unknown"
    if status_change is not None:
        status = ','.join(status_change)
        oldstat = str(status.split(",")[0])
        newstat = str(status.split(",")[1])
        if oldstat == ("left" or "kicked") and newstat == ("member"
                                                           or "administrator"):
            new_group = (
                f"<b>{html.escape(chat.title) or chat.first_name or chat.id}:</b>\n"
                f"#NEW_CHAT\n"
                f"<b>Chat:</b> {chatname}\n"
                f"<b>Added by:</b> {cause_name or 'none'}\n"
                f"<b>ID</b>: <code>{update.effective_user.id}</code>\n"
                f"<b>Chat ID</b>: <code>{update.effective_chat.id}</code>")
            await context.bot.send_message(OWNER_ID,
                                           new_group,
                                           parse_mode=ParseMode.HTML)


async def admincacheupdates(update: Update):
    try:
        oldstat = update.chat_member.old_chat_member.status
        newstat = update.chat_member.new_chat_member.status
    except AttributeError:
        return
    if (oldstat == "administrator" and newstat != "administrator"
            or oldstat != "administrator" and newstat == "administrator"):

        A_CACHE[update.effective_chat.
                id] = update.effective_chat.get_administrators()
        # B_CACHE[update.effective_chat.id] = update.effective_chat.get_member(1241223850)


async def botstatchanged(update: Update):
    if update.effective_chat.type != "private":
        with contextlib.suppress(TelegramError):
            B_CACHE[update.effective_chat.
                    id] = update.effective_chat.get_member(1241223850)


NEKO_PTB.add_handler(ChatMemberHandler(chatmemberupdates,
                                           ChatMemberHandler.CHAT_MEMBER),
                         group=-21)
NEKO_PTB.add_handler(ChatMemberHandler(mychatmemberupdates,
                                           ChatMemberHandler.MY_CHAT_MEMBER),
                         group=-23)
NEKO_PTB.add_handler(ChatMemberHandler(botstatchanged,
                                           ChatMemberHandler.MY_CHAT_MEMBER),
                         group=-25)
NEKO_PTB.add_handler(ChatMemberHandler(admincacheupdates,
                                           ChatMemberHandler.CHAT_MEMBER),
                         group=-22)
