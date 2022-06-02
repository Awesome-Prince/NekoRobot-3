from pyrogram.types import CallbackQuery
from NekoRobot pbot as bot
from pyrogram import filters

#nandhabaka


@bot.on_callback_query(filters.regex("close"))
async def close(_, query: CallbackQuery):
           query = query.message
           await query.delete()
         
