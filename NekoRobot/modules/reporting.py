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
import NekoRobot.modules.sql.log_channel_sql as logsql

from NekoRobot import LOGGER, NEKO_PTB
from NekoRobot.modules.helper_funcs.anonymous import user_admin
from NekoRobot.modules.helper_funcs.chat_status import user_not_admin
from NekoRobot.modules.log_channel import loggable
from NekoRobot.modules.sql import reporting_sql as sql
from telegram import Chat, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest, Forbidden
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    CommandHandler,
    filters,
    MessageHandler,
)

from telegram.helpers import mention_html

REPORT_GROUP = 12
#REPORT_IMMUNE_USERS = SUDO_USERS + TIGER_USERS + WHITELIST_USERS



@user_admin
async def report_setting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    msg = update.effective_message

    if chat.type == chat.PRIVATE:
        if len(args) >= 1:
            if args[0] in ("yes", "on"):
                sql.set_user_setting(chat.id, True)
                 msg.reply_text(
                    "Turned on reporting! You'll be notified whenever anyone reports something.",
                )

            elif args[0] in ("no", "off"):
                sql.set_user_setting(chat.id, False)
                 msg.reply_text("Turned off reporting! You wont get any reports.")
        else:
             msg.reply_text(
                f"Your current report preference is: `{sql.user_should_report(chat.id)}`",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

    elif len(args) >= 1:
        if args[0] in ("yes", "on"):
            sql.set_chat_setting(chat.id, True)
             msg.reply_text(
                "Turned on reporting! Admins who have turned on reports will be notified when /report "
                "or @admin is called.",
            )

        elif args[0] in ("no", "off"):
            sql.set_chat_setting(chat.id, False)
             msg.reply_text(
                "Turned off reporting! No admins will be notified on /report or @admin.",
            )
    else:
         msg.reply_text(
            f"This group's current setting is: `{sql.chat_should_report(chat.id)}`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )



@user_not_admin
@loggable
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    args = context.args
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    log_setting = logsql.get_chat_setting(chat.id)
    if not log_setting:
        logsql.set_chat_setting(logsql.LogChannelSettings(chat.id, True, True, True, True, True))
        log_setting = logsql.get_chat_setting(chat.id)

    if message.sender_chat:
        admin_list =  bot.getChatAdministrators(chat.id)
        reported = "Reported to admins."
        for admin in admin_list:
            if admin.user.is_bot:  # AI didnt take over yet
                continue
            with contextlib.suppress(BadRequest):
                reported += f"<a href=\"tg://user?id={admin.user.id}\">\u2063</a>"
                LOGGER.exception("Exception while reporting user")
         message.reply_text(reported, parse_mode=ParseMode.HTML)

    if chat and message.reply_to_message and sql.chat_should_report(chat.id):
        reported_user = message.reply_to_message.from_user
        chat_name = chat.title or chat.username
        admin_list = chat.get_administrators()
        message = update.effective_message

        if not args:
             update.effective_message.reply_text("Add a reason for reporting first.")
            return ""

        if user.id == reported_user.id:
             update.effective_message.reply_text("Uh yeah, Sure sure...maso much?")
            return ""

        if user.id == bot.id:
             update.effective_message.reply_text("Nice try.")
            return ""
#        if reported_user.id in REPORT_IMMUNE_USERS:
#             update.effective_message.reply_text("Uh? You reporting a disaster?")
#            return ""

        if chat.username and chat.type == Chat.SUPERGROUP:

            reported = f"{mention_html(user.id, user.first_name)} reported {mention_html(reported_user.id, reported_user.first_name)} to the admins!"

            msg = (
                f"<b>⚠️ Report: </b>{html.escape(chat.title)}\n"
                f"<b> ❍ Report by:</b> {mention_html(user.id, user.first_name)}(<code>{user.id}</code>)\n"
                f"<b> ❍ Reported user:</b> {mention_html(reported_user.id, reported_user.first_name)} (<code>{reported_user.id}</code>)\n"
            )
            link = f"<b> ❍ Reported message:</b> <a href='https://telegram.dog/{chat.username}/{message.reply_to_message.message_id}'>click here</a>"
            should_forward = False
            keyboard = [
                [
                    InlineKeyboardButton(
                        "➡ Message",
                        url=f"https://telegram.dog/{chat.username}/{message.reply_to_message.message_id}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "⚠ Kick",
                        callback_data=f"report_{chat.id}=kick={reported_user.id}={reported_user.first_name}",
                    ),
                    InlineKeyboardButton(
                        "⛔️ Ban",
                        callback_data=f"report_{chat.id}=banned={reported_user.id}={reported_user.first_name}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "❎ Delete Message",
                        callback_data=f"report_{chat.id}=delete={reported_user.id}={message.reply_to_message.message_id}",
                    ),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            reported = (
                f"{mention_html(user.id, user.first_name)} reported "
                f"{mention_html(reported_user.id, reported_user.first_name)} to the admins!"
            )

            msg = f"{mention_html(user.id, user.first_name)} is calling for admins in '{html.escape(chat_name)}'!"
            link = ""
            should_forward = True

        for admin in admin_list:
            if admin.user.is_bot:  # can't message bots
                continue

            if sql.user_should_report(admin.user.id):
                try:
                    if chat.type != Chat.SUPERGROUP:
                         bot.send_message(
                            admin.user.id, msg + link, parse_mode=ParseMode.HTML,
                        )

                        if should_forward:
                            message.reply_to_message.forward(admin.user.id)

                            if (
                                len(message.text.split()) > 1
                            ):  # If user is giving a reason, send his message too
                                 message.forward(admin.user.id)
                    if not chat.username:
                         bot.send_message(
                            admin.user.id, msg + link, parse_mode=ParseMode.HTML,
                        )

                        if should_forward:
                            message.reply_to_message.forward(admin.user.id)

                            if (
                                len(message.text.split()) > 1
                            ):  # If user is giving a reason, send his message too
                                 message.forward(admin.user.id)

                    if chat.username and chat.type == Chat.SUPERGROUP:
                         bot.send_message(
                            admin.user.id,
                            msg + link,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup,
                        )

                        if should_forward:
                            message.reply_to_message.forward(admin.user.id)

                            if (
                                len(message.text.split()) > 1
                            ):  # If user is giving a reason, send his message too
                                 message.forward(admin.user.id)

                except Forbidden:
                    pass
                except BadRequest as excp:  # TODO: cleanup exceptions
                    LOGGER.exception("Exception while reporting user")

        message.reply_to_message.reply_text(
            f"{mention_html(user.id, user.first_name)} reported the message to the admins.",
            parse_mode=ParseMode.HTML,
        )
        return msg

    return ""


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, _):
    return f"This chat is setup to send user reports to admins, via /report and @admin: `{sql.chat_should_report(chat_id)}`"


def __user_settings__(user_id):
    return (
        "You will receive reports from chats you're admin."
        if sql.user_should_report(user_id) is True
        else "You will *not* receive reports from chats you're admin."
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot = context.bot
    query = update.callback_query
    splitter = query.data.replace("report_", "").split("=")
    if splitter[1] == "kick":
        try:
             bot.banChatMember(splitter[0], splitter[2])
             bot.unbanChatMember(splitter[0], splitter[2])
             query.answer("✅ Succesfully kicked")
            return ""
        except Exception as err:
             query.answer("🛑 Failed to kick")
             bot.sendMessage(
                text=f"Error: {err}",
                chat_id=query.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
    elif splitter[1] == "banned":
        try:
             bot.banChatMember(splitter[0], splitter[2])
             query.answer("✅  Succesfully Banned")
            return ""
        except Exception as err:
             bot.sendMessage(
                text=f"Error: {err}",
                chat_id=query.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
             query.answer("🛑 Failed to Ban")
    elif splitter[1] == "delete":
        try:
             bot.deleteMessage(splitter[0], splitter[3])
             query.answer("✅ Message Deleted")
            return ""
        except Exception as err:
             bot.sendMessage(
                text=f"Error: {err}",
                chat_id=query.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
             query.answer("🛑 Failed to delete message!")

__help__ = """
➛ /report <reason>*:* reply to a message to report it to admins.
 ➛ `@admins*:* reply to a message to report it to admins.
*NOTE:* Neither of these will get triggered if used by admins.
*Admins only:*
➛ /reports <on/off>*:* change report setting, or view current status.
   ➛ If done in pm, toggles your status.
   ➛ If in group, toggles that groups's status.
"""

NEKO_PTB.add_handler(CommandHandler("reports", report_setting))
NEKO_PTB.add_handler(CommandHandler("report", report, filters=filters.ChatType.GROUPS))
NEKO_PTB.add_handler(MessageHandler(filters.Regex(r"(?i)@admins(s)?"), report))
NEKO_PTB.add_handler(CallbackQueryHandler(buttons, pattern=r"report_"))


__mod_name__ = "Reporting"
