import discord
from discord.ext import commands
import praw
import random
import asyncio

reddit = praw.Reddit(client_id="vUbW-MNqGXFHTw",
                     client_secret="tfaL2Z5vI-AG-T0eb77h0-gLzPyWtw",
                     username="Aman_Rajput",
                     password="aman5368",
                     user_agent="pythonpraw",
                     check_for_async=False)

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="joke", description="This Command Sends A Random Joke")
    @commands.guild_only()
    async def joke(self, ctx):
        subreddit = reddit.subreddit("jokes")
        all_subs = []

        hot = subreddit.hot(limit=100)

        for submission in hot:
            all_subs.append(submission)

        random_sub = random.choice(all_subs)

        name = random_sub.title
        text = random_sub.name

        em = discord.Embed(title = name, value = text, color=discord.Color.random())

        await ctx.send(embed=em)

    @commands.command(name="meme", description="This command sends a random meme from the subreddit `r/memes`")
    async def meme(self, ctx):
        subreddit = reddit.subreddit("memes")
        all_subs = []

        hot = subreddit.hot(limit=100)

        for submission in hot:
            all_subs.append(submission)

        random_sub = random.choice(all_subs)

        name = random_sub.title
        url = random_sub.url
        vote = random_sub.score
        comments = random_sub.num_comments
        post = random_sub.permalink

        em = discord.Embed(title = name, color=random.choice(self.client.color_list), url=f"https://reddit.com/{post}")
        em.set_image(url = url)
        em.set_footer(text=f"👍🏻 {vote} | 💬 {comments}")

        await ctx.send(embed=em)

    @commands.command(name="cat", description="This Sends A Random Cat Picture", aliases=['cats'])
    async def cat(self, ctx):
        subreddit = reddit.subreddit("catpictures")
        all_subs = []

        hot = subreddit.hot(limit=100)

        for submission in hot:
            all_subs.append(submission)

        random_sub = random.choice(all_subs)

        url = random_sub.url

        em = discord.Embed(title = ":heart_eyes_cat:Meow", color=random.choice(self.client.color_list))

        em.set_image(url = url)

        await ctx.send(embed = em)

    @commands.command(name="dog", description="This Sends A Random Dog Picture", aliases=['dogs'])
    async def dog(self, ctx, url=None):
        subreddit = reddit.subreddit("dogpictures")
        all_subs = []

        hot = subreddit.hot(limit=100)

        for submission in hot:
            all_subs.append(submission)

        random_sub = random.choice(all_subs)

        url = random_sub.url
        
        em = discord.Embed(title = ":dog:Woof", color=random.choice(self.client.color_list))
        em.set_image(url = url)

        await ctx.send(embed=em)

    @commands.command(name="dankmeme", description="This commands sends a random meme from subreddit `r/dankmemes`.", aliases=['dmeme','deme'])
    async def dankmeme(self, ctx):
        subreddit = reddit.subreddit("dankmemes")
        all_subs = []

        hot = subreddit.hot(limit=100)

        for submission in hot:
            all_subs.append(submission)

        random_sub = random.choice(all_subs)

        name = random_sub.title
        url = random_sub.url
        vote = random_sub.score
        comments = random_sub.num_comments
        post = random_sub.permalink

        em = discord.Embed(title = name, color=random.choice(self.client.color_list), url=f"https://reddit.com/{post}")
        em.set_image(url = url)
        em.set_footer(text=f"👍🏻{vote} | 💬{comments}")

        await ctx.send(embed=em)

    @commands.command(name="8ball", description="This command answers a question like a 8Ball", usage="<question>")
    async def _8ball(self, ctx, *, question=None):
        responses = ["It is certain",
                     "It is decidedly so",
                     "Without a doubt",
                     "Yes, definitely",
                     "You may rely on it",
                     "As I see it, yes",
                     "Most likely",
                     "Outlook good",
                     "Yes",
                     "Signs point to yes",
                     "Reply hazy try again",
                     "Ask again later",
                     "Better not tell you now",
                     "Cannot predict now",
                     "Concentrate and ask again",
                     "Don't count on it",
                     "My reply is no",
                     "My sources say no",
                     "Outlook not so good",
                     "Very doubtful"]
                                                        
        if question==None:
          await ctx.send("Question is a required argument which is missing!!")
          return
        embed=discord.Embed(title=":8ball:| **8Ball**", color=discord.Color.random())
        embed.add_field(name="**Question**:", value=f"{question}", inline=False)
        embed.add_field(name="**Answer**:", value=f"{random.choice(responses)}", inline=False)
        embed.set_footer(text=f"Asked By {ctx.author.name}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="pat", description="This command pats a user on back.", usage="<user>")
    @commands.guild_only()
    async def pat(self, ctx, member:discord.Member=None):
            if member==None:
                await ctx.send("There is no one to pat here it's just you and me ;-;")
                return
            if member==ctx.author:
                await ctx.send("You can't pat yourself find someone!!")
                return

            pat_gif=['https://media.giphy.com/media/5tmRHwTlHAA9WkVxTU/giphy.gif', 'https://images-ext-1.discordapp.net/external/5gTEJjgFQmEsfinxmX8eyo8-fiCOW7e-DA_J9KNxh5Q/https/cdn.nekos.life/pat/pat_015.gif', 'https://media.giphy.com/media/N0CIxcyPLputW/giphy.gif', 'https://media.giphy.com/media/Lb3vIJjaSIQWA/giphy.gif']

            random_pat = random.choice(pat_gif)
            embed = discord.Embed(title=f'{ctx.author.name} pats {member.name}', color=discord.Color.random())
            embed.set_image(url=random_pat)
            await ctx.send(embed=embed)

    @commands.command(name="kill", description="This command kills a user for you! Oops.", usage="<user>")
    @commands.guild_only()
    async def kill(self, ctx, member:discord.Member=None):
        if member==None:
            await ctx.send("Who do you wanna kill man?")
            return
        if member==ctx.author:
            await ctx.send("You can't kill yourself mate! ;-;")
            return
        if member.bot:
            await ctx.send("Why are you trying to kill my fellow mate??")
            return
        
        kill_text=['died of hunger', 'died with getting squashed by anvil', 'died after seeing cringy fortnite', 'died after seeing the mirror', 'died while writing the sucide note', 'died of POG!', 'died after seeing the power of Pypke The Cat...']

        random_kill=random.choice(kill_text)
        await ctx.send(f"{member} {random_kill}")

    @commands.command()
    async def egg(self, ctx):
        await ctx.send("This Is An Easter Egg!!", delete_after=2)

    @commands.command(name="hack", description="This command can hack a user!! THIS IS NOT A JOKE.", usage="<user>")
    @commands.guild_only()
    async def hack(self, ctx, member:discord.Member=None):
        if member==None:
            await ctx.send("Who do you wanna hack?")
            return
        if member==ctx.author:
            await ctx.send("You can't hack yourself! ;-;")
            return
        if member.bot:
            await ctx.send("Why are you trying to hack a bot??")
            return

        ip=['120.10.12.13', '120.10.20.11', '170.18.15.23', '150.23.16.13', '192.158.1.38', '255.158.255.38', '192.158.101.101']
        email=[f'{member.display_name}_smallpp.com', f'{member.display_name}_PlayzMinecraft@gmail.com', f'{member.display_name}_xxx@hotmail.com', 'poggers@games.com', 'heck@theworld.org', 'why_not@lol.com', 'flex@gmail.com']
        password=['peepoopeepoo', '12345678', 'poggers', 'PA55W0RD', 'ilovemom', 'dreamnoob']

        random_ip=random.choice(ip)
        random_email=random.choice(email)
        random_password=random.choice(password)
        msg1 = await ctx.send(f"Hacking {member.name} now!")
        await asyncio.sleep(1.5)
        await msg1.edit(content="Finding IP address..")
        await asyncio.sleep(1.5)
        await msg1.edit(content=f"IP Address Hacked: {random_ip}")
        await asyncio.sleep(1.5)
        await msg1.edit(content="Stealing Their Data...")
        await asyncio.sleep(1.5)
        await msg1.edit(content="Data Stoled...")
        await asyncio.sleep(1.5)
        await msg1.edit(content="Selling Data To Government!!")
        await asyncio.sleep(1.5)
        await msg1.edit(content="Trying To Hack Their Password...")
        await asyncio.sleep(1.5)
        await msg1.edit(content="Bypassing 2FA Authentication...")
        await asyncio.sleep(1.5)
        await msg1.edit(content=f"Email: `{random_email}`\nPassword: `{random_password}`")
        await asyncio.sleep(1.5)
        await msg1.edit(content="Report Discord For Breaking TOS....")
        await asyncio.sleep(1.5)
        await msg1.edit(content="**If You See This You Are So Cool**")
        await asyncio.sleep(0.2)
        await msg1.edit(content=f"Finished Hacking {member.name}!!")
        await ctx.send("The *totally* real and dangerous hacking is complete!!")

def setup(client):
    client.add_cog(Fun(client))