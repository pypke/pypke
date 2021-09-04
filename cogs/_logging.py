#This Is Currently In Devlopment
import discord
from discord.ext import commands, audit_logs


class Logging(commands.Cog):
    def __init__(self, client):
        self.client = client

    guild = discord.Guild

    @commands.Cog.listener()
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban):
    channel=[]
    em=discord.Embed(title="Moderation Action Taken"description=f'{0.user} banned {0.target}'.format(entry), color=discord.Color.blue())

def setup(client):
    client.add_cog(Logging(client))