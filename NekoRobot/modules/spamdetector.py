from NekoRobot import telethn as tbot
import time
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from pymongo import MongoClient
from NekoRobot import MONGO_DB_URI, OWNER_ID
from telethon import events

global spamcounter
spamcounter = 0 

@tbot.on(events.NewMessage(pattern=None))
async def leechers(event):
    if str(event.sender_id) in str(OWNER_ID):
        return
    global spamcounter
    starttimer = time.time()
    spamcounter += 1
    sender = event.sender_id
    senderr = await event.get_sender()
    check = sender
    USERSPAM = []

    if len(USERSPAM) >= 1:
        if event.sender_id == USERSPAM[0]:
            pass
        else:
            spamcounter = 0
            USERSPAM = []
            USERSPAM.append(check)
    else:
        USERSPAM = []
        USERSPAM.append(check)

    print (spamcounter)
    if spamcounter > 4:
        spamtimecheck = time.time() - starttimer

    if (
        spamcounter > 4
        and event.sender_id == USERSPAM[0]
        and (time.strftime("%S", time.gmtime(spamtimecheck))) <= "03"
    ):
        spamcounter = 0  
        if senderr.username is None:
            st = senderr.first_name
            hh = senderr.id
            final = f"[{st}](tg://user?id={hh}) you are detected as a spammer according to my algorithms.\nYou will be restricted from using any bot commands for 24 hours !"
        else:
            st = senderr.username
            final = f"@{st} you are detected as a spammer according to my algorithms.\nYou will be restricted from using any bot commands for 24 hours !"
            pass
    else:
        return

    dev = await event.respond(final)

    client = MongoClient(MONGO_DB_URI)
    db = client["EmiliaAnimeBot"]
    leechers = db.leecher

    users = leechers.find({})
    for c in users:
        if USERSPAM[0] == c["id"]:
            print("spammers never die")
            return
    timerr = time.time()
    leechers.insert_one({"id": USERSPAM[0], "time": timerr})
    
    try:
        MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
        await tbot(EditBannedRequest(event.chat_id, event.sender_id, MUTE_RIGHTS))
        await dev.edit(final + "\nYou are now muted !")
    except Exception:
        pass
