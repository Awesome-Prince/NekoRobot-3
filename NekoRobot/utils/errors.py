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

import sys
import traceback
from functools import wraps

from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden

from NekoRobot import pgram as app

LOG_GROUP_ID = int(-1001644963220)


def split_limits(text):

    if len(text) < 2048:

        return [text]

    lines = text.splitlines(True)

    small_msg = ""

    result = []

    for line in lines:

        if len(small_msg) + len(line) < 2048:

            small_msg += line

        else:

            result.append(small_msg)

            small_msg = line

    else:

        result.append(small_msg)

    return result


def capture_err(func):
    @wraps(func)
    async def capture(client, message, *args, **kwargs):

        try:

            return await func(client, message, *args, **kwargs)

        except ChatWriteForbidden:

            await app.leave_chat(message.chat.id)

            return

        except Exception as err:

            exc_type, exc_obj, exc_tb = sys.exc_info()

            errors = traceback.format_exception(
                etype=exc_type,
                value=exc_obj,
                tb=exc_tb,
            )

            error_feedback = split_limits(
                "**ERROR** | `{}` | `{}`\n\n```{}```\n\n```{}```\n".format(
                    0 if not message.from_user else message.from_user.id,
                    0 if not message.chat else message.chat.id,
                    message.text or message.caption,
                    "".join(errors),
                ),
            )

            for x in error_feedback:

                await app.send_message(LOG_GROUP_ID, x)

            raise err

    return capture
