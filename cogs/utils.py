import discord, random, asyncio, aiohttp, os
from discord.ext import commands
from pytz import timezone
from dotenv import load_dotenv
load_dotenv(dotenv_path="/home/tyman/code/utilibot/.env")

def randcolor():
	return int("%06x" % random.randint(0, 0xFFFFFF), 16)

def permsfromvalue(value):
	perms = discord.Permissions(permissions=value)
	perms_true = sorted([x for x,y in dict(perms).items() if y])
	perms_false = sorted([x for x,y in dict(perms).items() if not y])
	nice_perms = ""
	perms_true = ["\u2705 `" + s for s in perms_true]
	perms_false = ["\u274c `" + s for s in perms_false]
	perms_combined = sorted(perms_true + perms_false, key=lambda x: x.strip('\u2705\u274c'))
	for perm in perms_combined:
		nice_perms = nice_perms + perm.replace("_", " ").capitalize() + "`\n"
	return nice_perms

class Utils(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="allperms")
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	@commands.guild_only()
	async def loop_channels(self, ctx, permission, state, role: discord.Role):
		"""
		Change permission overrides for all channels.
		"""
		state = state.lower()
		permission = permission.lower()
		if state == "true":
			state = True
		elif state == "neutral":
			state = None
		elif state == "false":
			state = False
		else:
			return await ctx.send("State must be one of: True, Neutral, or False")
		m = await ctx.send(f"Changing permission `{permission}` to state `{state}` for role {role.name} on all channels.")
		for channel in ctx.guild.channels:
			await channel.set_permissions(role, **{permission: state})
		await m.edit(content=f"Changed permission `{permission}` to state `{state}` for role {role.name} on all channels.")

	@commands.command(name="rolemembers", aliases=['members'])
	@commands.guild_only()
	async def rolemembers(self, ctx, *, role: discord.Role):
		if ctx.channel.permissions_for(ctx.me).embed_links == False:
			return await ctx.send("It appears I do not have the `Embed Links` permission in this channel. Please give me this permission or try again in a channel where I do have it, as it is necessary to run this command.")
		color = role.color
		name = ""	
		embed = discord.Embed(title=f"Members with the role __{role.name}__", color=color.value)
		for member in role.members:
			name = f"{name}\n• `{member.name}#{member.discriminator}"
		if len(name) > 2048:
			await ctx.send("List is to big to send.")
		else:
			embed.description=name
			await ctx.send(embed=embed)

	@commands.command(name="humans")
	@commands.guild_only()
	@commands.has_permissions(kick_members=True)
	async def humans(self, ctx):
		members = ""
		for member in ctx.guild.members:
			if member.bot:
				pass
			else:
				members = f"{members}\n{member.name}"
		if len(members) > 2000:
			await ctx.send("Too long.")
		else:
			await ctx.send(members)



	# @commands.command(name="allroles")
	# @commands.has_permissions(manage_roles=True)
	# @commands.bot_has_permissions(manage_roles=True)
	# async def loop_roles(self, ctx, permission, state):
	# 	"""
	# 	Change permission overrides for all roles.
	# 	"""
	# 	state = state.lower()
	# 	permission = permission.lower()
	# 	if state == "true":
	# 		state = True
	# 	elif state == "neutral":
	# 		state = None
	# 	elif state == "false":
	# 		state = False
	# 	else:
	# 		return await ctx.send("State must be one of: True, Neutral, or False")
	# 	for role in ctx.guild.roles:
	# 		await ctx.send(f"Role: {role}")
	# 		if role == ctx.guild.default_role:
	# 			continue
	# 		perms = role.permissions.update(**{permission: state})
	# 		await role.edit(permissions=perms)
	
	@commands.command(name="permissions", aliases=['perms', 'permsvalue'])
	async def permissions_from_value(self, ctx, value: int):
		"""
		Shows the permissions that correspond to a permissions value
		"""
		if ctx.channel.permissions_for(ctx.me).embed_links == False:
			return await ctx.send("It appears I do not have permission to `Link embeds` in this channel. Please give me this permission or try in a channel where I do have it, as it is necessary to run this command.")
		await ctx.send(embed=discord.Embed(title=f"Permissions for value {value}:", description=permsfromvalue(value), color=randcolor()))

	@commands.command(name="userinfo", aliases=['ui', 'user', 'info'])
	async def userinfo(self, ctx, user: discord.Member=None):
		bot = self.bot
		if user is None:
			user = ctx.guild.get_member(ctx.author.id)
		if user.status == discord.Status.online:
			status = bot.get_emoji(774816041632137226)
		elif user.status == discord.Status.idle:
			status = bot.get_emoji(774816228739907624)
		elif user.status == discord.Status.dnd:
			status = bot.get_emoji(774816849908727888)
		elif user.status == discord.Status.offline:
			status = bot.get_emoji(774816333912473611)
		if user.is_on_mobile():
			mobile = "✅"
		else:
			mobile = "❌"
		embed = discord.Embed(
			title=f"{str(user)}'s info:", 
			description=f"""**Nickname:** {user.nick}
			**User ID:** `{user.id}`
			**Role count:** {len(user.roles)}
			**Joined Server on:** {user.joined_at.astimezone(timezone('US/Mountain')).strftime("%a %B %d %Y %I:%M%p MST")}
			**Account Created on:** {user.created_at.astimezone(timezone('US/Mountain')).strftime("%a %B %d %Y %I:%M%p MST")}
			**Status:** {status}
			**Bot:** {'✅' if user.bot else '❌'}
			**Mobile:** {mobile}"""
			.replace("	", ""),
			thumbnail=user.avatar_url,
			color=user.color
			)
		await ctx.send(embed=embed)

	@commands.command(aliases=["tr"])
	async def translate(self, ctx, lang, *, text):
		async with aiohttp.ClientSession() as s:
			async with ctx.typing():
				async with s.get("https://api.cognitive.microsofttranslator.com/languages?api-version=3.0") as resp:
					langs = await resp.json()
					langs = langs["translation"]
				if not lang in langs:
					return await ctx.send("Not a valid language code.")
				async with s.post(f"https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to={lang}", headers={"Ocp-Apim-Subscription-Key": os.getenv('TRANSLATE_TOKEN'), "Ocp-Apim-Subscription-Region": "centralus", "Content-Type": "application/json"}, data="[{'Text':'"+text+"'}]") as resp:
					response = await resp.json()
					await ctx.send(f'Translated from:\n - Lang: `{langs[response[0]["detectedLanguage"]["language"]]["name"]}`\n - Certainty: `{response[0]["detectedLanguage"]["score"]*100}%`\n\nTranslation:\n - `{response[0]["translations"][0]["text"]}`')

	@commands.command(aliases=["ftr"])
	async def fromtranslate(self, ctx, fromlang, tolang, *, text):
		async with aiohttp.ClientSession() as s:
			async with ctx.typing():
				async with s.get("https://api.cognitive.microsofttranslator.com/languages?api-version=3.0") as resp:
					langs = await resp.json()
					langs = langs["translation"]
				if not (tolang in langs and fromlang in langs):
					return await ctx.send("Not a valid language code.")
				async with s.post(f"https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to={tolang}&from={fromlang}", headers={"Ocp-Apim-Subscription-Key": os.getenv('TRANSLATE_TOKEN'), "Ocp-Apim-Subscription-Region": "centralus", "Content-Type": "application/json"}, data="[{'Text':'"+text+"'}]") as resp:
					response = await resp.json()
					await ctx.send(f'Translation:\n - `{response[0]["translations"][0]["text"]}`')

	@commands.command()
	async def langs(self, ctx):
		async with aiohttp.ClientSession() as s:
			async with ctx.typing():
				async with s.get("https://api.cognitive.microsofttranslator.com/languages?api-version=3.0") as resp:
					langs = await resp.json()
					langsDict = langs["translation"]
					niceLangs = ""
					for key, value in langsDict.items():
						niceLangs = niceLangs + f"`{key}`: `{value['name']}`, "
					await ctx.send(niceLangs)

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.guild)
	async def web(self, ctx, *, url: str):
		async with ctx.typing():
			async with aiohttp.ClientSession() as s:
				async with s.post("http://magmachain.herokuapp.com/api/v1", headers=dict(website=url)) as r:
					website = (await r.json())["snapshot"]
					await ctx.send(embed=discord.Embed(color=discord.Color.blurple()).set_image(url=website))


def setup(bot):
	bot.add_cog(Utils(bot))
	print('[UtilsCog] Utils cog loaded')
