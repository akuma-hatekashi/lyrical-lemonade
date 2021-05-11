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

from discord.ext import commands, tasks
import pyfiglet
from prettytable import PrettyTable
import asyncio
from db.db import *
import logging
from cogs.music import *

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

with open('./config.json', 'r') as f:
	config = json.load(f)

EXTENSIONS = [
	"general",
	"fun",
	"giveaway",
	"moderator",
	# "TopGG",
	"music",
	"owner",
	"help",
	"config",
]


def get_prefix(bot, message):
	try:
		guild = message.guild.id
	except AttributeError:
		return ["@", "<@!{}>".format(bot.user.id)]
	prefix = cr.execute("SELECT prefix FROM guilds WHERE guild_id = ?", (guild,))
	return commands.when_mentioned_or(prefix.fetchone()[0])(bot, message)


class SumBot(commands.Bot):
	def __init__(self):
		super().__init__(
			command_prefix=get_prefix,
			case_insensitive=True,
			allowed_mentions=discord.AllowedMentions(
				everyone=config["mention"]["everyone"],
				users=config["mention"]["users"],
				roles=config["mention"]["roles"])
		)

		self.owner_id = None
		self.owner_ids = config["owner_ids"]
		self.client_id = config["client_id"]
		self.remove_command('help')

		if config["token"] == "" or config["token"] == "token":
			self.token = os.environ['token']
		else:
			self.token = config["token"]

		bag = False
		self.load_extension("error_handler.error_handler")
		for filename in EXTENSIONS:
			if bag:
				try:
					self.load_extension(f'cogs.{filename}')
					print('lode {}'.format(filename))
				except Exception as error:
					if bag:
						print('error_handler in {}\n{}'.format(filename, error))
			else:
				self.load_extension(f'cogs.{filename}')
				print('lode {}'.format(filename))

	@tasks.loop(seconds=10.0)
	async def change_stats(self):

		status = [
			'@help',
			'One of the best open source discord bots'
		]
		await self.change_presence(activity=discord.Game(type=discord.ActivityType.listening, name=(status[0])))
		await asyncio.sleep(30)
		await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status[1]))
		await asyncio.sleep(10)
		# await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status[2]))
		# await asyncio.sleep(10)

	@tasks.loop(seconds=5)
	async def del_cooldown(self):
		if get_cooldown() is []:
			return
		cr.execute("DELETE FROM cooldown")
		commit()

	async def on_ready(self):
		self.change_stats.start()
		self.del_cooldown.start()
		for i in self.guilds:
			cr.execute(
				"INSERT OR IGNORE INTO guilds(guild_id, guild_name, prefix, language) VALUES(?, ?, ?, ?)",
				(i.id, i.name, "@", "en"))
			commit()
		tap = PrettyTable(
			['Name Bot', 'Tag', 'Id', 'prefix', 'guilds', 'commands', 'users'])
		tap.add_row([
			self.user.name,
			'#' + self.user.discriminator,
			self.user.id,
			"@",
			len(self.guilds),
			len(self.commands),
			len(self.users)
		])
		print(tap)
		print(pyfiglet.figlet_format(self.user.name), end=" ")

	async def on_guild_join(self, guild):
		self.cr.execute(
			"INSERT OR IGNORE INTO guilds(guild_id, prefix) VALUES(?, ?)", (guild.id, "@"))
		self.db.commit()
		channel = self.get_channel(config["channel"]["join"])
		owner = self.get_user(int(guild.owner_id))
		print(owner)
		try:
			embed = discord.Embed(title="add guild", color=0x46FF00)
			embed.add_field(name='name guild: ', value=guild.name, inline=False)
			embed.add_field(name='id guild: ', value=guild.id, inline=False)
			embed.add_field(name='owner guild: ', value=f"{owner.mention} | {owner}", inline=False)
			embed.add_field(name='owner id: ', value=str(owner.id), inline=False)
			embed.add_field(name='member guild: ', value=guild.member_count, inline=False)
			embed.add_field(name='bot server: ', value=f'{len(self.guilds)}', inline=False)
			embed.set_footer(text=guild.name, icon_url=guild.icon_url)
			embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
			await channel.send(embed=embed)
		except Exception as error:
			print(error)

	async def on_guild_remove(self, guild):
		self.cr.execute(
			"INSERT OR IGNORE INTO guilds(guild_id, prefix) VALUES(?, ?)", (guild.id, "@"))
		self.db.commit()
		channel = self.get_channel(config['channel']["remove"])
		owner = self.get_user(int(guild.owner_id))
		try:
			embed = discord.Embed(title="remove guild", color=0xFF0000)
			embed.add_field(name='name guild: ', value=guild.name, inline=False)
			embed.add_field(name='id guild: ', value=guild.id, inline=False)
			embed.add_field(name='owner guild: ', value=f"<@{str(guild.owner_id)}>", inline=False)
			embed.add_field(name='owner id: ', value=str(owner.id), inline=False)
			embed.add_field(name='member guild: ', value=guild.member_count, inline=False)
			embed.add_field(name='bot server: ', value=f"{len(self.guilds)}", inline=False)
			embed.set_footer(text=guild.name, icon_url=guild.icon_url)
			embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
			await channel.send(embed=embed)
		except Exception as r:
			print(r)

	def run(self):
		super().run(self.token, reconnect=True)


if __name__ == '__main__':
	client = SumBot()
	client.run()
