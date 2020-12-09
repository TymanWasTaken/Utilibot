import discord
from discord.ext import commands

class Tickets(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.group(name="ticket", aliases=['tickets'], invoke_without_command=True)
	@commands.guild_only()
	@commands.is_owner()
	async def ticket(self, ctx):
		"""
		Ticket commands.
		"""
		
		embed=discord.Embed(title="Ticket Help", description="WIP")
		await ctx.send(embed=embed)
		
	@ticket.command(name="open", aliases=['new', 'create'])
	async def open(self, ctx, *, reason):
		"""
		Creates a new support ticket.
		"""
		ticketchan = await ctx.guild.create_text_channel(name=f"ticket-{reason}", reason=f"Ticket created by {ctx.author} ({ctx.author.id})")
		await ctx.send(f"Created a new ticket: {ticketchan.mention}", delete_after=20)
		await ctx.author.send(f"Ticket {ticketchan.mention} opened in **{ctx.guild}**")

	@ticket.command(name="rename")
	async def rename(self, ctx, *, newname):
		"""
		Renames the current ticket.
		"""
		await ctx.channel.edit(name=f"ticket-{newname}", reason=f"Ticket renamed by {ctx.author} ({ctx.author.id})")
		await ctx.send(f"Renamed this ticket to {ctx.channel.mention}")
		
	@ticket.command(name="close", aliases=['end'])
	async def close(self, ctx, *, reason):
		"""
		Closes the current support ticket without deleting the channel.
		"""
		await ctx.channel.edit(name=str(ctx.channel.name).replace("ticket", "closed"), reason=f"Ticket closed by {ctx.author} ({ctx.author.id})")
		await ctx.send("Closed this ticket")

	
	
#def setup(bot):
#	bot.add_cog(Tickets(bot))
#	print('[TicketsCog] Tickets cog loaded!')
	
