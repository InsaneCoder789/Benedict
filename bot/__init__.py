import os
import sys
import json
import asyncio
import pathlib

import discord
from discord.ext import commands
from discord.ext.prettyhelp import PrettyHelp
from bot import db
from bot.views import PaginatedEmbedView

THEME = discord.Color.purple()

TESTING_GUILDS: list[int] | None = (
    list(map(int, json.loads(os.environ.get("TESTING_GUILDS") or "[]")))
    if "--debug" in sys.argv
    else None
)


intents = discord.Intents().all()
bot = commands.Bot(description="Eggs Benedict" ,intents = intents)

HELP_EMBEDS: list[discord.Embed] = []


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

@bot.slash_command(guild_ids=TESTING_GUILDS)
async def help(ctx: discord.ApplicationContext, command: str = None):
    """
    Get a list of commands or more information about a specific command
    """

    if command:
        cmd_info: discord.SlashCommand = bot.get_application_command(command)

        if not cmd_info:
            await ctx.respond(f"Command not found: `{command}`")
            return

        cmd_name = cmd_info.qualified_name
        formatted_options = []

        for option in cmd_info.options:
            if option.required:
                formatted_options.append(f"<{option.name}>")
            elif option.default is None:
                formatted_options.append(f"[{option.name}]")
            else:
                formatted_options.append(f"[{option.name}={option.default}]")

        options_str = " ".join(formatted_options)

        help_embed = discord.Embed(
            title=f"/{cmd_name}", color=THEME, description=cmd_info.description
        )
        help_embed.set_footer(
            text=(
                "Options wrapped in <> are required\n"
                "Options wrapped in [] are optional"
            )
        )

        help_embed.add_field(
            name="Usage",
            value=f"```/{cmd_name} {options_str}```",
            inline=False,
        )

        await ctx.respond(embed=help_embed)

    else:
        embed_view = PaginatedEmbedView(ctx.author.id, HELP_EMBEDS)
        msg = await ctx.respond(embed=HELP_EMBEDS[0], view=embed_view)
        timed_out = await embed_view.wait()

        if timed_out:
            if isinstance(msg, discord.Interaction):
                await msg.delete_original_message()
            else:
                await msg.delete()


def add_cogs():
    slash_cogs_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "cogs"
    )
    for filename in os.listdir(slash_cogs_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            bot.load_extension(f"bot.cogs.{filename[:-3]}")
            print(f"Loaded {filename[:-3]} slash cog!")
            
    bot.load_extension("jishaku")


def generate_help_embeds():
    index_embed = discord.Embed(
        title="Index", color=THEME, description=bot.description
    )
    index_embed.set_footer(
        text="You can use /help command to get more information about a command"
    )

    cog_embeds = []

    for cog_name, cog in list(bot.cogs.items()):

        cog_name = cog_name.replace("Slash", "")

        embed = discord.Embed(
            title=cog_name, color=THEME, description=cog.description
        )

        for cmd_info in cog.walk_commands():
            embed.add_field(
                name=f"/{cmd_info.qualified_name}",
                value=cmd_info.description,
            )

        if embed.fields:
            index_embed.add_field(name=cog_name, value=cog.description)
            cog_embeds.append(embed)

    HELP_EMBEDS.append(index_embed)
    HELP_EMBEDS.extend(cog_embeds)
    print("Generated Help Embeds!")


def main(token: str):
    loop = asyncio.get_event_loop()

    try:
        db.init_engine()
        add_cogs()
        generate_help_embeds()
        loop.run_until_complete(bot.start(token))
    except KeyboardInterrupt or SystemExit:
        pass
    finally:
        print("Exiting...")
        loop.run_until_complete(bot.close())
        loop.run_until_complete(db.close())
