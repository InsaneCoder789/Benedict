import discord
from discord.ext import commands
from discord.mentions import AllowedMentions

from bot import TESTING_GUILDS, db
from bot.db import models
from bot.image import generate_levels_image


class Levels(commands.Cog):
    levels_group = discord.SlashCommandGroup(
        "levels", "Commands for the leveling system", guild_ids=TESTING_GUILDS
    )

    @levels_group.command()
    async def rank(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Member | None = None,
    ):
        """
        Check your rank in the current server
        """

        if not (mem := member or ctx.author):
            return

        await ctx.defer()

        async with db.async_session() as session:
            member_data: models.Member | None = await session.get(
                models.Member, mem.id
            )

            if member_data:
                level = member_data.level
                xp = member_data.xp
            else:
                new_member_data = models.Member(
                    id=mem.id, guild_id=ctx.guild_id
                )
                session.add(new_member_data)
                await session.commit()

                level = new_member_data.level
                xp = new_member_data.xp

        max_xp = (
            models.Member.base_level_requirement
            + models.Member.level_requirement_factor * level
        )
        levels_img = await generate_levels_image(mem, level, xp, max_xp)  # type: ignore

        # Make a cool image thing here
        await ctx.respond(
            f"{mem.mention}'s current level is **{level}** in this server",
            file=discord.File(levels_img, filename=levels_img.name),
            allowed_mentions=AllowedMentions.none(),
        )


def setup(bot):
    bot.add_cog(Levels())
