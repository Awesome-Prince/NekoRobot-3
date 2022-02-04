from .. events import register

@register(pattern="^(?i)neko")
async def start(event):
    await event.send_message(event.chat_id, "Hello I'm Neko"
