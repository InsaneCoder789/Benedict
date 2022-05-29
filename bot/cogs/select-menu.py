import email
import discord
import traceback
import random
from discord.ext import commands

class Dropdown(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(
                label="Moderation", description="Commands to uphold the peace and integrity of the server", emoji="⚙️"
            ),
            discord.SelectOption(
                label="Fun", description="Commands to have some fun and relieve stress (or induce it)", emoji="🎊"
            ),
            discord.SelectOption(
                label="Bot Commands", description="Commands related to the bot, such as it's information etc", emoji="📜"
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
            e = discord.Embed(title="Moderation Commands", color=discord.Color.blue(), description="**Clear**(`/clear`)\nClears messages in a channel\n\n**ClearCap**(`/clearcap`) \n Set the maximum numbers of messages to be cleared\n\n**Slowmode**(`/slowmode`)\nAdd slowmode delay in the current channel\n\n**Ban**(`/ban`)\nPermanently remove a person from the server\n\n**Unban**(`/unban`)\nUnban a person from the server\n\n**Kick**(`/kick`)\nRemove a person from the server\n\n**Warn**(`/warn`)\nWarn a member for doing something they weren't supposed to\n\n**Infractions**(`/infractions`)\nSee all the infractions in this server\n\n**ClearInfractions**(`/clearinfractions`)\nClear somebody's infractions in the current server\n\n**Nuke**(`/nuke`)\nNuke is an easy way of deleting all messages in a channel!\n\n**ServerInfo**(`/serverinfo`)\nGet general information about the server\n\n**UserInfo**(`/memberinfo`)\nGet general information about a member")
            await interaction.response.send_message(embed=e, ephemeral=True)
        if self.values[0] == "Fun":
            e = discord.Embed(title="Fun Commands", color=discord.Color.blue(), description="**Flip**(`/coinflip`)\nFlip a coin\n\n**RockPaperScissors**(`/rps`)\nPlay Rock Paper Scissors with Edith!\n\n**Emojify**(`/emojify`)\nTurn a sentence into emojis\n\n**Password**(`/password`)\nGenerate a password\n\n**AI**(`/ai`)\nAsk the AI a question!\n\n**Joke**(`/joke`)\nGives you a joke\n\n**ASCII**(`/ascii`)\nTurn a sentence into cool ASCII art\n\n**8Ball**(`/8ball`)\nCall upon the powers of the all knowning magic 8Ball\n\n**Remind**(`/remind`)\nSet a reminder. Example: /remind 1d 2h 12m 5s make lunch (All time options are not required)\n\n**AFK**(`/afk`)\nSets your AFK status\n\n**UnAFK**(`/unafk`)\nUnset your AFK status\n\n**Roll**(`/roll`)\nRoll a dice\n\n**Choose**(`/choose`)\nLet Edith choose the best option for you\n\n**YouTube**(`/youtube`)\nSearch for YouTube videos")
            await interaction.response.send_message(embed=e, ephemeral=True)
        if self.values[0] == "Bot Commands":
            e = discord.Embed(title="Bot Commands", color=discord.Color.blue(), description="**Bot Information**(`/botinfo`)\nShows information about Edith\n\n**Uptime**(`/uptime`)\nShows the time the bot has been online for\n\n**Ping**(`/ping`)\nCheck the bots ping\n\n**Invite**(`/invite`)\nGives you a link to invite Edith\n\n**Vote**(`/vote`)\nGives you a link to vote for the bot(please do it!)")
            await interaction.response.send_message(embed=e, ephemeral=True)


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown())

class Help(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.slash_command()
    async def help(self, ctx):
        await ctx.defer()
        e = discord.Embed(title="Benedict help", description="I'm a cool multi-purpose to help you manage your server better...", color=discord.Color.blue())
        e.add_field(name="1) Moderation", value="```Commands to uphold the peace and integrity of the server```")
        e.add_field(name="2) Fun", value="```Commands to have some fun and relieve stress (or induce it)```")
        e.add_field(name="3) Bot commands", value="```Commands related to the bot, such as it's information etc```")
        await ctx.respond(embed=e, view=DropdownView())

def setup(bot):
    bot.add_cog(Help(bot))