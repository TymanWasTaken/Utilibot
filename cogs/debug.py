import discord, sys, os
from discord.ext import commands
from jishaku import models

async def is_owner(ctx):
	return ctx.author.id == 487443883127472129

class Debug(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.is_owner()
	async def quit(self, ctx):
		"""
		Kill the bot.
		"""
		await ctx.send('Shutting down...')
		print('Recived quit command, shutting down.')
		sys.exit()

	@commands.command()
	@commands.is_owner()
	async def git(self, ctx, *, message=""):
		"""
		Upload code to github.
		"""
		m = await ctx.send("Updating repo...")
		code = os.system(f'/home/pi/utilibot/git.sh {message}')
		await m.edit(content=f'Updated repo successfully, with return code {code}!')

	@commands.command(name="rao")
	@commands.is_owner()
	async def run_as_owner(self, ctx: commands.Context, *, command_string: str):
		"""
		Run a command as the guild owner.
		"""
		if ctx.guild:
			# Try to upgrade to a Member instance
			# This used to be done by a Union converter, but doing it like this makes
			#  the command more compatible with chaining, e.g. `jsk in .. jsk su ..`
			target = ctx.guild.owner
		alt_ctx = await models.copy_context_with(ctx, author=target, content=ctx.prefix + command_string)

		if alt_ctx.command is None:
			if alt_ctx.invoked_with is None:
				return await ctx.send('This bot has been hard-configured to ignore this user.')
			return await ctx.send(f'Command "{alt_ctx.invoked_with}" is not found')

		return await alt_ctx.command.invoke(alt_ctx)

def setup(bot):
	bot.add_cog(Debug(bot))
	print('[DebugCog] Debug cog loaded')