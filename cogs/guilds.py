import discord, random, datetime, asyncio, postbin, traceback, re
from discord.ext import commands
import concurrent.futures

def func(lst):
	return sum(lst) / len(lst)

async def Average(bot, l):
	with concurrent.futures.ProcessPoolExecutor() as pool:
		return await bot.loop.run_in_executor(pool, func, l)

def func2(num, roundnum):
	return round(num, roundnum)

async def Round(bot, num, roundnum):
	with concurrent.futures.ProcessPoolExecutor() as pool:
		return await bot.loop.run_in_executor(pool, func2, num, roundnum)

class Guilds(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command=True)
	@commands.is_owner()
	async def guilds(self, ctx):
		guilds = len(self.bot.guilds)
		users = len(self.bot.users)
		avg = await Average(self.bot, [g.member_count for g in self.bot.guilds])
		avg = await Round(self.bot, avg, 0)
		await ctx.send(embed=discord.Embed(title="Guild data", description=f"""
		Guild count: {guilds}
		Total user count: {users}
		Average member count: {avg}
		""".replace("	", "")
		))

	@guilds.command()
	@commands.is_owner()
	async def leave(self, ctx, guild: discord.Guild):
		async with ctx.typing():
			try:
				await guild.leave()
				await ctx.send(f"Successfuly left guild \"{guild.name}\".")
			except Exception as error:
				tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
				url = await postbin.postAsync(tb)
				await ctx.send(f"An error occured while trying to leave that guild. Hastebin: {url}")

	@guilds.command()
	@commands.is_owner()
	async def botfarms(self, ctx):
		message = await ctx.send("Calculating...")
		text = ""
		e = discord.Embed(title="Bot farms detected:")
		for g in self.bot.guilds:
			await g.chunk()
			bots = []
			for m in g.members:
				if m.bot:
					bots.append(m.id)
			btm = (len(bots)/g.member_count)*100
			btmround = await Round(self.bot, btm, 2)
			if btm >= 75 and g.member_count > 20:
				e.add_field(name=g.name+":", value=f"- Bot %: `{btmround}%`\n- Bots/membercount: `{len(bots)}/{g.member_count}`\n- Guild ID: `{g.id}`\n\n")
		await message.edit(content="", embed=e)

	@guilds.command()
	@commands.is_owner()
	async def invite(self, ctx, guild_id: int, silent: bool=False):
		guild = self.bot.get_guild(guild_id)
		if guild is None:
			return await ctx.send("I could not get the guild for the given id, am I in it?")
		try:
			invites = await guild.invites()
			# Infinite and not temporary
			invites_inf_not_temp = [inv for inv in invites if inv.temporary == False and inv.max_age == 0]
			# Not infinite and not temporary
			invites_not_temp_not_inf = [inv for inv in invites if inv.temporary == False and inv.max_age != 0]
			# Infinite and temporary
			invites_inf_temp = [inv for inv in invites if inv.temporary == True and inv.max_age == 0]
			# Not infinite and temporary
			invites_not_inf_not_temp = [inv for inv in invites if inv.temporary == True and inv.max_age != 0]
			"""
			Invite priority:
			1. Infinite and not temporary
			2. Not infinite and not temporary
			3. Infinite and temporary
			4. Not infinite and temporary
			"""
			if len(invites_inf_not_temp) > 0:
				try:
					await ctx.author.send(f"Infinite invite link to `{guild.name}`:\n{invites_inf_not_temp[0].url}")
					return await ctx.message.add_reaction("✅")
				except:
					return await ctx.send("I could not DM you, do I have permission to?")
			elif len(invites_not_temp_not_inf) > 0:
				try:
					await ctx.author.send(f"Invite link to `{guild.name}`:\n{invites_not_temp_not_inf[0].url}")
					return await ctx.message.add_reaction("✅")
				except:
					return await ctx.send("I could not DM you, do I have permission to?")
			# After this, it means the only invites it could find were temporary permissions (or it couldn't find any), so attempt to generate an invite instead, unless "silent" is True
			if silent == True:
				if len(invites_inf_temp) > 0:
					try:
						await ctx.author.send(f"**TEMPORARY MEMBERSHIP**\nInfinite invite link to `{guild.name}`:\n{invites_inf_temp[0].url}")
						return await ctx.message.add_reaction("✅")
					except:
						return await ctx.send("I could not DM you, do I have permission to?")
				elif len(invites_not_inf_not_temp) > 0:
					try:
						await ctx.author.send(f"**TEMPORARY MEMBERSHIP**\nInvite link to `{guild.name}`:\n{invites_inf_temp[0].url}")
						return await ctx.message.add_reaction("✅")
					except:
						return await ctx.send("I could not DM you, do I have permission to?")
				elif len(invites) == 0:
					return await ctx.send("You specified this to be silent, and there were no invites.")
				else:
					await ctx.send("Something unexpected happened (somehow):/")
			else:
				# Gen invite
				for c in guild.channels:
					try:
						inv = await c.create_invite(max_age=0, max_uses=0, temporary=False, unique=True, reason="Invite created to join the server by my developer. This is most likely just to test something out.")
						try:
							await ctx.author.send(f"Invite link to `{guild.name}`:\n{inv.url}")
							return await ctx.message.add_reaction("✅")
						except:
							return await ctx.send("I could not DM you, do I have permission to?")
					except:
						continue
				else:
					return await ctx.send("Sadly there were no invites made, and I failed to make one in any of the channels.")
		except:
			# Gen invite unless silent
			return await ctx.send("I failed to get guild invites, and the rest of this is not made yet.\n\nsoon™")

def setup(bot):
	bot.add_cog(Guilds(bot))
	print('[Guilds] Guilds cog loaded')