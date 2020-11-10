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
		print("a")
		christmas = datetime.datetime(2020, 12, 25)
		now = datetime.datetime.now()
		days = (christmas - now).days
		c = await bot.fetch_channel(774455963709079552)
		ms = c.history(limit=None)
		ms = await ms.flatten()
		for message in ms:
			if message.id == 774829498586890240:
				await message.edit(content=f"Days until christmas: `{days}`")
				break
			else:
				continue
		else:
			return await c.send(content=f"Days until christmas: `{days}`")

def setup(bot):
	bot.add_cog(pEATS(bot))
	print('[pEATS] pEATS cog loaded')