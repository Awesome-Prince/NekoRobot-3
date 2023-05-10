"""
MIT License

Copyright (c) 2022 Aʙɪsʜɴᴏɪ

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
# ""DEAR PRO PEOPLE,  DON'T REMOVE & CHANGE THIS LINE
# TG :- @Abishnoi1M
#     MY ALL BOTS :- Abishnoi_bots
#     GITHUB :- KingAbishnoi ""

import asyncio

from pyrogram import filters

from NekoRobot import pgram as app
from NekoRobot.modules.mongo.karma_mongo import (
    alpha_to_int,
    get_karma,
    get_karmas,
    int_to_alpha,
    update_karma,
)
from NekoRobot.utils.errors import capture_err
from NekoRobot.utils.sections import section

regex_upvote = r"^((?i)\+|\+\+|\+1|thx|tnx|ty|thank you|thanx|thanks|pro|cool|good|👍|nice|noice|piro)$"
regex_downvote = r"^(\-|\-\-|\-1|👎|chutiya|noobda|noob|Noob|gross|fuck off)$"

karma_positive_group = 3
karma_negative_group = 4


from pymongo import MongoClient

from NekoRobot import MONGO_DB_URI

worddb = MongoClient(MONGO_DB_URI)
k = worddb["MikuKarma"]["karma_status"]


async def is_admins(chat_id: int):
    return [
        member.user.id
        async for member in app.iter_chat_members(chat_id, filter="administrators")
    ]


@app.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_upvote)
    & ~filters.via_bot
    & ~filters.bot,
    group=karma_positive_group,
)
async def upvote(_, message):
    chat_id = message.chat.id
    is_karma = k.find_one({"chat_id": chat_id})
    if not is_karma:
        if not message.reply_to_message.from_user:
            return
        if not message.from_user:
            return
        if message.reply_to_message.from_user.id == message.from_user.id:
            return
        user_id = message.reply_to_message.from_user.id
        user_mention = message.reply_to_message.from_user.mention
        current_karma = await get_karma(chat_id, await int_to_alpha(user_id))
        if current_karma:
            current_karma = current_karma["karma"]
            karma = current_karma + 1
        else:
            karma = 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
        await message.reply_text(
            f"Incremented Karma of {user_mention} By 1 \nTotal Points: {karma}"
        )


@app.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_downvote)
    & ~filters.via_bot
    & ~filters.bot,
    group=karma_negative_group,
)
async def downvote(_, message):
    chat_id = message.chat.id
    is_karma = k.find_one({"chat_id": chat_id})
    if is_karma:
        if not message.reply_to_message.from_user:
            return
        if not message.from_user:
            return
        if message.reply_to_message.from_user.id == message.from_user.id:
            return
        user_id = message.reply_to_message.from_user.id
        user_mention = message.reply_to_message.from_user.mention
        current_karma = await get_karma(chat_id, await int_to_alpha(user_id))
        if current_karma:
            current_karma = current_karma["karma"]
            karma = current_karma - 1
        else:
            karma = 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
        await message.reply_text(
            f"Decremented Karma Of {user_mention} By 1 \nTotal Points: {karma}"
        )

async def get_user_id_and_usernames(client) -> dict:
    with client.storage.lock, client.storage.conn:
        users = client.storage.conn.execute(
            'SELECT * FROM peers WHERE type in ("user", "bot") AND username NOT null'
        ).fetchall()
    users_ = {}
    for user in users:
        users_[user[0]] = user[3]
    return users_


@app.on_message(filters.command("karma") & filters.group)
@capture_err
async def command_karma(_, message):
    chat_id = message.chat.id
    if not message.reply_to_message:
        m = await message.reply_text("Analyzing Karma...")
        karma = await get_karmas(chat_id)
        if not karma:
            return await m.edit("No karma in DB for this chat.")
        msg = f"Karma list of {message.chat.title}"
        limit = 0
        karma_dicc = {}
        for i in karma:
            user_id = await alpha_to_int(i)
            user_karma = karma[i]["karma"]
            karma_dicc[str(user_id)] = user_karma
            karma_arranged = dict(
                sorted(
                    karma_dicc.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )
            )
        if not karma_dicc:
            return await m.edit("No karma in DB for this chat.")
        userdb = await get_user_id_and_usernames(app)
        karma = {}
        for user_idd, karma_count in karma_arranged.items():
            if limit > 15:
                break
            if int(user_idd) not in list(userdb.keys()):
                continue
            username = userdb[int(user_idd)]
            karma["➣ @" + username] = ["<b>" + str(karma_count) + "</b>"]
            limit += 1
        await m.edit(section(msg, karma))
    else:
        if not message.reply_to_message.from_user:
            return await message.reply("User has no karma.")

        user_id = message.reply_to_message.from_user.id
        karma = await get_karma(chat_id, await int_to_alpha(user_id))
        if karma:
            karma = karma["karma"]
            await message.reply_text(f"<b>Total Points</b>: __{karma}__")
        else:
            karma = 0
            await message.reply_text(f"<b>Total Points</b>: __{karma}__")


__mod_name__ = "Karma"
__help__ = """

*Upvote* - Use upvote keywords like "+", "+1", "thanks", etc. to upvote a message.
*Downvote* - Use downvote keywords like "-", "-1", etc. to downvote a message.
*Commands*
•/karma:- reply to a user to check that user's karma points.
•/karma:- send without replying to any message to check karma point list of top 10.
"""
