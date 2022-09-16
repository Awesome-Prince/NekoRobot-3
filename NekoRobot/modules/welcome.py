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
import contextlib
import html
import random
import re
import time
import NekoRobot.modules.sql.welcome_sql as sql

from functools import partial
from contextlib import suppress
from io import BytesIO
from NekoRobot import (
    DEV_USERS,
    LOGGER,
    OWNER_ID,
    SUDO_USERS,
    SUPPORT_USERS,
    WHITELIST_USERS,
    sw,
    JOIN_LOGGER,
    NEKO_PTB,
    SUPPORT_CHAT
)
from NekoRobot.modules.helper_funcs.chat_status import (
    is_user_ban_protected,
    user_admin as u_admin,
)
from NekoRobot.modules.helper_funcs.anonymous import user_admin, AdminPerms
from NekoRobot.modules.helper_funcs.misc import build_keyboard, revert_buttons
from NekoRobot.modules.helper_funcs.msg_types import get_welcome_type
from NekoRobot.modules.helper_funcs.string_handling import (
    escape_invalid_curly_brackets,
    markdown_parser,
)
from NekoRobot.modules.log_channel import loggable
from NekoRobot.modules.sql.global_bans_sql import is_user_gbanned
from telegram import (
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    User,
)
from telegram.error import BadRequest, TelegramError
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    CommandHandler,
    filters,
    MessageHandler,
)
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown, mention_html, mention_markdown
import NekoRobot.modules.sql.log_channel_sql as logsql
from ..modules.helper_funcs.anonymous import user_admin, AdminPerms

VALID_WELCOME_FORMATTERS = [
    "first",
    "last",
    "fullname",
    "username",
    "id",
    "count",
    "chatname",
    "mention",
]

ENUM_FUNC_MAP = {
    sql.Types.TEXT.value: NEKO_PTB.bot.send_message,
    sql.Types.BUTTON_TEXT.value: NEKO_PTB.bot.send_message,
    sql.Types.STICKER.value: NEKO_PTB.bot.send_sticker,
    sql.Types.DOCUMENT.value: NEKO_PTB.bot.send_document,
    sql.Types.PHOTO.value: NEKO_PTB.bot.send_photo,
    sql.Types.AUDIO.value: NEKO_PTB.bot.send_audio,
    sql.Types.VOICE.value: NEKO_PTB.bot.send_voice,
    sql.Types.VIDEO.value: NEKO_PTB.bot.send_video,
}

VERIFIED_USER_WAITLIST = {}
CAPTCHA_ANS_DICT = {}

from multicolorcaptcha import CaptchaGenerator

WHITELISTED = (
    [OWNER_ID] + DEV_USERS + SUDO_USERS + SUPPORT_USERS + WHITELIST_USERS
)


async def send(update, message, keyboard, backup_message):
    chat = update.effective_chat
    cleanserv = sql.clean_service(chat.id)
    reply = update.message.message_id
    # Clean service welcome
    if cleanserv:
        with contextlib.suppress(BadRequest):
             NEKO_PTB.bot.delete_message(chat.id, update.message.message_id)
        reply = False
    try:
        msg =  update.effective_message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=keyboard,
            reply_to_message_id=reply,
            allow_sending_without_reply=True,
        )
    except BadRequest as excp:
        if excp.message == "Button_url_invalid":
            msg =  update.effective_message.reply_text(
                markdown_parser(
                    (
                        backup_message
                        + "\nNote: the current message has an invalid url in one of its buttons. Please update."
                    )
                ),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_to_message_id=reply,
            )

        elif excp.message == "Have no rights to send a message":
            return
        elif excp.message == "Reply message not found":
            msg =  update.effective_message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=keyboard,
                quote=False,
            )

        elif excp.message == "Unsupported url protocol":
            msg =  update.effective_message.reply_text(
                markdown_parser(
                    (
                        backup_message
                        + "\nNote: the current message has buttons which use url protocols that are unsupported by "
                        "telegram. Please update. "
                    )
                ),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_to_message_id=reply,
            )

        elif excp.message == "Wrong url host":
            msg =  update.effective_message.reply_text(
                markdown_parser(
                    (
                        backup_message
                        + "\nNote: the current message has some bad urls. Please update."
                    )
                ),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_to_message_id=reply,
            )

            LOGGER.warning(message)
            LOGGER.warning(keyboard)
            LOGGER.exception("Could not parse! got invalid url host errors")
        else:
            msg =  update.effective_message.reply_text(
                markdown_parser(
                    (
                        backup_message
                        + "\nNote: An error occured when sending the custom message. Please update."
                    )
                ),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_to_message_id=reply,
            )

            LOGGER.exception()
    return msg


@loggable
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # sourcery no-metrics
    bot, job_queue = context.bot, context.job_queue
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    log_setting = logsql.get_chat_setting(chat.id)
    if not log_setting:
        logsql.set_chat_setting(
            logsql.LogChannelSettings(chat.id, True, True, True, True, True)
        )
        log_setting = logsql.get_chat_setting(chat.id)
    should_welc, cust_welcome, cust_content, welc_type = sql.get_welc_pref(chat.id)
    welc_mutes = sql.welcome_mutes(chat.id)
    human_checks = sql.get_human_checks(user.id, chat.id)
    raid, _, deftime = sql.getRaidStatus(str(chat.id))

    new_members = update.effective_message.new_chat_members

    for new_mem in new_members:

        welcome_log = None
        res = None
        sent = None
        should_mute = True
        welcome_bool = True
        media_wel = False

        if new_mem.id == bot.id and user.id not in DEV_USERS:
          try:
              tXt = "You Can't Add Me Because, You Are Not Member Of @Black_Knights_Union!"
              member = bot.get_chat_member(-1001151980503, user.id)
              if member.status in ("kicked", "left"):
                  with suppress(BadRequest):
                         bot.send_message(chat.id, text=tXt)
                   bot.leave_chat(chat.id)
                  return
          except BadRequest as BR:
              if BR.message in ("User not found", "User_not_mutual_contact", "User_not_participant"):
                  with suppress(BadRequest):
                         bot.send_message(chat.id, text=tXt)
                   bot.leave_chat(chat.id)
                  return

        if raid and new_mem.id not in WHITELISTED:
            bantime = deftime
            with contextlib.suppress(BadRequest):
                chat.ban_member(new_mem.id, until_date=bantime)
            return


        reply = update.message.message_id
        cleanserv = sql.clean_service(chat.id)
        # Clean service welcome
        if cleanserv:
            with contextlib.suppress(BadRequest):
                 NEKO_PTB.bot.delete_message(chat.id, update.message.message_id)
            reply = False

        if should_welc:

            # Give the owner a special welcome
            if new_mem.id == OWNER_ID:
                 update.effective_message.reply_text(
                    "Oh hi, my creator.", reply_to_message_id=reply
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"Bot Owner just joined the chat"
                )
                continue

            # Welcome Devs
            if new_mem.id in DEV_USERS:
                 update.effective_message.reply_text(
                    "Whoa! A member of the Eagle Union just joined!",
                    reply_to_message_id=reply,
                )
                continue

            # Welcome Sudos
            if new_mem.id in SUDO_USERS:
                 update.effective_message.reply_text(
                    "Huh! A Royal Nation just joined! Stay Alert!",
                    reply_to_message_id=reply,
                )
                continue

            # Welcome Support
            if new_mem.id in SUPPORT_USERS:
                 update.effective_message.reply_text(
                    "Huh! Someone with a Sakura Nation level just joined!",
                    reply_to_message_id=reply,
                )
                continue

            # Welcome Whitelisted
            if new_mem.id in WHITELIST_USERS:
                 update.effective_message.reply_text(
                    "Oof! A Sadegna Nation just joined!", reply_to_message_id=reply
                )
                continue

            # Welcome yourself
            if new_mem.id == bot.id:

                 update.effective_message.reply_text(
                    f"Hey {user.first_name}, I'm {context.bot.first_name}! Thank you for adding me to {chat.title}\n"
                    "Join support and channel update with clicking button below!",
                    reply_to_message_id=reply,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="🚑 Support", url=f"https://telegram.dog/{SUPPORT_CHAT}"
                                ),
                                InlineKeyboardButton(
                                    text="📢 Updates", url="https://telegram.dog/Programmer_Updates"
                                ),
                            ]
                        ],
                    ),
                )
                creator = None

                for x in bot.get_chat_administrators(update.effective_chat.id):
                    if x.status == "creator":
                        creator = x.user
                        break
                if creator:
                    bot.send_message(
                        JOIN_LOGGER,
                        f"""
                        \\#NEWGROUP \
                        \nGroup Name:   **\\{chat.title}** \
                        \nID:   `\\{chat.id}` \
                        \nCreator ID:   `\\{creator.id}` \
                        \nCreator Username:   \@{creator.username} \
                        """,
                        parse_mode=ParseMode.MARKDOWN_V2,
                    )
                else:
                    bot.send_message(
                        JOIN_LOGGER,
                        "#NEW_GROUP\n<b>Group name:</b> {}\n<b>ID:</b> <code>{}</code>".format(
                            html.escape(chat.title),
                            chat.id,
                        ),
                        parse_mode=ParseMode.HTML,
                    )

                continue

            buttons = sql.get_welc_buttons(chat.id)
            keyb = build_keyboard(buttons)

            if welc_type not in (sql.Types.TEXT, sql.Types.BUTTON_TEXT):
                media_wel = True

            first_name = (
                new_mem.first_name or "PersonWithNoName"
            )  # edge case of empty name - occurs for some bugs.

            if cust_welcome:
                if cust_welcome == sql.DEFAULT_WELCOME:
                    cust_welcome = random.choice(
                        sql.DEFAULT_WELCOME_MESSAGES
                    ).format(first=escape_markdown(first_name))

                if new_mem.last_name:
                    fullname = escape_markdown(f"{first_name} {new_mem.last_name}")
                else:
                    fullname = escape_markdown(first_name)
                count = chat.get_member_count()
                mention = mention_markdown(new_mem.id, escape_markdown(first_name))
                if new_mem.username:
                    username = "@" + escape_markdown(new_mem.username)
                else:
                    username = mention

                valid_format = escape_invalid_curly_brackets(
                    cust_welcome, VALID_WELCOME_FORMATTERS
                )
                res = valid_format.format(
                    first=escape_markdown(first_name),
                    last=escape_markdown(new_mem.last_name or first_name),
                    fullname=escape_markdown(fullname),
                    username=username,
                    mention=mention,
                    count=count,
                    chatname=escape_markdown(chat.title),
                    id=new_mem.id,
                )

            else:
                res = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                    first=escape_markdown(first_name)
                )
                keyb = []

            backup_message = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                first=escape_markdown(first_name)
            )
            keyboard = InlineKeyboardMarkup(keyb)

        else:
            welcome_bool = False
            res = None
            keyboard = None
            backup_message = None
            reply = None

        # User exceptions from welcomemutes
        if (
            is_user_ban_protected(update, new_mem.id, chat.get_member(new_mem.id))
            or human_checks
        ):
            should_mute = False
        # Join welcome: soft mute
        if new_mem.is_bot:
            should_mute = False

        if user.id == new_mem.id and should_mute:
            if welc_mutes == "soft":
                 bot.restrict_chat_member(
                    chat.id,
                    new_mem.id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                        can_invite_users=False,
                        can_pin_messages=False,
                        can_send_polls=False,
                        can_change_info=False,
                        can_add_web_page_previews=False,
                    ),
                    until_date=(int(time.time() + 24 * 60 * 60)),
                )
                sql.set_human_checks(user.id, chat.id)
            if welc_mutes == "strong":
                welcome_bool = False
                if not media_wel:
                    VERIFIED_USER_WAITLIST.update(
                        {
                            (chat.id, new_mem.id): {
                                "should_welc": should_welc,
                                "media_wel": False,
                                "status": False,
                                "update": update,
                                "res": res,
                                "keyboard": keyboard,
                                "backup_message": backup_message,
                            }
                        }
                    )
                else:
                    VERIFIED_USER_WAITLIST.update(
                        {
                            (chat.id, new_mem.id): {
                                "should_welc": should_welc,
                                "chat_id": chat.id,
                                "status": False,
                                "media_wel": True,
                                "cust_content": cust_content,
                                "welc_type": welc_type,
                                "res": res,
                                "keyboard": keyboard,
                            }
                        }
                    )
                new_join_mem = (
                    f"[{escape_markdown(new_mem.first_name)}](tg://user?id={user.id})"
                )
                message =  msg.reply_text(
                    f"{new_join_mem}, click the button below to prove you're human.\nYou have 120 seconds.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Yes, I'm human.",
                                    callback_data=f"user_join_({new_mem.id})",
                                )
                            ]
                        ]
                    ),
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_to_message_id=reply,
                    allow_sending_without_reply=True,
                )
                 bot.restrict_chat_member(
                    chat.id,
                    new_mem.id,
                    permissions=ChatPermissions(
                        can_send_messages=False,
                        can_invite_users=False,
                        can_pin_messages=False,
                        can_send_polls=False,
                        can_change_info=False,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False,
                    ),
                )
                job_data = {
                    'member': new_mem,
                    'id': chat.id,
                    'message_id': message.message_id,
                }

                job_queue.run_once(
                    callback = check_not_bot,
                    when = 120,
                    context = job_data,
                )
            if welc_mutes == "captcha":
                btn = []
                # Captcha image size number (2 -> 640x360)
                CAPCTHA_SIZE_NUM = 2
                # Create Captcha Generator object of specified size
                generator = CaptchaGenerator(CAPCTHA_SIZE_NUM)

                # Generate a captcha image
                captcha = generator.gen_captcha_image(difficult_level=3)
                # Get information
                image = captcha["image"]
                characters = captcha["characters"]
                # print(characters)
                fileobj = BytesIO()
                fileobj.name = f"captcha_{new_mem.id}.png"
                image.save(fp=fileobj)
                fileobj.seek(0)
                CAPTCHA_ANS_DICT[(chat.id, new_mem.id)] = int(characters)
                welcome_bool = False
                if not media_wel:
                    VERIFIED_USER_WAITLIST.update(
                        {
                            (chat.id, new_mem.id): {
                                "should_welc": should_welc,
                                "media_wel": False,
                                "status": False,
                                "update": update,
                                "res": res,
                                "keyboard": keyboard,
                                "backup_message": backup_message,
                                "captcha_correct": characters,
                            }
                        }
                    )
                else:
                    VERIFIED_USER_WAITLIST.update(
                        {
                            (chat.id, new_mem.id): {
                                "should_welc": should_welc,
                                "chat_id": chat.id,
                                "status": False,
                                "media_wel": True,
                                "cust_content": cust_content,
                                "welc_type": welc_type,
                                "res": res,
                                "keyboard": keyboard,
                                "captcha_correct": characters,
                            }
                        }
                    )

                nums = [random.randint(1000, 9999) for _ in range(7)]
                nums.append(characters)
                random.shuffle(nums)
                to_append = []
                # print(nums)
                for a in nums:
                    to_append.append(
                        InlineKeyboardButton(
                            text=str(a),
                            callback_data=f"user_captchajoin_({chat.id},{new_mem.id})_({a})",
                        )
                    )
                    if len(to_append) > 2:
                        btn.append(to_append)
                        to_append = []
                if to_append:
                    btn.append(to_append)

                message =  msg.reply_photo(
                    fileobj,
                    caption=f"Welcome [{escape_markdown(new_mem.first_name)}](tg://user?id={user.id}). Click the correct button to get unmuted!\n"
                    f"You got 120 seconds for this.",
                    reply_markup=InlineKeyboardMarkup(btn),
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_to_message_id=reply,
                    allow_sending_without_reply=True,
                )
                 bot.restrict_chat_member(
                    chat.id,
                    new_mem.id,
                    permissions=ChatPermissions(
                        can_send_messages=False,
                        can_invite_users=False,
                        can_pin_messages=False,
                        can_send_polls=False,
                        can_change_info=False,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False,
                    ),
                )
                job_queue.run_once(
                    partial(check_not_bot, new_mem, chat.id, message.message_id),
                    120,
                    name="welcomemute",
                )

        if welcome_bool:
            if media_wel:
                if ENUM_FUNC_MAP[welc_type] == NEKO_PTB.bot.send_sticker:
                    sent = ENUM_FUNC_MAP[welc_type](
                        chat.id,
                        cust_content,
                        reply_markup=keyboard,
                        reply_to_message_id=reply,
                    )
                else:
                    sent = ENUM_FUNC_MAP[welc_type](
                        chat.id,
                        cust_content,
                        caption=res,
                        reply_markup=keyboard,
                        reply_to_message_id=reply,
                        parse_mode="markdown",
                    )
            else:
                sent =  send(update, res, keyboard, backup_message)
            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                with contextlib.suppress(BadRequest):
                     bot.delete_message(chat.id, prev_welc)

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

        if not log_setting.log_joins:
            return ""
        if welcome_log:
            return welcome_log

    return ""


async def check_not_bot(
    member: User, chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE
):
    bot = context.bot
    member_dict = VERIFIED_USER_WAITLIST.pop((chat_id, member.id))
    member_status = member_dict.get("status")
    if not member_status:
        with contextlib.suppress(BadRequest):
             bot.unban_chat_member(chat_id, member.id)

        try:
             bot.edit_message_text(
                "*kicks user*\nThey can always rejoin and try.",
                chat_id=chat_id,
                message_id=message_id,
            )
        except TelegramError:
             bot.delete_message(chat_id=chat_id, message_id=message_id)
             bot.send_message(
                "{} was kicked as they failed to verify themselves".format(
                    mention_html(member.id, member.first_name)
                ),
                chat_id=chat_id,
                parse_mode=ParseMode.HTML,
            )


async def left_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # sourcery no-metrics
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user
    should_goodbye, cust_goodbye, goodbye_type = sql.get_gdbye_pref(chat.id)

    if user.id == bot.id:
        return

    reply = update.message.message_id
    cleanserv = sql.clean_service(chat.id)
    # Clean service welcome
    if cleanserv:
        with contextlib.suppress(BadRequest):
             NEKO_PTB.bot.delete_message(chat.id, update.message.message_id)
        reply = False

    if should_goodbye:

        left_mem = update.effective_message.left_chat_member
        if left_mem:

            # Thingy for spamwatched users
            if sw:
                sw_ban = sw.get_ban(left_mem.id)
                if sw_ban:
                    return

            # Dont say goodbyes to gbanned users
            if is_user_gbanned(left_mem.id):
                return

            # Ignore bot being kicked
            if left_mem.id == bot.id:
                return

            # Give the owner a special goodbye
            if left_mem.id == OWNER_ID:
                 update.effective_message.reply_text(
                    "Sorry to see you leave :(", reply_to_message_id=reply
                )
                return

            # Give the devs a special goodbye
            elif left_mem.id in DEV_USERS:
                 update.effective_message.reply_text(
                    "See you later at the Eagle Union!",
                    reply_to_message_id=reply,
                )
                return

            # if media goodbye, use appropriate function for it
            if goodbye_type not in [sql.Types.TEXT, sql.Types.BUTTON_TEXT]:
                ENUM_FUNC_MAP[goodbye_type](chat.id, cust_goodbye)
                return

            first_name = (
                left_mem.first_name or "PersonWithNoName"
            )  # edge case of empty name - occurs for some bugs.
            if cust_goodbye:
                if cust_goodbye == sql.DEFAULT_GOODBYE:
                    cust_goodbye = random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(
                        first=escape_markdown(first_name)
                    )
                if left_mem.last_name:
                    fullname = escape_markdown(f"{first_name} {left_mem.last_name}")
                else:
                    fullname = escape_markdown(first_name)
                count = chat.get_member_count()
                mention = mention_markdown(left_mem.id, first_name)
                if left_mem.username:
                    username = "@" + escape_markdown(left_mem.username)
                else:
                    username = mention

                valid_format = escape_invalid_curly_brackets(
                    cust_goodbye, VALID_WELCOME_FORMATTERS
                )
                res = valid_format.format(
                    first=escape_markdown(first_name),
                    last=escape_markdown(left_mem.last_name or first_name),
                    fullname=escape_markdown(fullname),
                    username=username,
                    mention=mention,
                    count=count,
                    chatname=escape_markdown(chat.title),
                    id=left_mem.id,
                )
                buttons = sql.get_gdbye_buttons(chat.id)
                keyb = build_keyboard(buttons)

            else:
                res = random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(
                    first=first_name
                )
                keyb = []

            keyboard = InlineKeyboardMarkup(keyb)

             send(
                update,
                res,
                keyboard,
                random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(first=first_name),
            )


@u_admin
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    chat = update.effective_chat
    # if no args, show current replies.
    if not args or args[0].lower() == "noformat":
        noformat = True
        pref, welcome_m, cust_content, welcome_type = sql.get_welc_pref(chat.id)
         update.effective_message.reply_text(
            f"This chat has it's welcome setting set to: `{pref}`.\n"
            f"*The welcome message (not filling the {{}}) is:*",
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        if welcome_type in [sql.Types.BUTTON_TEXT, sql.Types.TEXT]:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                 update.effective_message.reply_text(welcome_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                 send(update, welcome_m, keyboard, sql.DEFAULT_WELCOME)
        else:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                ENUM_FUNC_MAP[welcome_type](chat.id, cust_content, caption=welcome_m)

            else:
                if welcome_type in [sql.Types.TEXT, sql.Types.BUTTON_TEXT]:
                    kwargs = {'disable_web_page_preview': True}
                else:
                    kwargs = {}
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)
                ENUM_FUNC_MAP[welcome_type](
                    chat.id,
                    cust_content,
                    caption=welcome_m,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    **kwargs,
                )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_welc_preference(str(chat.id, True)
             update.effective_message.reply_text(
                "Okay! I'll greet members when they join."
            )

        elif args[0].lower() in ("off", "no"):
            sql.set_welc_preference(str(chat.id, False)
             update.effective_message.reply_text(
                "I'll go loaf around and not welcome anyone then."
            )

        else:
             update.effective_message.reply_text(
                "I understand 'on/yes' or 'off/no' only!"
            )


@u_admin
async def goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    chat = update.effective_chat

    if not args or args[0] == "noformat":
        noformat = True
        pref, goodbye_m, goodbye_type = sql.get_gdbye_pref(chat.id)
         update.effective_message.reply_text(
            f"This chat has it's goodbye setting set to: `{pref}`.\n"
            f"*The goodbye  message (not filling the {{}}) is:*",
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        if goodbye_type == sql.Types.BUTTON_TEXT:
            buttons = sql.get_gdbye_buttons(chat.id)
            if noformat:
                goodbye_m += revert_buttons(buttons)
                 update.effective_message.reply_text(goodbye_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                 send(update, goodbye_m, keyboard, sql.DEFAULT_GOODBYE)

        elif noformat:
            ENUM_FUNC_MAP[goodbye_type](chat.id, goodbye_m)

        else:
            ENUM_FUNC_MAP[goodbye_type](
                chat.id, goodbye_m, parse_mode=ParseMode.MARKDOWN_V2
            )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_gdbye_preference(str(chat.id, True)
             update.effective_message.reply_text("Ok!")

        elif args[0].lower() in ("off", "no"):
            sql.set_gdbye_preference(str(chat.id, False)
             update.effective_message.reply_text("Ok!")

        else:
            # idek what you're writing, say yes or no
             update.effective_message.reply_text(
                "I understand 'on/yes' or 'off/no' only!"
            )


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
         msg.reply_text("You didn't specify what to reply with!")
        return ""

    sql.set_custom_welcome(chat.id, content, text, data_type, buttons)
     msg.reply_text("Successfully set custom welcome message!")

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#SET_WELCOME\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Set the welcome message."
    )


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
async def reset_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_welcome(chat.id, None, sql.DEFAULT_WELCOME, sql.Types.TEXT)
     update.effective_message.reply_text(
        "Successfully reset welcome message to default!"
    )

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RESET_WELCOME\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Reset the welcome message to default."
    )


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
async def set_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
         msg.reply_text("You didn't specify what to reply with!")
        return ""

    sql.set_custom_gdbye(chat.id, content or text, data_type, buttons)
     msg.reply_text("Successfully set custom goodbye message!")
    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#SET_GOODBYE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Set the goodbye message."
    )


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
async def reset_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_gdbye(chat.id, sql.DEFAULT_GOODBYE, sql.Types.TEXT)
     update.effective_message.reply_text(
        "Successfully reset goodbye message to default!"
    )

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RESET_GOODBYE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Reset the goodbye message."
    )


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
async def welcomemute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    if len(args) >= 1:
        if args[0].lower() in ("off", "no"):
            sql.set_welcome_mutes(chat.id, False)
             msg.reply_text("I will no longer mute people on joining!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>➛ Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has toggled welcome mute to <b>OFF</b>."
            )
        elif args[0].lower() in ["soft"]:
            sql.set_welcome_mutes(chat.id, "soft")
             msg.reply_text(
                "I will restrict users' permission to send media for 24 hours."
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>➛ Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has toggled welcome mute to <b>SOFT</b>."
            )
        elif args[0].lower() in ["strong"]:
            sql.set_welcome_mutes(chat.id, "strong")
             msg.reply_text(
                "I will now mute people when they join until they prove they're not a bot.\nThey will have 120seconds "
                "before they get kicked. "
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>➛ Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has toggled welcome mute to <b>STRONG</b>."
            )
        elif args[0].lower() in ["captcha"]:
            sql.set_welcome_mutes(chat.id, "captcha")
             msg.reply_text(
                "I will now mute people when they join until they prove they're not a bot.\nThey have to solve a "
                "captcha to get unmuted. "
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>➛ Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has toggled welcome mute to <b>CAPTCHA</b>."
            )
        else:
             msg.reply_text(
                "Please enter `off`/`no`/`soft`/`strong`/`captcha`!",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            return ""
    else:
        curr_setting = sql.welcome_mutes(chat.id)
        reply = (
            f"\n Give me a setting!\nChoose one out of: `off`/`no` or `soft`, `strong` or `captcha` only! \n"
            f"Current setting: `{curr_setting}`"
        )
         msg.reply_text(reply, parse_mode=ParseMode.MARKDOWN_V2)
        return ""


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
async def clean_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user

    if not args:
        clean_pref = sql.get_clean_pref(chat.id)
        if clean_pref:
             update.effective_message.reply_text(
                "I should be deleting welcome messages up to two days old."
            )
        else:
             update.effective_message.reply_text(
                "I'm currently not deleting old welcome messages!"
            )
        return ""

    if args[0].lower() in ("on", "yes"):
        sql.set_clean_welcome(str(chat.id, True)
         update.effective_message.reply_text(
            "I'll try to delete old welcome messages!"
        )
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#CLEAN_WELCOME\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"Has toggled clean welcomes to <code>ON</code>."
        )
    elif args[0].lower() in ("off", "no"):
        sql.set_clean_welcome(str(chat.id, False)
         update.effective_message.reply_text(
            "I won't delete old welcome messages."
        )
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#CLEAN_WELCOME\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"Has toggled clean welcomes to <code>OFF</code>."
        )
    else:
         update.effective_message.reply_text(
            "I understand 'on/yes' or 'off/no' only!"
        )
        return ""


@user_admin(AdminPerms.CAN_CHANGE_INFO)
async def cleanservice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat = update.effective_chat  # type: Optional[Chat]
    if chat.type == chat.PRIVATE:
        curr = sql.clean_service(chat.id)
        if curr:
             update.effective_message.reply_text(
                "Welcome clean service is : on", parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
             update.effective_message.reply_text(
                "Welcome clean service is : off", parse_mode=ParseMode.MARKDOWN_V2
            )

    elif len(args) >= 1:
        var = args[0]
        if var in ("no", "off"):
            sql.set_clean_service(chat.id, False)
             update.effective_message.reply_text("Welcome clean service is : off")
        elif var in ("yes", "on"):
            sql.set_clean_service(chat.id, True)
             update.effective_message.reply_text("Welcome clean service is : on")
        else:
             update.effective_message.reply_text(
                "Invalid option", parse_mode=ParseMode.MARKDOWN_V2
            )
    else:
         update.effective_message.reply_text(
            "Usage is on/yes or off/no", parse_mode=ParseMode.MARKDOWN_V2
        )


async def user_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user = update.effective_user
    query = update.callback_query
    bot = context.bot
    match = re.match(r"user_join_\((.+?)\)", query.data)
    message = update.effective_message
    join_user = int(match[1])

    if join_user == user.id:
        sql.set_human_checks(user.id, chat.id)
        member_dict = VERIFIED_USER_WAITLIST[(chat.id, user.id)]
        member_dict["status"] = True
         query.answer(text="Yeet! You're a human, unmuted!")
         bot.restrict_chat_member(
            chat.id,
            user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_send_polls=True,
                can_change_info=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        with contextlib.suppress(Exception):
             bot.deleteMessage(chat.id, message.message_id)
        if member_dict["should_welc"]:
            if member_dict["media_wel"]:
                sent = ENUM_FUNC_MAP[member_dict["welc_type"]](
                    member_dict["chat_id"],
                    member_dict["cust_content"],
                    caption=member_dict["res"],
                    reply_markup=member_dict["keyboard"],
                    parse_mode="markdown",
                )
            else:
                sent =  send(
                    member_dict["update"],
                    member_dict["res"],
                    member_dict["keyboard"],
                    member_dict["backup_message"],
                )

            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                with contextlib.suppress(BadRequest):
                     bot.delete_message(chat.id, prev_welc)

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

    else:
         query.answer(text="You're not allowed to do this!")


async def user_captcha_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # sourcery no-metrics
    chat = update.effective_chat
    user = update.effective_user
    query = update.callback_query
    bot = context.bot
    # print(query.data)
    match = re.match(r"user_captchajoin_\(([\d\-]+),(\d+)\)_\((\d{4})\)", query.data)
    message = update.effective_message
    join_chat = int(match[1])
    join_user = int(match[2])
    captcha_ans = int(match[3])
    join_usr_data =  bot.getChat(join_user)

    if join_user == user.id:
        c_captcha_ans = CAPTCHA_ANS_DICT.pop((join_chat, join_user))
        if c_captcha_ans == captcha_ans:
            sql.set_human_checks(user.id, chat.id)
            member_dict = VERIFIED_USER_WAITLIST[(chat.id, user.id)]
            member_dict["status"] = True
             query.answer(text="Yeet! You're a human, unmuted!")
             bot.restrict_chat_member(
                chat.id,
                user.id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                    can_send_polls=True,
                    can_change_info=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )
            try:
                 bot.deleteMessage(chat.id, message.message_id)
            except BadRequest:
                pass
            if member_dict["should_welc"]:
                if member_dict["media_wel"]:
                    sent = ENUM_FUNC_MAP[member_dict["welc_type"]](
                        member_dict["chat_id"],
                        member_dict["cust_content"],
                        caption=member_dict["res"],
                        reply_markup=member_dict["keyboard"],
                        parse_mode="markdown",
                    )
                else:
                    sent =  send(
                        member_dict["update"],
                        member_dict["res"],
                        member_dict["keyboard"],
                        member_dict["backup_message"],
                    )

                prev_welc = sql.get_clean_pref(chat.id)
                if prev_welc:
                    with contextlib.suppress(BadRequest):
                         bot.delete_message(chat.id, prev_welc)

                    if sent:
                        sql.set_clean_welcome(chat.id, sent.message_id)
        else:
            try:
                 bot.deleteMessage(chat.id, message.message_id)
            except BadRequest:
                pass
            kicked_msg = f"""
            ❌ [{escape_markdown(join_usr_data.first_name)}](tg://user?id={join_user}) failed the captcha and was kicked.
            """
             query.answer(text="Wrong answer")
            res = chat.unban_member(join_user)
            if res:
                 bot.sendMessage(
                    chat_id=chat.id, text=kicked_msg, parse_mode=ParseMode.MARKDOWN_V2
                )

    else:
         query.answer(text="You're not allowed to do this!")


WELC_HELP_TXT = (
    "Your group's welcome/goodbye messages can be personalised in multiple ways. If you want the messages"
    " to be individually generated, like the default welcome message is, you can use *these* variables:\n"
    " ➛ `{first}`*:* this represents the user's *first* name\n"
    " ➛ `{last}`*:* this represents the user's *last* name. Defaults to *first name* if user has no "
    "last name.\n"
    " ➛ `{fullname}`*:* this represents the user's *full* name. Defaults to *first name* if user has no "
    "last name.\n"
    " ➛ `{username}`*:* this represents the user's *username*. Defaults to a *mention* of the user's "
    "first name if has no username.\n"
    " ➛ `{mention}`*:* this simply *mentions* a user - tagging them with their first name.\n"
    " ➛ `{id}`*:* this represents the user's *id*\n"
    " ➛ `{count}`*:* this represents the user's *member number*.\n"
    " ➛ `{chatname}`*:* this represents the *current chat name*.\n"
    "\nEach variable MUST be surrounded by `{}` to be replaced.\n"
    "Welcome messages also support markdown, so you can make any elements bold/italic/code/links. "
    "Buttons are also supported, so you can make your welcomes look awesome with some nice intro "
    "buttons.\n"
    f"To create a button linking to your rules, use this: `[Rules](buttonurl://t.me/NekoX_Bot?start=group_id)`. "
    "Simply replace `group_id` with your group's id, which can be obtained via /id, and you're good to "
    "go. Note that group ids are usually preceded by a `-` sign; this is required, so please don't "
    "remove it.\n"
    "You can even set images/gifs/videos/voice messages as the welcome message by "
    "replying to the desired media, and calling `/setwelcome`."
)

WELC_MUTE_HELP_TXT = (
    "You can get the bot to mute new people who join your group and hence prevent spambots from flooding your group. "
    "The following options are possible:\n"
    "➛ `/welcomemute soft`*:* restricts new members from sending media for 24 hours.\n"
    "➛ `/welcomemute strong`*:* mutes new members till they tap on a button thereby verifying they're human.\n"
    "➛ `/welcomemute captcha`*:*  mutes new members till they solve a button captcha thereby verifying they're human.\n"
    "➛ `/welcomemute off`*:* turns off welcomemute.\n"
    "*Note:* Strong mode kicks a user from the chat if they dont verify in 120seconds. They can always rejoin though"
)


@u_admin
async def welcome_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
     update.effective_message.reply_text(
        WELC_HELP_TXT, parse_mode=ParseMode.MARKDOWN_V2
    )


@u_admin
async def welcome_mute_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
     update.effective_message.reply_text(
        WELC_MUTE_HELP_TXT, parse_mode=ParseMode.MARKDOWN_V2
    )


# TODO: get welcome data from group butler snap
# def __import_data__(chat_id, data):
#     welcome = data.get('info', {}).get('rules')
#     welcome = welcome.replace('$username', '{username}')
#     welcome = welcome.replace('$name', '{fullname}')
#     welcome = welcome.replace('$id', '{id}')
#     welcome = welcome.replace('$title', '{chatname}')
#     welcome = welcome.replace('$surname', '{lastname}')
#     welcome = welcome.replace('$rules', '{rules}')
#     sql.set_custom_welcome(chat_id, welcome, sql.Types.TEXT)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    welcome_pref = sql.get_welc_pref(chat_id)[0]
    goodbye_pref = sql.get_gdbye_pref(chat_id)[0]
    return (
        "This chat has it's welcome preference set to `{}`.\n"
        "It's goodbye preference is `{}`.".format(welcome_pref, goodbye_pref)
    )


NEKO_PTB.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member, block=False))
NEKO_PTB.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left_member, block=False))
NEKO_PTB.add_handler(CommandHandler("welcome", welcome, filters=filters.ChatType.GROUPS))
NEKO_PTB.add_handler(CommandHandler("goodbye", goodbye, filters=filters.ChatType.GROUPS))
NEKO_PTB.add_handler(CommandHandler("setwelcome", set_welcome, filters=filters.ChatType.GROUPS))
NEKO_PTB.add_handler(CommandHandler("setgoodbye", set_goodbye, filters=filters.ChatType.GROUPS))
NEKO_PTB.add_handler(CommandHandler("resetwelcome", reset_welcome, filters=filters.ChatType.GROUPS))
NEKO_PTB.add_handler(CommandHandler("resetgoodbye", reset_goodbye, filters=filters.ChatType.GROUPS))
NEKO_PTB.add_handler(CommandHandler("welcomemute", welcomemute, filters=filters.ChatType.GROUPS))
NEKO_PTB.add_handler(CommandHandler("cleanservice", cleanservice, filters=filters.ChatType.GROUPS))
NEKO_PTB.add_handler(CommandHandler("cleanwelcome", clean_welcome, filters=filters.ChatType.GROUPS))
NEKO_PTB.add_handler(CommandHandler("welcomehelp", welcome_help))
NEKO_PTB.add_handler(CommandHandler("welcomemutehelp", welcome_mute_help))
NEKO_PTB.add_handler(CallbackQueryHandler(user_button, pattern=r"user_join_", block=False))
NEKO_PTB.add_handler(CallbackQueryHandler(user_captcha_button, pattern=r"user_captchajoin_\([\d\-]+,\d+\)_\(\d{4}\)", block=False))

__mod_name__ = "Greetings"