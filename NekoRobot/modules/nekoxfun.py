"""
MIT License
Copyright (C) 2022 Awesome-Prince
Copyright (c) 2022,Programmer  •  Network, <https://github.com/Awesome-Prince/NekoRobot-3>
This file is part of @NekoXRobot (Telegram Bot)
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the Software), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import nekos
from telegram import Chat
from telegram.ext import CommandHandler

from NekoRobot import NEKO_PTB


async def is_user_in_chat(chat: Chat, user_id: int) -> bool:
    member = chat.get_member(user_id)
    return member.status not in ("left", "kicked")


async def neko(update, context):
    msg = update.effective_message
    target = "neko"
    msg.reply_photo(nekos.img(target))


#
# async def feet(update, context):
#    msg = update.effective_message
#    target = "feet"
#    msg.reply_photo(nekos.img(target))


#
# async def yuri(update, context):
#    msg = update.effective_message
#    target = "yuri"
#    msg.reply_photo(nekos.img(target))


#
# async def trap(update, context):
#    msg = update.effective_message
#    target = "trap"
#    msg.reply_photo(nekos.img(target))


#
# async def futanari(update, context):
#    msg = update.effective_message
#    target = "futanari"
#    msg.reply_photo(nekos.img(target))


#
# async def hololewd(update, context):
#    msg = update.effective_message
#    target = "hololewd"
#    msg.reply_photo(nekos.img(target))


#
# async def lewdkemo(update, context):
#    msg = update.effective_message
#    target = "lewdkemo"
#    msg.reply_photo(nekos.img(target))


#
# async def sologif(update, context):
#    msg = update.effective_message
#    target = "solog"
#    msg.reply_video(nekos.img(target))


#
# async def feetgif(update, context):
#    msg = update.effective_message
#    target = "feetg"
#    msg.reply_video(nekos.img(target))


#
# async def cumgif(update, context):
#    msg = update.effective_message
#    target = "cum"
#    msg.reply_video(nekos.img(target))


#
# async def erokemo(update, context):
#    msg = update.effective_message
#    target = "erokemo"
#    msg.reply_photo(nekos.img(target))


async def lesbian(update, context):
    msg = update.effective_message
    target = "les"
    msg.reply_video(nekos.img(target))


#
# async def wallpaper(update, context):
#    msg = update.effective_message
#    target = "wallpaper"
#    msg.reply_photo(nekos.img(target))


#
# async def lewdk(update, context):
#   msg = update.effective_message
#    target = "lewdk"
#    msg.reply_photo(nekos.img(target))


#
# async def ngif(update, context):
#    msg = update.effective_message
#    target = "ngif"
#    msg.reply_video(nekos.img(target))


async def tickle(update, context):
    msg = update.effective_message
    target = "tickle"
    msg.reply_video(nekos.img(target))


#
# async def lewd(update, context):
#    msg = update.effective_message
#    target = "lewd"
#    msg.reply_photo(nekos.img(target))


async def feed(update, context):
    msg = update.effective_message
    target = "feed"
    msg.reply_video(nekos.img(target))


#
# async def eroyuri(update, context):
#    msg = update.effective_message
#    target = "eroyuri"
#    msg.reply_photo(nekos.img(target))


#
# async def eron(update, context):
#    msg = update.effective_message
#    target = "eron"
#    msg.reply_photo(nekos.img(target))


#
# async def cum(update, context):
#    msg = update.effective_message
#    target = "cum_jpg"
#    msg.reply_photo(nekos.img(target))


#
# async def bjgif(update, context):
#    msg = update.effective_message
#    target = "bj"
#    msg.reply_video(nekos.img(target))


#
# async def bj(update, context):
#    msg = update.effective_message
#    target = "blowjob"
#    msg.reply_photo(nekos.img(target))


#
# async def nekonsfw(update, context):
#    msg = update.effective_message
#    target = "nsfw_neko_gif"
#    msg.reply_video(nekos.img(target))


#
# async def solo(update, context):
#   msg = update.effective_message
#    target = "solo"
#    msg.reply_photo(nekos.img(target))


#
# async def kemonomimi(update, context):
#    msg = update.effective_message
#    target = "kemonomimi"
#    msg.reply_photo(nekos.img(target))


#
# async def avatarlewd(update, context):
#    msg = update.effective_message
#    target = "nsfw_avatar"
#    with open("temp.png", "wb") as f:
#        f.write(requests.get(nekos.img(target)).content)
#    img = Image.open("temp.png")
#    img.save("temp.webp", "webp")
#    msg.reply_document(open("temp.webp", "rb"))
#    os.remove("temp.webp")


#
# async def gasm(update, context):
#    msg = update.effective_message
#    target = "gasm"
#   with open("temp.png", "wb") as f:
#        f.write(requests.get(nekos.img(target)).content)
#    img = Image.open("temp.png")
#    img.save("temp.webp", "webp")
#    msg.reply_document(open("temp.webp", "rb"))
#    os.remove("temp.webp")


async def poke(update, context):
    msg = update.effective_message
    target = "poke"
    msg.reply_video(nekos.img(target))


#
# async def anal(update, context):
#    msg = update.effective_message
#    target = "anal"
#    msg.reply_video(nekos.img(target))


#
# async def hentai(update, context):
#    msg = update.effective_message
#    target = "hentai"
#    msg.reply_photo(nekos.img(target))


#
# async def avatar(update, context):
#    msg = update.effective_message
#    target = "nsfw_avatar"
#    with open("temp.png", "wb") as f:
#        f.write(requests.get(nekos.img(target)).content)
#    img = Image.open("temp.png")
#    img.save("temp.webp", "webp")
#    msg.reply_document(open("temp.webp", "rb"))
#    os.remove("temp.webp")


#
# async def erofeet(update, context):
#    msg = update.effective_message
#    target = "erofeet"
#    msg.reply_photo(nekos.img(target))


#
# async def holo(update, context):
#    msg = update.effective_message
#    target = "holo"
#    msg.reply_photo(nekos.img(target))


# async def keta(update, context):
#     msg = update.effective_message
#     target = 'keta'
#     if not target:
#         msg.reply_text("No URL was received from the API!")
#         return
#     msg.reply_photo(nekos.img(target))


#
# async def pussygif(update, context):
#    msg = update.effective_message
#    target = "pussy"
#    msg.reply_video(nekos.img(target))


#
# async def tits(update, context):
#    msg = update.effective_message
#    target = "tits"
#    msg.reply_photo(nekos.img(target))


#
# async def holoero(update, context):
#    msg = update.effective_message
#    target = "holoero"
#    msg.reply_photo(nekos.img(target))


#
# async def pussy(update, context):
#    msg = update.effective_message
#    target = "pussy_jpg"
#    msg.reply_photo(nekos.img(target))


#
# async def hentaigif(update, context):
#    msg = update.effective_message
#    target = "random_hentai_gif"
#    msg.reply_video(nekos.img(target))


#
# async def classic(update, context):
#    msg = update.effective_message
#    target = "classic"
#    msg.reply_video(nekos.img(target))


#
# async def kuni(update, context):
#    msg = update.effective_message
#    target = "kuni"
#    msg.reply_video(nekos.img(target))


async def kiss(update, context):
    msg = update.effective_message
    target = "kiss"
    msg.reply_video(nekos.img(target))


#
# async def femdom(update, context):
#    msg = update.effective_message
#    target = "femdom"
#    msg.reply_photo(nekos.img(target))


async def hug(update, context):
    msg = update.effective_message
    target = "cuddle"
    msg.reply_video(nekos.img(target))


#
# async def erok(update, context):
#    msg = update.effective_message
#    target = "erok"
#    msg.reply_photo(nekos.img(target))


async def foxgirl(update, context):
    msg = update.effective_message
    target = "fox_girl"
    msg.reply_photo(nekos.img(target))


#
# async def titsgif(update, context):
#    msg = update.effective_message
#    target = "boobs"
#    msg.reply_video(nekos.img(target))


#
# async def ero(update, context):
#    msg = update.effective_message
#    target = "ero"
#    msg.reply_photo(nekos.img(target))


async def smug(update, context):
    msg = update.effective_message
    target = "smug"
    msg.reply_video(nekos.img(target))


async def baka(update, context):
    msg = update.effective_message
    target = "baka"
    msg.reply_video(nekos.img(target))


#
# async def dva(update, context):
#    msg = update.effective_message
#    nsfw = requests.get("https://api.computerfreaker.cf/v1/dva").json()
#    url = nsfw.get("url")
# do shit with url if you want to
#    if not url:
#        msg.reply_text("No URL was received from the API!")
#        return
#    msg.reply_photo(url)


# LEWDKEMO_HANDLER = CommandHandler("lewdkemo", lewdkemo)
NEKO_HANDLER = CommandHandler("neko", neko, block=False)
# FEET_HANDLER = CommandHandler("feet", feet)
# YURI_HANDLER = CommandHandler("yuri", yuri)
# TRAP_HANDLER = CommandHandler("trap", trap)
# FUTANARI_HANDLER = CommandHandler("futanari", futanari)
# HOLOLEWD_HANDLER = CommandHandler("hololewd", hololewd)
# SOLOGIF_HANDLER = CommandHandler("sologif", sologif)
# CUMGIF_HANDLER = CommandHandler("cumgif", cumgif)
# EROKEMO_HANDLER = CommandHandler("erokemo", erokemo)
LESBIAN_HANDLER = CommandHandler("lesbian", lesbian, block=False)
# WALLPAPER_HANDLER = CommandHandler("wallpaper", wallpaper)
# LEWDK_HANDLER = CommandHandler("lewdk", lewdk)
# NGIF_HANDLER = CommandHandler("ngif", ngif)
TICKLE_HANDLER = CommandHandler("tickle", tickle, block=False)
# LEWD_HANDLER = CommandHandler("lewd", lewd)
FEED_HANDLER = CommandHandler("feed", feed, block=False)
# EROYURI_HANDLER = CommandHandler("eroyuri", eroyuri)
# ERON_HANDLER = CommandHandler("eron", eron)
# CUM_HANDLER = CommandHandler("cum", cum)
# BJGIF_HANDLER = CommandHandler("bjgif", bjgif)
# BJ_HANDLER = CommandHandler("bj", bj)
# NEKONSFW_HANDLER = CommandHandler("nekonsfw", nekonsfw)
# SOLO_HANDLER = CommandHandler("solo", solo)
# KEMONOMIMI_HANDLER = CommandHandler("kemonomimi", kemonomimi)
# AVATARLEWD_HANDLER = CommandHandler("avatarlewd", avatarlewd)
# GASM_HANDLER = CommandHandler("gasm", gasm)
POKE_HANDLER = CommandHandler("poke", poke, block=False)
# ANAL_HANDLER = CommandHandler("anal", anal)
# HENTAI_HANDLER = CommandHandler("hentai", hentai)
# AVATAR_HANDLER = CommandHandler("avatar", avatar)
# EROFEET_HANDLER = CommandHandler("erofeet", erofeet)
# HOLO_HANDLER = CommandHandler("holo", holo)
# TITS_HANDLER = CommandHandler("tits", tits)
# PUSSYGIF_HANDLER = CommandHandler("pussygif", pussygif)
# HOLOERO_HANDLER = CommandHandler("holoero", holoero)
# PUSSY_HANDLER = CommandHandler("pussy", pussy)
# HENTAIGIF_HANDLER = CommandHandler("hentaigif", hentaigif)
# CLASSIC_HANDLER = CommandHandler("classic", classic)
# KUNI_HANDLER = CommandHandler("kuni", kuni)

# LEWD_HANDLER = CommandHandler("lewd", lewd)
KISS_HANDLER = CommandHandler("kiss", kiss, block=False)
# FEMDOM_HANDLER = CommandHandler("femdom", femdom)
CUDDLE_HANDLER = CommandHandler("hug", hug, block=False)
# EROK_HANDLER = CommandHandler("erok", erok, block=False)
FOXGIRL_HANDLER = CommandHandler("foxgirl", foxgirl, block=False)
# TITSGIF_HANDLER = CommandHandler("titsgif", titsgif)
# ERO_HANDLER = CommandHandler("ero", ero)
SMUG_HANDLER = CommandHandler("smug", smug, block=False)
BAKA_HANDLER = CommandHandler("baka", baka, block=False)
# DVA_HANDLER = CommandHandler("dva", dva)

# NEKO_PTB.add_handler(LEWDKEMO_HANDLER)
NEKO_PTB.add_handler(NEKO_HANDLER)
# NEKO_PTB.add_handler(FEET_HANDLER)
# NEKO_PTB.add_handler(YURI_HANDLER)
# NEKO_PTB.add_handler(TRAP_HANDLER)
# NEKO_PTB.add_handler(FUTANARI_HANDLER)
# NEKO_PTB.add_handler(HOLOLEWD_HANDLER)
# NEKO_PTB.add_handler(SOLOGIF_HANDLER)
# NEKO_PTB.add_handler(CUMGIF_HANDLER)
# NEKO_PTB.add_handler(EROKEMO_HANDLER)
NEKO_PTB.add_handler(LESBIAN_HANDLER)
# NEKO_PTB.add_handler(WALLPAPER_HANDLER)
# NEKO_PTB.add_handler(LEWDK_HANDLER)
# NEKO_PTB.add_handler(NGIF_HANDLER)
NEKO_PTB.add_handler(TICKLE_HANDLER)
# NEKO_PTB.add_handler(LEWD_HANDLER)
NEKO_PTB.add_handler(FEED_HANDLER)
# NEKO_PTB.add_handler(EROYURI_HANDLER)
# NEKO_PTB.add_handler(ERON_HANDLER)
# NEKO_PTB.add_handler(CUM_HANDLER)
# NEKO_PTB.add_handler(BJGIF_HANDLER)
# NEKO_PTB.add_handler(BJ_HANDLER)
# NEKO_PTB.add_handler(NEKONSFW_HANDLER)
# NEKO_PTB.add_handler(SOLO_HANDLER)
# NEKO_PTB.add_handler(KEMONOMIMI_HANDLER)
# NEKO_PTB.add_handler(AVATARLEWD_HANDLER)
# NEKO_PTB.add_handler(GASM_HANDLER)
NEKO_PTB.add_handler(POKE_HANDLER)
# NEKO_PTB.add_handler(ANAL_HANDLER)
# NEKO_PTB.add_handler(HENTAI_HANDLER)
# NEKO_PTB.add_handler(AVATAR_HANDLER)
# NEKO_PTB.add_handler(EROFEET_HANDLER)
# NEKO_PTB.add_handler(HOLO_HANDLER)
# NEKO_PTB.add_handler(TITS_HANDLER)
# NEKO_PTB.add_handler(PUSSYGIF_HANDLER)
# NEKO_PTB.add_handler(HOLOERO_HANDLER)
# NEKO_PTB.add_handler(PUSSY_HANDLER)
# NEKO_PTB.add_handler(HENTAIGIF_HANDLER)
# NEKO_PTB.add_handler(CLASSIC_HANDLER)
# NEKO_PTB.add_handler(KUNI_HANDLER)

# NEKO_PTB.add_handler(LEWD_HANDLER)
NEKO_PTB.add_handler(KISS_HANDLER)
# NEKO_PTB.add_handler(FEMDOM_HANDLER)
NEKO_PTB.add_handler(CUDDLE_HANDLER)
# NEKO_PTB.add_handler(EROK_HANDLER)
NEKO_PTB.add_handler(FOXGIRL_HANDLER)
# NEKO_PTB.add_handler(TITSGIF_HANDLER)
# NEKO_PTB.add_handler(ERO_HANDLER)
NEKO_PTB.add_handler(SMUG_HANDLER)
NEKO_PTB.add_handler(BAKA_HANDLER)
# NEKO_PTB.add_handler(DVA_HANDLER)

__handlers__ = [
    # NEKO_HANDLER,
    # FEET_HANDLER,
    # YURI_HANDLER,
    # TRAP_HANDLER,
    # FUTANARI_HANDLER,
    # HOLOLEWD_HANDLER,
    # SOLOGIF_HANDLER,
    # CUMGIF_HANDLER,
    # EROKEMO_HANDLER,
    LESBIAN_HANDLER,
    # WALLPAPER_HANDLER,
    # LEWDK_HANDLER,
    # NGIF_HANDLER,
    TICKLE_HANDLER,
    # LEWD_HANDLER,
    FEED_HANDLER,
    # EROYURI_HANDLER,
    # ERON_HANDLER,
    # CUM_HANDLER,
    # BJGIF_HANDLER,
    # BJ_HANDLER,
    # NEKONSFW_HANDLER,
    # SOLO_HANDLER,
    # KEMONOMIMI_HANDLER,
    # AVATARLEWD_HANDLER,
    # GASM_HANDLER,
    POKE_HANDLER,
    # ANAL_HANDLER,
    # HENTAI_HANDLER,
    # AVATAR_HANDLER,
    # EROFEET_HANDLER,
    # HOLO_HANDLER,
    # TITS_HANDLER,
    # PUSSYGIF_HANDLER,
    # HOLOERO_HANDLER,
    # PUSSY_HANDLER,
    # HENTAIGIF_HANDLER,
    # CLASSIC_HANDLER,
    # KUNI_HANDLER,
    # LEWD_HANDLER,
    KISS_HANDLER,
    # FEMDOM_HANDLER,
    # LEWDKEMO_HANDLER,
    CUDDLE_HANDLER,
    # EROK_HANDLER,
    FOXGIRL_HANDLER,
    # TITSGIF_HANDLER,
    # ERO_HANDLER,
    SMUG_HANDLER,
    BAKA_HANDLER,
    # DVA_HANDLER,
]
