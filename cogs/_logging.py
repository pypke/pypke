from datetime import datetime

import discord
from discord.ext import commands

# This Is Currently In Devlopment


class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_guild_log(self, guild):
        data = self.bot.config.get(guild.id)
        if data:
            log_channel = data["logging"]
            return log_channel

        possible_names = ["modlogs", "logs", "logging", "mod-logs", "log"]

        for name in possible_names:
            try:
                log_channel = discord.utils.get(guild.channels, name=name)
                return log_channel
            except:
                continue

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
            logs = self.get_guild_log(guild)
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
            logs = self.get_guild_log(guild)
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            embed = discord.Embed(
                title="nickname change",
                description=f"**Old Nickname:** {before.nick}\n**New Nickname:** {after.nick}",
                color=discord.Color.blue(),
                timestamp=datetime.now(),
            )
            logs = self.get_guild_log(before.guild)
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.User):
        embed = discord.Embed(
            title="join",
            description=f"**User:** {member.mention} **│** {member}\n**User ID:** {member.id}\n**User Age:** {member.created_at}",
            color=discord.Color.green(),
            timestamp=datetime.now(),
        )
        logs = self.get_guild_log(member.guild)
        await logs.send(embed=embed)


def setup(bot):
    bot.add_cog(LoggingCog(bot))
