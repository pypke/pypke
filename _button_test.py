import discord
from discord.ext import commands

"""
class Button(discord.ui.View):

    @discord.ui.button(label="Click Here!!", url="www.youtube.com/watch?v=xvFZjo5PgG0", style=discord.ButtonStyle.primary)
    async def rick_roll(self, button: discord.ui.Button, interaction: discord.Interaction):
        button.style = discord.ButtonStyle.success
        button.disabled = True
        button.label = str("You Got RickRolled Lmfao!!")
        
        await interaction.response.edit_message(view=self)
"""
viewpanel=discord.ui.View(timeout=180)
viewpanel.add_item(discord.ui.Button(style=discord.ButtonStyle.primary, url="https://www.youtube.com/watch?v=xvFZjo5PgG0", label='Click Here!!'))

class ButtonBot(commands.Cog):
    def __init__(self, client):
        self.client = client
    

    @commands.command()
    async def surprise(self, ctx):
        await ctx.send("What's The Surprise? Click To Know\n\n", view=viewpanel)

def setup(client):
    client.add_cog(ButtonBot(client))