import discord, os
from discord.ext import commands
from prsaw import RandomStuffV2 as RandomStuff 


rs = RandomStuff(async_mode = True, api_key=os.getenv('prsaw_key'))

class ChatBot(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if not message.guild:
            return

        chatbot_channels = await self.client.chatbot.get_all()
        data = await self.client.config.get_by_id(message.guild.id)
        if not data or "prefix" not in data:
            prefix = "#"
        else:
            prefix = data["prefix"]
        if message.content.lower().startswith(f"{prefix}"):
            return
        for channel in chatbot_channels:
            if int(channel['_id']) == message.channel.id:
                try:
                    response = await rs.get_ai_response(message.content)
                    await message.reply(response['message'], mention_author=False)
                except:
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