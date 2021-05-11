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
from discord.ext import commands
import random
import asyncio
from discord.ext.commands import command, cooldown, has_permissions, bot_has_guild_permissions, guild_only, group
from db import db


class Giveaway(commands.Cog):
    """
    Giveaway commands
    """
    def __init__(self, client):
        self.client = client
        self.db = db.db
        self.cr = db.cr

    @command(name='gcreate', help='to made giveaway advanced settings', usage='gcreate')
    @guild_only()
    @has_permissions(administrator=True)
    @cooldown(1, 3, commands.BucketType.user)
    async def giveaway_create(self, ctx):
        questions = [
            "Which channel should it be hosted in?",
            "What should be the duration of the giveaway? (s|m|h|d|mo)",
            "What is the prize of the giveaway?"]
        if db.get_lang(ctx) == "ar":
            questions[0] = "ما هي الروم التي يجب استضافتها؟"
            questions[1] = "حدد الوقت المناسب؟ (s|m|h|d|mo)"
            questions[2] = "ما هي جائزة الجفاوي؟"
        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel 
        for i in questions:
            await ctx.send(embed=discord.Embed(
                description=i,
                color=discord.Colour.red()
            ))
            try:
                msg = await self.client.wait_for('message', timeout=120.0, check=check)
            except asyncio.TimeoutError:
                msg = "You didn\'t answer in time, please be quicker next time!"
                if db.get_lang(ctx) == "ar":
                    msg = "لم تجب في الوقت المناسب ، من فضلك كن أسرع في المرة القادمة!"
                await ctx.send(embed=discord.Embed(
                    description=msg,
                    color=discord.Colour.red()
            ))
                return
            else:
                answers.append(msg.content)
        try:

            c_id = int(answers[0][2:-1])
        except:
            msg = f"You didn't mention a channel properly. Do it like this {ctx.channel.mention} next time."
            if db.get_lang(ctx) == "ar":
                msg = f"لم تذكر القناة بشكل صحيح. افعل ذلك مثل {ctx.channel.mention} في المرة القادمة."
            await ctx.send(embed=discord.Embed(
                description=msg,
                color=discord.Colour.red()
            ))
            return
        channel = self.client.get_channel(c_id)

        def convert(timer):

            pos = ["s", "m", "h", "d", "mo"]
            time_dict = {"s": 1, "m": 60, "h": 60*60, "d": 3600*24, "mo": 86400*30}
            unit = timer[-1]
            if unit not in pos:
                return -1
            try:
                val = int(timer[:-1])

            except:
                return -2

            return val * time_dict[unit]

        time = convert(answers[1])
        if time == -1:
            msg = f"You didn't answer the time with a proper unit. Use (s|m|h|d|mo) next time!"
            if db.get_lang(ctx) == "ar":
                msg = "لم ترد على الوقت بوحدة مناسبة. استخدم (s|m|h|d|mo) في المرة القادمة!"
            await ctx.send(embed=discord.Embed(
                description=msg,
                color=discord.Colour.red()
            ))
            return
        elif time == -2:
            msg = "The time must be an integer. Please enter an integer next time!!"
            if db.get_lang(ctx) == "ar":
                msg = "يجب أن يكون الوقت عددًا صحيحًا. الرجاء إدخال عدد صحيح في المرة القادمة!!"
            await ctx.send(embed=discord.Embed(
                description=msg,
                color=discord.Colour.red()
            ))
            return            
        prize = answers[2]
        message = f"The Giveaway will be in {channel.mention} and will last `{answers[1]}`!"
        if db.get_lang(ctx) == "ar":
            message = f"الجفاوي في روم {channel.mention} و الوقت المحدد هو `{answers[1]}`!"
        await ctx.send(embed=discord.Embed(
                description=message,
                color=discord.Colour.green()
            ))
        pr, end, host, win = "prize", "Ends At", "Host By", "winner"
        if db.get_lang(ctx) == "ar":
            pr, end, host, win = "الجائزه", "ينتهي بعد", "المسؤول", "الفائز"
        embed = discord.Embed(
            color=ctx.author.color,
            timestamp=ctx.message.created_at,
            description='**{}:** {}\n**{}** {}\n**{}:** {}'.format(pr, prize, end, answers[1], host, ctx.author.mention))
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        give = "giveaway"
        if db.get_lang(ctx) == "ar":
            give = "الجيفاوي"
        my_msg = await channel.send(f'🎉 {give}! 🎉', embed=embed)
        await my_msg.add_reaction("🎉")
        await asyncio.sleep(time)
        new_msg = await channel.fetch_message(my_msg.id)
        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))
        winner = random.choice(users)

        embed = discord.Embed(
            color=ctx.author.color,
            timestamp=ctx.message.created_at,
            description="**{}:** {}\n**{}:** {}\n**{}:** {}".format(
                pr, prize,
                host, ctx.author.mention,
                win, winner.mention))
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        await my_msg.edit(embed=embed)
        msg = f"the winner is {winner.mention} Won in **{prize}**!"
        if db.get_lang(ctx) == "ar":
            msg = f"الفائز هو {winner.mention} فاز في ** {prize} **!"
        await channel.send(embed=discord.Embed(
                description=msg,
                color=discord.Colour.red()
            ))

    @command(help='to re-winner in giveaway', usage="reroll <#channel> <message_id>")
    @guild_only()
    @has_permissions(administrator=True)
    @cooldown(1, 3, commands.BucketType.user)
    async def reroll(self, ctx, channel: discord.TextChannel, message_id: int):
        msg, msg1 = "The id was entered incorrectly.", "the winner is"
        try:
            new_msg = await channel.fetch_message(message_id)

        except:
            if db.get_lang(ctx) == "ar":
                msg, msg1 = "تم إدخال الايدي بشكل غير صحيح.", "الفائز هو"
            await ctx.send(embed=discord.Embed(
                description=msg,
                color=discord.Colour.red()
            ))
            return
        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))
        winner = random.choice(users)
        await channel.send(embed=discord.Embed(
                description=f"{msg1} {winner.mention}.!",
                color=discord.Colour.green()
            ))

    @command(name='gstart', help='to made giveaway quick', usage="gstart <time> <prize>")
    @guild_only()
    @has_permissions(administrator=True)
    @cooldown(1, 3, commands.BucketType.user)
    async def giveaway_start(self, ctx, time, *, prize: str):
        await ctx.message.delete()

        def convert(time):
            pos = ["s", "m", "h", "d", "mo"]
            time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600*24, "mo": 86400*30}
            unit = time[-1]
            if unit not in pos:
                return -1
            try:
                val = int(time[:-1])
            except:
                return -2
            return val * time_dict[unit]
        pr, end, host, win = "prize", "Ends At", "Host By", "winner"
        if db.get_lang(ctx) == "ar":
            pr, end, host, win = "الجائزه", "ينتهي بعد", "المسؤول", "الفائز"
        time1 = convert(time)
        embed = discord.Embed(
            color=ctx.author.color,
            timestamp=ctx.message.created_at,
            description='**{}:** {}\n**{}:** {}\n**{}:** {}'.format(pr, prize, end, time, host, ctx.author.mention))
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        give = "giveaway"
        if db.get_lang(ctx) == "ar":
            give = "الجيفاوي"
        my_msg = await ctx.send(f'🎉 {give}! 🎉', embed=embed)
        await my_msg.add_reaction("🎉")

        await asyncio.sleep(time1)

        new_msg = await ctx.channel.fetch_message(my_msg.id)
        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))
        winner = random.choice(users)
        embed = discord.Embed(
            color=ctx.author.color,
            timestamp=ctx.message.created_at,
            description='**{}:** {}\n**{}:** {}\n**{}:** {}'.format(
                pr, prize,
                host, ctx.author.mention,
                win, winner.mention))
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        await my_msg.edit(embed=embed)
        msg = f"the winner is {winner.mention} Won in **{prize}**!"
        if db.get_lang(ctx) == "ar":
            msg = f"الفائز هو {winner.mention} فاز في ** {prize} **!"
        await ctx.send(embed=discord.Embed(
                description=msg,
                color=discord.Colour.green()
            ))

               
def setup(client):
    client.add_cog(Giveaway(client))
