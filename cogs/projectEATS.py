import discord, random, datetime, asyncio
from discord.ext import commands
from discord.ext import tasks

class pEATS(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.editMessage.start()			

	@tasks.loop(seconds=30)
	async def editMessage(self):
		bot = self.bot
		christmas = datetime.datetime(2020, 12, 25, 11, 0)
		now = datetime.datetime.now()
		duration = christmas - now
		c = await bot.fetch_channel(774455963709079552)
		m = await c.fetch_message(774829498586890240)
		await m.edit(content=f"Seconds until the big reveal: `{duration}` (somebody pls help convert this to good duration)")

def setup(bot):
	bot.add_cog(pEATS(bot))
	print('[pEATS] pEATS cog loaded')
