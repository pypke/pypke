import discord
from discord.ext import commands


class ChatBot(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=False)
    async def chatbot(self, ctx):
        pass

    @chatbot.command()
    async def channel(self, ctx, channel: discord.TextChannel=None):
        channel = channel or ctx.channel
        data = {
            '_id': ctx.guild.id,
            'channel': channel.id
        }
        await self.client.chatbot.upsert(data)
        await ctx.send(f"ChatBot will now function in {channel.mention}, To stop it use `#chatbot stop`")

    @chatbot.command()
    async def stop(self, ctx):
        try:
            await self.client.chatbot.delete(ctx.guild.id)
        except:
            await ctx.send("ChatBot isn't setup for this server!!")

        await ctx.send(f"ChatBot has now stopped!!")

def setup(client):
    client.add_cog(ChatBot(client))