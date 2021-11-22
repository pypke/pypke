import asyncpraw, requests, random, asyncio, aiohttp
import akinator
from bs4 import BeautifulSoup as bs4
from html import unescape
from asyncprawcore import exceptions as prawexc
from akinator.async_aki import Akinator

import discord
from discord.ext import commands
from dislash import ActionRow, Button, ButtonStyle

DAGPI_KEY = "MTYzNzE4MTAyMA.Ey9BeBE87uBOMt3epgNAp0IZlnnWzgIz.440c8c658a6169b3"

reddit = asyncpraw.Reddit(
    client_id="vUbW-MNqGXFHTw",
    client_secret="tfaL2Z5vI-AG-T0eb77h0-gLzPyWtw",
    username="Aman_Rajput",
    password="aman5368",
    user_agent="pythonpraw"
)
                    
aki = Akinator()

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='akinator', aliases=['aki'], description='Let akinator guess about thing/animal/character', hidden=True)
    @commands.cooldown(1, 8, commands.BucketType.user)
    async def akinator_command(self, ctx):
        embed = discord.Embed(
            title='Akinator',
            description="Is It A?",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url='https://i.imgur.com/n6km6ch.png')
        guess = ActionRow()
        guess.add_button(
                style=ButtonStyle.gray,
                label='Character'
        )
        guess.add_button(
                style=ButtonStyle.gray,
                label='Animal'
        )
        guess.add_button(
                style=ButtonStyle.gray,
                label='Object'
        )
        msg = await ctx.send(embed=embed, components=[guess])
        while True:
            # Try and except blocks to catch timeout and break
            def check(inter):
                return inter.message.id == msg.id and inter.author.id == ctx.author.id

            try:
                inter = await ctx.wait_for_button_click(check=check, timeout=20.0)
                            
                if (inter.clicked_button.label == 'Character'):
                    question = await aki.start_game(language='en', child_mode=True)
                    await inter.reply(content='Starting..', ephemeral=True)
                    break
                elif (inter.clicked_button.label == 'Animal'):
                    question = await aki.start_game(language='en_animals', child_mode=True)
                    await inter.reply(content='Starting..', ephemeral=True)
                    break
                else:
                    question = await aki.start_game(language='en_objects', child_mode=True)
                    await inter.reply(content='Starting..', ephemeral=True)
                    break                
                    
            except asyncio.TimeoutError:
                await msg.edit("Timeout Cancelling!!")
                break
            except:
                break

        q_no = 0
        while aki.progression <= 80:
            q_no += 1
            embed = discord.Embed(
                title='Akinator',
                description=f'Answer This Question In 20 seconds\n`{question}`\n\n**Total Question:** {q_no}\n**Progression:** {aki.progression}',
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url='https://i.imgur.com/n6km6ch.png')
            choices = ActionRow()
            choices.add_button(
                style=ButtonStyle.green,
                label='Yes'
            )
            choices.add_button(
                style=ButtonStyle.red,
                label='No'
            )
            choices.add_button(
                style=ButtonStyle.grey,
                label='Idk'
            )
            choices.add_button(
                style=ButtonStyle.grey,
                label='Probably'
            )
            choices.add_button(
                style=ButtonStyle.grey,
                label='Probably Not'
            )
            await msg.edit(embed=embed, components=[choices])
            while True:
                def check(inter):
                    return inter.message.id == msg.id and inter.author.id == ctx.author.id
                    
                try:
                    inter = await ctx.wait_for_button_click(check=check, timeout=20.0)
                    
                    if (inter.clicked_button.label) == 'Yes':
                        question = await aki.answer('yes')
                    elif (inter.clicked_button.label) == 'No':
                        question = await aki.answer('no')
                    elif (inter.clicked_button.label) == 'Idk':
                        question = await aki.answer('idk')
                    elif (inter.clicked_button.label) == 'Probably':
                        question = await aki.answer('p')
                    elif (inter.clicked_button.label) == 'Probably Not':
                        question = await aki.answer('pn')

                    if aki.progression > 80:
                        await aki.win()
                        embed = discord.Embed(
                            title=f"It's {aki.first_guess['name']}",
                            description=f"{aki.first_guess['description']}"
                        )
                        embed.set_image(url=aki.first_guess['absolute_picture_path'])
                        await inter.respond(type=7, embed=embed, components=[])
                        break

                    embed = discord.Embed(
                        title='Akinator',
                        description=f'Answer This Question In 20 seconds\n`{question}`\n\n**Total Question:** {q_no}\n**Progression:** {aki.progression}',
                        color=discord.Color.blue()
                    )
                    embed.set_thumbnail(url='https://i.imgur.com/n6km6ch.png')
                    choices = ActionRow()
                    choices.add_button(
                        style=ButtonStyle.green,
                        label='Yes'
                    )
                    choices.add_button(
                        style=ButtonStyle.red,
                        label='No'
                    )
                    choices.add_button(
                        style=ButtonStyle.grey,
                        label='Idk'
                    )
                    choices.add_button(
                        style=ButtonStyle.grey,
                        label='Probably'
                    )
                    choices.add_button(
                        style=ButtonStyle.grey,
                        label='Probably Not'
                    )

                    await inter.respond(type=7, embed=embed, components=[choices])            
                except asyncio.TimeoutError:
                    await msg.edit('Timeout, Try Again!')
                except:
                    break                                  

    @commands.command(name='trivia', description='Answer difficult questions.')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def trivia(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://opentdb.com/api.php?amount=1') as r:
                if 300 > r.status >= 200:
                    data = await r.json()
                    choices = [] 
                    incorrects = data['results'][0]['incorrect_answers'] # Three Incorrect Answers
                    choices = choices + incorrects # added to choices list
                
                    answer = data['results'][0]['correct_answer'] # Correct Answer
                    choices.append(answer) # added to choices list
                    if data['results'][0]['type'] != "boolean":
                        random.shuffle(choices) # Shuffled The Answers If Multiple choice
                    new_list = []
                    for choice in choices:
                        choice = unescape(choice)
                        new_list.append(choice)
                    choices = new_list

                    if data['results'][0]['difficulty'] == "easy":
                        timeout = 15.0
                    elif data['results'][0]['difficulty'] == "medium":
                        timeout = 12.0
                    else:
                        timeout = 10.0

                    question = data['results'][0]['question']
                    question = unescape(question)
                    embed = discord.Embed(
                        description=f"**{question}**\n`Answer this question within {round(timeout)}.`",
                        color=self.client.randcolor
                    )
                    embed.set_author(name=f'{ctx.author.name}\'s Trivia', icon_url=ctx.author.avatar.url)
                    embed.add_field(name='Difficulty', value=f"`{data['results'][0]['difficulty'].capitalize()}`")
                    embed.add_field(name='Category', value=f"`{data['results'][0]['category']}`")
                    choicebtn = ActionRow()
                    for choice in choices:
                        choicebtn.add_button(
                            label = choice,
                            style = ButtonStyle.blurple
                        )
                    msg = await ctx.send(embed=embed, components=[choicebtn])

                    while True:
                     # Try and except blocks to catch timeout and break
                        def check(inter):
                            return inter.message.id == msg.id and inter.author.id == ctx.author.id
                    
                        try:
                            inter = await ctx.wait_for_button_click(check=check, timeout=timeout)
                            
                            if (inter.clicked_button.label == answer):
                                new_btn = ActionRow()
                                for choice in choices:
                                    if choice in incorrects:
                                        new_btn.add_button(
                                            label = choice,
                                            style = ButtonStyle.grey,
                                            disabled=True
                                        )
                                    else:
                                        new_btn.add_button(
                                            label = answer,
                                            style = ButtonStyle.green,
                                            disabled=True
                                        )
                                await inter.reply(type=7, content=f"Yes, The correct answer was `{answer}`! Well Done.", embed=embed, components=[new_btn])
                                break
                            else:
                                new_btn = ActionRow()
                                for choice in choices:
                                    if choice == inter.clicked_button.label:
                                        new_btn.add_button(
                                            label = choice,
                                            style = ButtonStyle.red,
                                            disabled=True
                                        )
                                    elif choice in incorrects:
                                        new_btn.add_button(
                                            label = choice,
                                            style = ButtonStyle.grey,
                                            disabled=True
                                        )
                                    else:
                                        new_btn.add_button(
                                            label = answer,
                                            style = ButtonStyle.green,
                                            disabled=True
                                        )
                                await inter.reply(type=7, content=f"No dumbo, The correct answer was `{answer}`!", embed=embed, components=[new_btn])
                                break

                        except asyncio.TimeoutError:
                            new_btn = ActionRow()
                            for choice in choices:
                                if choice in incorrects:
                                    new_btn.add_button(
                                        label = choice,
                                        style = ButtonStyle.grey,
                                        disabled=True
                                    )
                                else:
                                    new_btn.add_button(
                                        label = answer,
                                        style = ButtonStyle.green,
                                        disabled=True
                                    )
                            await msg.edit(content=f"Timeout.... Thought you wanted to play trivia, The correct answer was `{answer}`!", embed=embed, components=[new_btn])
                            break
                        except:
                            break

    @commands.command(
        name="wouldyourather",
        description="Would you rather use this command or solve a quadratic equation?.",
        aliases=["wyr"]
    )          
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def wyr_command(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://either.io/') as r:
                if r.status == 200:
                    text = await r.text()
                    soup = bs4(text, 'lxml')
                    choices = []
                    for choice in soup.find_all('span', {'class': 'option-text'}):
                        choices.append(choice.text)
                        
                    embed = discord.Embed(color=self.client.randcolor)
                    embed.set_author(name='Would You Rather...', url='https://either.io', )
                    embed.add_field(name='Either...', value=f':regional_indicator_a: {choices[0]}\n\uFEFF', inline=False)
                    embed.add_field(name='Or...', value=f':regional_indicator_b: {choices[1]}', inline=False)
                    msg = await ctx.send(embed=embed)
                    await msg.add_reaction("🇦")
                    await msg.add_reaction("🇧")
                    
    @commands.command(name="joke", description="This command sends a random joke.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def joke(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Dark,Pun,Spooky?blacklistFlags=nsfw,religious,political,racist,sexist,explicit') as r:
                if 300 > r.status >= 200:
                    data = await r.json()
                    joke = discord.Embed(
                        title=f"{data['category']} Joke",
                        color=random.choice(self.client.color_list)
                    )
                    if data['type'] == "single":
                        joke.description = data['joke']
                        await ctx.send(embed=joke)
                    if data['type'] == "twopart":
                        joke.description = f"{data['setup']}"
                        msg = await ctx.send(embed=joke)
                        await asyncio.sleep(5)
                        joke.description = f"{data['setup']}\n{data['delivery']}"
                        await msg.edit(embed=joke)               
                else:
                    await ctx.send("Something is wrong. I can't find jokes for you right now, Try Later!")   

    @commands.command(name="pokedex", description="This command sends info about a pokemon.", aliases=['dex'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pokedex(self, ctx, *, pokemon: str = None):
        if not pokemon:
            return await ctx.send(
                f"You need to provide the pokemon name `{ctx.prefix}pokedex <pokemon-name>`"
            )

        resp = requests.get(f"https://some-random-api.ml/pokedex?pokemon={pokemon}")
        if 300 > resp.status_code >= 200:
            data = resp.json()
        else:
            return await ctx.send(
                f"Something is wrong. I can't find dex entry for {pokemon} for you right now, Try Later!"
            )

        title = f"#{data['id']} - {data['name'].title()}"
        description = data['description'].capitalize()
        sprites = data['sprites']['animated']
        types = " "
        for ty in data['type']:
            types = types + f"{ty}\n"
        gender = " "
        for ty in data['gender']:
            gender = gender + f"{ty.title()}\n"
        appearance = f"**Height**: {data['height']}\n**Weight**: {data['weight']}\n**Gender**:\n{gender}\n"
        base_stats = f"**HP**: {data['stats']['hp']}\n**Attack**: {data['stats']['attack']}\n**Defense**: {data['stats']['defense']}\n**Sp. Atk**: {data['stats']['sp_atk']}\n**Sp. Def**: {data['stats']['sp_def']}\n**Speed**: {data['stats']['speed']}\n**Total**: {data['stats']['total']}"
        embed = discord.Embed(
            title=title,
            description=description,
            color=0x2f3136
        )
        embed.add_field(name="Types", value=types)
        embed.add_field(name="Appearance", value=appearance)
        embed.add_field(name="Base Stats", value=base_stats)
        embed.set_thumbnail(url=sprites)
        embed.set_footer(text="© The Pokémon Company")
        await ctx.send(embed=embed)

    @commands.command(
        name="whosthatpokemon",
        description="Who's That Pokémon?",
        aliases=["wtp"]
    )
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def wtp_command(self, ctx):
        headers = {
        'Authorization': DAGPI_KEY
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get('https://api.dagpi.xyz/data/wtp') as r:
                if 300 > r.status >= 200:
                    data = await r.json()
                else:
                    return await ctx.send("Can't seem to fetch who's that pokemon right now!")
                
                answer = data['Data']['name']
                    
                answer_img = data['answer']
                question_img = data['question']

                embed = discord.Embed(
                    title="Who's That Pokemon?",
                    color=self.client.colors["red"]
                )
                embed.set_image(url=question_img)
                embed.set_footer(text="© The Pokémon Company")
                msg = await ctx.send(embed=embed)

                while True:
                    def check(message):
                        return ctx.channel.id == message.channel.id and not message.author.bot and not message.content.startswith(ctx.prefix)

                    try:
                        message = await self.client.wait_for("message", check=check, timeout=30.0)

                        if message.content.lower() == answer.lower():
                            await ctx.send(f"{message.author.mention}, Correct!!")
                            embed = discord.Embed(
                                title=f"It's {answer}!",
                                color=self.client.colors["red"]
                            )
                            embed.set_image(url=answer_img)
                            embed.set_footer(text="© The Pokémon Company")
                            await msg.edit(embed=embed)
                            break
                        elif "end" in message.content.lower():
                            embed = discord.Embed(
                                title=f"It's {answer}!",
                                color=self.client.colors["red"]
                            )
                            embed.set_image(url=answer_img)
                            embed.set_footer(text="© The Pokémon Company")
                            await msg.edit(embed=embed)
                            break
                        else:
                            await ctx.send("Try again! Reply with `end` to stop guessing.", delete_after=6)

                    except asyncio.TimeoutError:
                        embed = discord.Embed(
                            title=f"It's {answer}!",
                            color=self.client.colors["red"]
                        )
                        embed.set_image(url=answer_img)
                        embed.set_footer(text="© The Pokémon Company")
                        await msg.edit(content="Timeout!", embed=embed)
                        break

                    except discord.HTTPException:
                        pass

    @commands.command(
        name="reddit",
        description="This command sends a random post from given subreddit."
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def reddit_command(self, ctx, subreddit: str):
        try:
            subreddit = await reddit.subreddit(subreddit, fetch=True)
        except prawexc.Forbidden:
            return await ctx.send("Sorry, The subreddit you are requesting is not currently available.")
        except prawexc.NotFound:
            return await ctx.send("Sorry, This subreddit doesn't exist.")

        all_subs = []

        if subreddit.over18:
            if not ctx.channel.is_nsfw():
                return await ctx.send("The subreddit you are requesting is NSFW. So, This channel needs to be marked NSFW.")

        async for submission in subreddit.hot(limit=100):
            if not submission.locked and not submission.stickied:
                all_subs.append(submission)

        random_sub = random.choice(all_subs)

        name = random_sub.title
        description = random_sub.selftext if len(random_sub.selftext) < 2001 else ""
        url = random_sub.url
        vote = random_sub.score
        comments = random_sub.num_comments
        post = random_sub.permalink

        em = discord.Embed(
            title=name,
            description=description,
            color=self.client.randcolor,
            url=f"https://reddit.com{post}"
        )
        em.set_image(url=url)
        em.set_footer(text=f"👍🏻 {vote} | 💬 {comments} | r/{subreddit.display_name}")
        await ctx.send(embed=em)

    @commands.command(
        name="meme",
        description="This command sends a random meme from reddit."
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def meme(self, ctx):
        subreddit = await reddit.subreddit(random.choice(["memes", "dankmemes", "wholesomemes"]))
        all_subs = []

        async for submission in subreddit.hot(limit=100):
            if not submission.locked and not submission.stickied:
                all_subs.append(submission)

        random_sub = random.choice(all_subs)

        name = random_sub.title
        url = random_sub.url
        vote = random_sub.score
        comments = random_sub.num_comments
        post = random_sub.permalink

        em = discord.Embed(
            title=name,
            color=self.client.randcolor,
            url=f"https://reddit.com{post}"
        )
        em.set_image(url=url)
        em.set_footer(text=f"👍🏻 {vote} | 💬 {comments}")

        await ctx.send(embed=em)

    @commands.command(
        name="cat",
        description="This Sends A Random Cat Picture",
        aliases=['cats']
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cat(self, ctx):
        subreddit = await reddit.subreddit("catpictures")
        all_subs = []

        async for submission in subreddit.hot(limit=100):
            if not submission.locked and not submission.stickied:
                all_subs.append(submission)

        random_sub = random.choice(all_subs)
        url = random_sub.url

        em = discord.Embed(
            title=":heart_eyes_cat: Meow",
            color=random.choice(self.client.color_list)
        )
        em.set_image(url=url)
        await ctx.send(embed=em)

    @commands.command(
        name="dog",
        description="This Sends A Random Dog Picture",
        aliases=['dogs']
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dog(self, ctx, url=None):
        subreddit = await reddit.subreddit("dogpictures")
        all_subs = []
        
        async for submission in subreddit.hot(limit=100):
            if not submission.locked and not submission.stickied:
                all_subs.append(submission)

        random_sub = random.choice(all_subs)
        url = random_sub.url

        em = discord.Embed(
            title=":dog: Woof",
            color=random.choice(self.client.color_list)
        )
        em.set_image(url=url)

        await ctx.send(embed=em)

    @commands.command(
        name="8ball",
        description="This command answers a question like a 8Ball",
        usage="<question>"
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def _8ball(self, ctx, *, question):
        responses = [
            "It is certain", "It is decidedly so", "Without a doubt",
            "Yes, definitely", "You may rely on it", "As I see it, yes",
            "Most likely", "Outlook good", "Yes", "Signs point to yes",
            "Reply hazy try again", "Ask again later",
            "Better not tell you now", "Cannot predict now",
            "Concentrate and ask again", "Don't count on it", "My reply is no",
            "My sources say no", "Outlook not so good", "Very doubtful"
        ]

        if question == None:
            await ctx.send("Question is a required argument which is missing!!")
            return

        embed = discord.Embed(title=":8ball:| **8Ball**",
                              color=discord.Color.random())
        embed.add_field(name="**Question**:",
                        value=f"{question}",
                        inline=False)
        embed.add_field(name="**Answer**:",
                        value=f"{random.choice(responses)}",
                        inline=False)
        embed.set_footer(text=f"Asked By {ctx.author.name}",
                         icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(
        name="choose",
        description="This command helps you to choose between things.",
        aliases=["choices"]
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def choose_command(self, ctx, *choices):
        if len(choices) > 10:
            return await ctx.reply("Jeez, Give me less choices! Max 10.")
        elif len(choices) < 2:
            return await ctx.reply("Give me atleast 2 choices to choose from.")

        choice = random.choice(choices)
        choice = discord.utils.escape_mentions(choice)
        await ctx.send(f"I choose {choice}.")

    @commands.command(
        name="pat",
        description="This command pats a user on back."
    )
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pat(self, ctx, member: discord.Member):
        if member == None:
            await ctx.send(
                "There is no one to pat here")
            return
        if member == ctx.author:
            await ctx.send("You can't pat yourself find someone!!")
            return

        pat_gif = [
            'https://media.giphy.com/media/5tmRHwTlHAA9WkVxTU/giphy.gif',
            'https://images-ext-1.discordapp.net/external/5gTEJjgFQmEsfinxmX8eyo8-fiCOW7e-DA_J9KNxh5Q/https/cdn.nekos.life/pat/pat_015.gif',
            'https://media.giphy.com/media/N0CIxcyPLputW/giphy.gif',
            'https://media.giphy.com/media/Lb3vIJjaSIQWA/giphy.gif'
        ]

        random_pat = random.choice(pat_gif)
        embed = discord.Embed(title=f'{ctx.author.name} pats {member.name}',
                              color=discord.Color.random())
        embed.set_image(url=random_pat)
        await ctx.send(embed=embed)

    @commands.command(
        name="kill",
        description="This command kills a user for you! Oops.",
        hidden=True
    )
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def kill(self, ctx, member: discord.Member):
        if member == None:
            await ctx.send("Who do you wanna kill man?")
            return
        if member == ctx.author:
            await ctx.send("You can't kill yourself mate! ;-;")
            return
        if member.bot:
            await ctx.send("Why are you trying to kill my fellow mate??")
            return

        kill_text = [
            'died of hunger', 'died with getting squashed by anvil',
            'died after seeing cringy fortnite',
            'died after seeing the mirror',
            'died while writing the sucide note', 'died of POG!',
            'died after seeing the power of Pypke The Cat...'
        ]

        random_kill = random.choice(kill_text)
        await ctx.send(f"{member} {random_kill}")

    @commands.command(hidden=True)
    @commands.cooldown(1, 18000, commands.BucketType.user)
    async def egg(self, ctx):
        await ctx.send("This Is An Easter Egg!!", delete_after=2)

    @commands.command(
        name="hack",
        description="This command can hack a user!! THIS IS NOT A JOKE.",
        usage="<user>",
        hidden=True
    )
    @commands.guild_only()
    @commands.cooldown(1, 9, commands.BucketType.user)
    async def hack(self, ctx, member: discord.Member = None):
        if member == None:
            await ctx.send("Who do you wanna hack?")
            return
        if member == ctx.author:
            await ctx.send("You can't hack yourself! ;-;")
            return
        if member.bot:
            await ctx.send("Why are you trying to hack a bot??")
            return

        ip = [
            '120.10.12.13', '120.10.20.11', '170.18.15.23', '150.23.16.13',
            '192.158.1.38', '255.158.255.38', '192.158.101.101'
        ]
        email = [
            f'{member.display_name}_smallpp.com',
            f'{member.display_name}_PlayzMinecraft@gmail.com',
            f'{member.display_name}_xxx@hotmail.com', 'poggers@games.com',
            'heck@theworld.org', 'why_not@lol.com', 'flex@gmail.com'
        ]
        password = [
            'peepoopeepoo', '12345678', 'poggers', 'PA55W0RD', 'ilovemom',
            'dreamnoob'
        ]

        random_ip = random.choice(ip)
        random_email = random.choice(email)
        random_password = random.choice(password)
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
        await msg1.edit(
            content=f"Email: `{random_email}`\nPassword: `{random_password}`")
        await asyncio.sleep(1.5)
        await msg1.edit(content="Report Discord For Breaking TOS....")
        await asyncio.sleep(1.5)
        await msg1.edit(content="**If You See This You Are So Cool**")
        await asyncio.sleep(0.2)
        await msg1.edit(content=f"Finished Hacking {member.name}!!")
        await ctx.send("The *totally* real and dangerous hacking is complete!!"
                       )


def setup(client):
    client.add_cog(Fun(client))
