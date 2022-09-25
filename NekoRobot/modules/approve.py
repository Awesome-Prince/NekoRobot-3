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

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram.utils.helpers import mention_html

import NekoRobot.modules.sql.approve_sql as sql
from NekoRobot import DRAGONS, NEKO_PTB
from NekoRobot.modules.disable import DisableAbleCommandHandler
from NekoRobot.modules.helper_funcs.chat_status import user_admin
from NekoRobot.modules.helper_funcs.extraction import extract_user
from NekoRobot.modules.log_channel import loggable


@loggable
@user_admin
def approve(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status in ["administrator", "creator"]:
        message.reply_text(
            "User is already admin - locks, blocklists, and antiflood already don't apply to them."
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"[{member.user['first_name']}](tg://user?id={member.user['id']}) is already approved in {chat_title}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    sql.approve(message.chat_id, user_id)
    message.reply_text(
        f"[{member.user['first_name']}](tg://user?id={member.user['id']}) has been approved in {chat_title}! They will now be ignored by automated admin actions like locks, blocklists, and antiflood.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return f"<b>{html.escape(chat.title)}:</b>\n#APPROVED\n<b>Admin:</b> {mention_html(user.id, user.first_name)}\n<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"


@loggable
@user_admin
def disapprove(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status in ["administrator", "creator"]:
        message.reply_text("This user is an admin, they can't be unapproved.")
        return ""
    if not sql.is_approved(message.chat_id, user_id):
        message.reply_text(f"{member.user['first_name']} isn't approved yet!")
        return ""
    sql.disapprove(message.chat_id, user_id)
    message.reply_text(
        f"{member.user['first_name']} is no longer approved in {chat_title}."
    )
    return f"<b>{html.escape(chat.title)}:</b>\n#UNAPPROVED\n<b>Admin:</b> {mention_html(user.id, user.first_name)}\n<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"


@user_admin
def approved(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "The following users are approved.\n"
    approved_users = sql.list_approved(message.chat_id)
    for i in approved_users:
        member = chat.get_member(int(i.user_id))
        msg += f"- `{i.user_id}`: {member.user['first_name']}\n"
    if msg.endswith("approved.\n"):
        message.reply_text(f"No users are approved in {chat_title}.")
        return ""
    else:
        message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


@user_admin
def approval(update, context):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    member = chat.get_member(int(user_id))
    if not user_id:
        message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"{member.user['first_name']} is an approved user. Locks, antiflood, and blocklists won't apply to them."
        )
    else:
        message.reply_text(
            f"{member.user['first_name']} is not an approved user. They are affected by normal commands."
        )


def unapproveall(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in DRAGONS:
        update.effective_message.reply_text(
            "Only the chat owner can unapprove all users at once."
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Unapprove all users", callback_data="unapproveall_user"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Cancel", callback_data="unapproveall_cancel"
                    )
                ],
            ]
        )
        update.effective_message.reply_text(
            f"Are you sure you would like to unapprove ALL users in {chat.title}? This action cannot be undone.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


def unapproveall_btn(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "unapproveall_user":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            approved_users = sql.list_approved(chat.id)
            users = [int(i.user_id) for i in approved_users]
            for user_id in users:
                sql.disapprove(chat.id, user_id)

        if member.status == "administrator":
            query.answer("Only owner of the chat can do this.")

        if member.status == "member":
            query.answer("You need to be admin to do this.")
    elif query.data == "unapproveall_cancel":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            message.edit_text("Removing of all approved users has been cancelled.")
            return ""
        if member.status == "administrator":
            query.answer("Only owner of the chat can do this.")
        if member.status == "member":
            query.answer("You need to be admin to do this.")


__help__ = """
Sometimes, you might trust a user not to send unwanted content.
Maybe not enough to make them admin, but you might be ok with locks, blacklists, and antiflood not applying to them.

That's what approvals are for - approve of trustworthy users to allow them to send 

*Admin commands:*
- `/approval`*:* Check a user's approval status in this chat.
- `/approve`*:* Approve of a user. Locks, blacklists, and antiflood won't apply to them anymore.
- `/unapprove`*:* Unapprove of a user. They will now be subject to locks, blacklists, and antiflood again.
- `/approved`*:* List all approved users.
- `/unapproveall`*:* Unapprove *ALL* users in a chat. This cannot be undone.
"""

APPROVE = DisableAbleCommandHandler("approve", approve, run_async=True)
DISAPPROVE = DisableAbleCommandHandler("unapprove", disapprove, run_async=True)
APPROVED = DisableAbleCommandHandler("approved", approved, run_async=True)
APPROVAL = DisableAbleCommandHandler("approval", approval, run_async=True)
UNAPPROVEALL = DisableAbleCommandHandler("unapproveall", unapproveall, run_async=True)
UNAPPROVEALL_BTN = CallbackQueryHandler(
    unapproveall_btn, pattern=r"unapproveall_.*", run_async=True
)

NEKO_PTB.add_handler(APPROVE)
NEKO_PTB.add_handler(DISAPPROVE)
NEKO_PTB.add_handler(APPROVED)
NEKO_PTB.add_handler(APPROVAL)
NEKO_PTB.add_handler(UNAPPROVEALL)
NEKO_PTB.add_handler(UNAPPROVEALL_BTN)

__mod_name__ = "Approvals"
__command_list__ = ["approve", "unapprove", "approved", "approval"]
__handlers__ = [APPROVE, DISAPPROVE, APPROVED, APPROVAL]
