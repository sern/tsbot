import os

TOKEN = os.environ["DISCORD_TOKEN"]
assert TOKEN


import discord
from io import BytesIO
import requests
import asyncio
from discord.ext.commands import Bot
from musicbot import get_metadata


bot = Bot(command_prefix="")


@bot.command(name="test")
async def _test(ctx, arg):
    print("good")


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


@bot.command(
    name="music",
    description="Plays an audio in the voice channel",
    pass_ctx=True,
)
async def music(ctx):

    # guild = ctx.guild
    # voice_channel = guild.voice_channels[0]

    # grab the user who sent the command
    user = ctx.message.author
    print(user)
    # if not user.voice:
    #     user.voice.channel
    voice_channel = user.voice.channel
    # only play music if user is in a voice channel

    music_filename = "./01-ふわふわ時間.m4a"

    metadata = get_metadata(music_filename)
    title = metadata.title
    artist = metadata.artist
    (album, cover) = metadata.album
    desc = ""
    if title:
        desc += "Title: " + title + "\n"
    if artist:
        desc += "Artist: " + artist + "\n"
    if album:
        desc += "Album: " + album + "\n"

    if voice_channel:
        # grab user's voice channel
        print("User is in channel: " + voice_channel.name)
        # create StreamPlayer
        player = None
        for voice_client in bot.voice_clients:
            if voice_client.channel.id == voice_channel.id:
                player = voice_client
        if not player:
            player = await voice_channel.connect()
        if player.is_playing():
            player.stop()
        await ctx.channel.send(desc)
        if cover:
            content = BytesIO(bytearray(cover.data))
            f = discord.File(content, filename="cover." + cover.ext())
            await ctx.channel.send(file=f)
        player.play(
            discord.FFmpegPCMAudio(
                music_filename,
            ),
            after=lambda e: print("done", e),  # disconnect?
        )
        while not player.is_done():
            await asyncio.sleep(1)
        # disconnect after the player has finished
        player.stop()
        # await vc.disconnect()
    else:
        await ctx.channel.send("Please join a voice channel and retry.")
        print("User is not in a channel.")
        # await bot.say("User is not in a channel.")


if __name__ == "__main__":
    bot.run(TOKEN)
