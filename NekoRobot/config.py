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

    API_ID = 14056295 # integer value, dont use ""
    API_HASH = "9ae65901d2eeb5854cc5aa562566d34a"
    TOKEN = "5687579083:AAG13Q0fN81Kx95DLI7zWBRf0WoDF5lncnU"  # This var used to be API_KEY but it is now TOKEN, adjust accordingly.
    STRING_SESSION = "BQBBn6gvZ6jDWYZ8EoQQvu91K7fn_VnIFgM8AIF06OnTFqFdFaP0Sn28YWGbJ2mpAE8bREr84XNa2KhJGaUr7DoPe42dzKfeCjgBKrFvA4Vup9C0XVoM0juUJzK0VnawXV9DDAaXEWsCHfLfFujOfIZmdLWUZ0cgsZR6Uj6McpLomEAXevJXPvW16b3COf-Poe5mrfo4fYCflwIenrPcoh-A1EyyX-ebptNas8k5JAkyCgi7YU9VELbuxsdaD_TNOF29Lxb16wVCVPzXw39pR6hTBNqtYNE3VLrNBmiOS7wgwlGva6KUiYIGTqIz9ScfdNRRTib1XL9wXdH6TLSrYkbdAAAAAGukwXgA"
    OWNER_ID = 1805959544  # If you dont know, run the bot and do /id in your private chat with it, also an integer
    OWNER_USERNAME = "Fazal000001"
    ERROR_LOGS = (
       -1001893268779
    )
    SUPPORT_CHAT = "sukunaXsupport"  # Your own group for support, do not add the @
    JOIN_LOGGER = (
        -1001893268779
    )  # Prints any new group the bot is added to, prints just the name and ID.
    EVENT_LOGS = (
        -1001893268779
    )  # Prints information like gbans, sudo promotes, AI enabled disable states that may help in debugging and shit

    # RECOMMENDED
    SQLALCHEMY_DATABASE_URI = "postgres://ilstovrn:BuRYkzlUAbaDXwu4IMp-FGkGYLbHUFD7@fanny.db.elephantsql.com/ilstovrn"  # needed for any database modules
    DB_URL = "mongodb+srv://sukuna:sukuna@sukuna.vipbn9a.mongodb.net/?retryWrites=true&w=majority"
    REDIS_URL = "redis://sukuna:@Sukuna123@redis-13592.c90.us-east-1-3.ec2.cloud.redislabs.com:13592/sukuna"
    LOAD = []
    NO_LOAD = ["rss", "cleaner", "connection", "math"]
    WEBHOOK = False
    INFOPIC = True
    URL = None
    SPAMWATCH_API = "F7tTqg9Sm5slUt3gfzXCGfQRRuen04tTD_EkGNEU1IgWlIN3L3_mh9nFSXKKyPKf"  # go to support.spamwat.ch to get key
    SPAMWATCH_SUPPORT_CHAT = "@SpamWatchSupport"
    ARQ_API_KEY = "MVJVCA-IEFPMI-WXCBKD-WSKJXU-ARQ"
    ARQ_API_URL = "https://arq.hamker.in"
    BOT_NAME = "ѕυкυиα"
    BOT_USERNAME = "SukunaXimmortalbot"
    OPENWEATHERMAP_ID = "ca1f9caacbb92187db96c0bf5686017b"
    REM_BG_API_KEY = "PxCe5v4ZX3RmoQnPdDzf2TTz"

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
    CASH_API_KEY = (
        "VQ45LFKYPMJ2LKIU"  # Get your API key from https://www.alphavantage.co/support/#api-key
    )
    TIME_API_KEY = "RMUWWFM11HK9"  # Get your API key from https://timezonedb.com/api
    WALL_API = (
        "65G8ZKE6050P"  # For wallpapers, get one from https://wall.alphacoders.com/api.php
    )
    AI_API_KEY = "SOME1HING_privet_990022"  # For chatbot, get one from https://coffeehouse.intellivoid.net/dashboard
    BL_CHATS = []  # List of groups that you want blacklisted.
    SPAMMERS = None


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True  # Create a new config.py or rename this to config.py file in same dir and import, then extend this class.


import json
import os


def get_user_list(config, key):
    with open(f"{os.getcwd()}/NekoRobot/{config}", "r") as json_file:
        return json.load(json_file)[key]
