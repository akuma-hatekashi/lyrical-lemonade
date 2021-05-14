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

import discord
from discord import Colour, Embed
from discord.ext import commands
import time
from PIL import Image
from io import BytesIO
from PIL import ImageFont, ImageDraw, ImageOps
import arabic_reshaper
import qrcode
import os
from discord.ext.commands import command, cooldown, guild_only, group
from bidi.algorithm import get_display
from db.db import *


class General(commands.Cog):
    """
    General commands
    """
    def __init__(self, client):
        self.client = client

    # @command(aliases=['em'], help='get link emoji', usage="em <emoji>")
    # @guild_only()
    # @cooldown(1, 3, commands.BucketType.user)
    # async def emoji(self, ctx, emoji):
    #     id = emoji.split(":")[2].split(">")[0]
    #     print(id)
    #     emoji = await self.client.fetch_emoji(emoji_id=818209893982142464)
    #     print(emoji)
    #     link = f"https://cdn.discordapp.com/emojis/{emoji.id}.png"
    #     if emoji.animated:
    #         link = f"https://cdn.discordapp.com/emojis/{emoji.id}.gif"
    #     await ctx.send(link)

    @command(aliases=['inv'], help='invite bot', description='To invite the bot in your server', usage="invite")
    @guild_only()
    @cooldown(1, 3, commands.BucketType.user)
    async def invite(self, ctx):
        description = f'''
**Thanks from use the SumBot ✨**
`-` Invite SumBot: [invite](https://sumbot.xyz/invite)
`-` support SumBot: [support](https://sumbot.xyz/support)
`-` Dashboard SumBot: [dashboard](https://sumbot.xyz)
        '''
        if get_lang(ctx) == "ar":
            description = f'''
**شكرا لاستخدامك سام بوت ✨**
`-` دعوعه سامبوت : [دعوه](https://sumbot.xyz/invite)
`-` الدعم الفني سامبوت : [دعم فني](https://sumbot.xyz/support)
`-` لوحة تحكم سامبوت : [لوحد تحكم](https://sumbot.xyz)
            '''
        embed = discord.Embed(
            description=description,
            color=Colour.red())
        m = "Requested By"
        if get_lang(ctx) == "ar":
            m = "بطلب من"
        embed.set_footer(text=f"{m}: {ctx.author}")
        await ctx.send(embed=embed)

    @command(invoke_without_command=True, help='To know the connection speed of the bot on the server', usage="ping")
    @guild_only()
    @cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx):
        before = time.monotonic()
        msg = await ctx.send("pong!!")
        ping = (time.monotonic() - before) * 1000
        await msg.edit(content="`-` Time taken: **{}ms**\n`-` Discord API: **{}ms**".format(
            int(ping),
            round(self.client.latency * 1000))
        )

    @group(invoke_without_command=True, help='To know the personal avatar', aliases=["ava"], usage="avatar [member]")
    @guild_only()
    @cooldown(1, 3, commands.BucketType.user)
    async def avatar(self, ctx, member: discord.Member = None):
        member = member if member else ctx.author
        avatar = [
            member.avatar_url_as(format="png"),
            member.avatar_url_as(format="jpg"),
            member.avatar_url_as(format="jpeg")
        ]
        dec = '**[png]({}) | [jpg]({}) | [jpeg]({}) **'.format(
            avatar[0], avatar[1], avatar[2])
        if member.is_avatar_animated():
            avatar.append(member.avatar_url_as(format="gif"))
            dec = '**[png]({}) | [jpg]({}) | [jpeg]({}) | [gif]({})**'.format(
                avatar[0], avatar[1], avatar[2], avatar[3]
            )
        embed = discord.Embed(
            title='avatar',
            description=dec, timestamp=ctx.message.created_at, color=Colour.random())
        embed.set_image(url=member.avatar_url_as(size=1024))
        await ctx.send(embed=embed)

    @avatar.command(help="To show avatar bot", usage="avatar bot")
    @guild_only()
    @cooldown(1, 3, commands.BucketType.user)
    async def bot(self, ctx):
        embed = discord.Embed(
            title="Bot avatar",
            description="[Bot avatar]({}).".format(self.client.user.avatar_url_as(size=1024, format="png")),
            colour=ctx.author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_image(url=self.client.user.avatar_url)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @avatar.command(aliases=["server"], help="to show guild icon", usage="avatar server")
    @guild_only()
    @cooldown(1, 3, commands.BucketType.user)
    async def server_avatar(self, ctx):
        embed = Embed(
            title="server icon",
            description=f"[icon]({ctx.guild.icon_url})",
            color=ctx.author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_image(url=ctx.guild.icon_url)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @command(name='bot', aliases=['botinfo', "info"], help='show bot info', usage="bot")
    @guild_only()
    @cooldown(1, 5, commands.BucketType.user)
    async def botinfo_command(self, ctx):
        embed = discord.Embed(
            timestamp=ctx.message.created_at,
            color=ctx.author.color,
            description=f"""
[Dashboard](https://sumbot.xyz) **|** [Invite](https://discord.com/api/oauth2/authorize?client_id=738120633430573176&permissions=8&scope=bot) **|** [support](https://sumbot.xyz/support) **|** [Vote](https://top.gg/bot/738120633430573176) **|** [github](https://github.com/SumBot/SumBot)
""")
        img = Image.open("./img/info_bot.jpg")  # import img
        draw = ImageDraw.Draw(img)  # draw img
        font = ImageFont.truetype("./font/Arial.ttf", size=60)  # font all text

        draw.text(
            [300, 140],
            F"{len(self.client.guilds)}",
            font=font,
            fill="#d9d9d9")

        draw.text(
            [380, 225],
            "Python",
            font=font,
            fill="#d9d9d9")

        draw.text(
            [290, 320],
            "discord.py",
            font=font,
            fill="#d9d9d9")

        img.save(f'./img/bot.png')  # save img
        file = discord.File(f"./img/bot.png", filename="botinfo.png")
        embed.set_image(url="attachment://botinfo.png")
        # embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(file=file, embed=embed)

    @command(pass_context=True, help='show server info', usage="server")
    @guild_only()
    @cooldown(1, 3, commands.BucketType.user)
    async def server_command(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(
            title='server info',
            timestamp=ctx.message.created_at,
            color=ctx.author.color
        )
        embed.add_field(name='📛 | Name', value=guild.name)
        embed.add_field(name='🆔 | guild id', value=guild.id)
        embed.add_field(name='👑 | Owner', value='<@' + str(guild.owner_id) + ">")
        embed.add_field(name='👥 | Members', value=guild.member_count)
        embed.add_field(
            name=f'channels({len(guild.channels)})',
            value=f'''
📣 Categories: {len(guild.categories)}
💬 text: {len(ctx.guild.text_channels)} 
🔊 voice: {len(ctx.guild.voice_channels)}''')
        embed.add_field(name='🕍 | created at', value=guild.created_at.strftime("%m/%d/%Y, %H:%M:%S %p"))
        embed.set_thumbnail(url=guild.icon_url)
        embed.set_author(name=self.client.user.display_name, icon_url=self.client.user.avatar_url)
        embed.set_footer(text='Requested by {}'.format(ctx.author.display_name), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @command(name="user", aliases=["id", "userinfo"], help='show user info', usage="user [@member]")
    @cooldown(1, 3, commands.BucketType.user)
    @guild_only()
    async def user(self, ctx, member: discord.Member = None):

        member = ctx.author if not member else member

        embed = discord.Embed(
            timestamp=ctx.message.created_at,
            color=ctx.author.color
        )

        embed.set_author(
            name=self.client.user,
            url="https://discord.com/oauth2/authorize?client_id=738120633430573176&permissions=8&scope=bot",
            icon_url=self.client.user.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url)
        embed.add_field(name="{} ╎ Member:".format(self.client.get_emoji(795052145635622942)), value=member.mention)
        embed.add_field(name="🆔 ╎ ID:", value=member.id)
        embed.add_field(name="{} ╎ Join At:".format(self.client.get_emoji(795053266111168562)), value=member.created_at.strftime("%Y/%m/%d"))
        embed.add_field(name="{} ╎ Join Server At:".format(self.client.get_emoji(795053825395654666)), value=member.joined_at.strftime("%Y/%m/%d"))
        roles = " ".join([role.mention for role in member.roles if role != ctx.guild.default_role])
        roles = "Nothing" if not roles else roles
        embed.add_field(name="{} ╎ Roles ({}):".format(self.client.get_emoji(795054968700403712), len(member.roles) - 1), value=roles, inline=False)

        await ctx.send(embed=embed)

    def cleanword(self, word):
        if len(word) == 1:
            return word
        if word[0] == word[1]:
            return self.cleanword(word[1:])
        return word[0] + self.cleanword(word[1:])

    @command(help='show the profile', usage="profile [member]")
    @guild_only()
    @cooldown(1, 10, commands.BucketType.user)
    async def profile(self, ctx, user: discord.Member = None):
        if user == None:
            user = ctx.author

        ava = user.avatar_url_as(size=128, format='png')  # save avatar user
        data = BytesIO(await ava.read())  # None
        pfp = Image.open(data)

        pfp = pfp.resize((94, 94))
        bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
        mask = Image.new('L', bigsize, 0)

        draw = ImageDraw.Draw(mask)

        draw.ellipse((0, 0) + bigsize, fill=255)

        mask = mask.resize(pfp.size, Image.ANTIALIAS)

        pfp.putalpha(mask)

        output = ImageOps.fit(pfp, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        output.save('./img/output.png')
        background = Image.open('./img/Profile_.png')

        draw = ImageDraw.Draw(background)  # draw img
        background.paste(pfp, (15, 14), pfp)

        font = ImageFont.truetype("font/Arial.ttf", size=24)  # font all text
        shadow_color = "white"  # shadow color all text
        stroke_width = 1  # stroke width
        color_stroke = f"{user.color}"  # color stroke

        username = user.name  # get user name
        user_tag = "#" + user.discriminator  # get user tag
        join_at = user.created_at.strftime("%Y/%m/%d")  # get join at
        user_id = user.id  # get user id

        reshaped_text = arabic_reshaper.reshape(username)
        bidi_text = get_display(reshaped_text)
        text = self.cleanword(word=bidi_text)
        if len(text) > 9:
            text = text[:10] + "..."
        elif len(text) > 8:
            text = text[:9] + ".."
        elif len(text) > 7:
            text = text[:8] + "."
        # fonts and size name
        # draw.text(
        #     [142, 129],
        #     text,  # add arabic
        #     font=font,
        #     stroke_fill="black"
        # )
        draw.text(
            [141, 128],
            text,  # add arabic
            font=font,
            fill=shadow_color,
            stroke_width=stroke_width,
            stroke_fill=color_stroke
        )

        # fonts and size tag
        draw.text(
            [141, 173],
            user_tag,
            font=font,
            fill=shadow_color,
            stroke_width=stroke_width,
            stroke_fill=color_stroke)

        # fonts and size join at
        draw.text(
            [141, 217],
            join_at,
            font=font,
            fill=shadow_color,
            stroke_width=stroke_width,
            stroke_fill=color_stroke)

        # fonts and size user id
        draw.text(
            [46, 259],
            str(user_id),
            font=font,
            fill=shadow_color,
            stroke_width=stroke_width,
            stroke_fill=color_stroke)

        background.save('./img/profile.png')  # save img

        await ctx.send(file=discord.File(f"./img/profile.png"))  # send profile img
        os.remove("./img/profile.png")
        os.remove("./img/output.png")

    @command(aliases=["qrcode", "qr_code", "qr-code"], help="To make your own QR code", usage="qr [date]")
    @cooldown(1, 3, commands.BucketType.user)
    @guild_only()
    async def qr(self, ctx, date):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(date)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save("img/qr.png")
        await ctx.send(file=discord.File("img/qr.png"))
        os.remove("img/qr.png")

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.id in get_cooldown():
            return
        if ctx.content == f"<@!{self.client.user.id}>":
            cr.execute("INSERT OR IGNORE INTO cooldown(user_id) VALUES(?)", (ctx.author.id,))
            commit()
            embed = Embed(
                description="""
**Thanks form use the SumBot ✨**
`-` __**All commands:**__
[**`sumbot.xyz/commands`**](https://sumbot.xyz/commands)
`-` __**Invite sumbot:**__
[**`sumbot.xyz/invite`**](https://sumbot.xyz/invite)
`-` __**Support SumBot:**__
[**`sumbot.xyz/support`**](https://sumbot.xyz/support)
""",
                color=Colour.red(),
                # timestamp=ctx.message.created_at
            )
            embed.set_footer(text=f"Prefix in the server: {get_prefix(ctx)}")
            embed.set_author(name=f"{self.client.user.name} | Total commands: {len(self.client.commands)}", icon_url=self.client.user.avatar_url)
            embed.set_thumbnail(url=self.client.user.avatar_url)
            await ctx.channel.send(embed=embed, delete_after=5)
            return


def setup(client):
    client.add_cog(General(client))
