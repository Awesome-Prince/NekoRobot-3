from typing import Union

from future.utils import string_types
from telegram import Chat, ParseMode, Update
from telegram.ext import CommandHandler, MessageHandler
from telegram.utils.helpers import escape_markdown

from NekoRobot import NEKO_PTB
from NekoRobot.modules.connection import connected
from NekoRobot.modules.helper_funcs.alternate import send_message, typing_action
from NekoRobot.modules.helper_funcs.handlers import CMD_STARTERS
from NekoRobot.modules.helper_funcs.misc import is_module_loaded
from NekoRobot.modules.language import gs


async def get_help(chat):
    return gs(chat, "disable_help")


CMD_STARTERS = tuple(CMD_STARTERS)


FILENAME = __name__.rsplit(".", 1)[-1]

# If module is due to be loaded, then setup all the magical handlers
if is_module_loaded(FILENAME):
    from NekoRobot.modules.helper_funcs.chat_status import is_user_admin, user_admin
    from NekoRobot.modules.sql import disable_sql as sql

    DISABLE_CMDS = []
    DISABLE_OTHER = []
    ADMIN_CMDS = []

    class DisableAbleCommandHandler(CommandHandler):
        async def __init__(
            self, command, callback, run_async=True, admin_ok=False, **kwargs
        ):
            super().__init__(command, callback, run_async=run_async, **kwargs)
            self.admin_ok = admin_ok
            if isinstance(command, string_types):
                DISABLE_CMDS.append(command)
                if admin_ok:
                    ADMIN_CMDS.append(command)
            else:
                DISABLE_CMDS.extend(command)
                if admin_ok:
                    ADMIN_CMDS.extend(command)

        async def check_update(self, update):
            if not isinstance(update, Update) or not update.effective_message:
                return
            message = update.effective_message

            if message.text and len(message.text) > 1:
                fst_word = message.text.split(None, 1)[0]
                if len(fst_word) > 1 and any(
                    fst_word.startswith(start) for start in CMD_STARTERS
                ):
                    args = message.text.split()[1:]
                    command = fst_word[1:].split("@")
                    command.append(message.bot.username)

                    if not (
                        command[0].lower() in self.command
                        and command[1].lower() == message.bot.username.lower()
                    ):
                        return None

                    filter_result = self.filters(update)
                    if filter_result:
                        chat = update.effective_chat
                        user = update.effective_user
                        # disabled, admincmd, user admin
                        if sql.is_command_disabled(chat.id, command[0].lower()):
                            # check if command was disabled
                            is_disabled = command[0] in ADMIN_CMDS and is_user_admin(
                                update, user.id
                            )
                            if not is_disabled:
                                return None
                            else:
                                return args, filter_result

                        return args, filter_result
                    else:
                        return False

    class DisableAbleMessageHandler(MessageHandler):
        async def __init__(
            self, pattern, callback, run_async=True, friendly="", **kwargs
        ):
            super().__init__(pattern, callback, run_async=run_async, **kwargs)
            DISABLE_OTHER.append(friendly or pattern)
            self.friendly = friendly or pattern

        async def check_update(self, update):
            if isinstance(update, Update) and update.effective_message:
                chat = update.effective_chat
                return self.filters(update) and not sql.is_command_disabled(
                    chat.id, self.friendly
                )

    @user_admin
    @typing_action
    async def disable(update, context):
        chat = update.effective_chat  # type: Optional[Chat]
        user = update.effective_user
        args = context.args

        conn = connected(context.bot, update, chat, user.id, need_admin=True)
        if conn:
            chat = NEKO_PTB.bot.getChat(conn)
            chat_name = NEKO_PTB.bot.getChat(conn).title
        else:
            if update.effective_message.chat.type == "private":
                send_message(
                    update.effective_message,
                    "This command meant to be used in group not in PM",
                )
                return ""
            chat = update.effective_chat
            chat_name = update.effective_message.chat.title

        if len(args) >= 1:
            disable_cmd = args[0]
            if disable_cmd.startswith(CMD_STARTERS):
                disable_cmd = disable_cmd[1:]

            if disable_cmd in set(DISABLE_CMDS + DISABLE_OTHER):
                sql.disable_command(chat.id, disable_cmd)
                if conn:
                    text = "Disabled the use of `{}` command in *{}*!".format(
                        disable_cmd, chat_name
                    )
                else:
                    text = "Disabled the use of `{}` command!".format(disable_cmd)
                send_message(
                    update.effective_message,
                    text,
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
            else:
                send_message(update.effective_message, "This command can't be disabled")

        else:
            send_message(update.effective_message, "What should I disable?")

    @user_admin
    @typing_action
    async def enable(update, context):
        chat = update.effective_chat  # type: Optional[Chat]
        user = update.effective_user
        args = context.args

        conn = connected(context.bot, update, chat, user.id, need_admin=True)
        if conn:
            chat = NEKO_PTB.bot.getChat(conn)
            chat_name = NEKO_PTB.bot.getChat(conn).title
        else:
            if update.effective_message.chat.type == "private":
                send_message(
                    update.effective_message,
                    "This command is meant to be used in group not in PM",
                )
                return ""
            chat = update.effective_chat
            update.effective_chat.id
            chat_name = update.effective_message.chat.title

        if len(args) >= 1:
            enable_cmd = args[0]
            if enable_cmd.startswith(CMD_STARTERS):
                enable_cmd = enable_cmd[1:]

            if sql.enable_command(chat.id, enable_cmd):
                if conn:
                    text = "Enabled the use of `{}` command in *{}*!".format(
                        enable_cmd, chat_name
                    )
                else:
                    text = "Enabled the use of `{}` command!".format(enable_cmd)
                send_message(
                    update.effective_message,
                    text,
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
            else:
                send_message(update.effective_message, "Is that even disabled?")

        else:
            send_message(update.effective_message, "What should I enable?")

    @user_admin
    @typing_action
    async def list_cmds(update, context):
        if DISABLE_CMDS + DISABLE_OTHER:
            result = "".join(
                " - `{}`\n".format(escape_markdown(str(cmd)))
                for cmd in set(DISABLE_CMDS + DISABLE_OTHER)
            )

            update.effective_message.reply_text(
                "The following commands are toggleable:\n{}".format(result),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        else:
            update.effective_message.reply_text("No commands can be disabled.")

    # do not async
    async def build_curr_disabled(chat_id: Union[str, int]) -> str:
        disabled = sql.get_all_disabled(chat_id)
        if not disabled:
            return "No commands are disabled!"

        result = "".join(" - `{}`\n".format(escape_markdown(cmd)) for cmd in disabled)
        return "The following commands are currently restricted:\n{}".format(result)

    @typing_action
    async def commands(update, context):
        chat = update.effective_chat
        user = update.effective_user
        conn = connected(context.bot, update, chat, user.id, need_admin=True)
        if conn:
            chat = NEKO_PTB.bot.getChat(conn)
        else:
            if update.effective_message.chat.type == "private":
                send_message(
                    update.effective_message,
                    "This command is meant to use in group not in PM",
                )
                return ""
            chat = update.effective_chat
            update.effective_chat.id

        text = build_curr_disabled(chat.id)
        send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN_V2)

    async def __import_data__(chat_id, data):
        disabled = data.get("disabled", {})
        for disable_cmd in disabled:
            sql.disable_command(chat_id, disable_cmd)

    async def __stats__():
        return "• {} disabled items, across {} chats.".format(
            sql.num_disabled(), sql.num_chats()
        )

    async def __migrate__(old_chat_id, new_chat_id):
        sql.migrate_chat(old_chat_id, new_chat_id)

    async def __chat_settings__(chat_id, user_id):
        return build_curr_disabled(chat_id)

    __mod_name__ = "Disabling"

    __help__ = """
Not everyone wants every feature that the bot offers. Some commands are best \
left unused; to avoid spam and abuse.

This allows you to disable some commonly used commands, so noone can use them. \
It'll also allow you to autodelete them, stopping people from bluetexting.

 • /cmds: Check the current status of disabled commands

*Admin only:*
 • /enable <cmd name>: Enable that command
 • /disable <cmd name>: Disable that command
 • /listcmds: List all possible disablable commands
    """

    DISABLE_HANDLER = CommandHandler(
        "disable", disable, run_async=True
    )  # , filters=Filters.chat_type.groups)
    ENABLE_HANDLER = CommandHandler(
        "enable", enable, run_async=True
    )  # , filters=Filters.chat_type.groups)
    COMMANDS_HANDLER = CommandHandler(
        ["cmds", "disabled"], commands, run_async=True
    )  # , filters=Filters.chat_type.groups)
    TOGGLE_HANDLER = CommandHandler(
        "listcmds", list_cmds, run_async=True
    )  # , filters=Filters.chat_type.groups)

    NEKO_PTB.add_handler(DISABLE_HANDLER)
    NEKO_PTB.add_handler(ENABLE_HANDLER)
    NEKO_PTB.add_handler(COMMANDS_HANDLER)
    NEKO_PTB.add_handler(TOGGLE_HANDLER)

else:
    DisableAbleCommandHandler = CommandHandler
    DisableAbleMessageHandler = MessageHandler
