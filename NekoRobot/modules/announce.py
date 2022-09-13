import html

from telegram import Update
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_html

import NekoRobot.modules.sql.logger_sql as sql
from NekoRobot.modules.helper_funcs.anonymous import AdminPerms
from NekoRobot.modules.helper_funcs.anonymous import user_admin as u_admin
from NekoRobot.modules.helper_funcs.decorators import nekocmd
from NekoRobot.modules.log_channel import loggable


@nekocmd(command="announce", pass_args=True)
@u_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
def announcestat(update: Update, context: CallbackContext) -> str:
    args = context.args
    if len(args) > 0:
        update.effective_user
        message = update.effective_message
        chat = update.effective_chat
        user = update.effective_user
        if args[0].lower() in ["on", "yes", "true"]:
            sql.enable_chat_log(update.effective_chat.id)
            update.effective_message.reply_text(
                "I've enabled announcemets in this group. Now any admin actions in your group will be announced."
            )
            logmsg = f"<b>{html.escape(chat.title)}:</b>\n#ANNOUNCE_TOGGLED\nAdmin actions announcement has been <b>enabled</b>\n<b>Admin:</b> {message.sender_chat.title if message.sender_chat else mention_html(user.id, user.first_name)}\n "

            return logmsg
        elif args[0].lower() in ["off", "no", "false"]:
            sql.disable_chat_log(update.effective_chat.id)
            update.effective_message.reply_text(
                "I've disabled announcemets in this group. Now admin actions in your group will not be announced."
            )
            logmsg = f"<b>{html.escape(chat.title)}:</b>\n#ANNOUNCE_TOGGLED\nAdmin actions announcement has been <b>disabled</b>\n<b>Admin:</b> {message.sender_chat.title if message.sender_chat else mention_html(user.id, user.first_name)}\n "

            return logmsg
    else:
        update.effective_message.reply_text(
            f"Give me some arguments to choose a setting! on/off, yes/no!\n\nYour current setting is: {sql.does_chat_log(update.effective_chat.id)}\nWhen True, any admin actions in your group will be announced.When False, admin actions in your group will not be announced."
        )

        return ""


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)
