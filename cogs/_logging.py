import discord
from discord.ext import commands
from datetime import datetime

# This Is Currently In Devlopment


def get_log(guild):
    possible_names = ["modlogs", "logs", "logging", "mod-logs", "log"]

    for name in possible_names:
        try:
            log_channel = discord.utils.get(guild.channels, name=name)
            return log_channel
        except:
            continue


class LoggingCog(commands.Cog, description="This cog handles the logging of various events!"):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
            print("{0.user} banned {0.target}".format(entry))
            embed = discord.Embed(
                title="ban",
                description=f"**Offender:** {entry.target} **│** {entry.target.mention}\n**Responsible Moderator:** {entry.user}\n**Reason:** {entry.reason if entry.reason else 'No Reason Provided'}",
                color=discord.Color.red(),
                timestamp=datetime.now(),
            )
            logs = get_log(guild)
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        async for entry in guild.audit_logs(action=discord.AuditLogAction.unban, limit=1):
            print("{0.user} Unbanned {0.target}".format(entry))
            embed = discord.Embed(
                title="unban",
                description=f"**Offender:** {entry.target} **│** {entry.target.mention}\n**Responsible Moderator:** {entry.user}\n**Reason:** {entry.reason if entry.reason else 'No Reason Provided'}",
                color=discord.Color.green(),
                timestamp=datetime.now(),
            )
            logs = get_log(guild)
            await logs.send(embed=embed)


def setup(client):
    client.add_cog(LoggingCog(client))
