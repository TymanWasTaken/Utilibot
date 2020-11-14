import discord, dpytils
from discord.ext import commands

utils = dpytils.utils()

class Logging(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="log")
	async def log(self, ctx):
		"""
		Will config logging eventually.
		"""
		await ctx.send("Logging coming soon!")

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		if before.content == after.content:
			return
		logchannel = discord.utils.get(before.guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		embed = discord.Embed(title="Message edited", description=f"Message edited in {before.channel.mention}:\n\nBefore:```{before.clean_content.replace('`', '​`​')}```After:```{after.clean_content.replace('`', '​`​')}```Message link: [click here]({before.jump_url})", color=utils.randcolor())
		await logchannel.send(embed=embed)

def setup(bot):
	bot.add_cog(Logging(bot))
	print('[LoggingCog] Logging cog loaded')