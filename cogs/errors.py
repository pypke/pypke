import discord
import dislash
from discord.ext import commands

class Errors(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You can't do that?.", delete_after=5)
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Bot doesn't have required permission to do that mind giving the bot the required perms!!.\nOr you are trying to do it to a member with higher role than the bot", delete_after=5)
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(f"That's not a valid command! Do `{self.client.prefix}help` for the list of commands...", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please enter the required argument!", delete_after=5)
        elif isinstance(error, commands.NotOwner):
            await ctx.send("Only Owner Of The Bot Can Use This Command!!")
        elif isinstance(error, commands.UserNotFound):
            await ctx.send("User With That Name Not Found. Try Again!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Member With That Name Not Found. Try Again!")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send("Channel Not Found. Try Again!")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send("This Command Is On Cooldown So, Chill!")
        elif isinstance(error, RuntimeWarning):
            pass
        elif isinstance(error, commands.ExtensionNotLoaded):
            pass
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            pass
        elif isinstance(error, commands.ExtensionNotFound):
            pass
        elif isinstance(error, commands.CommandInvokeError):
            if ctx.channel.id == 887258899726606336:
                await ctx.send(f"Oops Looks Like Something Went Wrong!!\nDetails:-`{error}`", delete_after=5)
                raise error
            else:
                raise error
        else:
            raise error
            
def setup(client):
    client.add_cog(Errors(client))