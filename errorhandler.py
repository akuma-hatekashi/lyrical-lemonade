import discord
from discord import Embed, Colour
from db import db
from discord.ext import commands, tasks
import time


t = True

def error_en(ctx, used=None, description=None, aliases=None, type=None):
    embed = Embed(
        description="> **Used:** `{}{}`\n**> Description:** `{}` \n> **Aliases:** `{}`\n> **Type:** `{}`".format(
            db.get_prefix(ctx=ctx),
            used,
            description,
            aliases,
            type
        ), color=Colour.red())
    return embed


def error_ar(ctx, used=None, description=None, aliases=None, type=None):
    embed = Embed(
        description="> **الأستعمال:** `{}{}`\n> **الوصف:** `{}` \n> **الأختصارات:** `{}`\n> "
                    "**النوع:** `{}`".format(
            db.get_prefix(ctx=ctx),
            used,
            description,
            aliases,
            type
        ), color=Colour.red())
    return embed


def error_permissions_en():
    embed = Embed(
        description="> 🙄 You don't have permissions",
        color=Colour.red())
    return embed


def error_permissions_ar():
    embed = Embed(
        description="> 🙄 ليس لديك أذونات كافيه",
        color=Colour.red())
    return embed


def bot_missing_permissions_en():
    embed = Embed(
        description='> ❌ I do not have permissions',
        color=Colour.red()
    )
    return embed


def bot_missing_permissions_ar():
    embed = Embed(
        description='> ❌ ليس لدي أذونات كافيه',
        color=Colour.red()
    )
    return embed


def channel_not_found_en():
    embed = Embed(
        description="> ❌ I could not find this channel",
        color=Colour.red()
    )
    return embed


def channel_not_found_ar():
    embed = Embed(
        description="> ❌ لم أجد هذه الروم",
        color=Colour.red()
    )
    return embed


def member_not_found_en():
    embed = Embed(
        description="> ❌ I could not find this member",
        color=Colour.red()
    )
    return embed


def member_not_found_ar():
    embed = Embed(
        description="> ❌ لم أجد هذا العضو",
        color=Colour.red()
    )
    return embed


def cooldown_er(error):
    m, s = divmod(error.retry_after, 60)
    embed = discord.Embed(
        description="> ❌ Command Cooldown, please wait `{}` and try again".format("%02d seconds" % s),
        color=0xf7072b
    )
    return embed


def cooldown_ar(error):
    m, s = divmod(error.retry_after, 60)
    embed = discord.Embed(
        description="> يرجى الانتظار `{}` و المحاوله مرا اخرا".format("%02d ثانيه" % s),
        color=0xf7072b
    )
    return embed


def winner_not_find_en():
    embed = discord.Embed(
        description="> ❌ I can't find a winner",
        color=discord.Colour.red())
    return embed


def winner_not_find_ar():
    embed = discord.Embed(
        description="> ❌ لا يمكنني العثور على فائز",
        color=discord.Colour.red())
    return embed


class ErrorHandler(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.cooldown = []

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # print(db.get_cooldown())
        if ctx.author.id in db.get_cooldown():
            return
        elif isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            await ctx.send(embed=discord.Embed(
                description=f"This command is currently **on cooldown** for ,Please **try again in** `{'%02d seconds' % (s,)}`.",
                color=discord.Colour.red()
            ),  delete_after=2)

            db.cr.execute("INSERT OR IGNORE INTO cooldown(user_id) VALUES(?)", (ctx.author.id,))
            db.commit()
            return
        elif isinstance(ctx.channel, discord.channel.DMChannel):
            return
        elif isinstance(error, commands.errors.MemberNotFound):
            embed = member_not_found_en()
            if db.get_lang(ctx) == "ar":
                embed = member_not_found_ar()
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            aliases = []
            if ctx.command.aliases == []:
                aliases = None
            else:
                aliases = ", ".join(ctx.command.aliases)
            embed = discord.Embed(
                description=f"**command:** {ctx.command.name}\n\
**help:** {ctx.command.help}\n\
**used:** {db.get_prefix(ctx)}{ctx.command.usage}\n\
**aliases:** {aliases}\n",
                color=Colour.red()
            ).set_author(name=ctx.command.cog_name)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.errors.BadArgument):
            aliases = []
            if ctx.command.aliases == []:
                aliases = None
            else:
                aliases = ", ".join(ctx.command.aliases)
            embed = discord.Embed(
                description=f"**command:** {ctx.command.name}\n\
**help:** {ctx.command.help}\n\
**used:** {db.get_prefix(ctx)}{ctx.command.usage}\n\
**aliases:** {aliases}\n",
                color=Colour.red()
            ).set_author(name=ctx.command.cog_name)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(error)
        else:
            pass


def setup(client):
    client.add_cog(ErrorHandler(client))
