import discord
from discord.ext import commands
from discord.mentions import AllowedMentions

from bot import TESTING_GUILDS, db
from bot.db import models


class Levels(commands.Cog):
    levels_group = discord.SlashCommandGroup(
        "levels", "Commands for the leveling system", guild_ids=TESTING_GUILDS
    )

    @levels_group.command()
    async def query(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Member | None = None,
    ):
        if not (mem := member or ctx.author):
            return

        async with db.async_session() as session:
            member_data: models.Member | None = await session.get(
                models.Member, mem.id
            )

            if member_data:
                level = member_data.level
            else:
                new_member_data = models.Member(
                    id=mem.id, guild_id=ctx.guild_id
                )
                session.add(new_member_data)
                await session.commit()

                level = new_member_data.level

        # Make a cool image thing here
        await ctx.respond(
            f"{mem.mention}'s current level is **{level}** in this server",
            allowed_mentions=AllowedMentions.none(),
        )


def setup(bot):
    bot.add_cog(Levels())
