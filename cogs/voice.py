import discord
from discord.ext import commands

@commands.has_permissions(move_members=True)
@commands.bot_has_permissions(move_members=True)
@commands.guild_only()
@commands.command(name="voicekick", aliases=['vkick', 'disconnect'])
async def voicekick(self, ctx, member: discord.Member, *, reason=None):
	"""
	Kicks the given user from their current voice channel.
	"""
	voice = member.voice
	if voice:
		await member.edit(voice_channel=None, reason=f"Kicked by {ctx.author}{f' with reason {reason}' if reason else ''}")
		await ctx.send(f"Kicked {member} from {voice.channel.name}!")
	else:
		await ctx.send(f"{member} is not in a voice channel!")

@commands.has_permissions(move_members=True)
@commands.bot_has_permission(move_members=True)
@commands.guild_only()
@commands.command(name="voicemove", aliases=['vmove', 'move'])
async def voicemove(self, ctx, member: discord.Member, channel: discord.VoiceChannel, *, reason=None):
	"""
	Moves the given user to the given channel.
	"""
	voice = member.voice
	if voice:
		await member.edit(voice_channel=channel, reason=f"Moved by {ctx.author}{f' with reason {reason}' if reason else ''}")
		await ctx.send(f"Moved {member} from {voice.channel.name} to {channel.name}!")
	else:
		await ctx.send(f"{member} is not in a voice channel!")

@commands.has_permissions(move_members=True)
@commands.bot_has_permissions(move_members=True)
@commands.guild_only()
@commands.command(name="massmove")
async def massmove(self, ctx, origin: discord.VoiceChannel, destination: discord.VoiceChannel, *, reason=None):
	"""
	Moves everybody in the origin channel to the destination channel.
	"""
	if origin.members:
		if origin != destination:
			moved = []
			for member in origin.members:
				await member.edit(voice_channel=destination, reason=f"Massmoved by {ctx.author}{f' with reason {reason}' if reason else ''}")
				moved.append(member)
			embed = discord.Embed(title=f"Moved Members!", color=self.bot.colors['blue'], description=f"Moved {len(moved)} members from {origin.name} to {destination.name}!\nPeople moved: {', '.join([m.mention for m in moved])}")
			await ctx.send(embed=embed)
		else:
			await ctx.send(f"You can't move people to the same voice channel that they're already in!")
	else:
		await ctx.send(f"{origin.name} is empty!")