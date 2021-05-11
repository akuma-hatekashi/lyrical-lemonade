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

import dbl
import discord
from discord.ext import commands, tasks
import json
import asyncio
import logging


with open('./config.json', 'r') as f:
    config = json.load(f)


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, client):
        self.client = client
        self.token = config['TopGG_token']
        self.dblpy = dbl.DBLClient(self.client, self.token, autopost=True)

    @commands.Cog.listener()
    async def on_guild_post(self):
        channel = self.client.get_channel(807372813153075200)
        await channel.send("Server count posted successfully")

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        # channel = self.client.get_channel(807372813153075200)
        # user = data['user']
        # await user.author.send(f"hey **{user}**, thanks for voting SumBot!")
        # await channel.send(f"hey **{data}**, thanks for voting SumBot!")
        print(data)


def setup(client):
    client.add_cog(TopGG(client))
