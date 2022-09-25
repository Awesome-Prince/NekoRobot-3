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
import json
import os
from typing import Optional

from telegram import ParseMode, TelegramError, Update
from telegram.ext import CallbackContext, CommandHandler
from telegram.utils.helpers import mention_html

from NekoRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    NEKO_PTB,
    OWNER_ID,
    SUPPORT_CHAT,
    TIGERS,
    WOLVES,
)
from NekoRobot.modules.helper_funcs.chat_status import (
    dev_plus,
    sudo_plus,
    whitelist_plus,
)
from NekoRobot.modules.helper_funcs.extraction import extract_user
from NekoRobot.modules.log_channel import gloggable

ELEVATED_USERS_FILE = os.path.join(os.getcwd(), "NekoRobot/elevated_users.json")


def check_user_id(user_id: int, context: CallbackContext) -> Optional[str]:
    bot = context.bot
    if not user_id:
        return "That...is a chat! baka ka omae?"

    elif user_id == bot.id:
        return "This does not work that way."

    else:
        return None


# This can serve as a deeplink example.
# disasters =
# """ Text here """

# do not async, not a handler
# def send_disasters(update):
#    update.effective_message.reply_text(
#        disasters, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

### Deep link example ends


@dev_plus
@gloggable
def addsudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        message.reply_text("This member is already a A Rank Hunter")
        return ""

    if user_id in DEMONS:
        rt += "Requested HA to promote a B Rank Hunter to A Rank Hunter."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "Requested HA to promote a D Rank Hunter to A Rank Hunter."
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    data["sudos"].append(user_id)
    DRAGONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        (
            rt
            + f"\nSuccessfully set Power Level {user_member.first_name} to A Rank Hunter!"
        )
    )

    log_message = (
        f"#SUDO\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n{log_message}"

    return log_message


@sudo_plus
@gloggable
def addsupport(
    update: Update,
    context: CallbackContext,
) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "Requested HA to demote this A Rank Hunter to B Rank Hunter"
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        message.reply_text("This user is already a B Rank Hunter.")
        return ""

    if user_id in WOLVES:
        rt += "Requested HA to promote this D Rank Hunter to B Rank Hunter"
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    data["supports"].append(user_id)
    DEMONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        f"{rt}\n{user_member.first_name} was added as a B Rank Hunter!"
    )

    log_message = (
        f"#SUPPORT\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n{log_message}"

    return log_message


@sudo_plus
@gloggable
def addwhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "This member is a A Rank Hunter, Demoting to D Rank Hunter."
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "This user is already a B Rank Hunter, Demoting to D Rank Hunter."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        message.reply_text("This user is already a D Rank Hunter.")
        return ""

    data["whitelists"].append(user_id)
    WOLVES.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        f"{rt}\nSuccessfully promoted {user_member.first_name} to a D Rank Hunter!"
    )

    log_message = (
        f"#WHITELIST\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))} \n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n{log_message}"

    return log_message


@sudo_plus
@gloggable
def addtiger(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "This member is a A Rank Hunter, Demoting to C Rank Hunter."
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "This user is already a B Rank Hunter, Demoting to C Rank Hunter."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "This user is already a D Rank Hunter, Demoting to C Rank Hunter."
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    if user_id in TIGERS:
        message.reply_text("This user is already a C Rank Hunter.")
        return ""

    data["tigers"].append(user_id)
    TIGERS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        f"{rt}\nSuccessfully promoted {user_member.first_name} to a C Rank Hunter!"
    )

    log_message = (
        f"#TIGER\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))} \n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n{log_message}"

    return log_message


@dev_plus
@gloggable
def removesudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        message.reply_text("Requested HA to demote this user to Civilian")
        DRAGONS.remove(user_id)
        data["sudos"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNSUDO\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message

    else:
        message.reply_text("This user is not a A Rank Hunter!")
        return ""


@sudo_plus
@gloggable
def removesupport(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DEMONS:
        message.reply_text("Requested HA to demote this user to Civilian")
        DEMONS.remove(user_id)
        data["supports"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNSUPPORT\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n{log_message}"

        return log_message

    else:
        message.reply_text("This user is not a B Rank Hunter!")
        return ""


@sudo_plus
@gloggable
def removewhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in WOLVES:
        message.reply_text("Demoting to normal user")
        WOLVES.remove(user_id)
        data["whitelists"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNWHITELIST\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n{log_message}"

        return log_message
    else:
        message.reply_text("This user is not a D Rank Hunter!")
        return ""


@sudo_plus
@gloggable
def removetiger(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in TIGERS:
        message.reply_text("Demoting to normal user")
        TIGERS.remove(user_id)
        data["tigers"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNTIGER\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n{log_message}"

        return log_message
    else:
        message.reply_text("This user is not a Tiger Disaster!")
        return ""


@whitelist_plus
def whitelistlist(update: Update, context: CallbackContext):
    reply = "<b>Known D Rank Hunters 🐺:</b>\n"
    bot = context.bot
    for each_user in WOLVES:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)

            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def tigerlist(update: Update, context: CallbackContext):
    reply = "<b>Known C Rank Hunters 🐯:</b>\n"
    bot = context.bot
    for each_user in TIGERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def supportlist(update: Update, context: CallbackContext):
    bot = context.bot
    reply = "<b>Known B Rank Hunters 👹:</b>\n"
    for each_user in DEMONS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def sudolist(update: Update, context: CallbackContext):
    bot = context.bot
    true_sudo = list(set(DRAGONS) - set(DEV_USERS))
    reply = "<b>Known A Rank Hunters 🐉:</b>\n"
    for each_user in true_sudo:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def devlist(update: Update, context: CallbackContext):
    bot = context.bot
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply = "<b>S Rank Hunters ⚡️:</b>\n"
    for each_user in true_dev:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


__help__ = f"""
*⚠️ Notice:*
Commands listed here only work for users with special access are mainly used for troubleshooting, debugging purposes.
Group admins/group owners do not need these commands. 

 ╔ *List all special users:*
 •`/aranks`*:* Lists all A Rank Hunters
 •`/branks`*:* Lists all B Rank Hunters
 •`/cranks`*:* Lists all C Rank Hunters
 •`/dranks`*:* Lists all D Rank Hunters
 •`/sranks`*:* Lists all S Rank Hunters
 •`/addarank`*:* Adds a user to A Rank Hunter
 •`/addbrank`*:* Adds a user to B Rank Hunter
 •`/addcrank`*:* Adds a user to C Rank Hunter
 •`/adddrank`*:* Adds a user to D Rank Hunter
 ╚ `Add dev doesnt exist, devs should know how to add themselves`

 ╔ *Ping:*
 •`/ping`*:* gets ping time of bot to telegram server
 ╚ `/pingall`*:* gets all listed ping times

 ╔ *Broadcast: (Bot owner only)*
 • *Note:* This supports basic markdown
 •`/broadcastall`*:* Broadcasts everywhere
 •`/broadcastusers`*:* Broadcasts too all users
 ╚ `/broadcastgroups`*:* Broadcasts too all groups

 ╔ *Groups Info:*
 •`/groups`*:* List the groups with Name, ID, members count as a txt
 •`/leave <ID>`*:* Leave the group, ID must have hyphen
 •`/stats`*:* Shows overall bot stats
 •`/getchats`*:* Gets a list of group names the user has been seen in. Bot owner only
 ╚ `/ginfo username/link/ID`*:* Pulls info panel for entire group

 ╔ *Access control:* 
 •`/ignore`*:* Blacklists a user from 
 • using the bot entirely
 •`/notice`*:* Removes user from blacklist
 ╚ `/ignoredlist`*:* Lists ignored users

 ╔ *Module loading:*
 •`/listmodules`*:* Prints modules and their names
 •`/unload <name>`*:* Unloads module dynamically
 ╚ `/load <name>`*:* Loads module

 ╔ *Speedtest:*
 ╚ `/speedtest`*:* Runs a speedtest and gives you 2 options to choose from, text or image output

 ╔ *Global Bans:*
 •`/gban user reason`*:* Globally bans a user
 ╚ `/ungban user reason`*:* Unbans the user from the global bans list

 ╔ *Module loading:*
 •`/listmodules`*:* Lists names of all modules
 •`/load modulename`*:* Loads the said module to 
 •  memory without restarting.
 •`/unload modulename`*:* Loads the said module from
 ╚   memory without restarting.memory without restarting the bot 

 ╔ *Remote commands:*
 •`/rban user group`*:* Remote ban
 •`/runban user group`*:* Remote un-ban
 •`/rpunch user group`*:* Remote punch
 •`/rmute user group`*:* Remote mute
 ╚ `/runmute user group`*:* Remote un-mute

 ╔ *Windows self hosted only:*
 •`/reboot`*:* Restarts the bots service
 ╚ `/gitpull`*:* Pulls the repo and then restarts the bots service

 ╔ *Chatbot:* 
 ╚ `/listaichats`*:* Lists the chats the chatmode is enabled in
 
 ╔ *Debugging and Shell:* 
 •`/debug <on/off>`*:* Logs commands to updates.txt
 •`/logs`*:* Run this in support group to get logs in pm
 •`/eval`*:* Self explanatory
 •`/sh`*:* Runs shell command
 •`/shell`*:* Runs shell command
 •`/clearlocals`*:* As the name goes
 •`/dbcleanup`*:* Removes deleted accs and groups from db
 ╚ `/py`*:* Runs python code
 
 ╔ *Global Bans:*
 •`/gban <id> <reason>`*:* Gbans the user, works by reply too
 •`/ungban`*:* Ungbans the user, same usage as gban
 ╚ `/gbanlist`*:* Outputs a list of gbanned users

Visit @{SUPPORT_CHAT} for more information.
"""

SUDO_HANDLER = CommandHandler(("addsudo", "addarank"), addsudo, run_async=True)
SUPPORT_HANDLER = CommandHandler(("addsupport", "addbrank"), addsupport, run_async=True)
TIGER_HANDLER = CommandHandler(("addtiger", "addcrank"), addtiger, run_async=True)
WHITELIST_HANDLER = CommandHandler(
    ("addwhitelist", "adddrank"), addwhitelist, run_async=True
)
UNSUDO_HANDLER = CommandHandler(
    ("removesudo", "removearank"), removesudo, run_async=True
)
UNSUPPORT_HANDLER = CommandHandler(
    ("removesupport", "removebrank"), removesupport, run_async=True
)
UNTIGER_HANDLER = CommandHandler(
    ("removetiger", "removecrank"), removetiger, run_async=True
)
UNWHITELIST_HANDLER = CommandHandler(
    ("removewhitelist", "removedrank"), removewhitelist, run_async=True
)

WHITELISTLIST_HANDLER = CommandHandler(
    ["whitelistlist", "dranks"], whitelistlist, run_async=True
)
TIGERLIST_HANDLER = CommandHandler(["tigers", "cranks"], tigerlist, run_async=True)
SUPPORTLIST_HANDLER = CommandHandler(
    ["supportlist", "branks"], supportlist, run_async=True
)
SUDOLIST_HANDLER = CommandHandler(["sudolist", "aranks"], sudolist, run_async=True)
DEVLIST_HANDLER = CommandHandler(["devlist", "sranks"], devlist, run_async=True)

NEKO_PTB.add_handler(SUDO_HANDLER)
NEKO_PTB.add_handler(SUPPORT_HANDLER)
NEKO_PTB.add_handler(TIGER_HANDLER)
NEKO_PTB.add_handler(WHITELIST_HANDLER)
NEKO_PTB.add_handler(UNSUDO_HANDLER)
NEKO_PTB.add_handler(UNSUPPORT_HANDLER)
NEKO_PTB.add_handler(UNTIGER_HANDLER)
NEKO_PTB.add_handler(UNWHITELIST_HANDLER)

NEKO_PTB.add_handler(WHITELISTLIST_HANDLER)
NEKO_PTB.add_handler(TIGERLIST_HANDLER)
NEKO_PTB.add_handler(SUPPORTLIST_HANDLER)
NEKO_PTB.add_handler(SUDOLIST_HANDLER)
NEKO_PTB.add_handler(DEVLIST_HANDLER)

__mod_name__ = "Ranks"
__handlers__ = [
    SUDO_HANDLER,
    SUPPORT_HANDLER,
    TIGER_HANDLER,
    WHITELIST_HANDLER,
    UNSUDO_HANDLER,
    UNSUPPORT_HANDLER,
    UNTIGER_HANDLER,
    UNWHITELIST_HANDLER,
    WHITELISTLIST_HANDLER,
    TIGERLIST_HANDLER,
    SUPPORTLIST_HANDLER,
    SUDOLIST_HANDLER,
    DEVLIST_HANDLER,
]
