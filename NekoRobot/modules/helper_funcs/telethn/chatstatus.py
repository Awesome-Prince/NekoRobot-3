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

from telethon.tl.types import ChannelParticipantsAdmins

from NekoRobot import DRAGONS
from NekoRobot.modules.helper_funcs.telethn import IMMUNE_USERS, tbot


async def user_is_ban_protected(user_id: int, message):
    status = False
    if message.is_private or user_id in (IMMUNE_USERS):
        return True

    async for user in tbot.iter_participants(
        message.chat_id,
        filter=ChannelParticipantsAdmins,
    ):
        if user_id == user.id:
            status = True
            break
    return status


async def user_is_admin(user_id: int, message):
    status = False
    if message.is_private:
        return True

    async for user in tbot.iter_participants(
        message.chat_id,
        filter=ChannelParticipantsAdmins,
    ):
        if user_id == user.id or user_id in DRAGONS:
            status = True
            break
    return status


async def is_user_admin(user_id: int, chat_id):
    status = False
    async for user in tbot.iter_participants(
        chat_id,
        filter=ChannelParticipantsAdmins,
    ):
        if user_id == user.id or user_id in DRAGONS:
            status = True
            break
    return status


async def cutiepii_is_admin(chat_id: int):
    status = False
    cutiepii = await tbot.get_me()
    async for user in tbot.iter_participants(
        chat_id,
        filter=ChannelParticipantsAdmins,
    ):
        if cutiepii.id == user.id:
            status = True
            break
    return status


async def is_user_in_chat(chat_id: int, user_id: int):
    status = False
    async for user in tbot.iter_participants(chat_id):
        if user_id == user.id:
            status = True
            break
    return status


async def can_change_info(message):
    return message.chat.admin_rights.change_info if message.chat.admin_rights else False


async def can_ban_users(message):
    return message.chat.admin_rights.ban_users if message.chat.admin_rights else False


async def can_pin_messages(message):
    return (
        message.chat.admin_rights.pin_messages if message.chat.admin_rights else False
    )


async def can_invite_users(message):
    return (
        message.chat.admin_rights.invite_users if message.chat.admin_rights else False
    )


async def can_add_admins(message):
    return message.chat.admin_rights.add_admins if message.chat.admin_rights else False


async def can_delete_messages(message):

    if message.is_private:
        return True
    if message.chat.admin_rights:
        return message.chat.admin_rights.delete_messages
    return False
