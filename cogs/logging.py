import discord
from discord.ext import commands

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
	async def on_raw_message_edit(self, payload):
		channel = self.bot.get_channel(payload.channel_id)
		message = await channel.fetch_message(payload.message_id)
		logchannel = discord.utils.get(channel.guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		embed = discord.Embed(title="Message edited", description=f"Message edited in {channel.mention}:\n\nBefore:```{message.clean_content.replace('`', '​`​')}")

def setup(bot):
	bot.add_cog(Logging(bot))
	print('[LoggingCog] Logging cog loaded')