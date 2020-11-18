import discord, asyncio, aiohttp, pytz, datetime
from discord.ext import commands

time_for_thing_to_happen = datetime.time(hour=12).astimezone("US/Mountain")

class FriendServer(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def sendDuoMessage(self):
		while True:
			now = datetime.datetime.utcnow()
			date = now.date()
			if now.time() > time_for_thing_to_happen:
				date = now.date() + datetime.timedelta(days=1)
			then = datetime.datetime.combine(date, time_for_thing_to_happen)
			await discord.utils.sleep_until(then)
			async with aiohttp.ClientSession() as session:
				webhook = discord.Webhook.from_url('https://discord.com/api/webhooks/749360350901567607/KLeRMONub0E4-sktBG3tiCUFkweKW4YIgXqQWqn8Ucl5iJP05r3OJvVo53GylMlRPGbj', adapter=discord.AsyncWebhookAdapter(session))
				await webhook.send('<@&747527158095675464> Time to do your daily streak! ᵒʳ ᵉˡˢᵉ')
	
	def exception_catching_callback(self, task):
		if task.exception():
			task.print_stack()

def setup(bot):
	cog = FriendServer(bot)
	bot.add_cog(cog)
	task = asyncio.create_task(cog.sendDuoMessage())
	task.add_done_callback(cog.exception_catching_callback)
	print('[FriendServer] FriendServer cog loaded')