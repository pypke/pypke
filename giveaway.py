import discord
from discord.ext import commands
import asyncio
import datetime
import random

def convert(time):
        pos = ["s","m","h","d"]

        time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 3600*24}

        unit = time[-1]

        if unit not in pos:
            return -1
        try:
            val = int(time[:-1])
        except:
            return -2


        return val * time_dict[unit]

class Giveaway(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def gstart(self, ctx, mins : int, * , prize: str):
        embed = discord.Embed(title = "Giveaway!", description = f"**Prize**:- `{prize}`\nReact To <:diamond:809829519338242048> To Enter The **Giveaway**!", color = discord.Color.blue())

        end = datetime.datetime.utcnow() + datetime.timedelta(seconds = mins*60) 

        embed.add_field(name="Ends In:", value = f"**{mins} Minutes** From Now!")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f"Hosted By {ctx.author.name}", icon_url=ctx.author.avatar_url)

        my_msg = await ctx.send(embed = embed)

        await my_msg.add_reaction("<:diamond:809829519338242048>")

        await asyncio.sleep(mins*60)

        new_msg = await ctx.channel.fetch_message(my_msg.id)

        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))

        winner = random.choice(users)

        await ctx.send(f"Congratulations! {winner.mention} Won The Prize:-`{prize}`!")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def gcreate(self, ctx):
        await ctx.send("Let's start with this giveaway!\n`Answer these questions within 15 seconds!`")

        questions = ["**Which channel should it be hosted in?**", 
                    "**What should be the duration of the giveaway?** `(s|m|h|d)`",
                    "**What is the prize of the giveaway?**"]

        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel 

        for i in questions:
            await ctx.send(i)

            try:
                msg = await self.client.wait_for('message', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send('You didn\'t answer in time, please be quicker next time!')
                return
            else:
                answers.append(msg.content)
        try:
            c_id = int(answers[0][2:-1])
        except:
            await ctx.send(f"You didn't mention a channel properly. **Do it like this {ctx.channel.mention} next time.**")
            return

        channel = self.client.get_channel(c_id)

        time = convert(answers[1])
        if time == -1:
            await ctx.send("You didn't answer the time with a proper unit. Use `(s|m|h|d)` next time!")
            return
        elif time == -2:
            await ctx.send("The time must be a number. Please enter a number next time")
            return            

        prize = answers[2]

        await ctx.send(f"The Giveaway will be in {channel.mention} and will last {answers[1]}!")

        embed = discord.Embed(title = "Giveaway!", description = f"**Prize**:- `{prize}`\nReact To 🎉 To Enter The **Giveaway**!", color = discord.Color.blue())
        embed.add_field(name="Ends In:", value = f"**{answers[1]}** From Now!")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f"Hosted By {ctx.author.name}", icon_url=ctx.author.avatar_url)

        my_msg = await channel.send(embed = embed)

        await my_msg.add_reaction('🎉')
        await asyncio.sleep(time)

        new_msg = await channel.fetch_message(my_msg.id)

        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))

        winner = random.choice(users)

        await channel.send(f"Congratulations! {winner.mention} Won The Prize:-`{prize}`!")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def greroll(self, ctx, channel : discord.TextChannel, id_ : int):
        if channel == None:
            channel = ctx.channel
        else:
            discord.TextChannel
        try:
            new_msg = await channel.fetch_message(id_)
        except:
            await ctx.send("The id was entered incorrectly.")
            return
        
        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))

        winner = random.choice(users)

        await channel.send(f"Congratulations! The new winner is {winner.mention}!")

def setup(client):
    client.add_cog(Giveaway(client))