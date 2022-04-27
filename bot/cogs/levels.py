import discord
from uuid import uuid4
from discord.ext import commands
from sqlalchemy.future import select

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

        async with db.async_session() as session:
            q = (
                select(models.Member)
                .where(models.Member.user_id == mem.id)
                .where(models.Member.guild_id == ctx.guild_id)
            )
            result = await session.execute(q)
            member_data = result.scalar()

            if member_data:
                level = member_data.level
                xp = member_data.xp
            else:
                new_member_data = models.Member(
                    id=uuid4().hex, user_id=mem.id, guild_id=ctx.guild_id
                )
                session.add(new_member_data)
                await session.commit()

                level = new_member_data.level
                xp = new_member_data.xp

        await ctx.defer()

        max_xp = (
            models.Member.base_level_requirement
            + models.Member.level_requirement_factor * level
        )
        levels_img = await generate_levels_image(mem, level, xp, max_xp)  # type: ignore

        # Make a cool image thing here
        await ctx.respond(
            file=discord.File(levels_img, filename=levels_img.name)
        )


def setup(bot):
    bot.add_cog(Levels())
