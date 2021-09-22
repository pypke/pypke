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
            await ctx.send("Bot doesn't have required permission to do that mind giving the bot the required perms!!.", delete_after=5)
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(f"That's not a valid command! Do `{self.client.prefix}help` for the list of commands...", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please enter the required argument!", delete_after=5)
        elif isinstance(error, commands.NotOwner):
            await ctx.send("You Don't Own This Bot!!")
        elif isinstance(error, commands.UserNotFound):
            await ctx.send("There's no user named that please trying mention the user or the users id eg- 578545334578.")
        elif isinstance(error, RuntimeWarning):
            pass
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.channel.purge(limit=1)
            await ctx.send(f"Oops Looks Like Something Went Wrong!! Details:-`{error}`", delete_after=5)
            raise error
        else:
            raise error
            
def setup(client):
    client.add_cog(Errors(client))