import asyncio
import uuid
import discord
from datetime import datetime
from discord.ext import commands
from sqlalchemy.future import select
from bot import THEME , TESTING_GUILDS
class Miscellaneous(commands.Cog):
    """
 Benedict's General Information Cog
    """
@commands.slash_command(guild_ids=TESTING_GUILDS)
async def info(self, ctx: discord.ApplicationContext):
        """
        Display bot information
        """

        ping = int(self.bot.latency * 1000)
        guild_count = str(len(self.bot.guilds))
        total_member_count = 0

        for guild in self.bot.guilds:
            total_member_count += guild.member_count

        info_embed = discord.Embed(title="Benedict Information", color=THEME)
        info_embed.set_author(
            name=str(ctx.author), icon_url=ctx.author.avatar.url
        )
        info_embed.set_thumbnail(url=self.bot.user.avatar.url)

        info_embed.add_field(
            name="Latency/Ping", value=f"{ping}ms", inline=False
        )
        info_embed.add_field(
            name="Server Count", value=guild_count, inline=False
        )
        info_embed.add_field(
            name="Total Member Count",
            value=str(total_member_count),
            inline=False,
        )

        await ctx.respond(embed=info_embed)

@commands.slash_command(guild_ids=TESTING_GUILDS)
async def github(self, ctx: discord.ApplicationContext):
        """
        Link to the GitHub Repository
        """

        github_link = "https://github.com/InsaneCoder789/Benedict"
        await ctx.respond(github_link)

@commands.slash_command(guild_ids=TESTING_GUILDS)
async def support(self, ctx: discord.ApplicationContext):
        """
        Invite link for Benedict's Support Server
        """

        support_link = "https://discord.gg/nVNwGMKmd3"
        await ctx.respond(support_link)

@commands.slash_command(guild_ids=TESTING_GUILDS)
async def uptime(self, ctx: discord.ApplicationContext):
        """
        Check how long the bot has been up for
        """

        humanized_time = f"<t:{self.launched_at}:R>"
        await ctx.respond(f"I was last restarted {humanized_time}")

def setup(bot):
    bot.add_cog(Miscellaneous(bot))