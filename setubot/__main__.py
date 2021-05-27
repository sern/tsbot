TOKEN = "x"

import discord
import os
import time
from io import BytesIO
import requests
import asyncio
from discord.ext.commands import Bot


client = discord.Client()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == "来点涩图":
        setu = requests.get("https://api.lolicon.app/setu/").json()["data"][0]
        print(setu)
        title = setu["title"]
        author = setu["author"]
        author_url = f"https://www.pixiv.net/users/{setu['uid']}"
        url = f'https://www.pixiv.net/artworks/{setu["pid"]}'
        tags = " ".join([f"#{tag}" for tag in setu["tags"]])

        info = (
            discord.Embed(title=setu["title"])
            .add_field(
                name="author",
                value=f"[{author}]({author_url})",
            )
            .add_field(name="source", value=url)
            .add_field(name="tags", value=tags)
        )
        setu_url = setu["url"]
        setu = requests.get(setu_url).content
        setu_f = BytesIO(setu)
        f = discord.File(setu_f, filename="setu.jpg")
        await message.channel.send(embed=info, file=f)


class PixivApi(object):
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0"

    def __init__(self, phpsessid: str):
        self.session = requests.Session()
        self.session.cookies.update({"PHPSESSID": phpsessid})

    def get(self, url):
        return self.session.get(url)


# curl 'https://www.pixiv.net/ranking.php?mode=daily_r18&p=1&format=json' \
#     -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0' \
#     -H 'Cookie: PHPSESSID=xxx'

if __name__ == "__main__":
    client.run(TOKEN)
