from pyrogram import filters
from NekoRobot import pbot , musicbot
import pytgcalls


calls = pytgcalls.GroupCallFactory(musicbot).get_group_call()


@pbot.on_message(filters.command('play'))
async def play(_,message):
  reply = message.reply_to_message
  if reply:
    fk = await message.reply('Downloading....')
    path = await reply.download()
    await calls.join(message.chat.id)
    await calls.start_audio(path)
    await fk.edit('playing...')

    
@pbot.on_message(filters.command('vplay'))
async def vplay(_,message):
  reply = message.reply_to_message
  if reply:
    path = reply.download()
    await calls.join(message.chat.id)
    await calls.start_video(path)
    await fk.edit('playing...')

    
@pbot.on_message(filters.command('leavevc'))
def leavevc(_,message):
  await group_call.stop()
  await group_call.leave_current_group_call()
