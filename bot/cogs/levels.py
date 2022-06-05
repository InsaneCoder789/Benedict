import asyncio
import random
from datetime import datetime

import discord
from discord.ext import commands
from sqlalchemy.future import select

from bot import TESTING_GUILDS, db
from bot.db import models
from bot.image import generate_levels_image


class Levels(commands.Cog):
    XP_REWARD_RANGE = (2, 8)  # first number is min, second is max
    LVL_UP_MSG = "Congrats {member.mention}! You've reached level {level}!"

    levels_group = discord.SlashCommandGroup(
        "levels", "Commands for the leveling system", guild_ids=TESTING_GUILDS
    )

    # { guild id : { user id : time of last XP acknowledged msg } }
    prev_msg_times: dict[int, dict[int, datetime]] = {}

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
                    user_id=mem.id, guild_id=ctx.guild_id
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

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot or not msg.guild:
            return

        member = msg.author
        guild = msg.guild

        if guild.id not in self.prev_msg_times:
            self.prev_msg_times[guild.id] = {}

        if member.id not in self.prev_msg_times[guild.id]:
            self.prev_msg_times[guild.id][member.id] = msg.created_at
            return

        prev_time = self.prev_msg_times[guild.id][member.id]

        if (msg.created_at - prev_time).total_seconds() > 60:
            async with db.async_session() as session:
                q = (
                    select(models.Member)
                    .where(models.Member.user_id == member.id)
                    .where(models.Member.guild_id == guild.id)
                )
                result = await session.execute(q)
                member_data = result.scalar()

                if not member_data:
                    new_member_data = models.Member(
                        user_id=member.id, guild_id=guild.id
                    )
                    session.add(new_member_data)

                    result = await session.execute(q)
                    member_data = result.scalar()

                xp_goal = models.Member.base_level_requirement + (
                    models.Member.level_requirement_factor * member_data.level
                )
                member_data.xp += random.randint(*self.XP_REWARD_RANGE)

                if member_data.xp >= xp_goal:
                    member_data.xp -= xp_goal
                    member_data.level += 1

                    # TODO: Add option to change level channel
                    asyncio.create_task(
                        msg.channel.send(
                            self.LVL_UP_MSG.format(
                                member=member, level=member_data.level
                            )
                        )
                    )

                await session.commit()

            self.prev_msg_times[guild.id][member.id] = msg.created_at


def setup(bot):
    bot.add_cog(Levels())
