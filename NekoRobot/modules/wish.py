import random
from PIL import Image
from KURUMIBOT import telethn as miku
from telethon import events
@miku.on(events.NewMessage(pattern="/wish ?(.*)"))
async def wish(e):

 if e.is_reply:
         mm = random.randint(1,100)
         lol = await e.get_reply_message()
         fire = "https://telegra.ph/file/82decd7a6cd88bd964f92.jpg"
         await miku.send_file(e.chat_id, fire,caption=f"**Hey [{e.sender.first_name}](tg://user?id={e.sender.id}), Your wish has been cast.✨**\n\n__chance of success {mm}%__", reply_to=lol)
 if not e.is_reply:
         mm = random.randint(1,100)
         fire = "https://telegra.ph/file/82decd7a6cd88bd964f92.jpg"
         await miku.send_file(e.chat_id, fire,caption=f"**Hey [{e.sender.first_name}](tg://user?id={e.sender.id}), Your wish has been cast.✨**\n\n__chance of success {mm}%__", reply_to=e)
