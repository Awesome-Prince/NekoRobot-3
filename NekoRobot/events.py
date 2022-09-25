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

from telethon import events

from NekoRobot import tbot


def register(**args):
    """Registers a new message."""
    pattern = args.get("pattern")

    r_pattern = r"^[/!]"

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = f"(?i){pattern}"

    args["pattern"] = pattern.replace("^/", r_pattern, 1)

    def decorator(func):
        tbot.add_event_handler(func, events.NewMessage(**args))
        return func

    return decorator


def chataction(**args):
    """Registers chat actions."""

    def decorator(func):
        tbot.add_event_handler(func, events.ChatAction(**args))
        return func

    return decorator


def userupdate(**args):
    """Registers user updates."""

    def decorator(func):
        tbot.add_event_handler(func, events.UserUpdate(**args))
        return func

    return decorator


def inlinequery(**args):
    """Registers inline query."""
    pattern = args.get("pattern")

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = f"(?i){pattern}"

    def decorator(func):
        tbot.add_event_handler(func, events.InlineQuery(**args))
        return func

    return decorator


def callbackquery(**args):
    """Registers inline query."""

    def decorator(func):
        tbot.add_event_handler(func, events.CallbackQuery(**args))
        return func

    return decorator
