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
		c = bot.get_channel(774455963709079552)
		m = await c.fetch_message(791763456646447135)
		stripmilli = (str(duration).split('.'))[0]
		separate = stripmilli.split(':')
		hours = separate[0]
		minutes = separate[1]
		seconds = separate[2]
		formatted = f"0 days, {hours} hour{'s' if int(hours) > 1 else ''}, {minutes} minute{'s' if int(minutes) > 1 else ''}, and {seconds} second{'s' if int(seconds) > 1 else ''}"
		await m.edit(content=f"T- `{formatted}`")

def setup(bot):
	bot.add_cog(pEATS(bot))
	print('[pEATS] pEATS cog loaded')
