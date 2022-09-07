from functools import wraps
from threading import RLock

from telegram import (
    Chat,
    ChatMember,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import CallbackContext as Ctx
from telegram.ext import CallbackQueryHandler as CBHandler

from NekoRobot import NEKO_PTB

from .admin_status_helpers import ADMINS_CACHE as A_CACHE
from .admin_status_helpers import BOT_ADMIN_CACHE as B_CACHE
from .admin_status_helpers import DRAGONS, AdminPerms
from .admin_status_helpers import anon_callbacks as a_cb
from .admin_status_helpers import button_expired_error as bxp
from .admin_status_helpers import edit_anon_msg as eam

anon_callbacks = {}
anon_callback_messages = {}


def bot_is_admin(chat: Chat, bot_id: int, bot_member: ChatMember = None) -> bool:
    if chat.type == "private" or chat.all_members_are_administrators:
        return True

    if not bot_member:
        bot_member = chat.get_member(bot_id)

    return bot_member.status in ("administrator", "creator")


# decorator, can be used as
# @bot_perm_check() with no perm to check for admin-ship only
# or as @bot_perm_check(AdminPerms.value) to check for a specific permission
def bot_admin_check(permission: AdminPerms = None):
    def wrapper(func):
        @wraps(func)
        async def wrapped(update: Update, context: Ctx, *args, **kwargs):
            nonlocal permission
            chat = update.effective_chat
            if chat.type == "private" or chat.all_members_are_administrators:
                return func(update, context, *args, **kwargs)
            bot_id = {BOT_ID}

            try:  # try to get from cache
                bot_member = B_CACHE[chat.id]
            except (
                KeyError,
                IndexError,
            ):  # if not in cache, get from API and save to cache
                bot_member = NEKO_PTB.bot.getChatMember(chat.id, bot_id)
                B_CACHE[chat.id] = bot_member

            if permission:  # if a perm is required, check for it
                if getattr(bot_member, permission.value):
                    func(update, context, *args, **kwargs)
                    return
                return await update.effective_message.reply_text(
                    f"I can't perform this action due to missing permissions;\n"
                    f"Make sure i am an admin and {permission.name.lower().replace('is_', 'am ').replace('_', ' ')}!"
                )

            if (
                bot_member.status == "administrator"
            ):  # if no perm is required, check for admin-ship only
                return func(update, context, *args, **kwargs)
            return await update.effective_message.reply_text(
                "I can't perform this action because I'm not admin!"
            )

        return wrapped

    return wrapper


def user_is_admin(
    update: Update,
    user_id: int,
    channels: bool = False,  # if True, returns True if user is anonymous
    allow_moderators: bool = False,  # if True, returns True if user is a moderator
    perm: AdminPerms = None,  # if not None, returns True if user has the specified permission
) -> bool:
    chat = update.effective_chat
    if chat.type == "private" or user_id in (DRAGONS if allow_moderators else DRAGONS):
        return True

    if channels and (
        update.effective_message.sender_chat is not None
        and update.effective_message.sender_chat.type != "channel"
    ):
        return True  # return true if user is anonymous

    member: ChatMember = get_mem_from_cache(user_id, chat.id)

    if not member:  # not in cache so not an admin
        return False

    if perm:  # check perm if its required
        try:
            the_perm = perm.value
        except AttributeError:
            return bxp(update)
        return getattr(member, the_perm) or member.status == "creator"

    return member.status in ["administrator", "creator"]  # check if user is admin


RLOCK = RLock()


async def get_mem_from_cache(user_id: int, chat_id: int) -> ChatMember:
    with RLOCK:
        try:
            for i in A_CACHE[chat_id]:
                if i.user.id == user_id:
                    return i

        except (KeyError, IndexError):
            admins = await NEKO_PTB.bot.getChatAdministrators(chat_id)
            A_CACHE[chat_id] = admins
            for i in admins:
                if i.user.id == user_id:
                    return i


def user_admin_check(permission: AdminPerms = None):
    def wrapper(func):
        @wraps(func)
        async def awrapper(update: Update, context: Ctx, *args, **kwargs):
            nonlocal permission
            if update.effective_chat.type == "private":
                return func(update, context, *args, **kwargs)
            message = update.effective_message
            if update.effective_message.sender_chat:
                callback_id = (
                    f"anoncb/{message.chat.id}/{message.message_id}/{permission.value}"
                )
                anon_callbacks[(message.chat.id, message.message_id)] = (
                    (update, context),
                    func,
                )
                anon_callback_messages[(message.chat.id, message.message_id)] = (
                    await message.reply_text(
                        "Seems like you're anonymous, click the button below to prove your identity",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="Prove identity", callback_data=callback_id
                                    )
                                ]
                            ]
                        ),
                    )
                ).message_id
            else:
                user_id = message.from_user.id
                chat_id = message.chat.id
                mem = await context.bot.get_chat_member(
                    chat_id=chat_id, user_id=user_id
                )
                if (
                    getattr(mem, permission.value) is True
                    or mem.status == "creator"
                    or user_id in DRAGONS
                ):
                    return func(update, context, *args, **kwargs)
                else:
                    return await message.reply_text(
                        f"You lack the permission: `{permission.name}`",
                        parse_mode=ParseMode.MARKDOWN,
                    )

        return awrapper

    return wrapper


# decorator, can be used as @user_not_admin_check to check user is not admin
def user_not_admin_check(func):
    @wraps(func)
    def wrapped(update: Update, context: Ctx, *args, **kwargs):
        message = update.effective_message
        user = message.sender_chat or update.effective_user
        if (
            message.is_automatic_forward
            or (message.sender_chat and message.sender_chat.type != "channel")
            or not user
        ):
            return
        if not user_is_admin(update, user.id, channels=True):
            return func(update, context, *args, **kwargs)
        return

    return wrapped


def perm_callback_check(upd: Update, _: Ctx):
    callback = upd.callback_query
    chat_id = int(callback.data.split("/")[1])
    message_id = int(callback.data.split("/")[2])
    perm = callback.data.split("/")[3]
    user_id = callback.from_user.id
    msg = upd.effective_message

    mem = user_is_admin(upd, user_id, perm=perm if perm != "None" else None)

    if not mem:  # not admin or doesn't have the required perm
        eam(
            msg,
            "You need to be an admin to perform this action!"
            if perm != "None"
            else f"You lack the permission: `{perm}`!",
        )

        return

    try:
        cb = a_cb.pop((chat_id, message_id), None)
    except (KeyError, IndexError):
        eam(msg, "This message is no longer valid.")
        return

    msg.delete()

    # update the `Update` and `CallbackContext` attributes by the correct values, so they can be used properly
    setattr(cb[0][0], "_effective_user", upd.effective_user)
    setattr(cb[0][0], "_effective_message", cb[2][0])

    return cb[1](cb[0][0], cb[0][1])  # return func(update, context)


NEKO_PTB.add_handler(CBHandler(perm_callback_check, pattern="anonCB"))
