import asyncio
import random
import time
import pbot as app
from sys import version as pyver
from typing import Dict, List, Union

import psutil
from pyrogram import filters
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)

__MODULE__ = "FunBot"
__HELP__ = """
neko 
- check neko is online.
"""

@app.on_callback_query(filters.regex("neko"))
async def okaybhai(_, CallbackQuery):
    await CallbackQuery.answer("What's up!")
    out = start_pannel()
    await CallbackQuery.edit_message_text(
        text="Mewo (=^･ｪ･^=)",
        reply_markup=InlineKeyboardMarkup(out[1]),
    )


