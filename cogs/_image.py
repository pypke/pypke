import  io, aiohttp, PIL
from PIL import Image
from asyncdagpi import Client, ImageFeatures
from urllib.parse import quote_plus
from typing import Optional, Union

import discord
from discord.ext import commands

DAGPI_KEY = "MTYzNzE4MTAyMA.Ey9BeBE87uBOMt3epgNAp0IZlnnWzgIz.440c8c658a6169b3"
ImgClient = Client(DAGPI_KEY)


class Images(commands.Cog, description="This modules handles image manupulation stuff."):
    def __init__(self, client):
        self.client = client

    @commands.command(
        name="pixelate",
        description="Pixelate avatar image."
    )
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def pixelate_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.pixel(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="mirror",
        description="Mirror the avatar along the y-axis."
    )
    async def mirror_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.mirror(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="flip",
        description="Flip an image."
    )
    async def flip_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.flip(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="colors",
        description="Image with the colors present in the image."
    )
    async def colors_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.colors(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="america",
        description="Stars?"
    )
    async def america_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.america(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="communism",
        description="Support the soviet union comrade. Let the red flag fly!"
    )
    async def communism_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.communism(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="triggered",
        description= "Allows you to get a triggered gif."
    )
    async def triggered_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.triggered(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="expand",
        description= "Animation that streches an image."
    )
    async def expand_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.expand(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)
        
    @commands.command(
        name="wasted",
        description="Allows you to get an image with GTA V Wasted screen"
    )
    async def wasted_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

    @commands.command(
        name="sketch",
        description="Cool efffect that shows how an image would have been created by an artist."
    )
    async def sketch_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author


        img = await ImgClient.image_process(ImageFeatures.sketch(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="spin",
        description="You spin me right round baby."
    )
    async def spin_command (self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author


        img = await ImgClient.image_process(ImageFeatures.spin(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="petpet",
        description="Petpet someone."
    )
    async def petpet_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.petpet(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="bonk",
        description="Get bonked."
    )
    async def bonk_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.bonk(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)
    
    @commands.command(
        name="bomb",
        description="Explosion."
    )
    async def bomb_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.bomb(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

   
    @commands.command(
        name="shake",
        description="Shake it."
    )
    async def shake_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.sh(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="invert",
        description="Allows you to get an image with an inverted color effect."
    )
    async def invert_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.invert(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="sobel",
        description="Allows you to get an image with the sobel effect."
    )
    async def sobel_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.sobel(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)


    @commands.command(
        name="hog",
        description="Histogram of Oriented Gradients for an image."
    )
    async def hog_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.hog(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="triangle",
        description="Cool triangle effect for an image."
    )
    async def triangle_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.triangle(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="blur",
        description="Blurs a given image."
    )
    async def blur_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.blur(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="rgb",
        description="Get an RGB graph of an image's colors.Headers."
    )
    async def rgb_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.rgb(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)


    @commands.command(
        name="angel",
        description="Image on the Angels face."
    )
    async def angel_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.angel(), member.avatar.url) 
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="satan",
        description="Image on the Angels face."
    )
    async def satan_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.satan(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="delete",
        description="Generates a windows error meme based on a given image."
    )
    async def delete_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.delete(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="fedora",
        description="Tips fedora in appreciation. Perry the Platypus."
    )
    async def fedora_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.fedora(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="lego",
        description="Every group of pixels is a lego brick."
    )
    async def lego_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.lego(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="wanted",
        description="Wanted poster of an image."
    )
    async def wanted_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.wanted(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="stringify",
        description="Turn your image into a ball of yarn."
    )
    async def stringify_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.stringify(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="burn",
        description="Light your image on fire."
    )
    async def burn_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.burn(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="freeze",
        description="Blue ice like tint.."
    )
    async def freeze_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author
        img = await ImgClient.image_process(ImageFeatures.freeze(), member.avatar.url)
        
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="mosiac",
        description="Turn an image into a roman mosiac."
    )
    async def mosiac_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.mosiac(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)


    @commands.command(
        name="sithlord",
        description="Put an image on the Laughs in Sithlord meme."
    )
    async def sithlord_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        img = await ImgClient.image_process(ImageFeatures.sithlord(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="jail",
        description="Put an image behind bars."
    )
    async def jail_command(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author
        
        img = await ImgClient.image_process(ImageFeatures.jail(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="shatter",
        description="Put an image on the Laughs in Sithlord meme."
    )
    async def shatter_command (self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author
        
        img = await ImgClient.image_process(ImageFeatures.shatter(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)

    @commands.command(
        name="gay",
        description="Put an image on the Laughs in Sithlord meme."
    )
    async def shatter_command (self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author
        
        img = await ImgClient.image_process(ImageFeatures.shatter(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)


@commands.command(
        name="shatter",
        description="Put an image on the Laughs in Sithlord meme."
    )
    async def shatter_command (self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author
        
        img = await ImgClient.image_process(ImageFeatures.shatter(), member.avatar.url)
        file = discord.File(fp=img.image, filename=f"{ctx.command.qualified_name}.{img.format}")
        await ctx.send(file=file)
    # ------- ! -------- #   

    @commands.command(name="youtube", description="Makes a fake Youtube Comment")
    async def youtube(self, ctx, member: Optional[discord.Member], *, comment: str):
        member = member or ctx.author
        
        username = quote_plus(member.name)
        comment = quote_plus(comment)
        embed = discord.Embed(title="YouTube Comment", color=discord.Color.red())
        link = f"https://some-random-api.ml/canvas/youtube-comment?username={username}&comment={comment}&avatar={member.avatar.url}&dark=true"
        embed.set_image(url=link)
        return await ctx.send(embed=embed)

    @commands.command(
        name="wordcloud",
        description="Creates a wordcloud from your recent words."
    )
    async def wordcloud_command(self, ctx):
        print(self.client.cached_messages)
        json = {
            "format": "png",
            "fontFamily": "Karla",
            "scale": 'linear',
            "case": "upper",
            "backgroundColor": "000000",
            "useWordList": "True",
            'minWordLength': 4,
            'removeStopwords': "True",
            "text": "something you know"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post("https://quickchart.io/wordcloud", params=json) as r:
                if 300 > r.status > 200:
                    data = await r.json()
                else:
                    return await ctx.send("Can't fetch wordcloud for you right now!")

                await ctx.send(file=data)

    @commands.command(name="color", description="Visualize a color.", aliases=['colour'])
    async def color(self, ctx, color):
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