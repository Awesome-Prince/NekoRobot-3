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

import collections
import importlib

from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler

from NekoRobot import NEKO_PTB, tbot
from NekoRobot.__main__ import (
    CHAT_SETTINGS,
    DATA_EXPORT,
    DATA_IMPORT,
    HELPABLE,
    IMPORTED,
    MIGRATEABLE,
    STATS,
    USER_INFO,
    USER_SETTINGS,
)
from NekoRobot.modules.helper_funcs.chat_status import dev_plus, sudo_plus


@dev_plus
def load(update: Update, context: CallbackContext):
    message = update.effective_message
    text = message.text.split(" ", 1)[1]
    load_messasge = message.reply_text(
        f"Attempting to load module : <b>{text}</b>", parse_mode=ParseMode.HTML
    )

    try:
        imported_module = importlib.import_module(f"SungJinwooRobot.modules.{text}")
    except:
        load_messasge.edit_text("Does that module even exist?")
        return

    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        load_messasge.edit_text("Module already loaded.")
        return
    if "__handlers__" in dir(imported_module):
        handlers = imported_module.__handlers__
        for handler in handlers:
            if not isinstance(handler, tuple):
                NEKO_PTB.add_handler(handler)
            elif isinstance(handler[0], collections.Callable):
                callback, telethon_event = handler
                tbot.add_event_handler(callback, telethon_event)
            else:
                handler_name, priority = handler
                NEKO_PTB.add_handler(handler_name, priority)
    else:
        IMPORTED.pop(imported_module.__mod_name__.lower())
        load_messasge.edit_text("The module cannot be loaded.")
        return

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    load_messasge.edit_text(
        f"Successfully loaded module : <b>{text}</b>",
        parse_mode=ParseMode.HTML,
    )


@dev_plus
def unload(update: Update, context: CallbackContext):
    message = update.effective_message
    text = message.text.split(" ", 1)[1]
    unload_messasge = message.reply_text(
        f"Attempting to unload module : <b>{text}</b>", parse_mode=ParseMode.HTML
    )

    try:
        imported_module = importlib.import_module(f"SungJinwooRobot.modules.{text}")
    except:
        unload_messasge.edit_text("Does that module even exist?")
        return

    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__
    if imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED.pop(imported_module.__mod_name__.lower())
    else:
        unload_messasge.edit_text("Can't unload something that isn't loaded.")
        return
    if "__handlers__" in dir(imported_module):
        handlers = imported_module.__handlers__
        for handler in handlers:
            if isinstance(handler, bool):
                unload_messasge.edit_text("This module can't be unloaded!")
                return
            elif not isinstance(handler, tuple):
                NEKO_PTB.remove_handler(handler)
            elif isinstance(handler[0], collections.Callable):
                callback, telethon_event = handler
                tbot.remove_event_handler(callback, telethon_event)
            else:
                handler_name, priority = handler
                NEKO_PTB.remove_handler(handler_name, priority)
    else:
        unload_messasge.edit_text("The module cannot be unloaded.")
        return

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE.pop(imported_module.__mod_name__.lower())

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.remove(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.remove(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.remove(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.remove(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.remove(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS.pop(imported_module.__mod_name__.lower())

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS.pop(imported_module.__mod_name__.lower())

    unload_messasge.edit_text(
        f"Successfully unloaded module : <b>{text}</b>", parse_mode=ParseMode.HTML
    )


@sudo_plus
def listmodules(update: Update, context: CallbackContext):
    message = update.effective_message
    module_list = []

    for helpable_module in HELPABLE:
        helpable_module_info = IMPORTED[helpable_module]
        file_info = IMPORTED[helpable_module_info.__mod_name__.lower()]
        file_name = file_info.__name__.rsplit("NekoRobot.modules.", 1)[1]
        mod_name = file_info.__mod_name__
        module_list.append(f"- <code>{mod_name} ({file_name})</code>\n")
    module_list = "Following modules are loaded : \n\n" + "".join(module_list)
    message.reply_text(module_list, parse_mode=ParseMode.HTML)


LOAD_HANDLER = CommandHandler("load", load, run_async=True)
UNLOAD_HANDLER = CommandHandler("unload", unload, run_async=True)
LISTMODULES_HANDLER = CommandHandler("listmodules", listmodules, run_async=True)

NEKO_PTB.add_handler(LOAD_HANDLER)
NEKO_PTB.add_handler(UNLOAD_HANDLER)
NEKO_PTB.add_handler(LISTMODULES_HANDLER)

__mod_name__ = "Modules"
