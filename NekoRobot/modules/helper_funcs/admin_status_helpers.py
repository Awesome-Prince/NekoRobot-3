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

from enum import Enum
from time import perf_counter

from cachetools import TTLCache
from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
)
from telegram.constants import ParseMode

from NekoRobot import DEV_USERS, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS

# stores admin in memory for 10 min.
ADMINS_CACHE = TTLCache(maxsize=512, ttl=(60 * 30), timer=perf_counter)

# stores bot admin status in memory for 10 min.
BOT_ADMIN_CACHE = TTLCache(maxsize=512, ttl=(60 * 10), timer=perf_counter)

SUDO_USERS = SUDO_USERS + DEV_USERS

WHITELIST_USERS = WHITELIST_USERS + SUDO_USERS

SUPPORT_USERS = SUPPORT_USERS + SUDO_USERS


class AdminPerms(Enum):
    CAN_RESTRICT_MEMBERS = "Can Restrict Members"
    CAN_PROMOTE_MEMBERS = "Can Promote Members"
    CAN_INVITE_USERS = "Can Invite Users"
    CAN_DELETE_MESSAGES = "Can Delete Messages"
    CAN_CHANGE_INFO = "Can Change Info"
    CAN_PIN_MESSAGES = "Can Pin Messages"
    IS_ANONYMOUS = "Is Anonymous"


class ChatStatus(Enum):
    CREATOR = "Creator"
    ADMIN = "Administrator"


# class SuperUsers(Enum):
# 	Owner = [OWNER_ID]
# 	SysAdmin = [OWNER_ID, SYS_ADMIN]
# 	Devs = DEV_USERS
# 	Sudos = SUDO_USERS
# 	Supports = SUPPORT_USERS
# 	Whitelist = WHITELIST_USERS
# 	Mods = MOD_USERS


async def anon_reply_markup(cb_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Prove identity", callback_data=cb_id)]]
    )


anon_reply_text = (
    "Seems like you're anonymous, click the button below to prove your identity"
)


async def edit_anon_msg(msg: Message, text: str):
    """
    edit anon check message and remove the button
    """
    msg.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=None)


async def user_is_not_admin_errmsg(
    msg: Message, permission: AdminPerms = None, cb: CallbackQuery = None
):
    errmsg = f"You are missing the following rights to use this command:\n*{permission.value}*"
    if cb:
        return cb.answer(errmsg, show_alert=True)
    return  msg.reply_text(errmsg, parse_mode=ParseMode.MARKDOWN_V2)


async def button_expired_error(u: Update):
    errmsg = "This button has expired!"
    if u.callback_query:
        u.callback_query.answer(errmsg, show_alert=True)
        u.effective_message.delete()
        return
    return u.effective_message.edit_text(errmsg, parse_mode=ParseMode.MARKDOWN_V2)


anon_callbacks = {}
