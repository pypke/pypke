import asyncpraw
import requests
import random
import asyncio
import aiohttp
import akinator
from bs4 import BeautifulSoup as bs4
from html import unescape
from asyncprawcore import exceptions as prawexc
from akinator.async_aki import Akinator
from typing import Optional

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


class Fun(commands.Cog, description="All the commands that you can have fun with."):
    def __init__(self, client):
        self.client = client

    async def rps_winner(self, player1_choice, player2_choice):
        if player2_choice == player1_choice:
            return "Draw"

        if player2_choice == "rock" and player1_choice == "scissors":
            return "P2"
        elif player2_choice == "paper" and player1_choice == "rock":
            return "P2"
        elif player2_choice == "scissors" and player1_choice == "paper":
            return "P2"
        else:
            return "P1"
        
    async def make_move(self, ctx, msg, player):
        while True:
            def check(inter):
                return inter.message.id == msg.id

            try:
                inter = await ctx.wait_for_button_click(check=check, timeout=20.0)

                if inter.author.id != player.id:
                    await inter.respond("This is not your turn.", ephemeral=True)
                else:
                    await inter.respond(type=6)
                    return inter.clicked_button.custom_id

            except asyncio.TimeoutError:
                embed = discord.Embed(
                    title="Rock Paper Scissors",
                    description="You took so long.",
                    color=self.client.colors["og_blurple"]
                )
                await msg.edit(f"{player.mention}, Game Over!", embed=embed, components=[])
                break

    @commands.command(
        name="coinflip",
        description="Flips a coin.",
        aliases=["coin"]
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def coinflip_command(self, ctx):
        sides = ["Heads", "Tails"]
        await ctx.send(f"It landed on {random.choice(sides)}!!")

    @commands.command(
        name="rps",
        description="Play rock paper scissors with friends or with me.",
    )
    @commands.cooldown(1, 8, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.user)
    async def rps_command(self, ctx, member: Optional[discord.Member], rounds: Optional[int] = 1):
        if rounds > 11:
            return await ctx.send(f"Yo, maximum rounds is capped at 11. Cause {rounds} would be too much :P")
        if member.bot:
            return await ctx.send(f"You can't play with other bots. Use `{ctx.prefix}rps [rounds]` to play with me.")
        if ctx.author.id == member.id:
            return await ctx.send(f"Lol, you can't play with yourself.")

        rps_btns = ActionRow(
            Button(
                style=ButtonStyle.gray,
                label="Rock",
                emoji="<:rock:924544402595135538>",
                custom_id="rock"
            ),
            Button(
                style=ButtonStyle.gray,
                label="Paper",
                emoji="<:paper:924544488590962718>",
                custom_id="paper"
            ),
            Button(
                style=ButtonStyle.gray,
                label="Scissors",
                emoji="<:scissors:924544545096626176>",
                custom_id="scissors"
            )
        )
        embed = discord.Embed(
            title="Rock Paper Scissors",
            description="Choose your move",
            color=self.client.colors["og_blurple"]
        )
        msg = await ctx.send(f"Starting", embed=embed, components=[rps_btns])

        i = 1
        player1_points = 0
        player2_points = 0
        draws = 0

        if member:
            player1 = random.choice([member, ctx.author])
            player2 = ctx.author if player1 == member else member
        else:
            player1 = ctx.author
            player2 = self.client.user

        while i <= rounds:
            if member:
                await msg.edit(f"{player1.mention}'s Turn | `Round {i}`", embed=embed, components=[rps_btns])
                player1_move = await self.make_move(ctx, msg, player1)

                if not player1_move:
                    return
                
                await msg.edit(f"{player2.mention}'s Turn | `Round {i}`", embed=embed, components=[rps_btns])
                player2_move = await self.make_move(ctx, msg, player2)
                
                winner = await self.rps_winner(player1_move, player2_move)
                if winner == "Draw":
                    draws += 1
                    point_given_to = None
                elif winner == "P2":
                    player2_points += 1
                    point_given_to = player2.name
                elif winner == "P1":
                    player1_points += 1
                    point_given_to = player1.name
                
                if point_given_to:
                    await ctx.send(
                        f"`{player1.name}` chose {player1_move} & `{player2.name}` chose {player2_move}!\n+1 point to `{point_given_to}`!",
                        delete_after=12
                    )
                else:
                    await ctx.send(f"Draw between `{player1.name}` & `{player2.name}`!", delete_after=10)
                i += 1
                
            else: # if there is no player 2
                await msg.edit(f"{player1.mention}'s Turn | `Round {i}`", embed=embed, components=[rps_btns])
                player1_move = await self.make_move(ctx, msg, player1)

                if not player1_move:
                    return 
                
                choices = ["rock", "paper", "scissors"]
                player2_move = random.choice(choices)
                
                winner = await self.rps_winner(player1_move, player2_move)
                if winner == "Draw":
                    draws += 1
                    point_given_to = None
                elif winner == "P2":
                    player2_points += 1
                    point_given_to = player2.name
                elif winner == "P1":
                    player1_points += 1
                    point_given_to = player1.name

                if point_given_to:
                    await ctx.send(
                        f"`{player1.name}` chose {player1_move} & `{player2.name}` chose {player2_move}!\n+1 point to `{point_given_to}`!",
                        delete_after=12
                    )
                else:
                    await ctx.send(f"Draw between `{player1.name}` & `{player2.name}`!", delete_after=10)
                i += 1
        
        if player1_points == player2_points:
            embed = discord.Embed(
                title="Draw!",
                description=f"{player1.name}: `{player1_points} points`\n{player2.name}: `{player2_points} points`\nDraws: `{draws}`",
                color=self.client.colors["og_blurple"]
            )
            await msg.edit(content=None, embed=embed)
        else:
            embed = discord.Embed(
                title=f"{player1.name if player1_points > player2_points else player2.name} Wins!",
                description=f"{player1.name}: `{player1_points} points`\n{player2.name}: `{player2_points} points`\nDraws: `{draws}`",
                color=self.client.colors["og_blurple"]
            )
            await msg.edit(content=None, embed=embed)

    @commands.command(name='akinator', aliases=['aki'], description='Akinator guesses about object/animal/character.', hidden=True)
    @commands.bot_has_permissions(read_messages=True, read_message_history=True)
    @commands.cooldown(1, 8, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.user)
    async def akinator_command(self, ctx):
        embed = discord.Embed(
            description="Can you specify is it a?",
            color=self.client.colors["purple"]
        )
        embed.set_author(
            name="Akinator", icon_url="https://i.imgur.com/n6km6ch.png")
        embed.set_thumbnail(url="https://i.imgur.com/n6km6ch.png")
        guess = ActionRow()
        guess.add_button(
            style=ButtonStyle.gray,
            label='Character',
            # disabled=True
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

                if not inter:
                    return await ctx.send("Something went wrong that shouldn't have happened huh.")
                elif (inter.clicked_button.label == 'Animal'):
                    question = await aki.start_game(language='en_animals', child_mode=True)
                    try:
                        await inter.respond(type=6)
                    except Exception:
                        pass

                    break
                elif (inter.clicked_button.label == 'Object'):
                    question = await aki.start_game(language='en_objects', child_mode=True)
                    try:
                        await inter.respond(type=6)
                    except Exception:
                        pass

                    break
                elif (inter.clicked_button.label == 'Character'):
                    question = await aki.start_game(child_mode=True)
                    try:
                        await inter.respond(type=6)
                    except Exception:
                        pass

                    break

            except asyncio.TimeoutError:
                await aki.close()
                await msg.edit("Timeout cancelling!!")
                break
            except Exception as e:
                await aki.close()
                raise e
                break

        while int(aki.progression) <= 85:
            embed = discord.Embed(
                title='Akinator',
                description=f'**Total Question:** {int(aki.step) + 1}\n**Progression:** {round(aki.progression)}%\n\nAnswer this question in 30 seconds.\n`{question}`',
                color=self.client.colors["purple"]
            )
            embed.set_thumbnail(url='https://i.imgur.com/n6km6ch.png')
            choices1 = ActionRow()
            choices1.add_button(
                style=ButtonStyle.green,
                label='Yes'
            )
            choices1.add_button(
                style=ButtonStyle.red,
                label='No'
            )
            choices1.add_button(
                style=ButtonStyle.grey,
                label='Idk'
            )
            choices2 = ActionRow()
            choices2.add_button(
                style=ButtonStyle.grey,
                label='Probably'
            )
            choices2.add_button(
                style=ButtonStyle.grey,
                label='Probably Not'
            )
            choices2.add_button(
                style=ButtonStyle.blurple,
                label='Back'
            )
            await msg.edit(embed=embed, components=[choices1, choices2])

            while True:
                def check(inter):
                    return inter.message.id == msg.id and inter.author.id == ctx.author.id

                try:
                    inter = await ctx.wait_for_button_click(check=check, timeout=30.0)

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
                    elif (inter.clicked_button.label) == 'Back':
                        try:
                            question = await aki.back()
                        except akinator.CantGoBackAnyFurther:
                            await inter.respond("You are on the first page.", ephemeral=True)

                    if aki.progression >= 85:
                        await aki.win()
                        embed = discord.Embed(
                            title=f"It's {aki.first_guess['name']}",
                            description=f"{aki.first_guess['description']}\n\n**Total Questions: **{int(aki.step) + 1}",
                            color=self.client.colors["purple"]
                        )
                        embed.set_thumbnail(
                            url='https://i.imgur.com/n6km6ch.png')
                        embed.set_image(
                            url=aki.first_guess['absolute_picture_path'])
                        await inter.respond(type=7, embed=embed, components=[])
                        await aki.close()
                        break
                    else:
                        pass

                    embed = discord.Embed(
                        title='Akinator',
                        description=f'**Total Question:** {int(aki.step) + 1}\n**Progression:** {round(aki.progression)}%\n\nAnswer this question in 30 seconds.\n`{question}`',
                        color=self.client.colors["purple"]
                    )
                    embed.set_thumbnail(url='https://i.imgur.com/n6km6ch.png')
                    choices1 = ActionRow()
                    choices1.add_button(
                        style=ButtonStyle.green,
                        label='Yes'
                    )
                    choices1.add_button(
                        style=ButtonStyle.red,
                        label='No'
                    )
                    choices1.add_button(
                        style=ButtonStyle.grey,
                        label='Idk'
                    )
                    choices2 = ActionRow()
                    choices2.add_button(
                        style=ButtonStyle.grey,
                        label='Probably'
                    )
                    choices2.add_button(
                        style=ButtonStyle.grey,
                        label='Probably Not'
                    )
                    choices2.add_button(
                        style=ButtonStyle.blurple,
                        label='Back'
                    )
                    try:
                        await inter.respond(type=7, embed=embed, components=[choices1, choices2])
                    except Exception:
                        await msg.edit(embed=embed, components=[choices1, choices2])
                except asyncio.TimeoutError:
                    await aki.close()
                    await msg.edit('Timeout, Try again!', components=[])
                    break
                except Exception as e:
                    await aki.close()
                    await msg.edit(components=[])
                    raise e
                    break

    @commands.command(name='trivia', description='Answer difficult questions.')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def trivia(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://opentdb.com/api.php?amount=1') as r:
                if 300 > r.status >= 200:
                    data = await r.json()
                    choices = []
                    # Three Incorrect Answers
                    incorrects = data['results'][0]['incorrect_answers']
                    choices = choices + incorrects  # added to choices list

                    # Correct Answer
                    answer = data['results'][0]['correct_answer']
                    choices.append(answer)  # added to choices list
                    if data['results'][0]['type'] != "boolean":
                        # Shuffled The Answers If Multiple choice
                        random.shuffle(choices)
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
                        color=random.choice(self.client.color_list)
                    )
                    embed.set_author(
                        name=f'{ctx.author.name}\'s Trivia', icon_url=ctx.author.avatar.url)
                    embed.add_field(
                        name='Difficulty', value=f"`{data['results'][0]['difficulty'].capitalize()}`")
                    embed.add_field(
                        name='Category', value=f"`{data['results'][0]['category']}`")
                    choicebtn = ActionRow()
                    for choice in choices:
                        choicebtn.add_button(
                            label=choice,
                            style=ButtonStyle.blurple
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
                                            label=choice,
                                            style=ButtonStyle.grey,
                                            disabled=True
                                        )
                                    else:
                                        new_btn.add_button(
                                            label=answer,
                                            style=ButtonStyle.green,
                                            disabled=True
                                        )
                                await inter.respond(type=7, content=f"Yes, The correct answer was `{answer}`! Well Done.", embed=embed, components=[new_btn])
                                break
                            else:
                                new_btn = ActionRow()
                                for choice in choices:
                                    if choice == inter.clicked_button.label:
                                        new_btn.add_button(
                                            label=choice,
                                            style=ButtonStyle.red,
                                            disabled=True
                                        )
                                    elif choice in incorrects:
                                        new_btn.add_button(
                                            label=choice,
                                            style=ButtonStyle.grey,
                                            disabled=True
                                        )
                                    else:
                                        new_btn.add_button(
                                            label=answer,
                                            style=ButtonStyle.green,
                                            disabled=True
                                        )
                                await inter.respond(type=7, content=f"No dumbo, The correct answer was `{answer}`!", embed=embed, components=[new_btn])
                                break

                        except asyncio.TimeoutError:
                            new_btn = ActionRow()
                            for choice in choices:
                                if choice in incorrects:
                                    new_btn.add_button(
                                        label=choice,
                                        style=ButtonStyle.grey,
                                        disabled=True
                                    )
                                else:
                                    new_btn.add_button(
                                        label=answer,
                                        style=ButtonStyle.green,
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

                    embed = discord.Embed(
                        color=random.choice(self.client.color_list))
                    embed.set_author(name='Would You Rather...',
                                     url='https://either.io', )
                    embed.add_field(
                        name='Either...', value=f':regional_indicator_a: {choices[0]}\n\uFEFF', inline=False)
                    embed.add_field(
                        name='Or...', value=f':regional_indicator_b: {choices[1]}', inline=False)
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

        resp = requests.get(
            f"https://some-random-api.ml/pokedex?pokemon={pokemon}")
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
        description="Random post from given subreddit.\n__NSFW subreddit requires NSFW marked text channel.__"
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

        if subreddit.over18 and not ctx.channel.is_nsfw():
            return await ctx.send("The subreddit you are requesting is NSFW. So, This channel needs to be marked NSFW.")

        async for submission in subreddit.hot(limit=75):
            if not submission.locked and not submission.stickied:
                if submission.over_18 and not ctx.channel.is_nsfw():
                    pass
                else:
                    all_subs.append(submission)

        random_sub = random.choice(all_subs)

        name = random_sub.title
        description = random_sub.selftext if len(
            random_sub.selftext) < 2001 else ""
        url = random_sub.url
        vote = random_sub.score
        comments = random_sub.num_comments
        post = random_sub.permalink

        em = discord.Embed(
            title=name,
            description=description,
            color=random.choice(self.client.color_list),
            url=f"https://reddit.com{post}"
        )
        em.set_image(url=url)
        em.set_footer(
            text=f"👍🏻 {vote} | 💬 {comments} | r/{subreddit.display_name}")
        await ctx.send(embed=em)

    @commands.command(
        name="meme",
        description="Random meme from reddit."
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def meme(self, ctx):
        subreddit = await reddit.subreddit(random.choice(["memes", "dankmemes", "wholesomemes"]))
        all_subs = []

        async for submission in subreddit.hot(limit=75):
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
            color=random.choice(self.client.color_list),
            url=f"https://reddit.com{post}"
        )
        em.set_image(url=url)
        em.set_footer(text=f"👍🏻 {vote} | 💬 {comments}")

        await ctx.send(embed=em)

    @commands.command(
        name="cat",
        description="Random cat image.",
        aliases=['cats']
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cat(self, ctx):
        subreddit = await reddit.subreddit("catpictures")
        all_subs = []

        async for submission in subreddit.hot(limit=75):
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
        description="Random dog image.",
        aliases=['dogs']
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dog(self, ctx, url=None):
        subreddit = await reddit.subreddit("dogpictures")
        all_subs = []

        async for submission in subreddit.hot(limit=75):
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
        description="Answers a question like a 8Ball",
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

        embed = discord.Embed(
            title=":8ball:| **8Ball**",
            color=self.client.colors["og_blurple"]
        )
        embed.add_field(
            name="**Question**:",
            value=f"{question}",
            inline=False
        )
        embed.add_field(
            name="**Answer**:",
            value=f"{random.choice(responses)}",
            inline=False
        )
        embed.set_footer(
            text=f"Asked by {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(
        name="choose",
        description="Chooses between things.",
        aliases=["pick"]
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def choose_command(self, ctx, *choices):
        if len(choices) > 10:
            return await ctx.reply("Jeez, Give me less choices! Max 10.")
        elif len(choices) < 2:
            return await ctx.reply("Give me atleast 2 choices to choose from.")

        choice = random.choice(choices)
        await ctx.send(f"I choose `{choice}`.")

    @commands.command(
        name="pat",
        description="Pats a user."
    )
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pat(self, ctx, member: discord.Member):
        if member == ctx.author:
            await ctx.send("You can't pat yourself lol!")
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
            await ctx.send("You can't kill yourself.")
            return
        if member.bot:
            await ctx.send("Why are you trying to kill my fellow friend??")
            return

        kill_text = [
            'died of hunger', 'died with getting squashed by anvil',
            'died after seeing cringy fortnite',
            'died after seeing the mirror',
            'died while writing the sucide note',
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
        description="This command can hack a user! THIS IS NOT A JOKE.",
        hidden=True
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hack(self, ctx, member: discord.Member):
        pass


def setup(client):
    client.add_cog(Fun(client))
