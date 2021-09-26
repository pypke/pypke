import discord
from discord.ext import commands
from datetime import datetime

# This Is Currently In Devlopment


def get_log(self, guild):
    possible_names = ["modlogs", "logs", "logging", "mod-logs", "log"]

    for name in possible_names:
        try:
            log_channel = discord.utils.get(guild.channels, name=name)
            return log_channel
        except:
            continue

async def get_entry(self):
    guild = discord.Guild()
    for entry in guild.audit_logs(action=discord.AuditLogAction.ban):
        description='{0.user} banned {0.target}'.format(entry)
        return description

class Logging(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        entry = guild.audit_logs(action=discord.AuditLogAction.ban)
        embed = discord.Embed(
            title="Member Banned",
            description=
            f"**Offender:** {member.name}\n**Moderator:** *work in-progress*" ,
            color=discord.Color.red(),
            timestamp=datetime.now()
            )
        logs = get_log(self, guild)
        content = await get_entry(self)
        await logs.send(content=content, embed=embed)


def setup(client):
    client.add_cog(Logging(client))
