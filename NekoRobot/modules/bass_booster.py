"""
MIT License

Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022 Hodacka
Copyright (c) 2022, Yūki • Black Knights Union, <https://github.com/Hodacka/NekoRobot-3>

This file is part of @NekoXRobot (Telegram Bot)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is

furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import io
import math
import os
import numpy as np

from pydub import AudioSegment
from telethon import events

from NekoRobot.utils.pluginhelpers import is_admin
from NekoRobot import telethn, BOT_ID, OWNER_ID, SUPPORT_CHAT

TMP_DOWNLOAD_DIRECTORY = "./"

@telethn.on(events.NewMessage(pattern="/bassboost (.*)"))
async def __(event):
    if not event.is_group:

        return
    if not await is_admin(event, BOT_ID):

        return
    if await event.message.sender_id != OWNER_ID:
        return

    v = False
    accentuate_db = 40
    reply = await event.get_reply_message()
    if not reply:
        await event.reply("Can You Reply To A MSG :?")
        return
    if event.pattern_match.group(1):
        ar = event.pattern_match.group(1)
        try:
            int(ar)
            if int(ar) >= 2 and int(ar) <= 100:
                accentuate_db = int(ar)
            else:
                await event.reply("`BassBost Level Should Be From 2 to 100 Only.`")
                return
        except Exception as exx:
            await event.reply("`SomeThing Went Wrong..` \n**Error:** " + str(exx))
            return
    else:
        accentuate_db = 2
    lel = await event.reply("`Downloading This File...`")
    # fname = await telethn.download_media(message=reply.media)
    r_message = message = reply.media
    fname = await telethn.download_media(r_message, TMP_DOWNLOAD_DIRECTORY)
    await lel.edit("`BassBoosting In Progress..`")
    if fname.endswith(".oga") or fname.endswith(".ogg"):
        v = True
        audio = AudioSegment.from_file(fname)
    elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
        audio = AudioSegment.from_file(fname)
    else:
        await lel.edit(
            "`This Format is Not Supported Yet` \n**Currently Supported :** `mp3, m4a and wav.`"
        )
        os.remove(fname)
        return
    sample_track = list(audio.get_array_of_samples())
    await asyncio.sleep(0.3)
    est_mean = np.mean(sample_track)
    await asyncio.sleep(0.3)
    est_std = 3 * np.std(sample_track) / (math.sqrt(2))
    await asyncio.sleep(0.3)
    bass_factor = int(round((est_std - est_mean) * 0.005))
    await asyncio.sleep(5)
    attenuate_db = 0
    filtered = audio.low_pass_filter(bass_factor)
    await asyncio.sleep(5)
    out = (audio - attenuate_db).overlay(filtered + accentuate_db)
    await asyncio.sleep(6)
    m = io.BytesIO()
    if v:
        m.name = "voice.ogg"
        out.split_to_mono()
        await lel.edit("`Now Exporting...`")
        await asyncio.sleep(0.3)
        out.export(m, format="ogg", bitrate="64k", codec="libopus")
        await lel.edit("`Process Completed. Uploading Now Here..`")
        await telethn.send_file(
            event.chat_id,
            m,
            voice_note=True,
            caption=f"Bass Boosted, \nDone By @{SUPPORT_CHAT}",
        )

    else:
        m.name = "BassBoosted.mp3"
        await lel.edit("`Now Exporting...`")
        await asyncio.sleep(0.3)
        out.export(m, format="mp3")
        await lel.edit("`Process Completed. Uploading Now Here..`")
        await telethn.send_file(
            event.chat_id,
            m,
            caption=f"Bass Boosted, \nDone By @{SUPPORT_CHAT}",
        )

    os.remove(m)
    await event.delete()

    os.remove(fname)
