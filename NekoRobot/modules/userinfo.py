import datetime
import html
import platform
import time
from platform import python_version

import requests
from psutil import boot_time, cpu_percent, disk_usage, virtual_memory
from telegram import (
    MAX_MESSAGE_LENGTH,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MessageEntity,
    ParseMode,
    Update,
)
from telegram import __version__ as ptbver
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler
from telegram.utils.helpers import escape_markdown, mention_html
from telethon import events
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import ChannelParticipantsAdmins

import NekoRobot.modules.sql.userinfo_sql as sql
from NekoRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    INFOPIC,
    NEKO_PTB,
    OWNER_ID,
    SUPPORT_CHAT,
    TIGERS,
    WOLVES,
    StartTime,
    sw,
    tbot,
)
from NekoRobot.__main__ import STATS, TOKEN, USER_INFO
from NekoRobot.modules.disable import DisableAbleCommandHandler
from NekoRobot.modules.helper_funcs.chat_status import sudo_plus
from NekoRobot.modules.helper_funcs.extraction import extract_user
from NekoRobot.modules.sql.afk_sql import check_afk_status, is_afk
from NekoRobot.modules.sql.global_bans_sql import is_user_gbanned
from NekoRobot.modules.sql.users_sql import get_user_num_chats

NEKO_IMG = "https://telegra.ph/file/a21731c0c4c7f27a3ec16.jpg"


def no_by_per(totalhp, percentage):
    """
    rtype: num of `percentage` from total
    eg: 1000, 10 -> 10% of 1000 (100)
    """
    return totalhp * percentage / 100


def get_percentage(totalhp, earnedhp):
    """
    rtype: percentage of `totalhp` num
    eg: (1000, 100) will return 10%
    """

    matched_less = totalhp - earnedhp
    per_of_totalhp = 100 - matched_less * 100.0 / totalhp
    per_of_totalhp = str(int(per_of_totalhp))
    return per_of_totalhp


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


def hpmanager(user):
    total_hp = (get_user_num_chats(user.id) + 10) * 10

    if not is_user_gbanned(user.id):
        # Assign new var `new_hp` since we need `total_hp` in
        # end to calculate percentage.
        new_hp = total_hp

        # if no username decrease 25% of hp.
        if not user.username:
            new_hp -= no_by_per(total_hp, 25)
        try:
            NEKO_PTB.bot.get_user_profile_photos(user.id).photos[0][-1]
        except IndexError:
            # no profile photo ==> -25% of hp
            new_hp -= no_by_per(total_hp, 25)
        # if no /setme exist ==> -20% of hp
        if not sql.get_user_me_info(user.id):
            new_hp -= no_by_per(total_hp, 20)
        # if no bio exsit ==> -10% of hp
        if not sql.get_user_bio(user.id):
            new_hp -= no_by_per(total_hp, 10)

        if is_afk(user.id):
            afkst = check_afk_status(user.id)
            # if user is afk and no reason then decrease 7%
            # else if reason exist decrease 5%
            new_hp -= no_by_per(total_hp, 7) if not afkst else no_by_per(total_hp, 5)
            # fbanned users will have (2*number of fbans) less from max HP
            # Example: if HP is 100 but user has 5 diff fbans
            # Available HP is (2*5) = 10% less than Max HP
            # So.. 10% of 100HP = 90HP

    else:
        new_hp = no_by_per(total_hp, 5)

    return {
        "earnedhp": int(new_hp),
        "totalhp": int(total_hp),
        "percentage": get_percentage(total_hp, new_hp),
    }


def make_bar(per):
    done = min(round(per / 10), 10)
    return "◈" * done + "◇" * (10 - done)


def get_id(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    chat = update.effective_chat
    msg = update.effective_message
    user_id = extract_user(msg, args)

    if user_id:
        if msg.reply_to_message and msg.reply_to_message.forward_from:
            user1 = message.reply_to_message.from_user
            user2 = message.reply_to_message.forward_from

            msg.reply_text(
                f"<b>Telegram ID:</b>,"
                f"• {html.escape(user2.first_name)} - <code>{user2.id}</code>.\n"
                f"• {html.escape(user1.first_name)} - <code>{user1.id}</code>.",
                parse_mode=ParseMode.HTML,
            )

        else:
            user = bot.get_chat(user_id)
            msg.reply_text(
                f"{html.escape(user.first_name)}'s id is <code>{user.id}</code>.",
                parse_mode=ParseMode.HTML,
            )

    elif chat.type == "private":
        msg.reply_text(
            f"Your id is <code>{chat.id}</code>.",
            parse_mode=ParseMode.HTML,
        )

    else:
        msg.reply_text(
            f"<b>{message.chat.title}</b>'s id is <code>{chat.id}</code>.",
            parse_mode=ParseMode.HTML,
        )


@tbot.on(
    events.NewMessage(
        pattern="/ginfo ",
        from_users=(TIGERS or []) + (DRAGONS or []) + (DEMONS or []),
    ),
)
async def group_info(event) -> None:
    chat = event.text.split(" ", 1)[1]
    try:
        entity = await event.client.get_entity(chat)
        totallist = await event.client.get_participants(
            entity,
            filter=ChannelParticipantsAdmins,
        )
        ch_full = await event.client(GetFullChannelRequest(channel=entity))
    except:
        await event.reply(
            "Can't for some reason, maybe it is a private one or that I am banned there.",
        )
        return
    msg = f"**ID**: `{entity.id}`"
    msg += f"\n**Title**: `{entity.title}`"
    msg += f"\n**Datacenter**: `{entity.photo.dc_id}`"
    msg += f"\n**Video PFP**: `{entity.photo.has_video}`"
    msg += f"\n**Supergroup**: `{entity.megagroup}`"
    msg += f"\n**Restricted**: `{entity.restricted}`"
    msg += f"\n**Scam**: `{entity.scam}`"
    msg += f"\n**Slowmode**: `{entity.slowmode_enabled}`"
    if entity.username:
        msg += f"\n**Username**: {entity.username}"
    msg += "\n\n**Member Stats:**"
    msg += f"\n`Admins:` `{len(totallist)}`"
    msg += f"\n`Users`: `{totallist.total}`"
    msg += "\n\n**Admins List:**"
    for x in totallist:
        msg += f"\n• [{x.id}](tg://user?id={x.id})"
    msg += f"\n\n**Description**:\n`{ch_full.full_chat.about}`"
    await event.reply(msg)


def gifid(update: Update, context: CallbackContext):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.animation:
        update.effective_message.reply_text(
            f"Gif ID:\n<code>{msg.reply_to_message.animation.file_id}</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        update.effective_message.reply_text("Please reply to a gif to get its ID.")


def info(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    chat = update.effective_chat
    buttons = [
        [
            InlineKeyboardButton(
                text="Health", url="https://t.me/Programmer_Updates/10"
            ),
            InlineKeyboardButton(
                text="Disasters", url="https://t.me/Programmer_Updates/11"
            ),
        ],
    ]
    user_id = extract_user(update.effective_message, args)

    if user_id:
        user = bot.get_chat(user_id)

    elif not message.reply_to_message and not args:
        user = message.from_user

    elif not message.reply_to_message and (
        not args
        or (
            len(args) >= 1
            and not args[0].startswith("@")
            and not args[0].isdigit()
            and not message.parse_entities([MessageEntity.TEXT_MENTION])
        )
    ):
        message.reply_text("I can't extract a user from this.")
        return

    else:
        return

    rep = message.reply_text("<code>Appraising...</code>", parse_mode=ParseMode.HTML)

    text = (
        f"╒═══「<b>• Appraisal results •</b> 」\n"
        f"• ID: <code>{user.id}</code>\n"
        f"• First Name: {html.escape(user.first_name)}"
    )

    if user.last_name:
        text += f"\n• Last Name: {html.escape(user.last_name)}"

    if user.username:
        text += f"\n• Username: @{html.escape(user.username)}"

    text += f"\n• Userlink: {mention_html(user.id, 'link')}"

    if chat.type != "private" and user_id != bot.id:
        _stext = "\n• Presence: <code>{}</code>"

        afk_st = is_afk(user.id)
        if afk_st:
            text += _stext.format("AFK")
        else:
            status = status = bot.get_chat_member(chat.id, user.id).status
            if status:
                if status in {"left", "kicked"}:
                    text += _stext.format("Not here")
                elif status == "member":
                    text += _stext.format("Detected")
                elif status in {"administrator", "creator"}:
                    text += _stext.format("Admin")
    if user_id not in [bot.id, 777000, 1087968824]:
        userhp = hpmanager(user)
        text += f"\n\n<b>Health:</b> <code>{userhp['earnedhp']}/{userhp['totalhp']}</code>\n[<i>{make_bar(int(userhp['percentage']))} </i>{userhp['percentage']}%]"

    try:
        spamwtc = sw.get_ban(int(user.id))
        if spamwtc:
            text += "\n\n<b>This person is Spamwatched!</b>"
            text += f"\nReason: <pre>{spamwtc.reason}</pre>"
            text += "\nAppeal at @SpamWatchSupport"
    except:
        pass  # don't crash if api is down somehow...

    if user.id == OWNER_ID:
        text += "\n\nThe Disaster level of this person is 'God'."
    elif user.id in DEV_USERS:
        text += "\n\nThis user is member of 'Heros Association'."
    elif user.id in DRAGONS:
        text += "\n\nThe Disaster level of this person is 'Dragon'."
    elif user.id in DEMONS:
        text += "\n\nThe Disaster level of this person is 'Demon'."
    elif user.id in TIGERS:
        text += "\n\nThe Disaster level of this person is 'Tiger'."
    elif user.id in WOLVES:
        text += "\n\nThe Disaster level of this person is 'Wolf'."
    elif user.id == 5561111332:
        text += "\n\nSenorita Is Girlfriend Of @Its_IZ_PRINCE_xD."

    try:
        user_member = chat.get_member(user.id)
        if user_member.status == "administrator":
            result = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={chat.id}&user_id={user.id}",
            )
            result = result.json()["result"]
            if "custom_title" in result.keys():
                custom_title = result["custom_title"]
                text += f"\n\nTitle:\n<b>{custom_title}</b>"
    except BadRequest:
        pass

    for mod in USER_INFO:
        try:
            mod_info = mod.__user_info__(user.id)
        except TypeError:
            mod_info = mod.__user_info__(user.id, chat.id)
        if mod_info:
            text += "\n\n" + mod_info

    if INFOPIC:
        try:
            profile = context.bot.get_user_profile_photos(user.id).photos[0][-1]
            context.bot.sendChatAction(chat.id, "upload_photo")
            context.bot.send_photo(
                chat.id,
                photo=profile,
                caption=(text),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.HTML,
            )
        # Incase user don't have profile pic, send normal text
        except IndexError:
            message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.HTML,
            )

    else:
        message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML,
        )

    rep.delete()


def about_me(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    user_id = extract_user(message, args)

    user = bot.get_chat(user_id) if user_id else message.from_user
    info = sql.get_user_me_info(user.id)

    if info:
        update.effective_message.reply_text(
            f"*{user.first_name}*:\n{escape_markdown(info)}",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    elif message.reply_to_message:
        username = message.reply_to_message.from_user.first_name
        update.effective_message.reply_text(
            f"{username} hasn't set an info message about themselves yet!",
        )
    else:
        update.effective_message.reply_text("There isnt one, use /setme to set one.")


def set_about_me(update: Update, context: CallbackContext):
    message = update.effective_message
    user_id = message.from_user.id
    if user_id in [777000, 1087968824]:
        message.reply_text("Error! Unauthorized")
        return
    bot = context.bot
    if message.reply_to_message:
        repl_message = message.reply_to_message
        repl_user_id = repl_message.from_user.id
        if repl_user_id in [bot.id, 777000, 1087968824] and (user_id in DEV_USERS):
            user_id = repl_user_id
    text = message.text
    info = text.split(None, 1)
    if len(info) == 2:
        if len(info[1]) < MAX_MESSAGE_LENGTH // 4:
            sql.set_user_me_info(user_id, info[1])
            if user_id in [777000, 1087968824]:
                message.reply_text("Authorized...Information updated!")
            elif user_id == bot.id:
                message.reply_text("I have updated my info with the one you provided!")
            else:
                message.reply_text("Information updated!")
        else:
            message.reply_text(
                "The info needs to be under {} characters! You have {}.".format(
                    MAX_MESSAGE_LENGTH // 4,
                    len(info[1]),
                ),
            )


@sudo_plus
def stats(update, context):
    uptime = datetime.datetime.fromtimestamp(boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    botuptime = get_readable_time((time.time() - StartTime))
    status = "*╒═══「 System statistics 」*\n\n"
    status += "*➢ System Start time:* " + str(uptime) + "\n"
    uname = platform.uname()
    status += "*➢ System:* " + str(uname.system) + "\n"
    status += "*➢ Node name:* " + escape_markdown(str(uname.node)) + "\n"
    status += "*➢ Release:* " + escape_markdown(str(uname.release)) + "\n"
    status += "*➢ Machine:* " + escape_markdown(str(uname.machine)) + "\n"
    mem = virtual_memory()
    cpu = cpu_percent()
    disk = disk_usage("/")
    status += "*➢ CPU:* " + str(cpu) + " %\n"
    status += "*➢ RAM:* " + str(mem[2]) + " %\n"
    status += "*➢ Storage:* " + str(disk[3]) + " %\n\n"
    status += "*➢ Python Version:* " + python_version() + "\n"
    status += "*➢ python-Telegram-Bot:* " + str(ptbver) + "\n"
    status += "*➢ Uptime:* " + str(botuptime) + "\n"
    try:
        update.effective_message.reply_photo(
            NEKO_IMG,
            status
            + "\n*Bot statistics*:\n"
            + "\n".join([mod.__stats__() for mod in STATS])
            + f"\n\n[✦ Support](https://t.me/{SUPPORT_CHAT}) | [✦ Updates](https://t.me/Programmer_Updates)\n\n"
            + "\n╘══「 by [Programmer • Network](https://t.me/Programmer_Network) 」\n",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Repo", url="github.com/Awesome-Prince/NekoRobot-3"
                        )
                    ]
                ]
            ),
        )
    except BaseException:
        update.effective_message.reply_text(
            (
                (
                    (
                        "\n*Bot statistics*:\n"
                        + "\n".join(mod.__stats__() for mod in STATS)
                    )
                    + f"\n\n✦ [Support](https://t.me/{SUPPORT_CHAT}) | ✦ [Updates](https://t.me/Programmer_Updates)\n\n"
                )
                + "╘══「 by [Programmer • Network](https://t.me/Programmer_Network) 」\n"
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Repo", url="github.com/Awesome-Prince/NekoRobot-3"
                        )
                    ]
                ]
            ),
        )


def about_bio(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    user_id = extract_user(message, args)
    user = bot.get_chat(user_id) if user_id else message.from_user
    info = sql.get_user_bio(user.id)

    if info:
        update.effective_message.reply_text(
            "*{}*:\n{}".format(user.first_name, escape_markdown(info)),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    elif message.reply_to_message:
        username = user.first_name
        update.effective_message.reply_text(
            f"{username} hasn't had a message set about themselves yet!\nSet one using /setbio",
        )
    else:
        update.effective_message.reply_text(
            "You haven't had a bio set about yourself yet!",
        )


def set_about_bio(update: Update, context: CallbackContext):
    message = update.effective_message
    sender_id = update.effective_user.id
    bot = context.bot

    if message.reply_to_message:
        repl_message = message.reply_to_message
        user_id = repl_message.from_user.id

        if user_id == message.from_user.id:
            message.reply_text(
                "Ha, you can't set your own bio! You're at the mercy of others here...",
            )
            return

        if user_id in [777000, 1087968824] and sender_id not in DEV_USERS:
            message.reply_text("You are not authorised")
            return

        if user_id == bot.id and sender_id not in DEV_USERS:
            message.reply_text(
                "Erm... yeah, I only trust the Ackermans to set my bio.",
            )
            return

        text = message.text
        bio = text.split(
            None,
            1,
        )  # use python's maxsplit to only remove the cmd, hence keeping newlines.

        if len(bio) == 2:
            if len(bio[1]) < MAX_MESSAGE_LENGTH // 4:
                sql.set_user_bio(user_id, bio[1])
                message.reply_text(
                    "Updated {}'s bio!".format(repl_message.from_user.first_name),
                )
            else:
                message.reply_text(
                    "Bio needs to be under {} characters! You tried to set {}.".format(
                        MAX_MESSAGE_LENGTH // 4,
                        len(bio[1]),
                    ),
                )
    else:
        message.reply_text("Reply to someone to set their bio!")


def __user_info__(user_id):
    bio = html.escape(sql.get_user_bio(user_id) or "")
    me = html.escape(sql.get_user_me_info(user_id) or "")
    result = ""
    if me:
        result += f"<b>About user:</b>\n{me}\n"
    if bio:
        result += f"<b>What others say:</b>\n{bio}\n"
    result = result.strip("\n")
    return result


__help__ = """
*ID:*
 • `/id`*:* get the current group id. If used by replying to a message, gets that user's id.
 • `/gifid`*:* reply to a gif to me to tell you its file ID.
 
*Self addded information:* 
 • `/setme <text>`*:* will set your info
 • `/me`*:* will get your or another user's info.
Examples:
 `/setme I am a wolf.`
 `/me @username(defaults to yours if no user specified)`
 
*Information others add on you:* 
 • `/bio`*:* will get your or another user's bio. This cannot be set by yourself.
• `/setbio <text>`*:* while replying, will save another user's bio 
Examples:
 `/bio @username(defaults to yours if not specified).`
 `/setbio This user is a wolf` (reply to the user)
 
*Overall Information about you:*
 • `/info`*:* get information about a user. 
 
*◢ Intellivoid SpamProtection:*
 • `/spwinfo`*:* SpamProtection Info
 
*json Detailed info:*
 • `/json`*:* Get Detailed info about any message.
 
*Covid info:*
 • `/covid`*:* Get Detailed info about Covid.
 
*ARQ Statistics:*
 /arq : ARQ API Stats.
 
*AFk:*
When marked as AFK, any mentions will be replied to with a message stating that you're not available!
 • `/afk <reason>`*:* Mark yourself as AFK.
  - brb <reason>: Same as the afk command, but not a command.\n 
  
"""

SET_BIO_HANDLER = DisableAbleCommandHandler("setbio", set_about_bio, run_async=True)
GET_BIO_HANDLER = DisableAbleCommandHandler("bio", about_bio, run_async=True)

STATS_HANDLER = CommandHandler(["stats", "statistics"], stats, run_async=True)
ID_HANDLER = DisableAbleCommandHandler("id", get_id, run_async=True)
GIFID_HANDLER = DisableAbleCommandHandler("gifid", gifid, run_async=True)
INFO_HANDLER = DisableAbleCommandHandler("info", info, run_async=True)

SET_ABOUT_HANDLER = DisableAbleCommandHandler("setme", set_about_me, run_async=True)
GET_ABOUT_HANDLER = DisableAbleCommandHandler("me", about_me, run_async=True)

NEKO_PTB.add_handler(STATS_HANDLER)
NEKO_PTB.add_handler(ID_HANDLER)
NEKO_PTB.add_handler(GIFID_HANDLER)
NEKO_PTB.add_handler(INFO_HANDLER)
NEKO_PTB.add_handler(SET_BIO_HANDLER)
NEKO_PTB.add_handler(GET_BIO_HANDLER)
NEKO_PTB.add_handler(SET_ABOUT_HANDLER)
NEKO_PTB.add_handler(GET_ABOUT_HANDLER)

__mod_name__ = "Info & AFK"
__command_list__ = ["setbio", "bio", "setme", "me", "info"]
__handlers__ = [
    ID_HANDLER,
    GIFID_HANDLER,
    INFO_HANDLER,
    SET_BIO_HANDLER,
    GET_BIO_HANDLER,
    SET_ABOUT_HANDLER,
    GET_ABOUT_HANDLER,
    STATS_HANDLER,
]
