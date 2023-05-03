import speedtest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, run_async

from NekoRobot import DEV_USERS, dispatcher
from NekoRobot.modules.disable import DisableAbleCommandHandler
from NekoRobot.modules.helper_funcs.chat_status import dev_plus
from NekoRobot import nekocmd

def convert(speed):
    return round(int(speed)/1048576, 2)


@dev_plus
@run_async
def speedtestxyz(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton("image", callback_data="speedtest_image"),
            InlineKeyboardButton("text", callback_data="speedtest_text"),
            InlineKeyboardButton("help", callback_data="help"), 
        ]
    ]
    update.effective_message.reply_text(
        "speedtest mode", reply_markup=InlineKeyboardMarkup(buttons)
        ) 

@run_async
def speedtestxyz_callback(update: Update, context: CallbackContext):
    query = update.callback_query

    if query.from_user.id in DEV_USERS:
        
        msg = update.effective_message.edit_text("running a speedtest...")
        speed = speedtest.Speedtest()
        speed.get_best_server()
        speed.download()
        speed.upload()
        replymsg = "speedtest result"
       
        if query.data == "speedtest_image":
           
            speedtest_image = speed.results.share()
            update.effective_message.reply_photo(
                photo=speedtest_image, caption=replymsg
           
            )
            
            msg.delete()
            

        elif query.data == "speedtest_text":
            
            result = speed.results.dict()
            replymsg += f"\nDownload: {convert(result['download'])}Mb/s\nUpload: {convert(result['upload'])}Mb/s\nPing: {result['ping']}"
            update.effective_message.edit_text(replymsg, parse_mode=ParseMode.MARKDOWN)
    else:
        return


SPEED_TEST_HANDLER = DisableAbleCommandHandler("speedtest", speedtestxyz)
SPEED_TEST_CALLBACKHANDLER = CallbackQueryHandler(
    speedtestxyz_callback, pattern="speedtest_.*"
)

dispatcher.add_handler(SPEED_TEST_HANDLER)
dispatcher.add_handler(SPEED_TEST_CALLBACKHANDLER)

help = """
» /speedtest *:* Runs a speedtest and check the server speed.
"""

mod_name = "speedtest"
command_list = ["speedtest"]
handlers = [SPEED_TEST_HANDLER, SPEED_TEST_CALLBACKHANDLER]
