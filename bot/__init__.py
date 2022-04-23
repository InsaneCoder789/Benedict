import os
import sys
import json

import discord
from discord.ext import commands

TESTING_GUILDS: list[int] | None = (
    list(map(int, json.loads(os.environ.get("TESTING_GUILDS") or "[]")))
    if "--debug" in sys.argv
    else None
)
bot = commands.Bot(description="Eggs Benedict")


@bot.event
async def on_ready():
    if user := bot.user:
        print("Logged in as", user)


@bot.slash_command(guild_ids=TESTING_GUILDS)
async def ping(ctx: discord.ApplicationContext):
    """
    Get the bot's websocket latency. You don't have to worry about this unless the bot is lagging.
    """

    latency = ctx.bot.latency * 1000
    await ctx.respond(f"Pong! Latency is {latency:.2f} ms")


def main(token: str):
    try:
        bot.run(token)
    except KeyboardInterrupt or SystemExit:
        pass
    finally:
        print("Exiting...")
