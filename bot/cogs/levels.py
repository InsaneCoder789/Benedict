import asyncio
import random
from datetime import datetime

import discord
from discord.ext import commands
from sqlalchemy.future import select

from bot import TESTING_GUILDS, db
from bot.db import models
from bot.image import generate_levels_image
from bot.checks import guild_setting


class Levels(commands.Cog):
    """
    To keep track of how talkative you are!
    """
    
    XP_REWARD_RANGE = (2, 8)  # first number is min, second is max
    LVL_UP_MSG = "Congrats {member.mention}! You've reached level {level}!"
    
    levels_group = discord.SlashCommandGroup(
        "levels", "Commands for the leveling system", guild_ids=TESTING_GUILDS
    )

    # { guild id : { user id : time of last XP acknowledged msg } }
    prev_msg_times: dict[int, dict[int, datetime]] = {}

    @commands.has_guild_permissions(administrator=True)
    @levels_group.command()
    async def enabled(self, ctx: discord.ApplicationContext, value: bool):
        """
        Enable or disable the leveling system in the current server
        """

        async with db.async_session() as session:
            guild_settings: models.GuildSettings | None = await session.get(
                models.GuildSettings, ctx.guild_id
            )

            if guild_settings:
                if guild_settings.levels_enabled == value:
                    await ctx.respond(
                        f"{'✅' if value else '❌'} Levels are already **{'enabled' if value else 'disabled'}** in this server."
                    )
                    return

                guild_settings.levels_enabled = value  # type: ignore
            else:
                new_guild_settings = models.GuildSettings(
                    guild_id=ctx.guild_id, levels_enabled=value
                )
                session.add(new_guild_settings)

            await session.commit()

        await ctx.respond(
            f"{'✅' if value else '❌'} Levels are now **{'enabled' if value else 'disabled'}** in this server."
        )

    @commands.has_guild_permissions(administrator=True)
    @levels_group.command()
    async def channel(
        self, ctx: discord.ApplicationContext, channel: discord.TextChannel
    ):
        """
        Set the channel where level up messages will be sent
        """

        async with db.async_session() as session:
            guild_settings: models.GuildSettings | None = await session.get(
                models.GuildSettings, ctx.guild_id
            )

            if guild_settings:
                if guild_settings.levels_channel == channel.id:
                    await ctx.respond(
                        f"Levels channel is already set to {channel.mention}."
                    )
                    return

                guild_settings.levels_channel = channel.id  # type: ignore

            else:
                new_guild_settings = models.GuildSettings(
                    guild_id=ctx.guild_id, levels_channel=channel.id
                )
                session.add(new_guild_settings)

            await session.commit()

        await ctx.respond(f"Levels channel is now set to {channel.mention}.")

    @guild_setting("levels_enabled", True)
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

        async with db.async_session() as session:
            if guild_settings := await session.get(
                models.GuildSettings, msg.guild.id
            ):
                if not guild_settings.levels_enabled:
                    return
            else:
                guild_settings = models.GuildSettings(guild_id=msg.guild.id)
                session.add(guild_settings)
                await session.commit()

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

                    lvl_up_channel: discord.TextChannel = guild.get_channel(guild_settings.levels_channel) if guild_settings.levels_channel else msg.channel  # type: ignore
                    asyncio.create_task(
                        lvl_up_channel.send(
                            self.LVL_UP_MSG.format(
                                member=member, level=member_data.level
                            )
                        )
                    )

                await session.commit()

            self.prev_msg_times[guild.id][member.id] = msg.created_at


def setup(bot):
    bot.add_cog(Levels(bot))
