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

import functools
from enum import Enum

from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

from NekoRobot import DEV_USERS, DRAGONS, NEKO_PTB
from NekoRobot.modules.helper_funcs.decorators import nekocallback


class AdminPerms(Enum):
    CAN_RESTRICT_MEMBERS = "can_restrict_members"
    CAN_PROMOTE_MEMBERS = "can_promote_members"
    CAN_INVITE_USERS = "can_invite_users"
    CAN_DELETE_MESSAGES = "can_delete_messages"
    CAN_CHANGE_INFO = "can_change_info"
    CAN_PIN_MESSAGES = "can_pin_messages"


class ChatStatus(Enum):
    CREATOR = "creator"
    ADMIN = "administrator"


anon_callbacks = {}
anon_callback_messages = {}


def user_admin(permission: AdminPerms):
    def wrapper(func):
        @functools.wraps(func)
        def awrapper(update: Update, context: CallbackContext, *args, **kwargs):
            nonlocal permission
            if update.effective_chat.type == "private":
                return func(update, context, *args, **kwargs)
            message = update.effective_message
            is_anon = bool(update.effective_message.sender_chat)

            if is_anon:
                callback_id = (
                    f"anoncb/{message.chat.id}/{message.message_id}/{permission.value}"
                )
                anon_callbacks[(message.chat.id, message.message_id)] = (
                    (update, context),
                    func,
                )
                anon_callback_messages[(message.chat.id, message.message_id)] = (
                    message.reply_text(
                        "Seems like you're anonymous, click the button below to prove your identity",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="Prove identity", callback_data=callback_id
                                    )
                                ]
                            ]
                        ),
                    )
                ).message_id
                # send message with callback f'anoncb{callback_id}'
            else:
                user_id = message.from_user.id
                chat_id = message.chat.id
                mem = context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
                if (
                    getattr(mem, permission.value) is True
                    or mem.status == "creator"
                    or user_id in DRAGONS
                ):
                    return func(update, context, *args, **kwargs)
                else:
                    return message.reply_text(
                        f"You lack the permission: `{permission.name}`",
                        parse_mode=ParseMode.MARKDOWN,
                    )

        return awrapper

    return wrapper


@nekocallback(pattern="anoncb")
def anon_callback_handler1(upd: Update, _: CallbackContext):
    callback = upd.callback_query
    perm = callback.data.split("/")[3]
    chat_id = int(callback.data.split("/")[1])
    message_id = int(callback.data.split("/")[2])
    try:
        mem = upd.effective_chat.get_member(user_id=callback.from_user.id)
    except BaseException as e:
        callback.answer(f"Error: {e}", show_alert=True)
        return
    if mem.status not in [ChatStatus.ADMIN.value, ChatStatus.CREATOR.value]:
        callback.answer("You're aren't admin.")
        NEKO_PTB.bot.delete_message(
            chat_id, anon_callback_messages.pop((chat_id, message_id), None)
        )
        NEKO_PTB.bot.send_message(
            chat_id, "You lack the permissions required for this command"
        )
    elif (
        getattr(mem, perm) is True
        or mem.status == "creator"
        or mem.user.id in DEV_USERS
    ):
        cb = anon_callbacks.pop((chat_id, message_id), None)
        if cb:
            message_id = anon_callback_messages.pop((chat_id, message_id), None)
            if message_id is not None:
                NEKO_PTB.bot.delete_message(chat_id, message_id)
            return cb[1](cb[0][0], cb[0][1])
    else:
        callback.answer("This isn't for ya")
