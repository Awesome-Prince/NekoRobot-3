"""
MIT License
Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022 Hodacka
Copyright (c) 2022, Yūki • Black Knights Union, <https://github.com/Hodacka/NekoRobot-3>
This file is part of @NekoXRobot (Telegram Bot)
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the Software), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import html
import random

from telegram import Update, MessageEntity
from telegram.ext import Filters, CallbackContext
from telegram.error import BadRequest
from NekoRobot.modules.sql import afk_sql as sql
from NekoRobot.modules.users import get_user_id
from NekoRobot.modules.helper_funcs.decorators import kigcmd, kigmsg

@kigmsg(Filters.regex("(?i)^brb"), friendly="afk", group=3)
@kigcmd(command="afk", group=3)
def afk(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    user = update.effective_user

    if not user:  # ignore channels
        return

    if user.id in (777000, 1087968824):
        return

    notice = ""
    if len(args) >= 2:
        reason = args[1]
        if len(reason) > 100:
            reason = reason[:100]
            notice = "\nYour afk reason was shortened to 100 characters."
    else:
        reason = ""

    sql.set_afk(update.effective_user.id, reason)
    fname = update.effective_user.first_name
    try:
        update.effective_message.reply_text("{} is now away!{}".format(fname, notice))
    except BadRequest:
        pass

@kigmsg((Filters.all & Filters.chat_type.groups), friendly='afk', group=1)
def no_longer_afk(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.effective_message

    if not user:  # ignore channels
        return

    res = sql.rm_afk(user.id)
    if res:
        if message.new_chat_members:  # dont say msg
            return
        firstname = update.effective_user.first_name
        try:
            options = [
                "{} is here!",
                "{} is back!",
                "{} is now in the chat!",
                "{} is awake!",
                "{} is back online!",
                "{} is finally here!",
                "Welcome back! {}",
                "Where is {}?\nIn the chat!",
            ]
            chosen_option = random.choice(options)
            update.effective_message.reply_text(
                chosen_option.format(firstname), parse_mode=None
            )
        except:
            return

@kigmsg((Filters.entity(MessageEntity.MENTION) | Filters.entity(MessageEntity.TEXT_MENTION) & Filters.chat_type.groups), friendly='afk', group=8)
def reply_afk(update: Update, context: CallbackContext):
    bot = context.bot
    message = update.effective_message
    userc = update.effective_user
    userc_id = userc.id
    if message.entities and message.parse_entities(
        [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
    ):
        entities = message.parse_entities(
            [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
        )

        chk_users = []
        for ent in entities:
            if ent.type == MessageEntity.TEXT_MENTION:
                user_id = ent.user.id
                fst_name = ent.user.first_name

                if user_id in chk_users:
                    return
                chk_users.append(user_id)

            if ent.type != MessageEntity.MENTION:
                return

            user_id = get_user_id(
                message.text[ent.offset : ent.offset + ent.length]
            )
            if not user_id:
                # Should never happen, since for a user to become AFK they must have spoken. Maybe changed username?
                return

            if user_id in chk_users:
                return
            chk_users.append(user_id)

            try:
                chat = bot.get_chat(user_id)
            except BadRequest:
                print(
                    "Error: Could not fetch userid {} for AFK module".format(
                        user_id
                    )
                )
                return
            fst_name = chat.first_name

            check_afk(update, context, user_id, fst_name, userc_id)

    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        fst_name = message.reply_to_message.from_user.first_name
        check_afk(update, context, user_id, fst_name, userc_id)


def check_afk(update, context, user_id, fst_name, userc_id):
    if int(userc_id) == int(user_id):
        return
    is_afk, reason = sql.check_afk_status(user_id)
    if is_afk:
        if not reason:
            res = "{} is afk".format(fst_name)
            update.effective_message.reply_text(res, parse_mode=None)
        else:
            res = "{} is afk.\nReason: <code>{}</code>".format(
                html.escape(fst_name), html.escape(reason)
            )
            update.effective_message.reply_text(res, parse_mode="html")


def __gdpr__(user_id):
    sql.rm_afk(user_id)

from NekoRobot.modules.language import gs

def get_help(chat):
    return gs(chat, "afk_help")

__mod_name__ = "AFK"
