from discord.ext import commands

class Prefix():
    def __init__(self, client):
        self.client = client

    # Code To Get Prefix
    async def get_prefix(self, client, message):
        # If dm's
        if not message.guild:
            return commands.when_mentioned_or(self.client.prefix)(self.client, message)

        try:
            data = await self.client.config.find(message.guild.id)

            # Make sure we have a useable prefix
            if not data or "prefix" not in data:
                return commands.when_mentioned_or(self.client.prefix)(self.client, message)
            return commands.when_mentioned_or(data["prefix"])(self.client, message)
        except:
            return commands.when_mentioned_or(self.client.prefix)(self.client, message)