import discord, random, asyncio
from discord.ext import commands

class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	async def purge(self, ctx, number):
		"""
		Purge a specified amount of messages from the current channel.
		"""
		deleted = await ctx.channel.purge(limit=int(number)+1)
		message = await ctx.channel.send(f'Deleted {len(deleted)-1} message(s)')
		await asyncio.sleep(2.5)
		await message.delete()

def setup(bot):
	bot.add_cog(Moderation(bot))
	print('[ModerationCog] Utils cog loaded')
