import asyncio, discord, youtube_dl, os, glob, re
from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

class VoiceError(Exception):
	pass

ytdl_format_options = {
	'format': 'bestaudio/best',
	'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
	'restrictfilenames': True,
	'noplaylist': True,
	'nocheckcertificate': True,
	'ignoreerrors': False,
	'logtostderr': False,
	'quiet': True,
	'no_warnings': True,
	'default_search': 'auto',
	'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
	'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

def cleanup(ctx, e, player, id):
	if e:
		print(f'Player error: {e}')
	else:
		for file in glob.glob(f"youtube-{id}*"):
			os.remove(file)

class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *, data, volume=0.5):
		super().__init__(source, volume)

		self.data = data

		self.title = data.get('title')
		self.url = data.get('url')

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

		if 'entries' in data:
			# take first item from a playlist
			data = data['entries'][0]

		filename = data['url'] if stream else ytdl.prepare_filename(data)
		return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
	status = {}
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def join(self, ctx, *, channel: discord.VoiceChannel):
		"""Joins a voice channel"""

		if ctx.voice_client is not None:
			return await ctx.voice_client.move_to(channel)

		await channel.connect()

	@commands.command()
	async def play(self, ctx, *, url):
		"""
		Plays a youtube video (Must be in the format "https://www.youtube.com/watch?v={Video ID}"
		"""
		url = url.lstrip("<").rstrip(">")
		if not re.search(r"https:\/\/www\.youtube\.com\/watch\?v=(?:.){11}$", url):
				return await ctx.send('Not a valid youtube URL!')
		if ctx.voice_client is None:
			if ctx.author.voice:
				await ctx.author.voice.channel.connect()
			else:
				await ctx.send('You are not connected to a voice channel.')
				raise VoiceError("You are not connected to a voice channel.")
		elif ctx.voice_client.is_playing():
			await ctx.send("Music is already playing!")
			raise VoiceError("Music is already playing!")

		async with ctx.typing():
			try:
				player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
				ctx.voice_client.play(player)
				await ctx.send(f'Now playing: {player.title}')
			except youtube_dl.utils.DownloadError:
				await ctx.send("Error downloading the file, is the link correct?")
				await ctx.voice_client.disconnect()

	# Broken might fix later
	# @commands.command()
	# async def stream(self, ctx, *, url):
	#     """Streams from a url (same as yt, but doesn't predownload)"""

	#     async with ctx.typing():
	#         player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
	#         ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

	#     await ctx.send('Now playing: {}'.format(player.title))

	@commands.command()
	async def volume(self, ctx, volume: int=None):
		"""Changes the player's volume"""

		if ctx.voice_client is None:
			return await ctx.send("Not connected to a voice channel.")

		if volume is None:
			return await ctx.send(f"Volume: {ctx.voice_client.source.volume * 100}")

		ctx.voice_client.source.volume = volume / 100
		await ctx.send("Changed volume to {}%".format(volume))

	@commands.command()
	async def stop(self, ctx):
		"""Stops and disconnects the bot from voice"""

		await ctx.voice_client.disconnect()
		

def setup(bot):
	bot.add_cog(Music(bot))
	print('[MusicCog] Music cog loaded')