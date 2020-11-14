import discord, dpytils
from discord.ext import commands
from datetime import datetime

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
		embed = discord.Embed(title=f"Message Edited in #{before.channel.name}", description=f"Before:```{before.clean_content.replace('`', '​`​')}```After:```{after.clean_content.replace('`', '​`​')}```Message link: [click here]({before.jump_url})", color=utils.randcolor(), timestamp=datetime.now())
		embed.set_author(name=f"Message sent by {before.author}", icon_url={str(before.author.avatar_url)})
		embed.set_footer(text=f"Author ID: {before.author.id}")
		await logchannel.send(embed=embed)

def setup(bot):
	bot.add_cog(Logging(bot))
	print('[LoggingCog] Logging cog loaded')