import discord
from discord.ext import commands

class Reminders(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command()
	async def remind(self, ctx, time, *, reminder):
		await ctx.send(self.bot.const_emojis['soontm'])
def setup(bot):
	bot.add_cog(Reminders(bot))
	print('[RemindersCog] Reminders cog loaded')
