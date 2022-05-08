import discord
import json
import os
import datetime
import traceback
import random
import asyncio
from discord.ext import commands
from discord.commands import \
    slash_command

class SlashMod(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="slowmode", description="Add slowmode delay in the current channel")
    async def slowmode(self, ctx, delay: int):
        try:
            if delay == 0:
                embed = discord.Embed(title='Slowmode turned off', color=discord.Color.green())
                await ctx.respond(embed=embed)
                await ctx.channel.edit(slowmode_delay=0)
            elif delay > 21600:
                embed = discord.Embed(
                    title='You cannot have a slowmode above 6hrs.', color=discord.Color.red())
                await ctx.respond(embed=embed)
            else:
                await ctx.channel.edit(slowmode_delay=delay)
                embed = discord.Embed(title=f'Slowmode set to {delay} seconds.', color=discord.Color.green())
                await ctx.respond(embed=embed)
        except Exception:
            traceback.print_exc()

    # @commands.slash_command(name="")
    # async def softban(self, ctx, member: discord.Member, *, reason='No reason provided'):
    #     await member.ban(reason=reason)
    #     await member.unban(reason=reason)
    #     embed = discord.Embed(title=f':white_check_mark: Successfully softbanned {member}!', color=discord.Color.green())
    #     await ctx.respond(embed=embed)

    @commands.slash_command(name="ban", description="Permanently remove a person from the server")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason):
        if member is None:
            em = discord.Embed(title='Please specify a member.', color=discord.Color.red())
            await ctx.respond(embed=em)
            return
        await member.ban(reason=reason)
        em = discord.Embed(title=f'{member} has been banned!', color=discord.Color.green())
        await ctx.respond(embed=em)

        embed = discord.Embed(
            title=f'You have been banned from {ctx.guild.name}', description=f'Banned by {member}', color=discord.Color.red())
        embed.add_field(name='Reason:', value=f'{reason}')
        await member.send(embed=embed)

    @commands.slash_command(name="unban", description="Unban a person from the server")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                em = discord.Embed(title=f':white_check_mark: {user.mention} has been unbanned!', color=discord.Color.green())
                await ctx.respond(embed=em)
                return

    @commands.slash_command(name="kick", description="Remove a person from the server")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason='No reason provided'):
        if not member:
            em = discord.Embed(title=':x: Please specify a member.', color=discord.Color.red())
            await ctx.respond(embed=em)
            return
        await member.kick()
        em = discord.Embed(title=f':white_check_mark: {member} has been kicked!', color=discord.Color.green())
        await ctx.respond(embed=em)
        embed = discord.Embed(
            title=f'You have been kicked from {ctx.guild.name}', description=f'Kicked by {member}', color=discord.Color.red())
        embed.add_field(name='Reason:', value=f'{reason}')
        await member.send(embed=embed)

    @commands.slash_command(name="warn", description="Warn a member for doing something they weren't supposed to")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        with open('warnings.json', 'r') as f:
            warns = json.load(f)
        if str(ctx.guild.id) not in warns:
            warns[str(ctx.guild.id)] = {}
        if str(member.id) not in warns[str(ctx.guild.id)]:
            warns[str(ctx.guild.id)][str(member.id)] = {}
            warns[str(ctx.guild.id)][str(member.id)]["warns"] = 1
            warns[str(ctx.guild.id)][str(member.id)]["warnings"] = [reason]
        else:
            warns[str(ctx.guild.id)][str(member.id)]["warnings"].append(reason)
        with open('warnings.json', 'w') as f:
            json.dump(warns, f)
            e = discord.Embed(title=f":white_check_mark: {member} has been warned for {reason}!", color=discord.Color.green())
            await ctx.respond(embed=e)
            embed = discord.Embed(
                title=f'You have been warned in {ctx.guild.name} ', description=f'You received a warning from {ctx.author}', color=discord.Color.red())
            embed.add_field(name='Reason:', value=f'{reason}')
            await member.send(embed=embed)

    @commands.slash_command(name="removewarn", description="Remove a warn from a member")
    @commands.has_permissions(manage_guild=True)
    async def removewarn(self, ctx, member: discord.Member, num: int, *, reason='No reason provided.'):
        with open('warnings.json', 'r') as f:
            warns = json.load(f)

        num -= 1
        warns[str(ctx.guild.id)][str(member.id)]["warns"] -= 1
        warns[str(ctx.guild.id)][str(member.id)]["warnings"].pop(num)
        with open('warnings.json', 'w') as f:
            json.dump(warns, f)
            e = discord.Embed(title=f":white_check_mark: Warn for {member} has been removed!", color=discord.Color.green())
            await ctx.respond(embed=e)
            embed = discord.Embed(
                title=f'Your warn in {ctx.guild.name} been removed', description=f'Your warning was removed by {ctx.author}', color=discord.Color.green())
            await member.send(embed=embed)

    @commands.slash_command(name="warns", description="Check warns for a user")
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx, member: discord.Member):
        with open('warnings.json', 'r') as f:
            warns = json.load(f)

        num = 1
        warnings = discord.Embed(title=f"{member}\'s warns", color=discord.Color.green())
        for warn in warns[str(ctx.guild.id)][str(member.id)]["warnings"]:
            warnings.add_field(name=f"Warn {num}", value=warn)
            num += 1
        await ctx.respond(embed=warnings)

def setup(bot):
    bot.add_cog(SlashMod(bot))
