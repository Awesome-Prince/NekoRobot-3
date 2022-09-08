"""
BSD 2-Clause License
Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022-2023, Awesome-Prince, [ https://github.com/Awesome-Prince]
Copyright (c) 2022-2023,Programmer Network, [ https://github.com/Awesome-Prince/NekoRobot-3 ]
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

from NekoRobot.modules.disable import DisableAbleCommandHandler, DisableAbleMessageHandler
from NekoRobot import LOGGER, NEKO_PTB as app

from typing import Optional, List

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, InlineQueryHandler, MessageHandler, filters
from telegram.ext.filters import BaseFilter


class Neko_TG_Handler:
    def __init__(self, app):
        self.app: Application = app

    def command(
        self,
        command: str,
        filters: Optional[BaseFilter] = None,
        admin_ok: bool = False,
        pass_chat_data: bool = False,
        run_async: bool = True,
        can_disable: bool = True,
        group: Optional[int] = 40,
    ):
        def _command(func):
            try:
                if can_disable:
                    self.app.add_handler(
                        DisableAbleCommandHandler(
                            command,
                            func,
                            filters=filters,
                            admin_ok=admin_ok,
                        ),
                        group,
                    )
                else:
                    self.app.add_handler(
                        CommandHandler(
                            command,
                            func,
                            filters=filters,
                        ),
                        group,
                    )
                LOGGER.debug(
                    f"[NEKO CMD] Loaded handler {command} for function {func.__name__} in group {group}"
                )
            except TypeError:
                if can_disable:
                    self.app.add_handler(
                        DisableAbleCommandHandler(
                            command,
                            func,
                            filters=filters,
                            admin_ok=admin_ok,
                            pass_chat_data=pass_chat_data,
                        )
                    )
                else:
                    self.app.add_handler(
                        CommandHandler(
                            command,
                            func,
                            filters=filters,
                            pass_chat_data=pass_chat_data,
                        )
                    )
                LOGGER.debug(
                    f"[NEKO CMD] Loaded handler {command} for function {func.__name__}"
                )

            return func

        return _command

    def message(
        self,
        pattern: Optional[BaseFilter] = None,
        can_disable: bool = True,
        block: bool = True,
        group: Optional[int] = 60,
        friendly=None,
    ):
        def _message(func):
            try:
                if can_disable:
                    self.app.add_handler(
                        DisableAbleMessageHandler(pattern, func, friendly=friendly),
                        group,
                    )
                else:
                    self.app.add_handler(MessageHandler(pattern, func), group)
                LOGGER.debug(
                    f"[NEKO MSG] Loaded filter pattern {pattern} for function {func.__name__} in group {group}"
                )
            except TypeError:
                if can_disable:
                    self.app.add_handler(
                        DisableAbleMessageHandler(pattern, func, friendly=friendly)
                    )
                else:
                    self.app.add_handler(MessageHandler(pattern, func))
                LOGGER.debug(
                    f"[NEKO MSG] Loaded filter pattern {pattern} for function {func.__name__}"
                )

            return func

        return _message

    def callbackquery(self, pattern: str = None):
        def _callbackquery(func):
            self.app.add_handler(CallbackQueryHandler(pattern=pattern, callback=func))
            LOGGER.debug(
                f"[NEKO CALLBACK] Loaded callbackquery handler with pattern {pattern} for function {func.__name__}"
            )
            return func

        return _callbackquery

    def inlinequery(
        self,
        pattern: Optional[str] = None,
#        run_async: bool = True,
        pass_user_data: bool = True,
        pass_chat_data: bool = True,
        chat_types: List[str] = None,
    ):
        def _inlinequery(func):
            self.app.add_handler(
                InlineQueryHandler(
                    pattern=pattern,
                    callback=func,
                    # pass_user_data=pass_user_data,
                    # pass_chat_data=pass_chat_data,
                    chat_types=chat_types,
                )
            )
            LOGGER.debug(
                f"[NEKO INLINE] Loaded inlinequery handler with pattern {pattern} for function {func.__name__} | PASSES "
                f"USER DATA: {pass_user_data} | PASSES CHAT DATA: {pass_chat_data} | CHAT TYPES: {chat_types}"
            )
            return func

        return _inlinequery


neko_cmd = Neko_TG_Handler(app).command
neko_msg = Neko_TG_Handler(app).message
neko_callback = Neko_TG_Handler(app).callbackquery
neko_inline = Neko_TG_Handler(app).inlinequery
