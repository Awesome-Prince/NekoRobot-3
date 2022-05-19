
import contextlib
import html
import logging
import random

from telegram import Update, MessageEntity
from telegram.ext import filters, CallbackContext
from telegram.error import BadRequest
from NekoRobot.modules.sql import afk_sql as sql
from NekoRobot.modules.users import get_user_id
from NekoRobot.modules.helper_funcs.decorators import kigcmd, kigmsg


@kigmsg(filters.Regex("(?i)^brb"), friendly="afk", group=3)
@kigcmd(command="afk", group=3)
async def afk(update: Update, context: CallbackContext):
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
    with contextlib.suppress(BadRequest):
        await update.effective_message.reply_text(f"{fname} is now away!{notice}")


@kigmsg((filters.ALL & filters.ChatType.GROUPS), friendly="afk", group=1)
async def no_longer_afk(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.effective_message

    if not user:  # ignore channels
        return

    if sql.rm_afk(user.id):
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
            await update.effective_message.reply_text(
                chosen_option.format(firstname), parse_mode=None
            )
        except Exception:
            return


@kig_cmd(
    (
        filters.Entity(MessageEntity.MENTION)
        | filters.Entity(MessageEntity.TEXT_MENTION) & filters.ChatType.GROUPS
    ),
    friendly="afk",
    group=8,
)
async def reply_afk(update: Update, context: CallbackContext):
    bot = context.bot
    message = update.effective_message
    userc = update.effective_user
    userc_id = userc.id
    if message.entities and (await message.parse_entities(
        [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
    )):
        entities = await message.parse_entities(
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

            user_id = await get_user_id(message.text[ent.offset : ent.offset + ent.length])
            if not user_id:
                # Should never happen, since for a user to become AFK they must have spoken. Maybe changed username?
                return

            if user_id in chk_users:
                return
            chk_users.append(user_id)

            try:
                chat = await bot.get_chat(user_id)
            except BadRequest:
                logging.error(f"Error: Could not fetch userid {user_id} for AFK module")
                return
            fst_name = chat.first_name

            await check_afk(update, context, user_id, fst_name, userc_id)

    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        fst_name = message.reply_to_message.from_user.first_name
        await check_afk(update, context, user_id, fst_name, userc_id)


async def check_afk(update, context, user_id, fst_name, userc_id):
    if int(userc_id) == int(user_id):
        return
    is_afk, reason = sql.check_afk_status(user_id)
    if is_afk:
        if not reason:
            res = f"{fst_name} is afk"
            await update.effective_message.reply_text(res, parse_mode=None)
        else:
            res = "{} is afk.\nReason: <code>{}</code>".format(
                html.escape(fst_name), html.escape(reason)
            )
            await update.effective_message.reply_text(res, parse_mode="html")


def __gdpr__(user_id):
    sql.rm_afk(user_id)


__mod_name__ = "AFK"
