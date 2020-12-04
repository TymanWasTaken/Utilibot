import discord, typing, json
from discord.ext import commands


class ChannelUtils(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(name="channelinfo", aliases=['ci'])
	@commands.guild_only()
	async def channelinfo(self, ctx, channel: typing.Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, None]):
		"""
		Shows some info on a channel.
		"""
		channel = channel or ctx.channel
		embed = discord.Embed(title=f"#{channel}'s Info")
		fields = {
			"ID": f"`{channel.id}`",
			"Topic": f"```{channel.topic}```",
			"Category": f"{channel.category} (`{channel.category.id}`)",
			"Position": str(channel.position),
			"NSFW?": f"{'Yes' if channel.nsfw else 'No'}",
			"Type": str(channel.type).capitalize(),
			"Slowmode": f"{f'{channel.slowmode_delay} seconds' if channel.slowmode_delay > 0 else 'Disabled'}"
		}
		for f in fields:
			embed.add_field(name=f, value=fields[f])
		embed.set_footer(text="Created at")
		embed.timestamp=channel.created_at
		await ctx.send(embed=embed)

	@commands.command(name="announcechannel", aliases=['ac', 'achan',])
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	@commands.guild_only()
	async def announcechannel(self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel]=None):
		"""
		A simple toggle to convert channels between Text and Announcements.
		"""
		if "NEWS" in ctx.guild.features:
			c = channel or ctx.channel
			curtype = c.type
			newtype = discord.ChannelType.news
			if curtype == discord.ChannelType.news:
				newtype = discord.ChannelType.text
			await c.edit(type=newtype, reason=f"{ctx.author} ({ctx.author.id}) converted this channel to type {newtype}.")
			await ctx.send(f"{self.bot.const_emojis['yes']} Changed <#{c.id}> to type `{newtype}`!")
		else:
			await ctx.send(f"{self.bot.const_emojis['no']} This server can't have announcement channels! Ask somebody with the `Manage Server` permission to enable Community in Server Settings, then try again.\nPlease do not run this command again until community has been enabled.")

	@commands.group(name="autopublish", aliases=['autopub', 'ap'])
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	@commands.guild_only()
	async def autopublish(self, ctx, channel: discord.TextChannel=None):
		channel = channel or ctx.channel
		if channel.is_news():
			db = await self.bot.dbquery("autopublish_channels", "data", "guildid=" + str(ctx.guild.id))
			chanlist = []
			action = f"Added {channel.mention} to"
			if db:
				chanlist = json.loads(db[0][0])
				await self.bot.dbexec("DELETE FROM autopublish_channels WHERE guildid=" + str(ctx.guild.id))
			if channel.id in chanlist:
				chanlist.remove(channel.id)
				action = f"Removed {channel.mention} from"
			else:
				chanlist.append(channel.id)
			total = []
			for c in chanlist:
				if ctx.guild.get_channel(c):
					if ctx.guild.get_channel(c).is_news():
						total.append(f"<#{c}>")
					else:
						chanlist.remove(channel.id)
				else:
					chanlist.remove(channel.id)
			await self.bot.dbexec(("INSERT INTO autopublish_channels VALUES (?, ?)", (str(ctx.guild.id), str(chanlist))))
			await ctx.send(f"{self.bot.const_emojis['yes']} {action} the list of channels that will have their messages autopublished!\nNew total list: {'`||`'.join(total)}")
		else:
			await ctx.send(f"{self.bot.const_emojis['no']} {channel.mention} is not an announcement channel!")
	
	

	@commands.command(name="publish")
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.guild_only()
	async def publish(self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel]=None, message=None):
		"""
		Publishes a message.
		"""
		publishing = False
		if not "NEWS" in ctx.guild.features:
			await ctx.send("This server has no announcement channels!")
		else:
			ch = channel or ctx.channel
			if ch.type != discord.ChannelType.news:
				er = await ctx.send(f"<#{ch.id}> is not an announcement channel!")
				await er.delete(delay=5)
			else:
				msg = await ch.fetch_message(message)
				if msg.author.id != ctx.author.id:
					if ctx.channel.permissions_for(ctx.author).manage_messages == False:
						return await ctx.send("You can't publish this message as you did not write it and you do not have manage messages permissions!")
					else:
						publishing = True
				else:
					publishing = True
				if publishing == True:
					await msg.publish()
					conf = await ctx.send(f"Successfully published <https://discord.com/channels/{ctx.guild.id}/{ch.id}/{msg.id}>!")
					await conf.delete(delay=5)

	@commands.command(name="channelname", aliases=['editchannelname', 'editcname', 'cname'])
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def cname(self, ctx, channel: typing.Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, None], *, name):
		"""
		Edits a channel's name.
		"""
		chan = channel or ctx.channel
		oldname = chan.name
		await chan.edit(name=name, reason=f"Name changed by {ctx.author} ({ctx.author.id}).")
		await ctx.send(f"Changed <#{chan.id}>'s name!\nBefore: `#{oldname}`\nAfter: `#{chan.name}`")


	@commands.command(name="channeltopic", aliases=['editchanneltopic', 'editctopic', 'ctopic'])
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def ctopic(self, ctx, channel: typing.Optional[discord.TextChannel]=None, *, topic=None):
		"""
		Edits a channel's topic.
		"""
		chan = channel or ctx.channel
		oldtopic = chan.topic
		if len(topic) > 512:
			return await ctx.send("The new topic is too long! Channel topics must be between 0 and 512 characters.")
		await chan.edit(topic=topic, reason=f"Topic changed by {ctx.author} ({ctx.author.id}).")
		await ctx.send(f"Changed <#{chan.id}>'s topic!\nBefore: `{oldtopic}`\nAfter: `{topic}`")

	@commands.command(name="deletechannel", aliases=['delchan', 'deletechan'])
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def delchan(self, ctx, channel: typing.Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, None], *, reason="None given."):
		"""
		Deletes a specified channel with an optional reason.
		"""
		chan = channel or ctx.channel
		await chan.delete(reason=f"Channel deleted by {ctx.author} ({ctx.author.id}) with reason: {reason}.")
		await ctx.send(f"Deleted `#{chan.name}`!")

	@commands.command(name="createchannel", aliases=['createchan', 'newchan'])
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def createchan(self, ctx, name, position: int=0, *, reason="None given."):
		"""
		Creates a text channel with an optional position and reason. Use `newvc` to create a voice channel.
		"""
		c = await ctx.guild.create_text_channel(name=name, reason=f"Channel created by {ctx.author} ({ctx.author.id}) with reason: {reason}")
		await c.edit(position=position)
		await c.send(f"I created this channel for you, {ctx.author.mention}!", delete_after=60)
		await ctx.send(f"{ctx.author.mention}, I created {c.mention} for you!", delete_after=60)

	@commands.command(name="createvoicechannel", aliases=['createvoicechan', 'newvoicechan', 'newvc'])
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def newvc(self, ctx, name, position: int=0, *, reason="None given."):
		"""
		Creates a voice channel with an optional position and reason. Use `newchan` to create a text channel.
		"""
		c = await ctx.guild.create_voice_channel(name=name, reason=f"Channel created by {ctx.author} ({ctx.author.id}) with reason: {reason}", position=position)
		await ctx.send(f"I created <#{c.id}> for you, {ctx.author.mention}!")

	@commands.command(name="nuke", aliases=['nukechan', 'clone', 'resetchan'])
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def nuke(self, ctx, channel: typing.Optional[discord.TextChannel]=None):
		"""
		Resets a text channel- Clones it and deletes the old one. Useful for clearing all the messages in a channel quickly.
		"""
		chan = channel or ctx.channel
		c = await chan.clone(reason=f"Channel reset by {ctx.author} ({ctx.author.id})")
		await c.edit(position=chan.position)
		try: 
			await chan.delete(reason=f"Channel reset by {ctx.author} ({ctx.author.id})")
		except:
			await chan.send(f"{ctx.author.mention}, I cannot delete this channel! (most likely cause is that it's set as a channel required for community servers)")
		await c.send(f"I reset this channel, {ctx.author.mention}!", delete_after=60)
		
	@commands.command(name="slowmode")
	@commands.guild_only()
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True)
	async def slowmode(self, ctx, slowmode: int, channel: typing.Optional[discord.TextChannel]=None):
		"""
		Sets a text channel's slowmode delay in seconds. Maximum of 21600 seconds (6 hours).
		"""
		channel = channel or ctx.channel
		if slowmode > 21600:
			await ctx.send(f"`{slowmode}` is too long of a delay! The new slowmode must be 21600 seconds or less (6 hours).")
		elif slowmode == 0:
			await channel.edit(slowmode_delay=slowmode, reason=f"Slowmode disabled by {ctx.author} ({ctx.author.id}).")
			await ctx.send(f"Disabled slowmode for {channel.mention}!")
		else:
			await channel.edit(slowmode_delay=slowmode, reason=f"Slowmode changed to {slowmode} seconds by {ctx.author} ({ctx.author.id}).")
			await ctx.send(f"Changed {channel.mention}'s slowmode to {slowmode} seconds.")

def setup(bot):
	bot.add_cog(ChannelUtils(bot))
	print('[ChannelUtilsCog] Channel Utils cog loaded')	
