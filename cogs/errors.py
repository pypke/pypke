import discord
from discord.ext import commands

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You can't do that?.", delete_after=5)
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("That's not a valid command! Do `#help` for the list of commands...", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please enter the required argument!", delete_after=5)
        elif isinstance(error, commands.NotOwner):
            await ctx.send("You Don't Own This Bot!!")
        elif isinstance(error, RuntimeWarning):
            pass
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.channel.purge(limit=1)
            await ctx.send(f"Oops Looks Like Something Went Wrong!! Details:-`{error}`", delete_after=5)
            raise error
        else:
            raise error
            
def setup(bot):
    bot.add_cog(Errors(bot))