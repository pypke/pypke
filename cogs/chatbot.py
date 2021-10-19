import discord, os, aiohttp
from discord.ext import commands
from urllib.parse import quote_plus

class ChatBot(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # if not message.guild:
        #     return

        chatbot_channels = await self.client.chatbot.get_all()
        data = await self.client.config.get_by_id(message.guild.id)
        if not data or "prefix" not in data:
            prefix = "#"
        else:
            prefix = data["prefix"]
        if message.content.lower().startswith(f"{prefix}"):
            return
        msg = quote_plus(message.content.lower())
        for channel in chatbot_channels:
            if int(channel['_id']) == message.channel.id:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'http://api.brainshop.ai/get?bid=160282&key=ymIz1TEF0CNxURTu&uid={message.author.id}&msg={msg}') as r:
                            if 300 > r.status >= 200:
                                data = await r.json()
                                response = data['cnt']
                                await message.reply(response, mention_author=False)
                except discord.HTTPException:
                    pass

    @commands.group(invoke_without_command=False)
    async def chatbot(self, ctx):
        pass

    @chatbot.command()
    async def channel(self, ctx, channel: discord.TextChannel=None):
        channel = channel or ctx.channel
        data = {
            '_id': channel.id
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