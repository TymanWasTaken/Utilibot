import discord, random, asyncio
from discord.ext import commands

# purge checks
async def is_bot(m):
	print(m.author.bot)
	return 	m.author.bot
async def is_not_bot(m):
	print(not(m.author.bot))
	return 	not(m.author.bot)

class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	async def purge(self, ctx, number, mode=None):
		"""
		Purge a specified amount of messages from the current channel.
		"""
		await ctx.message.delete()
		mode = str(mode).lower()
		number = int(number)
		if mode is None:
			deleted = await ctx.channel.purge(limit=number)
			print('Deleting all messages')
		elif mode == "bot":
			deleted = await ctx.channel.purge(limit=number, check=is_bot)
			print('Deleting bot messages')
		elif mode == "human":
			deleted = await ctx.channel.purge(limit=number, check=is_not_bot)
			print('Deleting human messages')
		else:
			return ctx.send('Mode must be one of: bot, human')
		message = await ctx.channel.send(f'Deleted {len(deleted)} message(s)')
		await asyncio.sleep(2.5)
		await message.delete()
		

def setup(bot):
	bot.add_cog(Moderation(bot))
	print('[ModerationCog] Utils cog loaded')
