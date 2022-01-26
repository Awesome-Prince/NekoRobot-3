<h2 align="center">
    ──「𝐍𝐞𝐤𝐨 𝐑𝐨𝐛𝐨𝐭」──
</h2>

<p align="center">
  <img src="https://telegra.ph/file/38d8d80632bca0556aae9.jpg">
</p>

<p align="center">
<a href="https://app.codacy.com/gh/Awesome-Prince/NekoRobot?utm_source=github.com&utm_medium=referral&utm_content=Awesome-Prince/NekoRobot&utm_campaign=Badge_Grade_Settings" alt="Codacy Badge">
<img src="https://api.codacy.com/project/badge/Grade/6141417ceaf84545bab6bd671503df51" /> </a>
<a href="https://github.com/Awesome-Prince/NekoRobot" alt="Libraries.io dependency status for GitHub repo"> <img src="https://img.shields.io/librariesio/github/animekaizoku/SaitamaRobot" /> </a>
</p>
<p align="center">
<a href="https://github.com/Awesome-Prince/NekoRobot" alt="GitHub release (latest by date including pre-releases)"> <img src="https://img.shields.io/github/v/release/animekaizoku/saitamarobot?include_prereleases?style=flat&logo=github" /> </a>
<a href="https://www.python.org/" alt="made-with-python"> <img src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg?style=flat&logo=python&color=blue" /> </a>
<a href="https://t.me/Awesome_Prince" alt="Owner!"> <img src="https://aleen42.github.io/badges/src/telegram.svg" /> </a>

## Starting the bot.

Once you've setup your database and your configuration (see below) is complete, simply run:

`python3 -m NekoRobot`


## Setting up the bot (Read this before trying to use!):
Please make sure to use python3.6, as I cannot guarantee everything will work as expected on older python versions!
This is because markdown parsing is done by iterating through a dict, which are ordered by default in 3.6.

### Configuration

There are two possible ways of configuring your bot: a config.py file, or ENV variables.

The prefered version is to use a `config.py` file, as it makes it easier to see all your settings grouped together.
This file should be placed in your `tg_bot` folder, alongside the `__main__.py` file . 
This is where your bot token will be loaded from, as well as your database URI (if you're using a database), and most of 
your other settings.

It is recommended to import sample_config and extend the Config class, as this will ensure your config contains all 
defaults set in the sample_config, hence making it easier to upgrade.

An example `config.py` file could be:
```
from tg_bot.sample_config import Config


class Development(Config):
    OWNER_ID = 12234  # my telegram ID
    OWNER_USERNAME = "Awesome-Prince"  # my telegram username
    API_KEY = "your bot api key"  # my api key, as provided by the botfather
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/database'  # sample db credentials
    LOAD = []
    NO_LOAD = ['rss]
```

If you can't have a config.py file (EG on heroku), it is also possible to use environment variables.
The following env variables are supported:
 - `ENV`: Setting this to ANYTHING will enable env variables

 - `TOKEN`: Your bot token, as a string.
 - `OWNER_ID`: An integer of consisting of your owner ID
 - `OWNER_USERNAME`: Your username

 - `DATABASE_URL`: Your database URL
 - `LOAD`: Space separated list of modules you would like to load
 - `NO_LOAD`: Space separated list of modules you would like NOT to load
 - `WEBHOOK`: Setting this to ANYTHING will enable webhooks when in env mode
 messages
 - `URL`: The URL your webhook should connect to (only needed for webhook mode)

 - `SUDO_USERS`: A space separated list of user_ids which should be considered sudo users
 - `SUPPORT_USERS`: A space separated list of user_ids which should be considered support users (can gban/ungban,
 nothing else)
 - `WHITELIST_USERS`: A space separated list of user_ids which should be considered whitelisted - they can't be banned.
 - `DONATION_LINK`: Optional: link where you would like to receive donations.
 - `CERT_PATH`: Path to your webhook certificate
 - `PORT`: Port to use for your webhooks
 - `DEL_CMDS`: Whether to delete commands from users which don't have rights to use that command
 - `STRICT_GBAN`: Enforce gbans across new groups as well as old groups. When a gbanned user talks, he will be banned.
 - `WORKERS`: Number of threads to use. 8 is the recommended (and default) amount, but your experience may vary.
 __Note__ that going crazy with more threads wont necessarily speed up your bot, given the large amount of sql data 
 accesses, and the way python asynchronous calls work.
 - `BAN_STICKER`: Which sticker to use when banning people.
 - `ALLOW_EXCL`: Whether to allow using exclamation marks ! for commands as well as /.

### Python dependencies

Install the necessary python dependencies by moving to the project directory and running:

`pip3 install -r requirements.txt`.

This will install all necessary python packages.

### Database

If you wish to use a database-dependent module (eg: locks, notes, userinfo, users, filters, welcomes),
you'll need to have a database installed on your system. I use postgres, so I recommend using it for optimal compatibility.

In the case of postgres, this is how you would set up a the database on a debian/ubuntu system. Other distributions may vary.

- install postgresql:

`sudo apt-get update && sudo apt-get install postgresql`

- change to the postgres user:

`sudo su - postgres`

- create a new database user (change YOUR_USER appropriately):

`createuser -P -s -e YOUR_USER`

This will be followed by you needing to input your password.

- create a new database table:

`createdb -O YOUR_USER YOUR_DB_NAME`

Change YOUR_USER and YOUR_DB_NAME appropriately.

- finally:

`psql YOUR_DB_NAME -h YOUR_HOST YOUR_USER`

This will allow you to connect to your database via your terminal.
By default, YOUR_HOST should be 0.0.0.0:5432.

You should now be able to build your database URI. This will be:

`sqldbtype://username:pw@hostname:port/db_name`

Replace sqldbtype with whichever db youre using (eg postgres, mysql, sqllite, etc)
repeat for your username, password, hostname (localhost?), port (5432?), and db name.

## NOTE:

  I'm making this note to whoever comes to see this repo. (I came through a lot to make this bot) - I would not say such dumb thing like this, the whole credits goes to [tg_bot](https://github.com/Awesome-Rj/CutiepiiRobot.git). You might ask me what you did?, well i did some edits with my knowledge to make this bot like my own. I don't give a shit about any illegal problems if anyone comes with that GPLv3 license stuff. After all i came through a lot from many developers, No one ever told me/us anything not even a simple guide. So i will make this repo public so anyone can learn or get code from here for my future updates.
## Bot stuff
    
* Bot Support chat : [Support](https://t.me/NekoXSupport)
* Bot Updates : [update](https://t.me/Black_Knights_Union)

## CREDITS

This whole repo was forked and edited from [Cutiepii_Robot](https://github.com/Awesome-Rj/CutiepiiRobot.git)
Appropriate copyright and Code ownership goes to the respective creators/developers/owners.
Some code has been created by my own and my team.
I thank everyone who is behind this huge project. 
