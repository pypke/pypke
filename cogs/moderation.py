import discord
from discord.ext import commands, tasks

from dateutil.relativedelta import relativedelta
from copy import deepcopy
from datetime import datetime
from utils.time import TimeConverter
import asyncio

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mute_task = self.check_current_mutes.start()

    def cog_unload(self):
        self.mute_task.cancel()

    @tasks.loop(minutes=5)
    async def check_current_mutes(self):
        currentTime = datetime.now()
        mutes = deepcopy(self.client.muted_users)
        for key, value in mutes.items():
            if value['muteDuration'] is None:
                continue

            unmuteTime = value['mutedAt'] + relativedelta(seconds=value['muteDuration'])

            if currentTime >= unmuteTime:
                guild = self.client.get_guild(value['guildId'])
                offender = guild.get_member(value['_id'])
                moderator = guild.get_member(value['mutedBy'])

                role = discord.utils.get(guild.roles, name="Muted")
                if role in offender.roles:
                    await offender.remove_roles(role)
                    try:
                        modlogs = discord.utils.get(guild.channels, name="modlogs")
                        time = int(value['muteDuration'])

                        # Converting Time Back To Readble Letters
                        minutes, seconds = divmod(time, 60)
                        hours, minutes = divmod(minutes, 60)
                        days, hours = divmod(hours, 24)
                        duration = ""
                        if days != 0:
                            duration = duration + f"{days} days "
                        if hours != 0:
                            duration = duration + f"{hours} hours "
                        if minutes != 0:
                            duration = duration + f"{minutes} minutes "
                        if seconds != 0:
                            duration = duration + f"{seconds} seconds "

                        embed = discord.Embed(
                            title="Auto-Unmuted", 
                            description=f"Offender: {offender.name} | {offender.mention}\nModerator: {moderator.name}\nDuration: {duration}",
                            color=discord.Color.green(),
                            timestamp=datetime.now()
                            )
                        await modlogs.send(embed=embed) 
                        
                        print(f"Unmuted: {offender.display_name}")                   
                    except:
                        print(f"Unmuted: {offender.display_name}")


                await self.client.mutes.delete(offender.id)
                try:
                    self.client.muted_users.pop(offender.id)
                except KeyError:
                    pass
    
    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.client.wait_until_ready()

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No Reason Provided"):
        try:
            await member.send(f"You Have Been Kicked From {ctx.guild.name}, Reason " + reason)
            await ctx.send(f"Kicked {member.name} From {ctx.guild.name}")
        except:
            await ctx.send(f"Kicked {member.name} From {ctx.guild.name}")
            
        await member.kick(reason=reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No Reason Provided"):
        try:
            await member.send(f"You Have Been Banned From {ctx.guild.name}, Reason " + reason)
            await ctx.send(f"Banned {member.name} From {ctx.guild.name}")
        except:
            await ctx.send(f"Banned {member.name} From {ctx.guild.name}")

        await member.ban(reason=reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(member_name + " Has Been Unbanned!")
                return

        await ctx.send(member + " was not found!")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, time: TimeConverter=None):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            await ctx.send("No muted role was found! Please create one called `Muted`")
            return

        try:
            if self.client.muted_users[member.id]:
                await ctx.send("This user is already muted")
                return
        except KeyError:
            pass

        data = {
            '_id': member.id,
            'mutedAt': datetime.now(),
            'muteDuration': time or None,
            'mutedBy': ctx.author.id,
            'guildId': ctx.guild.id,
        }
        await self.client.mutes.upsert(data)
        self.client.muted_users[member.id] = data

        await member.add_roles(role)

        if time and time > 2592000:
            ctx.send("Time cannot be greater than 1 Month/30 Days")
        else:
            pass
        
        if not time:
            await ctx.send(f"{member.display_name} Was Muted")
            modlogs = discord.utils.get(ctx.guild.channels, name="modlogs")
            embed = discord.Embed(
                            title="Muted", 
                            description=f"Offender: {member.name} | {member.mention}\nModerator: {ctx.author.name}",
                            color=discord.Color.red(),
                            timestamp=datetime.now()
                            )
            await modlogs.send(embed=embed)
        else:
            # Converting Time Back To Readble Letters
            minutes, seconds = divmod(time, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            duration = ""
            if days != 0:
                duration = duration + f"{days} days "
            if hours != 0:
                duration = duration + f"{hours} hours "
            if minutes != 0:
                duration = duration + f"{minutes} minutes "
            if seconds != 0:
                duration = duration + f"{seconds} seconds "

            try:
                modlogs = discord.utils.get(ctx.guild.channels, name="modlogs")
                embed = discord.Embed(
                            title="Muted", 
                            description=f"Offender: {member.name} | {member.mention}\nModerator: {ctx.author.name}\nDuration: {duration}",
                            color=discord.Color.red(),
                            timestamp=datetime.now()
                            )
                await modlogs.send(embed=embed)
                await ctx.send(f"{member.name} was muted for {duration}")
            except:
                await ctx.send(f"{member.name} was muted for {duration}")

        if time and time < 300:
            await asyncio.sleep(time)
            try:
                modlogs = discord.utils.get(ctx.guild.channels, name="modlogs")
                embed = discord.Embed(
                            title="Unmuted", 
                            description=f"Offender: {member.name} | {member.mention}\nModerator: {ctx.author.name}\nDuration: {duration}",
                            color=discord.Color.green(),
                            timestamp=datetime.now()
                            )
                await modlogs.send(embed=embed)
            except:
                pass

            if role in member.roles:
                await member.remove_roles(role)
                await ctx.send(f"{member.display_name} Was Unmuted ")

            await self.client.mutes.delete(member.id)
            try:
                self.client.muted_users.pop(member.id)
            except KeyError:
                pass

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            await ctx.send("No muted role was found! Please create one called `Muted`")
            return

        if role not in member.roles:
            await ctx.send("This member is not muted.")
            return

        await self.client.mutes.delete(member.id)
        try:
            self.client.muted_users.pop(member.id)
        except KeyError:
            pass

        await member.remove_roles(role)
        await ctx.send(f"{member.name} Was Unmuted")
        try:
            modlogs = discord.utils.get(ctx.guild.channels, name="modlogs")
            embed = discord.Embed(
                            title="Unmuted", 
                            description=f"Offender: {member.name} | {member.mention}\nModerator: {ctx.author.name}",
                            color=discord.Color.green(),
                            timestamp=datetime.now()
                            )
            await modlogs.send(embed=embed)
        except:
            pass
    
    @commands.group(invoke_without_command=True, pass_context=True)
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        channel = ctx.channel
        if ctx.guild.default_role not in channel.overwrites:
            # This is the same as the elif except it handles agaisnt empty overwrites dicts
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                self.client.user: discord.PermissionOverwrite(send_messages=True)
            }
            await channel.edit(overwrites=overwrites, reason=f"Channel Locked By {ctx.author.name}")
            await ctx.send(f":lock: Locked!! {channel.mention}")
        elif (
            channel.overwrites[ctx.guild.default_role].send_messages == True
            or channel.overwrites[ctx.guild.default_role].send_messages == None
        ):
            overwrites = channel.overwrites[ctx.guild.default_role]
            overwrites.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites, reason=f"Channel Locked By {ctx.author.name}")
            await ctx.send(f":lock: Locked!! {channel.mention}")

        elif channel.overwrites[ctx.guild.default_role].send_messages == False:
            await ctx.send("This Channel Is Already Locked!")
    
    @commands.group(invoke_without_command=True, pass_context=True)
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        channel = ctx.channel
        if ctx.guild.default_role not in channel.overwrites:
            await ctx.send("This Channel Is Not Locked!")
        elif (
            channel.overwrites[ctx.guild.default_role].send_messages == True
            or channel.overwrites[ctx.guild.default_role].send_messages == None
        ):
            await ctx.send("This Channel Is Not Locked!")
        else:
            overwrites = channel.overwrites[ctx.guild.default_role]
            overwrites.send_messages = None
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites, reason=f"Channel Unlocked By {ctx.author.name}")
            await ctx.send(f":unlock: Unlocked!! {channel.mention}")
        
    @lock.command(name="server")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def lserver(self, ctx):
        role = ctx.guild.default_role
        permissions = discord.Permissions()
        permissions.update(send_messages=False, read_messages=True, connect=True, speak=True, read_messages_history=True, use_external_emojis=True)
        await role.edit(reason=f"Server Lockdown By {ctx.author.name}", permissions=permissions)
        try: await ctx.send(f":lock: Server Locked!!")
        except: pass

    @unlock.command(name="server")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def ulserver(self, ctx):
        role = ctx.guild.default_role
        permissions = discord.Permissions()
        permissions.update(send_messages=True, read_messages=True, connect=True, speak=True, read_messages_history=True, use_external_emojis=True, add_reactions=True)
        await role.edit(reason=f"Server Unlocked By {ctx.author.name}", permissions=permissions)
        try: await ctx.send(f":unlock: Server Unlocked!!")
        except: pass

def setup(client):
    client.add_cog(Moderation(client))