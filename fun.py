#########################################################################################
# MIT License                                                                           #
#                                                                                       #
# Copyright (c) 2021 SumBot team                                                        #
#                                                                                       #
# Permission is hereby granted, free of charge, to any person obtaining a copy          #
# of this software and associated documentation files (the "Software"), to deal         #
# in the Software without restriction, including without limitation the rights          #
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell             #
# copies of the Software, and to permit persons to whom the Software is                 #
# furnished to do so, subject to the following conditions:                              #
#                                                                                       #
# The above copyright notice and this permission notice shall be included in all        #
# copies or substantial portions of the Software.                                       #
#                                                                                       #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR            #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,              #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE           #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER                #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,         #
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE         #
# SOFTWARE.                                                                             #
# © 2021 GitHub, Inc.                                                                   #
#########################################################################################

import io
import random
from random import randint
import aiohttp
import discord
import pyfiglet
from discord.ext import commands
from db import db
from PIL import Image
import os
from PIL import ImageFont, ImageDraw, ImageOps
from discord.ext.commands import command, guild_only, has_permissions, bot_has_permissions, cooldown


class Fun(commands.Cog):
    """
    Fun commands
    """

    def __init__(self, client):
        self.client = client
        self.db = db.db
        self.cr = db.cr

    @command(help='To take a random number', usage="roll [number]")
    @guild_only()
    @cooldown(1, 3, commands.BucketType.user)
    async def roll(self, ctx, faces: int = 100):
        msg = "You have got"
        if db.get_lang(ctx) == "ar":
            msg = "لقد حصلت على"
        number = randint(1, faces)
        await ctx.send(embed=discord.Embed(
            description=f'**🎲 {msg} `{str(number)}` !**',
            color=discord.Colour.green()
        ))

    @command(name='iq', help="IQ proportions to fun", usage="iq [@member]")
    @guild_only()
    @cooldown(1, 3, commands.BucketType.user)
    async def smart(self, ctx, member: discord.Member = None):
        # Open template and get drawing context
        im = Image.open('img/progress.png').convert('RGB')
        draw = ImageDraw.Draw(im)

        # Cyan-ish fill colour
        color = (98, 211, 245)

        # Draw circle at right end of progress bar
        x, y, diam = 254, 8, 34
        draw.ellipse([x, y, x + diam, y + diam], fill=color)

        # Flood-fill from extreme left of progress bar area to behind circle
        # await ctx.send(file=discord.File("img/result.png"))
        if member == None:
            member = ctx.author

            nam = randint(1, 100)
            msg = "progress IQ for"
            if db.get_lang(ctx) == "ar":
                msg = "نسبه ذكاء"
            embed = discord.Embed(
                description=f'{msg} {member.display_name} = `{nam}`',
                color=ctx.author.color,
                timestamp=ctx.message.created_at)
            embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
            embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)

            ImageDraw.floodfill(im, xy=(nam, 24), value=color, thresh=100)
            im.save('img/result.png')
            file = discord.File(f"./img/result.png", filename="result.png")
            embed.set_image(url="attachment://result.png")
            await ctx.send(file=file, embed=embed)
            os.remove("/img/result.png")

        elif member == self.client.user:
            sumbot_iq = "SumBot is smarter than your father `:-)`"
            if db.get_lang(ctx) == "ar":
                sumbot_iq = "سوم بوت اذكى من ابوك `:-)`"
            embed = discord.Embed(
                description=sumbot_iq,
                color=ctx.author.color,
                timestamp=ctx.message.created_at)
            embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
            embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
            ImageDraw.floodfill(im, xy=(14, 24), value=color, thresh=100)
            file = discord.File(f"./img/result.png", filename="result.png")
            im.save('img/result.png')
            embed.set_image(url="attachment://result.png")
            await ctx.send(file=file, embed=embed)
            os.remove("/img/result.png")

        else:
            msg = "progress IQ for"
            if db.get_lang(ctx) == "ar":
                msg = "نسبه ذكاء"
            nam = randint(1, 100)
            embed = discord.Embed(
                description=f'{msg} {member.display_name} = `{nam}`',
                color=ctx.author.color,
                timestamp=ctx.message.created_at)
            embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
            embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
            ImageDraw.floodfill(im, xy=(nam, 24), value=color, thresh=int(nam / 1.75), border=None)
            im.save('img/result.png')
            file = discord.File(f"./img/result.png", filename="result.png")
            embed.set_image(url="attachment://result.png")
            await ctx.send(file=file, embed=embed)
            os.remove("/img/result.png")

    @command(help='Rewrite what you say jotting', usage="tag <message>")
    @cooldown(1, 3, commands.BucketType.user)
    @guild_only()
    async def tag(self, ctx, *, arg: str):
        if ctx.author.bot:
            return
        msg = "The number of characters must be less than `20`"
        art = pyfiglet.figlet_format(arg)
        if db.get_lang(ctx) == "ar":
            msg = "يجب أن يكون عدد الأحرف أقل من `20`"
        if len(arg) >= 20:
            await ctx.send(embed=discord.Embed(
                description="❌ {}".format(msg),
                color=discord.Colour.red()
            ))
            return
        await ctx.send(f"""```javascript\n{art}```""")

    @command(help='Rewrite what you say awesome ASCII', usage="ascll <message>")
    @cooldown(1, 3, commands.BucketType.user)
    @guild_only()
    async def ascll(self, ctx, *, arg: str):
        msg = "The number of characters must be less than `30`"
        font = [
            'slant',
            "3-d",
            "3x5",
            "5lineoblique",
            "alphabet",
            "letters",
            "bubble",
            "bulbhead",
            "digital"
        ]
        ran = random.choice(font)
        if db.get_lang(ctx) == "ar":
            msg = "يجب أن يكون عدد الأحرف أقل من `30`"
        if len(arg) >= 30:
            await ctx.send(embed=discord.Embed(
                description="❌ {}".format(msg),
                color=discord.Colour.red()
            ))
            return
        await ctx.send(f"""```javascript\n{pyfiglet.figlet_format(text=arg, font=ran)}```""")

    @command(aliases=['reverse', 'rev'], help='To revers your message', usage='revers <message>')
    @guild_only()
    @cooldown(1, 3, commands.BucketType.user)
    async def revers(self, ctx, *, message):
        await ctx.send(embed=discord.Embed(
            description=message[::-1],
            color=discord.Colour.green()
        ))

    @command(help='To make a competitive match between two people', usage="vs <@member1> <@member2>")
    @guild_only()
    @cooldown(1, 3, commands.BucketType.user)
    async def vs(self, ctx, member1: discord.Member, member2: discord.Member):
        member1 = member1.avatar_url_as(size=1024, format=None, static_format='png')
        member2 = member2.avatar_url_as(size=1024, format=None, static_format='png')

        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                    f"https://nekobot.xyz/api/imagegen?type=whowouldwin&user1={member1}&user2={member2}") as r:
                res = await r.json()
                embed = discord.Embed(
                    color=ctx.author.color,
                    description=f"[Link img]({res['message']})",
                    timestamp=ctx.message.created_at
                )
                embed.set_image(url=res["message"])
                embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
                embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
                await ctx.send(embed=embed)

    @command(help='Modify the profile picture to become funny', usage="magik [@member] [intensity]")
    @guild_only()
    @cooldown(1, 30, commands.BucketType.user)
    async def magik(self, ctx, member: discord.Member, intensity: int = 5):
        member = member if member else ctx.author
        avatar = member.avatar_url_as(size=1024, format=None, static_format='png')
        msg = "Processing the image please wait!"
        if db.get_lang(ctx):
            msg = "جاري معالجة الصورة يرجى الانتظار!"
        message = await ctx.send(embed=discord.Embed(
            description=f"{str(self.client.get_emoji(797134049939816478))} — **{msg}**",
            color=discord.Colour.green()
        ))
        await message.delete(delay=15)

        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://nekobot.xyz/api/imagegen?type=magik&image={avatar}&intensity={intensity}") as r:
                res = await r.json()
                embed = discord.Embed(
                    color=ctx.author.color,
                    description=f"[Magik]({res['message']})",
                    timestamp=ctx.message.created_at
                )
                embed.set_image(url=res["message"])
                embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
                embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
                await ctx.send(embed=embed)

    @command(help="Makes your image like you are dangerous", usage="triggered [@member]")
    @guild_only()
    @cooldown(1, 3, commands.BucketType.user)
    async def triggered(self, ctx, member: discord.Member):
        member = member if member else ctx.author
        picture = member.avatar_url_as(size=1024, format=None, static_format='png')
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://some-random-api.ml/canvas/triggered?avatar={picture}") as r:
                res = io.BytesIO(await r.read())
                triggered_file = discord.File(res, filename=f"triggered.gif")
                embed = discord.Embed(
                    color=ctx.author.color,
                    description=f"Triggered",
                    timestamp=ctx.message.created_at
                )
                embed.set_image(url="attachment://triggered.gif")
                embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
                embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
                await ctx.send(embed=embed, file=triggered_file)

    @command(help='to show random img memes', usage="memes")
    @guild_only()
    @cooldown(1, 3, commands.BucketType.user)
    async def memes(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/meme") as r:
                res = await r.json()
                embed = discord.Embed(
                    color=ctx.author.color,
                    description=f"[Link Img]({res['image']})",
                    timestamp=ctx.message.created_at
                )
                embed.set_image(url=res['image'])
                embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
                embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
                await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Fun(client))
