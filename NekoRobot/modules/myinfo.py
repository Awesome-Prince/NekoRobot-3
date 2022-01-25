from telethon import events, Button, custom, version
from telethon.tl.types import ChannelParticipantsAdmins
import asyncio
import os,re
import requests
import datetime
import time
from datetime import datetime
import random
from PIL import Image
from io import BytesIO
from KURUMIBOT import telethn as bot
from KURUMIBOT import telethn as tgbot
from KURUMIBOT.events import register
from KURUMIBOT import dispatcher


edit_time = 5
""" =======================CONSTANTS====================== """
file1 = "https://telegra.ph/file/0eaa3fff64d8c82347b3e.jpg"
file2 = "https://telegra.ph/file/3cab40c48f095f3307da4.jpg"
file3 = "https://telegra.ph/file/7319947cede4fef8ba841.jpg"
file4 = "https://telegra.ph/file/665cd1fe141d78d19c072.jpg"
file5 = "https://telegra.ph/file/d96a1255cfa3bf9daf2d1.jpg"
""" =======================CONSTANTS====================== """

@register(pattern="/myinfo")
async def proboyx(event):
    chat = await event.get_chat()
    current_time = datetime.utcnow()
    betsy = event.sender.first_name
    button = [[custom.Button.inline("Click Here",data="information")]]
    on = await bot.send_file(event.chat_id, file=file2,caption= f"♡ Hey {betsy}, I'm Miku\n♡ I'm Created By [卄σ∂αкα](tg://user?id=2099092782)\n♡ Click The Button Below To Get Your Info", buttons=button)

    await asyncio.sleep(edit_time)
    ok = await bot.edit_message(event.chat_id, on, file=file3, buttons=button) 

    await asyncio.sleep(edit_time)
    ok2 = await bot.edit_message(event.chat_id, ok, file=file5, buttons=button)

    await asyncio.sleep(edit_time)
    ok3 = await bot.edit_message(event.chat_id, ok2, file=file1, buttons=button)

    await asyncio.sleep(edit_time)
    ok7 = await bot.edit_message(event.chat_id, ok6, file=file4, buttons=button)
    
    await asyncio.sleep(edit_time)
    ok4 = await bot.edit_message(event.chat_id, ok3, file=file2, buttons=button)
    
    await asyncio.sleep(edit_time)
    ok5 = await bot.edit_message(event.chat_id, ok4, file=file1, buttons=button)
    
    await asyncio.sleep(edit_time)
    ok6 = await bot.edit_message(event.chat_id, ok5, file=file3, buttons=button)
    
    await asyncio.sleep(edit_time)
    ok7 = await bot.edit_message(event.chat_id, ok6, file=file5, buttons=button)

    await asyncio.sleep(edit_time)
    ok7 = await bot.edit_message(event.chat_id, ok6, file=file4, buttons=button)

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"information")))
async def callback_query_handler(event):
  try:
    boy = event.sender_id
    PRO = await bot.get_entity(boy)
    LILIE = "YOUR DETAILS BY MIKU \n\n"
    LILIE += f"FIRST NAME : {PRO.first_name} \n"
    LILIE += f"LAST NAME : {PRO.last_name}\n"
    LILIE += f"YOU BOT : {PRO.bot} \n"
    LILIE += f"RESTRICTED : {PRO.restricted} \n"
    LILIE += f"USER ID : {boy}\n"
    LILIE += f"USERNAME : {PRO.username}\n"
    await event.answer(LILIE, alert=True)
  except Exception as e:
    await event.reply(f"{e}")

__help__ = """
/myinfo: shows your info in inline button
"""

__mod_name__ = "myinfoℹ️"
__command_list__ = [
    "myinfo"
]
