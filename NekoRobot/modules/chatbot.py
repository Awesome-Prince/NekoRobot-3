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

import re
import requests
from time import sleep


from NekoRobot import NEKO_PTB, DEV_USERS
from NekoRobot.modules.helper_funcs.chat_status import (
    is_user_admin,
)
from NekoRobot.modules.helper_funcs.anonymous import user_admin
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes, CallbackQueryHandler,
    CommandHandler, filters, MessageHandler,
)

CHATBOT_ENABLED_CHATS = []


@user_admin
async def chatbot_toggle(update: Update):
    keyboard = [
        [
            InlineKeyboardButton("Enable", callback_data="chatbot_enable"),
            InlineKeyboardButton("Disable", callback_data="chatbot_disable"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_message.reply_text("Choose an option:", reply_markup=reply_markup)


async def chatbot_handle_callq(update: Update):
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat
    action = query.data.split("_")[1]

    if not await is_user_admin(update, user.id):
        return await query.answer("This is not for you.")

    if action == "delete":
        await query.message.delete()

    elif action == "enable":
        if chat.id in CHATBOT_ENABLED_CHATS:
            return await query.answer("Chatbot is already enabled")
        CHATBOT_ENABLED_CHATS.append(chat.id)
        await query.answer("Chatbot enabled")
        await query.message.delete()

    elif action == "disable":
        if chat.id not in CHATBOT_ENABLED_CHATS:
            return await query.answer("Chatbot is already disabled")
        CHATBOT_ENABLED_CHATS.remove(chat.id)
        await query.answer("Chatbot disabled")
        await query.message.delete()

    else:
        await query.answer()


def chatbot_response(query: str) -> str:
    data = requests.get(
        f"https://www.kukiapi.xyz/api/apikey=5349869477-KUKIhU1ygu8mm0/Cutiepii/@Awesome_RJ/message={query}"
    )
    return data.json()["reply"]


def check_message(_: ContextTypes, message):
    reply_msg = message.reply_to_message
    text = message.text
    if re.search("[.|\n]{0,}"+context.bot.first_name+"[.|\n]{0,}", text, flags=re.IGNORECASE):
        return True
    return bool(
        reply_msg
        and reply_msg.from_user.id == BOT_ID
        or message.chat.type == "private"
    )


async def chatbot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    chat_id = update.effective_chat.id
    is_chat = chat_id in CHATBOT_ENABLED_CHATS
    bot = context.bot
    if not is_chat:
        return
    if msg.text and not msg.document:
        if not check_message(context, msg):
            return
        # lower the text to ensure text replace checks
        query = msg.text.lower()
        botname = bot.first_name.lower()
        if botname in query:
            query = query.replace(botname, "bot.name")
        await bot.sendChatAction(chat_id, action="typing")
        user_id = update.message.from_user.id
        response = chatbot_response(query, user_id)
        if "Aco" in response:
            response = response.replace("Aco", bot.first_name)
        if "bot.name" in response:
            response = response.replace("bot.name", bot.first_name)
        sleep(0.3)
        await msg.reply_text(response
#    , timeout=60
        )


async def list_chatbot_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "<b>AI-Enabled Chats</b>\n"
    for chat in CHATBOT_ENABLED_CHATS:
        x = await context.bot.get_chat(chat)
        name = x.title or x.first_name
        text += f"➛ <code>{name}</code>\n"
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


__help__ = f"""
Chatbot utilizes the Brainshop's API and allows {context.bot.first_name} to talk and provides a more interactive group chat experience.
*Commands:*
*Admins only:*
➛ /chatbot*:* Shows chatbot control panel
"""

NEKO_PTB.add_handler(CommandHandler("chatbot", chatbot_toggle, block=False))
NEKO_PTB.add_handler(CallbackQueryHandler(chatbot_handle_callq, pattern=r"chatbot_", block=False))
NEKO_PTB.add_handler(MessageHandler(filters.TEXT & (~filters.Regex(r"^#[^\s]+") & ~filters.Regex(r"^!") & ~filters.Regex(r"^\/")), chatbot, block=False))
NEKO_PTB.add_handler(CommandHandler("listaichats", list_chatbot_chats, filters=filters.User(DEV_USERS), block=False))

__mod_name__ = "Chatbot"
__command_list__ = ["chatbot", "listaichats"]
