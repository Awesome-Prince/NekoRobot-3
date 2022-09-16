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
import re
import time

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

import NekoRobot.modules.sql.connection_sql as sql
from NekoRobot import DEV_USERS, NEKO_PTB, SUDO_USERS
from NekoRobot.modules.helper_funcs import admin_status, chat_status
from NekoRobot.modules.helper_funcs.alternate import send_message

AdminPerms = admin_status.AdminPerms
user_admin_check = admin_status.user_admin_check
user_admin = chat_status.user_admin


@user_admin
async def allow_connections(update, context) -> str:

    chat = update.effective_chat
    args = context.args

    if chat.type == chat.user_admin_check:
        send_message(
            update.effective_message, "This command is for group only. Not in PM!"
        )

    elif len(args) >= 1:
        var = args[0]
        if var == "no":
            sql.set_allow_connect_to_chat(chat.id, False)
            send_message(
                update.effective_message,
                "Connection has been disabled for this chat",
            )
        elif var == "yes":
            sql.set_allow_connect_to_chat(chat.id, True)
            send_message(
                update.effective_message,
                "Connection has been enabled for this chat",
            )
        else:
            send_message(
                update.effective_message,
                "Please enter `yes` or `no`!",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
    elif get_settings := sql.allow_connect_to_chat(chat.id):
        send_message(
            update.effective_message,
            "Connections to this group are *Allowed* for members!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        send_message(
            update.effective_message,
            "Connection to this group are *Not Allowed* for members!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def connection_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    chat = update.effective_chat
    user = update.effective_user

    conn =  connected(context.bot, update, chat, user.id, need_admin=True)

    if conn:
        chat =  NEKO_PTB.bot.getChat(conn)
        chat_name =  NEKO_PTB.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type != "private":
            return
        chat = update.effective_chat
        chat_name = update.effective_message.chat.title

    if conn:
        message = "You are currently connected to {}.\n".format(chat_name)
    else:
        message = "You are currently not connected in any group.\n"
    send_message(update.effective_message, message, parse_mode="markdown")


async def connect_chat(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:  # sourcery no-metrics

    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    if update.effective_chat.type == "private":
        if args and len(args) >= 1:
            try:
                connect_chat = int(args[0])
                getstatusadmin =  context.bot.get_chat_member(
                    connect_chat, update.effective_message.from_user.id
                )
            except ValueError:
                try:
                    connect_chat = str(args[0])
                    get_chat =  context.bot.getChat(connect_chat)
                    connect_chat = get_chat.id
                    getstatusadmin =  context.bot.get_chat_member(
                        connect_chat, update.effective_message.from_user.id
                    )
                except BadRequest:
                    send_message(update.effective_message, "Invalid Chat ID!")
                    return
            except BadRequest:
                send_message(update.effective_message, "Invalid Chat ID!")
                return

            isadmin = getstatusadmin.status in ("administrator", "creator")
            ismember = getstatusadmin.status == "member"
            isallow = sql.allow_connect_to_chat(connect_chat)

            if (isadmin) or (isallow and ismember) or (user.id in SUDO_USERS):
                if connection_status := sql.connect(
                    update.effective_message.from_user.id, connect_chat
                ):
                    conn_chat =  NEKO_PTB.bot.getChat(
                         connected(
                            context.bot, update, chat, user.id, need_admin=False
                        )
                    )
                    chat_name = conn_chat.title
                    send_message(
                        update.effective_message,
                        "Successfully connected to *{}*. \nUse /helpconnect to check available commands.".format(
                            chat_name
                        ),
                        parse_mode=ParseMode.MARKDOWN_V2,
                    )
                    sql.add_history_conn(user.id, str(conn_chat.id), chat_name)
                else:
                    send_message(update.effective_message, "Connection failed!")
            else:
                send_message(
                    update.effective_message, "Connection to this chat is not allowed!"
                )
        else:
            gethistory = sql.get_history_conn(user.id)
            if gethistory:
                buttons = [
                    InlineKeyboardButton(
                        text="❎ Close button", callback_data="connect_close"
                    ),
                    InlineKeyboardButton(
                        text="🧹 Clear history", callback_data="connect_clear"
                    ),
                ]
            else:
                buttons = []
            conn =  connected(context.bot, update, chat, user.id, need_admin=False)
            if conn:
                connectedchat =  NEKO_PTB.bot.getChat(conn)
                text = (
                    f"You are currently connected to *{connectedchat.title}* (`{conn}`)"
                )
                buttons.append(
                    InlineKeyboardButton(
                        text="🔌 Disconnect", callback_data="connect_disconnect"
                    )
                )
            else:
                text = "Write the chat ID or tag to connect!"
            if gethistory:
                text += "\n\n*Connection history:*\n"
                text += "╒═══「 *Info* 」\n"
                text += "│  Sorted: `Newest`\n"
                text += "│\n"
                buttons = [buttons]
                for x in sorted(gethistory.keys(), reverse=True):
                    htime = time.strftime("%d/%m/%Y", time.localtime(x))
                    text += "╞═「 *{}* 」\n│   `{}`\n│   `{}`\n".format(
                        gethistory[x]["chat_name"], gethistory[x]["chat_id"], htime
                    )
                    text += "│\n"
                    buttons.append(
                        [
                            InlineKeyboardButton(
                                text=gethistory[x]["chat_name"],
                                callback_data=f'connect({gethistory[x]["chat_id"]})',
                            )
                        ]
                    )

                text += "╘══「 Total {} Chats 」".format(
                    f"{len(gethistory)} (max)"
                    if len(gethistory) == 5
                    else str(len(gethistory))
                )

                conn_hist = InlineKeyboardMarkup(buttons)
            elif buttons:
                conn_hist = InlineKeyboardMarkup([buttons])
            else:
                conn_hist = None
            send_message(
                update.effective_message,
                text,
                parse_mode="markdown",
                reply_markup=conn_hist,
            )

    else:
        getstatusadmin =  context.bot.get_chat_member(
            chat.id, update.effective_message.from_user.id
        )
        isadmin = getstatusadmin.status in ("administrator", "creator")
        ismember = getstatusadmin.status == "member"
        isallow = sql.allow_connect_to_chat(chat.id)
        if (isadmin) or (isallow and ismember) or (user.id in SUDO_USERS):
            if connection_status := sql.connect(
                update.effective_message.from_user.id, chat.id
            ):
                chat_name =  NEKO_PTB.bot.getChat(chat.id).title
                send_message(
                    update.effective_message,
                    f"Successfully connected to *{chat_name}*.",
                    parse_mode=ParseMode.MARKDOWN_V2,
                )

                try:
                    sql.add_history_conn(user.id, str(chat.id), chat_name)
                    context.bot.send_message(
                        update.effective_message.from_user.id,
                        "You are connected to *{}*. \nUse `/helpconnect` to check available commands.".format(
                            chat_name
                        ),
                        parse_mode="markdown",
                    )
                except (BadRequest, Forbidden):
                    pass
            else:
                send_message(update.effective_message, "Connection failed!")
        else:
            send_message(
                update.effective_message, "Connection to this chat is not allowed!"
            )


async def disconnect_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if update.effective_chat.type == "private":
        if disconnection_status := sql.disconnect(
            update.effective_message.from_user.id
        ):
            sql.disconnected_chat = send_message(
                update.effective_message, "Disconnected from chat!"
            )
        else:
            send_message(update.effective_message, "You're not connected!")
    else:
        send_message(update.effective_message, "This command is only available in PM.")


async def connected(bot: Bot, update: Update, chat, user_id, need_admin=True):
    user = update.effective_user

    if chat.type == chat.PRIVATE and sql.get_connected_chat(user_id):

        conn_id = sql.get_connected_chat(user_id).chat_id
        getstatusadmin =  bot.get_chat_member(
            conn_id, update.effective_message.from_user.id
        )
        isadmin = getstatusadmin.status in ("administrator", "creator")
        ismember = getstatusadmin.status == "member"
        isallow = sql.allow_connect_to_chat(conn_id)

        if (
            (isadmin)
            or (isallow and ismember)
            or (user.id in SUDO_USERS)
            or (user.id in DEV_USERS)
        ):
            if need_admin is not True:
                return conn_id
            if (
                getstatusadmin.status in ("administrator", "creator")
                or user_id in SUDO_USERS
                or user.id in DEV_USERS
            ):
                return conn_id
            else:
                send_message(
                    update.effective_message,
                    "You must be an admin in the connected group!",
                )
        else:
            send_message(
                update.effective_message,
                "The group changed the connection rights or you are no longer an admin.\nI've disconnected you.",
            )
            disconnect_chat(update, bot)
    else:
        return False


CONN_HELP = """
 Actions are available with connected groups:
➛ View and edit Notes
➛ View and edit filter.
➛ Get invite link of chat.
➛ Set and control AntiFlood settings. 
➛ Set and control Blacklist settings.
➛ Set Locks and Unlocks in chat.
➛ Enable and Disable commands in chat.
➛ Export and Imports of chat backup.
➛ More in future!
 """


async def help_connect_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    context.args

    if update.effective_message.chat.type != "private":
        send_message(update.effective_message, "PM me with that command to get help.")
        return
    else:
        send_message(update.effective_message, CONN_HELP, parse_mode="markdown")


async def connect_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user

    connect_match = re.match(r"connect\((.+?)\)", query.data)
    disconnect_match = query.data == "connect_disconnect"
    clear_match = query.data == "connect_clear"
    connect_close = query.data == "connect_close"

    if connect_match:
        target_chat = connect_match[1]
        getstatusadmin =  context.bot.get_chat_member(
            target_chat, query.from_user.id
        )
        isadmin = getstatusadmin.status in ("administrator", "creator")
        ismember = getstatusadmin.status == "member"
        isallow = sql.allow_connect_to_chat(target_chat)

        if (isadmin) or (isallow and ismember) or (user.id in SUDO_USERS):
            if connection_status := sql.connect(query.from_user.id, target_chat):
                conn_chat =  NEKO_PTB.bot.getChat(
                     connected(
                        context.bot, update, chat, user.id, need_admin=False
                    )
                )
                chat_name = conn_chat.title
                await query.message.edit_text(
                    "Successfully connected to *{}*. \nUse `/helpconnect` to check available commands.".format(
                        chat_name
                    ),
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
                sql.add_history_conn(user.id, str(conn_chat.id), chat_name)
            else:
                 query.message.edit_text("Connection failed!")
        else:
             context.bot.answer_callback_query(
                query.id, "Connection to this chat is not allowed!", show_alert=True
            )
    elif disconnect_match:
        if disconnection_status := sql.disconnect(query.from_user.id):
            sql.disconnected_chat =  query.message.edit_text(
                "Disconnected from chat!"
            )
        else:
             context.bot.answer_callback_query(
                query.id, "You're not connected!", show_alert=True
            )
    elif clear_match:
        sql.clear_history_conn(query.from_user.id)
         query.message.edit_text("History connected has been cleared!")
    elif connect_close:
         query.message.edit_text("Closed.\nTo open again, type /connect")
    else:
        connect_chat(update, context)


NEKO_PTB.add_handler(CommandHandler("connect", connect_chat))
NEKO_PTB.add_handler(CommandHandler("connection", connection_chat, block=False))
NEKO_PTB.add_handler(CommandHandler("disconnect", disconnect_chat, block=False))
NEKO_PTB.add_handler(CommandHandler("allowconnect", allow_connections, block=False))
NEKO_PTB.add_handler(CommandHandler("helpconnect", help_connect_chat, block=False))
NEKO_PTB.add_handler(
    CallbackQueryHandler(connect_button, pattern=r"connect", block=False)
)

__mod_name__ = "Connection"
