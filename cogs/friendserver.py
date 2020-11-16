import discord, aiocron, aiohttp, pytz
from discord.ext import commands

class FriendServer(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@aiocron.crontab('0 12 * * *', tz=pytz.timezone("US/Mountain"))
	async def sendDuoMessage(self=None):
		async with aiohttp.ClientSession() as session:
			webhook = discord.Webhook.from_url('https://discord.com/api/webhooks/749360350901567607/KLeRMONub0E4-sktBG3tiCUFkweKW4YIgXqQWqn8Ucl5iJP05r3OJvVo53GylMlRPGbj', adapter=discord.AsyncWebhookAdapter(session))
			await webhook.send('<@&747527158095675464> Time to do your daily streak! ᵒʳ ᵉˡˢᵉ')

def setup(bot):
	bot.add_cog(FriendServer(bot))
	print('[FriendServer] FriendServer cog loaded')