import dbl, discord, os
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv(dotenv_path="/home/tyman/code/utilibot/.env")

class TopGG(commands.Cog):
	"""Handles interactions with the top.gg API"""

	def __init__(self, bot):
		self.bot = bot
		self.token = os.getenv("DBL_TOKEN") # set this to your DBL token
		self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True, webhook_port=6779, webhook_path="/utilibotvote", webhook_auth="98ujwoasd90jqwd[pdqw;") # Autopost will post your guild count every 30 minutes

	@commands.command()
	async def vote(self, ctx):
		embed = discord.Embed(title="Vote link:", description="You can vote for me [here](https://top.gg/bot/755084857280954550/vote)!")
		if await self.dblpy.get_user_vote(ctx.author.id):
			await ctx.send(content="You have already voted, but you could send this to a friend:", embed=embed)
		else:
			await ctx.send(embed=embed)
	
	@commands.Cog.listener()
	async def on_dbl_vote(self, data):
		"""An event that is called whenever someone votes for the bot on top.gg."""
		await self.bot.get_channel(755979601788010527).send("Received an upvote:\n" + data)

	@commands.Cog.listener()
	async def on_dbl_test(self, data):
		"""An event that is called whenever someone tests the webhook system for your bot on top.gg."""
		await self.bot.get_channel(755979601788010527).send("Received a test upvote:\n" + data)

	@commands.Cog.listener()
	async def on_guild_post(self):
		data = await self.dblpy.get_guild_count(self.bot.user.id)
		guilds = data["server_count"]
		shards = len(data["shards"])
		if guilds == len(self.bot.guilds):
			await self.bot.get_channel(755979601788010527).send(f"Server count posted successfully, it is now showing `{guilds} servers`.")
		else:
			await self.bot.get_channel(755979601788010527).send(f"Server count posted, but incorrect. The correct number is `{len(self.bot.guilds)}`, but `{guilds}` was posted.")

def setup(bot):
	bot.add_cog(TopGG(bot))