"""
BSD 2-Clause License
Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022-2023, Awesome-Prince, [ https://github.com/Awesome-Prince]
Copyright (c) 2022-2023, BlackLover Network, [ https://github.com/Awesome-Prince/NekoRobot-3 ]
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

from NekoRobot import telethn as tbot
from NekoRobot.events import register

TMP_DOWNLOAD_DIRECTORY = "./"


import os
from datetime import datetime

from PIL import Image
from telegraph import Telegraph, exceptions, upload_file

emilia = "EMILIA"

telegraph = Telegraph()

r = telegraph.create_account(short_name=emilia)

auth_url = r["auth_url"]


@register(pattern="^/tg(m|xt) ?(.*)")
async def _(event):

    if event.fwd_from:

        return

    optional_title = event.pattern_match.group(2)

    if event.reply_to_msg_id:

        start = datetime.now()

        r_message = await event.get_reply_message()

        input_str = event.pattern_match.group(1)

        if input_str == "m":

            downloaded_file_name = await tbot.download_media(
                r_message, TMP_DOWNLOAD_DIRECTORY
            )

            end = datetime.now()

            ms = (end - start).seconds

            h = await event.reply(
                "Downloaded to {} in {} seconds.".format(downloaded_file_name, ms)
            )

            if downloaded_file_name.endswith((".webp")):

                resize_image(downloaded_file_name)

            try:

                start = datetime.now()

                media_urls = upload_file(downloaded_file_name)

            except exceptions.TelegraphException as exc:

                await h.edit("ERROR: " + str(exc))

                os.remove(downloaded_file_name)

            else:

                end = datetime.now()

                (end - start).seconds

                os.remove(downloaded_file_name)

                await h.edit(
                    "Uploaded to https://te.legra.ph{}".format(media_urls[0]),
                    link_preview=True,
                )

        elif input_str == "xt":

            user_object = await tbot.get_entity(r_message.sender_id)

            title_of_page = user_object.first_name  # + " " + user_object.last_name

            # apparently, all Users do not have last_name field

            if optional_title:

                title_of_page = optional_title

            page_content = r_message.message

            if r_message.media:

                if page_content != "":

                    title_of_page = page_content

                downloaded_file_name = await tbot.download_media(
                    r_message, TMP_DOWNLOAD_DIRECTORY
                )

                m_list = None

                with open(downloaded_file_name, "rb") as fd:

                    m_list = fd.readlines()

                for m in m_list:

                    page_content += m.decode("UTF-8") + "\n"

                os.remove(downloaded_file_name)

            page_content = page_content.replace("\n", "<br>")

            response = telegraph.create_page(title_of_page, html_content=page_content)

            end = datetime.now()

            ms = (end - start).seconds

            await event.reply(
                "Pasted to https://telegra.ph/{} in {} seconds.".format(
                    response["path"], ms
                ),
                link_preview=True,
            )

    else:

        await event.reply("Reply to a message to get a permanent telegra.ph link.")


def resize_image(image):

    im = Image.open(image)

    im.save(image, "PNG")


__mod_name__ = "telegraph"
