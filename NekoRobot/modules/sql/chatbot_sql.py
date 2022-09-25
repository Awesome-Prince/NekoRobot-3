"""
BSD 2-Clause License
Copyright (C) 2017-2019, Paul Larsen
Copyright (C) 2022-2023, Awesome-Prince, [ https://github.com/Awesome-Prince]
Copyright (c) 2022-2023, Programmer Network, [ https://github.com/Awesome-Prince/NekoRobot-3 ]
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import threading

from sqlalchemy import Column, String

from NekoRobot.modules.sql import BASE, SESSION


class KukiChats(BASE):
    __tablename__ = "kuki_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


KukiChats.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_kuki(chat_id):
    try:
        chat = SESSION.query(KukiChats).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()


def set_kuki(chat_id):
    with INSERTION_LOCK:
        kukichat = SESSION.query(KukiChats).get(str(chat_id))
        if not kukichat:
            kukichat = KukiChats(str(chat_id))
        SESSION.add(kukichat)
        SESSION.commit()


def rem_kuki(chat_id):
    with INSERTION_LOCK:
        kukichat = SESSION.query(KukiChats).get(str(chat_id))
        if kukichat:
            SESSION.delete(kukichat)
        SESSION.commit()


def get_all_kuki_chats():
    try:
        return SESSION.query(KukiChats.chat_id).all()
    finally:
        SESSION.close()
