import random
import string
import pyfiglet
import discord
from discord.ext import commands 
from discord.commands import Option
import aiohttp


from bot import TESTING_GUILDS, db
from bot import THEME
from bot.views import PollView


class Fun(commands.Cog):
    """
    Commands to have some fun and relieve stress (or induce it)
    """

    eight_ball_responses = [
        [
            "No.",
            "Nope.",
            "Highly Doubtful.",
            "Not a chance.",
            "Not possible.",
            "Don't count on it.",
        ],
        [
            "Yup",
            "Extremely Likely",
            "It is possible",
            "Very possibly.",
        ],
        ["I'm not sure", "Maybe get a second opinion", "Maybe"],
    ]

    emojify_symbols = {
        "0": ":zero:",
        "1": ":one:",
        "2": ":two:",
        "3": ":three:",
        "4": ":four:",
        "5": ":five:",
        "6": ":six:",
        "7": ":seven:",
        "8": ":eight:",
        "9": ":nine:",
        "!": ":exclamation:",
        "#": ":hash:",
        "?": ":question:",
        "*": ":asterisk:",
    }

    @commands.slash_command(guild_ids=TESTING_GUILDS)
    async def poll(
        self,
        ctx: discord.ApplicationContext,
        length: float,
        question: str,
        options: str,
    ):
        """
        Ask a question. The time must be in minutes. Separate each option with a comma (,).
        """
        await ctx.defer()

        length_lower_limit = 1  # 1 minute
        length_upper_limit = 7200  # 5 days
        option_limit = 10

        # Convert options in string format to list
        options = list(map(lambda x: x.strip(), options.split(",")))

        if length < length_lower_limit:
            await ctx.respond(
                f"The poll must last at least {length_lower_limit} minute."
            )
            return

        if length > length_upper_limit:
            await ctx.respond(
                f"The poll must last less than {length_upper_limit} minutes."
            )
            return

        if len(options) > option_limit:
            await ctx.respond(
                f"You can only have up to {option_limit} options."
            )
            return

        poll_embed = discord.Embed(
            title=question, color=THEME, description="**Options:**\n"
        )
        poll_embed.set_author(
            name=str(ctx.author), icon_url=ctx.author.avatar.url
        )
        # TODO: add an "Ends in..." message in the embed

        for i, option in enumerate(options):
            poll_embed.description += f"{i+1}) {option}\n"

        poll_view = PollView(options, length)
        interaction = await ctx.respond(embed=poll_embed, view=poll_view)
        await poll_view.wait()

        sorted_votes = sorted(
            list(poll_view.votes.items()), key=lambda x: x[1], reverse=True
        )

        poll_over_embed = discord.Embed(
            title="Poll Over", color=THEME, description="**Results:**\n"
        )
        poll_over_embed.set_author(
            name=str(ctx.author), icon_url=ctx.author.avatar.url
        )
        poll_over_embed.add_field(
            name="Total Votes", value=len(poll_view.voters)
        )
        poll_over_embed.add_field(name="Top Voted", value=sorted_votes[0][0])

        for i, (option, vote_count) in enumerate(sorted_votes):
            poll_over_embed.description += (
                f"{i+1}) {option} - {vote_count} votes\n"
            )

        await interaction.edit_original_message(
            embed=poll_over_embed, view=None
        )

    @commands.slash_command(guild_ids=TESTING_GUILDS)
    async def coinflip(self, ctx: discord.ApplicationContext):
        """
        Flip a coin
        """

        result = random.choice(["heads", "tails"])
        await ctx.respond(
            f"The coin has been flipped and resulted in **{result}**"
        )

    @commands.slash_command(guild_ids=TESTING_GUILDS)
    async def roll(self, ctx: discord.ApplicationContext, dice_count: int = 1):
        """
        Roll a dice
        """

        number = random.randint(dice_count, dice_count * 6)

        if dice_count > 1:
            await ctx.respond(
                f"You rolled **{dice_count} dice** and got a **{number}**"
            )
        else:
            await ctx.respond(f"You rolled a **{number}**")

    @commands.slash_command(guild_ids=TESTING_GUILDS)
    async def avatar(
        self, ctx: discord.ApplicationContext, member: discord.Member = None
    ):
        """
        Get somebody's Discord avatar
        """

        if not member:
            member = ctx.author

        av_embed = discord.Embed(title=f"{member}'s Avatar", color=THEME)
        av_embed.set_image(url=member.avatar.url)
        await ctx.respond(embed=av_embed)

    @commands.slash_command(guild_ids=TESTING_GUILDS)
    async def choose(self, ctx: commands.Context, options: str):
        """
        Let Sparta choose the best option for you. Separate the choices with a comma (,).
        """

        items = list(map(lambda x: x.strip(), options.split(",")))
        choice = random.choice(items)
        await ctx.respond(
            f"I choose {choice}",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.slash_command(name="8ball", guild_ids=TESTING_GUILDS)
    async def eight_ball(self, ctx: discord.ApplicationContext, question: str):
        """
        Call upon the powers of the all knowing magic 8Ball
        """

        group = random.choice(self.eight_ball_responses)
        response = random.choice(group)
        await ctx.respond(response)

    @commands.slash_command(guild_ids=TESTING_GUILDS)
    async def emojify(self, ctx: discord.ApplicationContext, sentence: str):
        """
        Turn a sentence into emojis
        """

        emojified_sentence = ""
        sentence = sentence.lower()

        for char in sentence:
            char_lower = char.lower()

            if char_lower in string.ascii_lowercase:
                emojified_sentence += f":regional_indicator_{char}:"
            elif char_lower in self.emojify_symbols:
                emojified_sentence += self.emojify_symbols[char_lower]
            elif char_lower == " ":
                emojified_sentence += "  "
            else:
                emojified_sentence += char

        await ctx.respond(emojified_sentence)

    @commands.slash_command(guild_ids=TESTING_GUILDS)
    async def ascii(self, ctx: discord.ApplicationContext, sentence: str):
        """
        Turn a sentence into cool ASCII art
        """

        ascii_text = pyfiglet.figlet_format(sentence)
        await ctx.respond(f"```{ascii_text}```")

    @commands.slash_command(guild_ids=TESTING_GUILDS)
    async def rps(self, ctx, pick: Option(str, "Choose your pick, Rock, Paper and Scissors", choices=["Rock", "Paper", "Scissors"])):
        """Play Rock Paper Scissors with Benedict's Appa !"""
        await ctx.defer()
        ai_rps = ["Rock", "Paper", "Scissors"]
        ai_pick = random.choice(ai_rps)
        if ai_pick == "Rock" and pick == "Scissors":
            await ctx.respond(f"**{ai_pick}**! You lose")
        if ai_pick == "Paper" and pick == "Rock":
            await ctx.respond(f"**{ai_pick}**! You lose")
        if ai_pick == "Scissors" and pick == "Paper":
            await ctx.respond(f"**{ai_pick}**! You lose")
        if pick == "Rock" and ai_pick == "Scissors":
            await ctx.respond(f"**{ai_pick}**! You win")
        if pick == "Paper" and ai_pick == "Rock":
            await ctx.respond(f"**{ai_pick}**! You win")
        if pick == "Scissors" and ai_pick == "Paper":
            await ctx.respond(f"**{ai_pick}**! You win")
        if pick == "Rock" and ai_pick == "Rock":
            await ctx.respond(f"**{ai_pick}**! Tie")
        if pick == "Scissors" and ai_pick == "Scissors":
            await ctx.respond(f"**{ai_pick}**! Tie")
        if pick == "Paper" and ai_pick == "Paper":
            await ctx.respond(f"**{ai_pick}**! Tie")

    @commands.slash_command(guild_ids=TESTING_GUILDS)
    async def password(self, ctx, amount: int = 2):
        """Generates a password"""
        if amount > 31:
            await ctx.send("The password must be 30 characters or lower", ephemeral=True)
            return
        try:
            nwpss = []
            lst = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                   'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '!', '@',
                   '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '{', ",", '}', ']',
                   '[', ';', ':', '<', '>', '?', '/', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '`', '~', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            for x in range(amount):
                newpass = random.choice(lst)
                nwpss.append(newpass)
            fnpss = ''.join(nwpss)

            e = discord.Embed(title="`Please check your direct messages!`", color=THEME)
            await ctx.respond(embed=e)
            e = discord.Embed(title="Password Generator", description=f"Your One-Time-Password: {fnpss}", color=THEME)
            await ctx.author.send(embed=e)
        except Exception as e:
            print(e)

    @commands.slash_command(name="serverinfo", guild_ids=TESTING_GUILDS)
    async def server_info(self, ctx: discord.ApplicationContext):
        """
        Get general information about the server
        """
        await ctx.defer()

        human_count = len(
            [member for member in ctx.guild.members if not member.bot]
        )
        bot_count = ctx.guild.member_count - human_count

        bene_embed = discord.Embed(
            title=f"{ctx.guild.name} Information", color=THEME
        )
        if icon := ctx.guild.icon:
            bene_embed.set_thumbnail(url=icon.url)

        bene_embed.add_field(
            name="Human Members", value=str(human_count), inline=False
        )
        bene_embed.add_field(
            name="Bot Members", value=str(bot_count), inline=False
        )
        bene_embed.add_field(
            name="Total Members",
            value=str(ctx.guild.member_count),
            inline=False,
        )
        bene_embed.add_field(
            name="Role Count", value=str(len(ctx.guild.roles)), inline=False
        )
        bene_embed.add_field(
            name="Server Owner", value=str(ctx.guild.owner), inline=False
        )
        bene_embed.add_field(name="Server ID", value=ctx.guild.id, inline=False)
        bene_embed.add_field(
            name="Server Age",
            value=f"Created on <t:{int(ctx.guild.created_at.timestamp())}>",
            inline=False,
        )

        await ctx.respond(embed=bene_embed)

    @commands.slash_command(name="memberinfo", guild_ids=TESTING_GUILDS)
    async def member_info(
        self, ctx: discord.ApplicationContext, member: discord.Member = None):
        """Displays Information of a User!"""
        await ctx.defer()
        if not member:
            member = ctx.author

        bene_embed = discord.Embed(title=f"{member} Information", color=THEME)
        if avatar := member.avatar:
            bene_embed.set_thumbnail(url=avatar.url)

        bene_embed.add_field(name="Member ID", value=member.id, inline=False)
        bene_embed.add_field(
            name="Joined Discord",
            value=f"<t:{int(member.created_at.timestamp())}>",
            inline=False,
        )
        bene_embed.add_field(
            name="Joined Server",
            value=f"<t:{int(member.joined_at.timestamp())}>",
            inline=False,
        )
        bene_embed.add_field(
            name="Highest Role", value=member.top_role.mention, inline=False
        )
        bene_embed.add_field(
            name="Bot?", value="Yes" if member.bot else "No", inline=False
        )
        await ctx.respond(embed = bene_embed)

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
    bot.add_cog(Fun())