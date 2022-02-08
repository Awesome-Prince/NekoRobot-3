import html
import random
import time

import NekoRobot.modules.NekoFunBot_Strings as fun_strings
from NekoRobot import dispatcher
from NekoRobot.modules.disable import DisableAbleCommandHandler, DisableAbleMessageHandler
from NekoRobot.modules.helper_funcs.chat_status import is_user_admin
from NekoRobot.modules.helper_funcs.alternate import typing_action
from NekoRobot.modules.helper_funcs.filters import CustomFilters
from NekoRobot.modules.helper_funcs.extraction import extract_user
from telegram import ChatPermissions, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, run_async, CommandHandler, Filters



