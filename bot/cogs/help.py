import email
import discord
import traceback
import random
from discord.ext import commands

from bot import THEME
import bot


class Dropdown(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(
                label="Moderation",
                description="Commands to uphold the peace and integrity of the server",
                emoji="⚙️",
            ),
            discord.SelectOption(
                label="Fun",
                description="Commands to have some fun and relieve stress (or induce it)",
                emoji="🎊",
            ),
            discord.SelectOption(
                label="Bot Commands",
                description="Commands related to the bot, such as it's information etc",
                emoji="📜",
            ),
            discord.SelectOption(
                label="Music", description="Commands to for playing music with Benedict", emoji="🎶"
            ),
            discord.SelectOption(
            
                label="Levelling", description="To check how Chit-Chatty you are!", emoji="📈"
            )
        ]

        super().__init__(
            placeholder="Select a Category",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Moderation":
            e = discord.Embed(title="Moderation Commands", color=THEME, description=
            "**Clear**(`/clear`)\nClears messages in a channel\n\n**ClearCap**(`/clearcap`) \n Set the maximum numbers of messages to be cleared\n\n**Slowmode**(`/slowmode`)\nAdd slowmode delay in the current channel\n\n**Ban**(`/ban`)\nPermanently remove a person from the server\n\n**Unban**(`/unban`)\nUnban a person from the server\n\n**Kick**(`/kick`)\nRemove a person from the server\n\n**Warn**(`/warn`)\nWarn a member for doing something they weren't supposed to\n\n**Infractions**(`/infractions`)\nSee all the infractions in this server\n\n**ClearInfractions**(`/clearinfractions`)\nClear somebody's infractions in the current server\n\n**Nuke**(`/nuke`)\nNuke is an easy way of deleting all messages in a channel!\n\n**ServerInfo**(`/serverinfo`)\nGet general information about the server\n\n**UserInfo**(`/memberinfo`)\nGet general information about a member")
            await interaction.response.send_message(embed=e, ephemeral=True)
        if self.values[0] == "Fun":
            e = discord.Embed(title="Fun Commands", color=THEME, description="**Flip**(`/coinflip`)\nFlip a coin\n\n**RockPaperScissors**(`/rps`)\nPlay Rock Paper Scissors with Benedict\n\n**Emojify**(`/emojify`)\nTurn a sentence into emojis\n\n**Password**(`/password`)\nGenerate a password\n\n**AI**(`/ai`)\nAsk the AI a question!\n\n**Joke**(`/joke`)\nGives you a joke\n\n**ASCII**(`/ascii`)\nTurn a sentence into cool ASCII art\n\n**8Ball**(`/8ball`)\nCall upon the powers of the all knowning magic 8Ball\n\n**Remind**(`/remind`)\nSet a reminder. Example: /remind 1d 2h 12m 5s make lunch (All time options are not required)\n\n**AFK**(`/afk`)\nSets your AFK status\n\n**Roll**(`/roll`)\nRoll a dice\n\n**Choose**(`/choose`)\nLet Benedict choose the best option for you\n\n**YouTube**(`/youtube`)\nSearch for YouTube videos")
            await interaction.response.send_message(embed=e, ephemeral=True)
        if self.values[0] == "Bot Commands":
            e = discord.Embed(title="Bot Commands", color=THEME, description="**Bot Information**(`/botinfo`)\nShows information about Benedict\n\n**Uptime**(`/uptime`)\nShows the time the bot has been online for\n\n**Ping**(`/ping`)\nCheck the bots ping\n\n**Invite**(`/invite`)\nGives you a link to invite Benedict")
            await interaction.response.send_message(embed=e, ephemeral=True)
        if self.values[0] == "Music":
            e = discord.Embed(title="Music Commands", color=THEME, description="**Join**(`/join`)\nMakes the Bot Join the Voice channel\n\n**Summon**(`/summon`)\nSummons the bot to a voice channel.\n\n**Leave**(`/leave`)\nLeaves the voice channel\n\n**Volume**(`/volume`)\nSets the volume of the player!\n\n**Now**(`/now`)\nDisplays the currently playing song.\n\n**Pause**(`/pause`)\nPauses the Current Playing Song \n\n**Resume**(`/resume`)\nResumes the Currently paused song\n\n**Stop**(`/stop`)\nStops playing the song and clears the queue\n\n**Skip**(`/skip`)\nSkips the currently playomg song and plays the next one in queue\n\n**Queue**(`/queue`)\nShows the Music Player's Queue\n\n**Shuffle**(`/shuffle`)\nShuffles the songs in the queue\n\n**Remove**(`/remove`)\nRemoves the song from the queue\n\n**Loop**(`/loop`)\nLoops the currently playing song\n\n**Play**(`/play`)\n Plays a song!")
            await interaction.response.send_message(embed=e, ephemeral=True)
        if self.values[0] == "Levelling":
            e = discord.Embed(title="Levelling Commands",color=THEME, description="Currently Under Devlopment , Sorry for the inconvinience!")
            await interaction.response.send_message(embed=e, ephemeral=True) 


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown())


class Help(commands.Cog):
    """
    Benedict's Command Helper!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def help(self, ctx):
        """
        Get help regarding the working of a specific command!
        """
        await ctx.defer()
        e = discord.Embed(
            title="Benedict help",
            description="I'm a cool multi-purpose to help you manage your server better...",
            color=THEME)
        e.set_thumbnail(url = ctx.bot.user.avatar.url )
        e.set_author(
            name = ctx.author,
            icon_url = ctx.author.avatar.url)
        e.add_field(name="1) Moderation", value="```Commands to uphold the peace and integrity of the server```")
        e.add_field(name="2) Fun", value="```Commands to have some fun and relieve stress (or induce it)```")
        e.add_field(name="3) Bot commands", value="```Commands related to the bot, such as it's information etc```")
        e.add_field(name="4) Music", value="```Commands to for playing music with Benedict```")
        e.add_field(name="5) Levelling", value="```To check how Chit-Chatty you are!```")
        
        await ctx.respond(embed=e, view=DropdownView())


def setup(bot):
    bot.add_cog(Help(bot))
