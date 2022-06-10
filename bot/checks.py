from typing import Any
from discord.ext import commands

from bot import db
from bot.db import models
from bot.errors import CommandDisabledError


def guild_setting(setting: str, value: Any):
    """
    Command check for validating a particular guild setting.

    :param setting: The setting to check.
    :param value: If the setting's value matches this value, the check succeeds.
    """

    async def predicate(ctx) -> bool:
        if not ctx.guild:
            return False

        async with db.async_session() as session:
            guild_settings: models.GuildSettings | None = await session.get(
                models.GuildSettings, ctx.guild.id
            )

            if guild_settings:
                requested_setting = guild_settings.__getattribute__(setting)
            else:
                new_guild_settings = models.GuildSettings(
                    guild_id=ctx.guild.id
                )
                session.add(new_guild_settings)
                await session.commit()

                requested_setting = new_guild_settings.__getattribute__(
                    setting
                )

        if requested_setting != value:
            raise CommandDisabledError(ctx.command)

        return True

    return commands.check(predicate)
