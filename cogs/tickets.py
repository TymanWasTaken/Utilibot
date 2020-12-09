import discord
from discord.ext import commands

class Tickets(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(name="ticket", aliases=['tickets'], invoke_without_command=True)
	@commands.guild_only()
	async def ticket(self, ctx):
		await ctx.send("o.o tickets soon? :wink:")
	
def setup(bot):
	bot.add_cog(Tickets(bot))
	print('[TicketsCog] Tickets cog loaded!')
	
