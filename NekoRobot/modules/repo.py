

import github
from pyrogram import filters

from NekoRobot import pgram


@pgram.on_edited_message(filters.command("repo"))
async def give_repo(m):
    g = github.Github()
    repo = g.get_repo("Awesome-Prince/NekoRobot-3")
    list_of_users = "".join(
        f"*{count}.* [{i.login}](https://github.com/{i.login})\n"
        for count, i in enumerate(repo.get_contributors(), start=1)
    )

    text = f"""[Github](https://github.com/Awesome-Prince/NekoRobot-3.git) | [Support Chat](https://t.me/ProgrammerSupport)
```----------------
| Contributors |
----------------```
{list_of_users}"""
    await m.reply(text, disable_web_page_preview=False)


__mod_name__ = "Repository"
