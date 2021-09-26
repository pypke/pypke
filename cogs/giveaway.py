import discord
from discord.ext import commands, tasks
import asyncio, random, epoch
from utils.time import TimeConverter
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from datetime import datetime

class Giveaway(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.giveaways_task = self.check_current_giveaways.start()

    def cog_unload(self):
        self.giveaways_task.cancel()

    @tasks.loop(minutes=1)
    async def check_current_giveaways(self):
        currentTime = datetime.now()
        current_giveaways = deepcopy(self.client.current_giveaways)
        for key, value in current_giveaways.items():
            if value['gaDuration'] is None:
                continue

            endTime = value['startedAt'] + relativedelta(seconds=value['gaDuration'])

            if currentTime >= endTime:
                guild = self.client.get_guild(value['guildId'])
                channel = guild.get_channel(value['channelId'])
                msg = await channel.fetch_message(value['_id'])

                users = await msg.reactions[0].users().flatten()
                users.pop(users.index(self.client.user))
                winner = random.choice(users)
                ended_time = round(epoch.now())
                end_embed = discord.Embed(
                                          title=value['prize'], 
                                          description=f"Ended: <t:{ended_time}:R> (<t:{ended_time}:f>)\nWinner: {winner.mention}",
                                          color=discord.Color.orange()
                                         )
                end_embed.set_footer(icon_url=guild.icon_url, text=guild.name)
                await msg.edit(embed=end_embed)
                await msg.reply(f"Congratulations! {winner.mention} Has Won The `{value['prize']}`!")

                await self.client.giveaways.delete(msg.id)
                try:
                    self.client.current_giveaways.pop(msg.id)
                except KeyError:
                    pass

    @check_current_giveaways.before_loop
    async def before_check_current_giveaways(self):
        await self.client.wait_until_ready()

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def gstart(self, ctx, time : TimeConverter, channel: discord.TextChannel=None, * , prize: str):
        etime = round(epoch.now())
        epoch_time = etime + time
        
        channel = ctx.channel or channel
        embed = discord.Embed(
            title=f"{prize}", 
            description=f"React With 🎉 To Enter!\nEnds: <t:{epoch_time}:R> (<t:{epoch_time}:f>)\nHosted By {ctx.author.name}",
            color = discord.Color.orange()
            )
        embed.set_footer(icon_url=ctx.guild.icon_url, text=ctx.guild.name)
        my_msg = await channel.send(embed = embed)

        data = {
            '_id': my_msg.id,
            'startedAt': datetime.now(),
            'gaDuration': time or None,
            'prize': prize,
            'channelId': ctx.channel.id,
            'guildId': ctx.guild.id
        }
        await self.client.giveaways.upsert(data)
        await my_msg.add_reaction('🎉')

        if time < 300:
            await asyncio.sleep(time)

            new_msg = await channel.fetch_message(my_msg.id)
            users = await new_msg.reactions[0].users().flatten()
            users.pop(users.index(self.client.user))
            winner = random.choice(users)
            ended_time = round(epoch.now())
            end_embed = discord.Embed(
                                      title=prize, 
                                      description=f"Ended: <t:{ended_time}:R> (<t:{ended_time}:f>)\nWinner: {winner.mention}",
                                      color=discord.Color.orange()
                                    )
            end_embed.set_footer(icon_url=ctx.guild.icon_url, text=ctx.guild.name)
            await new_msg.edit(embed=end_embed)
            await new_msg.reply(f"Congratulations! {winner.mention} Has Won The `{prize}`!")

            await self.client.giveaways.delete(my_msg.id)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def gcreate(self, ctx):
        await ctx.send("Let's start with this giveaway!\n`Answer these questions within 30 seconds!`")

        questions = ["**Which channel should it be hosted in?**", 
                    "**What should be the duration of the giveaway?** `(s|m|h|d)`",
                    "**What is the prize of the giveaway?**"]

        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel 

        for i in questions:
            await ctx.send(i)

            try:
                msg = await self.client.wait_for('message', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send('Time\'s Up, please be quicker next time!')
                return
            else:
                answers.append(msg.content)
                
        try:
            c_id = int(answers[0][2:-1])
            channel = self.client.get_channel(c_id)
            if channel:
                pass
            else:
                await ctx.send(f"Channel should be in this guild!!")
                return
        except:
            await ctx.send(f"You didn't mention a channel properly. Do it like this {ctx.channel.mention} next time.")
            return

        time = answers[1]
        time = await TimeConverter.convert(self, ctx, time)
        etime = round(epoch.now())
        epoch_time = etime + time
        
        prize = answers[2]

        await ctx.send(f"The Giveaway will be in {channel.mention} and will last till <t:{epoch_time}:f> !")
        embed = discord.Embed(
            title=f"{prize}", 
            description=f"React With 🎉 To Enter!\nEnds: <t:{epoch_time}:R> (<t:{epoch_time}:f>)\nHosted By {ctx.author.name}",
            color = discord.Color.orange()
            )
        embed.set_footer(icon_url=ctx.guild.icon_url, text=ctx.guild.name)
        my_msg = await channel.send(embed = embed)

        data = {
            '_id': my_msg.id,
            'startedAt': datetime.now(),
            'gaDuration': time or None,
            'prize': prize,
            'channelId': ctx.channel.id,
            'guildId': ctx.guild.id
        }
        await self.client.giveaways.upsert(data)
        await my_msg.add_reaction('🎉')

        if time < 300:
            await asyncio.sleep(time)

            new_msg = await channel.fetch_message(my_msg.id)
            users = await new_msg.reactions[0].users().flatten()
            users.pop(users.index(self.client.user))
            winner = random.choice(users)
            ended_time = round(epoch.now())
            end_embed = discord.Embed(
                                      title=prize, 
                                      description=f"Ended: <t:{ended_time}:R> (<t:{ended_time}:f>)\nWinner: {winner.mention}",
                                      color=discord.Color.orange()
                                    )
            end_embed.set_footer(icon_url=ctx.guild.icon_url, text=ctx.guild.name)
            await new_msg.edit(embed=end_embed)
            await new_msg.reply(f"Congratulations! {winner.mention} Has Won The `{prize}`!")

            await self.client.giveaways.delete(my_msg.id)  

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def greroll(self, ctx, channel : discord.TextChannel, _id : int):
        if channel == None:
            channel = ctx.channel
        else:
            discord.TextChannel
        try:
            new_msg = await channel.fetch_message(_id)
        except:
            await ctx.send("The Message Id Is Incorrect Or The Message Is Deleted.")
            return
        
        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))

        winner = random.choice(users)

        await channel.send(f"Congratulations! The new winner is {winner.mention}!")

def setup(client):
    client.add_cog(Giveaway(client))