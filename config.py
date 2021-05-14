import discord
from discord.ext import commands
from discord import Embed, Colour
from discord.ext.commands import guild_only, has_permissions, group, cooldown
from db.db import *


class Config(commands.Cog):
    def __init__(self, client):
        self.client = client

    @group(invoke_without_command=True, name="config", aliases=["settings"], usage="config")
    @has_permissions(manage_guild=True)
    @guild_only()
    @cooldown(1, 10, commands.BucketType.guild)
    async def config_commands(self, ctx):
        m = "**{0}config lang** - to set the language in your guild\n**{0}config prefix** - to set the prefix"
        if get_lang(ctx) == "ar":
            m = "**{0}config lang** - لتغير لغه البوت في خادمك\n**{0}config prefix** - لتغير بادئه البوت في خادمك"
        await ctx.send(embed=Embed(
            description=m.format(get_prefix(ctx)),
            color=Colour.red())
        )

    @config_commands.command(
        name="lang", aliases=['set_lang', "set-lang", "language"], invoke_without_command=True, usage="config lang <new_lang(en, ar)>")
    @has_permissions(manage_guild=True)
    @guild_only()
    @cooldown(1, 10, commands.BucketType.guild)
    async def language_command(self, ctx, new_lang):
        if new_lang == "ar":
            cr.execute("UPDATE guilds SET language = 'ar' WHERE guild_id = ?", (ctx.guild.id,))
            await ctx.send(embed=discord.Embed(
                description=f"تمت إعادة تعيين اللغة إلى `ar`",
                color=discord.Colour.green()
            ))
            commit()
        elif new_lang == "en":
            cr.execute("UPDATE guilds SET language = 'en' WHERE guild_id = ?", (ctx.guild.id,))
            await ctx.send(embed=discord.Embed(
                description=f"the language has been reset to `en`",
                color=discord.Colour.green()
            ))
            commit()
        else:
            await ctx.send(embed=discord.Embed(
                description=f"Available languages are Arabic and English(ar, en)",
                color=discord.Colour.red()
            ))

    @config_commands.command(name="prefix", aliases=['set_prefix', "set-prefix", "setprefix"], invoke_without_command=True, usage="config prefix <new_prefix>")
    @has_permissions(manage_guild=True)
    @guild_only()
    @cooldown(1, 10, commands.BucketType.guild)
    async def prefix(self, ctx, new_prefix: str):
        m11, m12 = "لا يمكن أن تكون البادئة أكثر من 5 أحرف.", "تمت إعادة ضبط البادئة إلى "
        if get_lang(ctx) == "en":
            m11, m12 = "The prefix cannot be more than 5 characters long.", "the prefix has been reset to"
        if len(new_prefix) > 5:
            await ctx.send(embed=discord.Embed(
                description=m11,
                color=discord.Colour.red()
            ))
            return
        cr.execute("UPDATE guilds SET prefix = ? WHERE guild_id = ?", (new_prefix, ctx.guild.id))
        commit()
        prefix = cr.execute("SELECT prefix FROM guilds WHERE guild_id = ?", (ctx.guild.id,))
        await ctx.send(embed=discord.Embed(
            description=f"{m12} `{prefix.fetchone()[0]}`",
            color=discord.Colour.green()))
        return


def setup(client):
    client.add_cog(Config(client))
