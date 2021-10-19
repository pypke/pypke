import discord, io, aiohttp
from discord.ext import commands
from urllib.parse import quote_plus
from PIL import Image

class Images(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="youtube", description="Makes a fake Youtube Comment")
    async def youtube(self, ctx, *, comment: str):
        if comment.startswith("<@"):
            user = discord.utils.get(self.client.get_all_members(), id=comment[2:19])
        else:
            user = ctx.author
        username = quote_plus(user.name)
        comment = quote_plus(comment)
        embed = discord.Embed(title="YouTube Comment", description=discord.Embed.Empty, color=discord.Color.red())
        link = f"https://some-random-api.ml/canvas/youtube-comment?username={username}&comment={comment}&avatar={user.avatar.url}&dark=true"
        embed.set_image(url=link)
        return await ctx.send(embed=embed)

    @commands.command(name="image", description="Change The Users Avatar Into Various Types.")
    async def image(self, ctx, option:str = None, user: discord.Member = None,):
        user = user or ctx.author
        valid_options = ['gay', 'glass', 'wasted', 'passed', 'jail', 'comrade', 'triggered']
        if not option:
            embed = discord.Embed(
                                title="Image Commands", 
                                description=f"These are the valid types.\n\n" + "\n\n".join(
                                                                                    f"**{str(option).capitalize()}:** `#image {option}`"
                                                                                    for i, option in enumerate(valid_options)
                                                                                ), 
                                color=0xF7770F)
            embed.set_thumbnail(url=self.client.user.avatar.url)
            return await ctx.send(embed=embed)
        if option not in valid_options:
            await ctx.send("Not, A Valid Option!")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://some-random-api.ml/canvas/{option}?avatar={user.avatar.with_format("png")}') as pic:
                if option == "triggered":
                    ext = "gif"
                else:
                    ext = "png"
                if 300 > pic.status >= 200:
                    image = io.BytesIO(await pic.read())
                    file = discord.File(image, f"{user.id}.{ext}")
                    return await ctx.send(file=file)
    
    @commands.command(name="color", description="Visualize a color.", aliases=['colour'])
    async def color(self, ctx, color=None):
        if not color:
            await ctx.send("You need to specify Hex (Example: 000000) or RGB (Example: 100, 100, 100) color value.")
        elif color:
            try:
                r, g, b = color.split(",")
            except:
                hex = color

            if hex:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'http://thecolorapi.com/id?hex={color}') as r:
                        data = await r.json()
                        hex = data['hex']['value']
                        r, g, b = data['rgb']['r'], data['rgb']['g'], data['rgb']['b']
                        h, s, l = data['hsl']['h'], data['hsl']['s'], data['hsl']['l']
                        embed = discord.Embed(
                                                title=data['name']['value'],
                                                color=discord.Color.from_rgb(r, g, b)
                                            )
                        embed.add_field(name='Hex', value=hex)
                        embed.add_field(name='RGB', value=f"{r}, {g}, {b}")
                        embed.add_field(name='HSL', value=f"{h}, {s}, {l}")
                        embed.set_image(url=f"https://serux.pro/rendercolour?hex={color}&height=100&width=225")
                        
                        return await ctx.reply(embed=embed, mention_author=False)

def setup(client):
    client.add_cog(Images(client))