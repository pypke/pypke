from utils.time import TimeConverter

import asyncio, random, epoch
from typing import Optional
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from datetime import datetime

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Greedy

class GiveawayHelper:

    async def roll_giveaway(self, _id):
        data = await self.client.giveaways.find(_id)

        try:
            guild = self.client.get_guild(data['guildId'])
            channel = guild.get_channel(data['channelId'])
            msg = await channel.fetch_message(data['_id'])

        except discord.HTTPException:
            await GiveawayHelper.remove_giveaway(self, data['_id'])
            print(f"Removed Deleted Giveaway. Id: {data['_id']}")
            return

        users = await msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))

        try:
            winner = random.choice(users)
        except IndexError:
            await GiveawayHelper.remove_giveaway(self, _id)
            ended_time = round(epoch.now())
            end_embed = discord.Embed(
                title=data['prize'],
                description=f"Ended: <t:{ended_time}:R> (<t:{ended_time}:f>)\nWinner: No one",
                color=self.client.colors["og_blurple"]
            )
            end_embed.set_footer(icon_url=guild.icon.url, text=guild.name)
            await msg.edit(embed=end_embed)
            return await msg.reply("No one entered for the giveaway!")

        ended_time = round(epoch.now())
        end_embed = discord.Embed(
            title=data['prize'],
            description=f"Ended: <t:{ended_time}:R> (<t:{ended_time}:f>)\nWinner: {winner.mention}",
            color=self.client.colors["og_blurple"]
        )
        end_embed.set_footer(icon_url=guild.icon.url, text=guild.name)
        try:
            await msg.edit(embed=end_embed)
            await msg.reply(f"Congratulations! {winner.mention} has won `{data['prize']}`!")
        except discord.HTTPException:
            pass

        await GiveawayHelper.remove_giveaway(self, data['_id'])

    async def remove_giveaway(self, _id):
        await self.client.giveaways.delete(_id)

        try:
            self.client.current_giveaways.pop(_id)
        except KeyError:
            pass

        print(f"Removed Giveaway! Id: {_id}")

class Giveaway(commands.Cog, description="Commands for giveaway creation."):
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
                await GiveawayHelper.roll_giveaway(self, value['_id'])

    @check_current_giveaways.before_loop
    async def before_check_current_giveaways(self):
        await self.client.wait_until_ready()

    @commands.command(
        name="gstart",
        description="Create a giveaway quickly!\nTime should be in \"69m 420s\"\n\n**Example:**\n`#gstart \"1h 1m 10s\" The prize`"
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def gstart_command(self, ctx, time: TimeConverter, channel: Optional[discord.TextChannel], *, prize: str):
        etime = round(epoch.now())
        epoch_time = etime + time
        channel = channel or ctx.channel

        embed = discord.Embed(
            title=f"{prize}",
            description=
            f"React With 🎉 To Enter!\nEnds: <t:{epoch_time}:R> (<t:{epoch_time}:f>)\nHosted By {ctx.author.name}",
            color=self.client.colors["og_blurple"])
        embed.set_footer(icon_url=ctx.guild.icon.url, text=ctx.guild.name)
        await ctx.send(
            f"The Giveaway will be in {channel.mention} and will last till <t:{epoch_time}:f> !"
        )
        my_msg = await channel.send(embed=embed)

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
            await GiveawayHelper.roll_giveaway(self, my_msg.id)

    @commands.command(name="gcreate", description="Create a Giveaway interactively!")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def gcreate_command(self, ctx):
        embed = discord.Embed(
            title="Create Giveaway!",
            description="Let's start with this giveaway!\n`Answer these questions within 30 seconds!`",
            color=self.client.colors["og_blurple"]
        )
        ques_msg = await ctx.send(embed=embed)
        await asyncio.sleep(2)

        questions = [
            f"**Which channel should the giveaway be hosted?**\ni.e. {ctx.channel.mention}",
            f"**What should be the duration of the giveaway?** `(s|m|h|d)`\ni.e. \"1h 30m\"",
            f"**What is the prize of the giveaway?**"
        ]

        embeds = []
        for question in questions:
            embed = discord.Embed(
                title="Create Giveaway!",
                description=question,
                color=self.client.colors["og_blurple"]
            )
            embeds.append(embed)

        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for embed in embeds:
            await ques_msg.edit(embed=embed)

            try:
                msg = await self.client.wait_for('message', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send('Time\'s Up, please be quicker next time!')
                return
            else:
                answers.append(msg.content)
                await msg.delete()

        try:
            c_id = int(answers[0][2:-1])
            channel = self.client.get_channel(c_id)
            if channel:
                pass
            else:
                await ctx.send(f"Channel should be in this guild!!")
                return
        except:
            await ctx.send(
                f"You didn't mention a channel properly. Do it like this {ctx.channel.mention} next time."
            )
            return

        time = answers[1]
        time = await TimeConverter.convert(self, ctx, time)
        etime = round(epoch.now())
        epoch_time = etime + time

        prize = answers[2]

        await ques_msg.delete()
        await ctx.send(
            f"The Giveaway will be in {channel.mention} and will last till <t:{epoch_time}:f> !"
        )
        embed = discord.Embed(
            title=f"{prize}",
            description=f"React With 🎉 To Enter!\nEnds: <t:{epoch_time}:R> (<t:{epoch_time}:f>)\nHosted By {ctx.author.name}",
            color=self.client.colors["og_blurple"]
        )
        embed.set_footer(icon_url=ctx.guild.icon.url, text=ctx.guild.name)
        my_msg = await channel.send(embed=embed)

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
            await GiveawayHelper.roll_giveaway(self, my_msg.id)

    @commands.command(name="greroll", description="Reroll a previous ended giveaway.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def greroll_command(self, ctx, channel: discord.TextChannel, message_id: int):
        _id = message_id

        data = await self.client.giveaways.get_by_id(_id)
        if data:
            return await ctx.send(f"This giveaway hasn't ended yet. If you want to end it use `{ctx.prefix}gend` instead.")

        try:
            new_msg = await channel.fetch_message(_id)
        except:
            await ctx.send("The message id is incorrect or the message is deleted")
            return

        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))

        try:
            winner = random.choice(users)
        except IndexError:
            return await channel.send("No one entered for the giveaway, So Nobody won!")

        await channel.send(f"Congratulations! The new winner is {winner.mention}!")

    @commands.command(name="gend", description="End a giveaway before time.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def gend_command(self, ctx, message_id: int):
        _id = message_id

        try:
            data = await self.client.giveaways.find(_id)
        except Exception:
            await ctx.send("The message id is incorrect or the message is deleted.")
            return

        if data == None:
            await ctx.send("The message id is incorrect or the message is deleted.")
            return

        await GiveawayHelper.roll_giveaway(self, _id)

    @commands.command(name="gdelete", description="Delete a ongoing giveaway.", aliases=['gcancel'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def gdelete_command(self, ctx, message_id: int):
        _id = message_id

        try:
            data = await self.client.giveaways.find(_id)
        except Exception:
            await ctx.send("The message id is incorrect or the message is deleted.")
            return

        if data == None:
            await ctx.send("The message id is incorrect or the message is deleted.")
            return

        await GiveawayHelper.remove_giveaway(self, _id)
        await ctx.send("Deleted the giveaway!")

def setup(client):
    client.add_cog(Giveaway(client))
