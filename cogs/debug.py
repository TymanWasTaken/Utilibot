import discord, sys, os
from discord.ext import commands
from jishaku import models

class ManualError(Exception):
	pass

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
		code = os.system(f'../git.sh {message}')
		await m.edit(content=f'Updated repo successfully, with return code {code}!')

	@commands.command(name="su")
	@commands.is_owner()
	async def bypass_all(self, ctx: commands.Context, *, command_string: str):
		"""
		Runs a command bypassing all checks, basically forcing the command to run.
		"""

		alt_ctx = await models.copy_context_with(ctx, content=ctx.prefix + command_string)

		if alt_ctx.command is None:
			return await ctx.send(f'Command "{alt_ctx.invoked_with}" is not found')

		return await alt_ctx.command.reinvoke(alt_ctx)
	
	@commands.command()
	@commands.is_owner()
	async def error(self, ctx):
		raise ManualError("Error caused by command, probably for debugging purposes")

def setup(bot):
	bot.add_cog(Debug(bot))
	print('[DebugCog] Debug cog loaded')