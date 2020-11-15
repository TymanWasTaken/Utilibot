import discord, dpytils, postbin
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
		embed = discord.Embed(title=f"Message Edited in #{before.channel.name}", description=f"**Before:**```{before.clean_content.replace('`', '​`​')}```**After:**```{after.clean_content.replace('`', '​`​')}```Message link: [click here]({before.jump_url})", color=0x1184ff, timestamp=datetime.now())
		embed.set_author(name=before.author, icon_url=before.author.avatar_url)
		embed.set_footer(text=f"Author ID: {before.author.id}")
		await logchannel.send(embed=embed)
	
	@commands.Cog.listener()
	async def on_message_delete(self, message):
		logchannel = discord.utils.get(message.guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		embed=discord.Embed(title=f"Message Deleted in #{message.channel.name}", description=f"```{message.clean_content.replace('`', '​`​')}```", color=0xe41212, timestamp=datetime.now())
		embed.set_author(name=message.author, icon_url=message.author.avatar_url)
		embed.set_footer(text=f"Author ID: {message.author.id}")
		await logchannel.send(embed=embed)
	
	@commands.Cog.listener()
	async def on_bulk_message_delete(self, messages):
		obj = messages[0]
		logchannel = discord.utils.get(obj.guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		post = f"{len(messages)} messages deleted in #{obj.channel.name} in {obj.guild.name}:\n\n"
		for message in messages:
			post = f"{post}\n\n\n{message.author} ({message.author.id}): {message.content}"
		url = await postbin.postAsync(post)
		embed=discord.Embed(title=f"{len(messages)} Messages Purged in #{obj.channel.name}", description=f"View them here: {str(url).replace(".com",".com/raw")}", color=0xa50003, timestamp=datetime.now())
		await logchannel.send(embed=embed)

def setup(bot):
	bot.add_cog(Logging(bot))
	print('[LoggingCog] Logging cog loaded')