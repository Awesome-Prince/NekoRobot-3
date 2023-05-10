# Create a new config.py or rename this to config.py file in same dir and import, then extend this class.
import json
import os


def get_user_list(config, key):
    with open(f"{os.getcwd()}/NekoRobot/{config}", "r") as json_file:
        return json.load(json_file)[key]


# Create a new config.py or rename this to config.py file in same dir and import, then extend this class.
class Config(object):
    LOGGER = True
    # REQUIRED
    # Login to https://my.telegram.org and fill in these slots with the details given by it

    API_ID = 16743442  # integer value, dont use ""
    API_HASH = "12bbd720f4097ba7713c5e40a11dfd2a"
    TOKEN = "6286654828:AAGVeE7Rz8X9VdUOgm1LAqu5c9x418-zFA"  # This var used to be API_KEY but it is now TOKEN, adjust accordingly.
    STRING_SESSION = ""
    REDIS_URL = "redis://default:neko69@redis-18084.c289.us-west-1-2.ec2.cloud.redislabs.com:18084/Neko-Free-db"
    MONGO_DB = "NekoRobot"
    HELP_IMG = ""
    TEMP_DOWNLOAD_DIRECTORY = "./"
    MONGO_DB_URI = "mongodb+srv://sonu55:sonu55@cluster0.vqztrvk.mongodb.net/?retryWrites=true&w=majority"
    OWNER_ID = 5885920877  # If you dont know, run the bot and do /id in your private chat with it, also an integer
    OWNER_USERNAME = "MH17_KUNAL"
    SUPPORT_CHAT = "Anime_Krew"  # Your own group for support, do not add the @
    JOIN_LOGGER = (
        -1001935950378
    )  # Prints any new group the bot is added to, prints just the name and ID.
    EVENT_LOGS = (
        -1001935950378
    )  # Prints information like gbans, sudo promotes, AI enabled disable states that may help in debugging and shit

    # RECOMMENDED
    SQLALCHEMY_DATABASE_URI = "postgresql://kunalgaikwad932244:tIQq5nmiW7KY@ep-little-wood-723080.ap-southeast-1.aws.neon.tech/neondb"  # needed for any database modules
    DB_URL = "postgresql://kunalgaikwad932244:tIQq5nmiW7KY@ep-little-wood-723080.ap-southeast-1.aws.neon.tech/neondb"
    LOAD = []
    BOT_USERNAME = "Wolfwood_Bot"
    ARQ_API_URL = "arq.hamker.dev"
    ARQ_API_KEY = "CPYPCC-ZGUYAQ-RUMHTL-KMEAYY-ARQ"
    ERROR_LOGS = -1001909608236
    BOT_NAME = "ᴡᴏʟғᴡᴏᴏᴅ"
    NO_LOAD = ["rss", "cleaner", "connection", "math"]
    OPENWEATHERMAP_ID = ""
    WEBHOOK = False
    INFOPIC = True
    URL = None
    REM_BG_API_KEY = "PxCe5v4ZX3RmoQnPdDzf2TTz"
    SPAMWATCH_API = "F7tTqg9Sm5slUt3gfzXCGfQRRuen04tTD_EkGNEU1IgWlIN3L3_mh9nFSXKKyPKf"  # go to support.spamwat.ch to get key
    SPAMWATCH_SUPPORT_CHAT = "@SpamWatchSupport"

    # OPTIONAL
    ##List of id's -  (not usernames) for users which have sudo access to the bot.
    DRAGONS = get_user_list("elevated_users.json", "sudos")
    ##List of id's - (not usernames) for developers who will have the same perms as the owner
    DEV_USERS = get_user_list("elevated_users.json", "devs")
    ##List of id's (not usernames) for users which are allowed to gban, but can also be banned.
    DEMONS = get_user_list("elevated_users.json", "supports")
    # List of id's (not usernames) for users which WONT be banned/kicked by the bot.
    TIGERS = get_user_list("elevated_users.json", "tigers")
    WOLVES = get_user_list("elevated_users.json", "whitelists")
    DONATION_LINK = None  # EG, paypal
    CERT_PATH = None
    PORT = 5000
    DEL_CMDS = True  # Delete commands that users dont have access to, like delete /ban if a non admin uses it.
    STRICT_GBAN = True
    WORKERS = (
        8  # Number of subthreads to use. Set as number of threads your processor uses
    )
    BAN_STICKER = ""  # banhammer marie sticker id, the bot will send this sticker before banning or kicking a user in chat.
    ALLOW_EXCL = True  # Allow ! commands as well as / (Leave this to true so that blacklist can work)
    CASH_API_KEY = "VQ45LFKYPMJ2LKIU"  # Get your API key from https://www.alphavantage.co/support/#api-key
    TIME_API_KEY = "RMUWWFM11HK9"  # Get your API key from https://timezonedb.com/api
    WALL_API = "65G8ZKE6050P"  # For wallpapers, get one from https://wall.alphacoders.com/api.php
    AI_API_KEY = "SOME1HING_privet_990022"  # For chatbot, get one from https://coffeehouse.intellivoid.net/dashboard
    BL_CHATS = []  # List of groups that you want blacklisted.
    SPAMMERS = None


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True  # Create a new config.py or rename this to config.py file in same dir and import, then extend this class.
