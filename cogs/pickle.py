import discord
from discord.ext import commands
import datetime
import json
import time
import logging
import aiohttp
import hypixel

now = datetime.datetime.now()
launchtime = datetime.datetime.utcnow()

logging.basicConfig(filename='bot.log',level=logging.INFO)

print("hypixel.py has been loaded")

with open('config.json', 'r') as cfg:
	config = json.load(cfg)

hypixelkey = config['hypixel']
keys = [config['hypixel']]
hypixel.setKeys(keys)

def isadmin(ctx):
	if str(ctx.author.id) not in config['admins']:
		admin = False
	else:
		admin = True
	return admin

async def getprefix(ctx):
	if not ctx.guild:
		return "$"
	with open('prefixes.json', 'r') as pfx:
		customprefix = json.load(pfx)
	try:
		prefix = customprefix[str(ctx.guild.id)]
	except Exception:
		prefix = "$"
	return prefix

class pickle(commands.Cog, name="Hypixel Commands"):
	def __init__(self, bot):
		self.bot = bot
  
	@commands.command(description="Get hypixel stats")
	async def hypixel(self, ctx, arg1: str = None, arg2: str = None):
		"""Get hypixel stats"""
		if arg1 == None:
			msg = await ctx.send("I need an IGN, `help`, `key` or `watchdog`")
			time.sleep(5)
			try:
				await msg.delete()
			except Exception as e:
				print(f"I failed to delete a message due to... {e}")
			return
		if arg1.lower() == "help":
			await ctx.send('help embed coming soon')
			return
		if arg1.lower() == "tournament":
			if arg2 == None:
				async with aiohttp.ClientSession() as session:
					async with session.get(f'https://api.hypixel.net/gamecounts?key={hypixelkey}') as resp:
						games = await resp.json()
				hall = games['games']['TOURNAMENT_LOBBY']['players']
				players = games['games']['SkyWars']['modes']['solo_crazyinsane']
				embed = discord.Embed(title="Tournament Player Count", colour=ctx.author.color, url="https://hypixel.net/threads/hypixel-tournaments-skywars-crazy-solo.1958904/", timestamp=datetime.datetime.now())
				embed.set_footer(text="Do `hypixel tournament <player>` to get a player's stats.")
				embed.add_field(name="Tournament Hall", value=format(hall, ',d'), inline=False)
				embed.add_field(name="Games", value=format(players, ',d'), inline=False)
				await ctx.send(embed=embed)
				return
			else:
				try:
					player = hypixel.Player(arg2)
				except hypixel.PlayerNotFoundException:
					await ctx.send('I couldn\'t find that player...')
					return
				p = player.JSON
				try:
					tributes = p['tourney']['total_tributes']
				except KeyError:
					trubutes = 0
				mode = p['stats']['SkyWars']['lastMode']
				if mode == "CRAZYTOURNEY":
					tournamentmode = True
				else:
					tournamentmode = False
				try:
					kills = p['stats']['SkyWars']['kills_crazytourney']
				except KeyError:
					kills = 0
				try:
					assists = p['stats']['SkyWars']['assists_crazytourney']
				except KeyError:
					assists = 0
				try:
					quits = p['stats']['SkyWars']['tourney_sw_crazy_solo_0_quits']
				except KeyError:
					quits = 0
				try:
					randomkit = p['stats']['SkyWars']['activeKit_TEAMS_tourney_random']
				except KeyError:
					randomkit = None
				if randomkit == False:
					kit = p['stats']['SkyWars']['activeKit_TEAMS_tourney']
					kit = kit.split('_')
					kit = kit[3]
					kit = kit.capitalize()
				elif randomkit == True:
					kit = 'Random'
				else:
					kit = 'Unknown'
				try:
					playtime = p['tourney']['sw_crazy_solo_0']['playtime']
				except KeyError:
					playtime = 'Hasn\'t played'
				if type(playtime) != int:
					playtime = 'Hasn\'t played'
				elif playtime > 60:
					hours = playtime // 60
					minutes = playtime % 60
					playtime = f'{hours} hours and {minutes} minutes'
				elif playtime >= 1:
					playtime = f'{playtime} minutes'
				embed = discord.Embed(title=f"Tournament stats for {arg2}", colour=ctx.author.color, url="https://hypixel.net/threads/hypixel-tournaments-skywars-crazy-solo.1958904/", timestamp=datetime.datetime.now())
				embed.set_footer(text="Want more integrations? Use the suggest command to suggest some")
				embed.add_field(name="Current Tournament", value="Skywars", inline=True)
				embed.add_field(name="Started on", value="March 15th, 2019", inline=True)
				embed.add_field(name="Recently Played?", value=tournamentmode, inline=True)
				embed.add_field(name="Total Tributes", value=tributes, inline=True)
				embed.add_field(name="Kills", value=kills, inline=True)
				embed.add_field(name="Assists", value=assists, inline=True)
				embed.add_field(name="Quits", value=quits, inline=True)
				embed.add_field(name="Kit", value=kit, inline=True)
				embed.add_field(name="Time Played", value=playtime, inline=True)
				await ctx.send(embed=embed)
				return
		if arg1.lower() == "watchdog":
			async with aiohttp.ClientSession() as session:
				async with session.get(f'https://api.hypixel.net/watchdogstats?key={hypixelkey}') as resp:
					watchdog = await resp.json()
			color = ctx.author.color
			embed = discord.Embed(title="Watchdog Stats", colour=color, timestamp=datetime.datetime.now())
			embed.set_thumbnail(url="https://hypixel.net/attachments/cerbtrimmed-png.245674/")
			embed.set_footer(text="Want more integrations? Use the suggest command to suggest some")
			embed.add_field(name="Watchdog Bans in the last minute", value=watchdog['watchdog_lastMinute'], inline=False)
			embed.add_field(name="Staff bans in the last day", value=watchdog['staff_rollingDaily'], inline=False)
			embed.add_field(name="Watchdog bans in the last day", value=watchdog['watchdog_rollingDaily'], inline=False)
			embed.add_field(name="Staff Total Bans", value=watchdog['staff_total'], inline=False)
			embed.add_field(name="Watchdog Total Bans", value=watchdog['watchdog_total'], inline=False)
			await ctx.send(embed=embed)
		if arg1.lower() == "key":
			lastmin = "0"
			async with aiohttp.ClientSession() as session:
				async with session.get(f'https://api.hypixel.net/key?key={hypixelkey}') as resp:
					key = await resp.json()
			try:
				lastmin = key['record']['queriesInPastMin']
			except Exception as e:
				pass
			color = ctx.author.color
			embed = discord.Embed(title="My API Key Stats", colour=color, timestamp=datetime.datetime.now())
			embed.set_footer(text="Want more integrations? Use the suggest command to suggest some")
			embed.add_field(name="Owner", value="PoppyIsFake (4686e7b58815485d8bc4a45445abb984)", inline=False)
			embed.add_field(name="Total Requests", value=key['record']['totalQueries'], inline=False)
			embed.add_field(name="Requests in the past minute", value=lastmin, inline=False)
			await ctx.send(embed=embed)
		else:
			msg = await ctx.send(f"Requesting info about `{arg1}` from the Hypixel API!")
			channel = ctx.message.channel
			color = ctx.author.color
			async with channel.typing():
				player = hypixel.Player(arg1)
				p = player.JSON
				try:
					tributes = p['tourney']['total_tributes'] # TOURNAMENT TRIBUTES
				except KeyError:
					tributes = 0
				level = round(player.getLevel())
				try:
					rankcolor = p['rankPlusColor']
				except Exception:
					rankcolor = "RED"
				try:
					prefixcolor = p['monthlyRankColor']
				except Exception as e:
					prefixcolor = "GOLD"
				lastlogin = p['lastLogin']
				lastlogout = p['lastLogout']
				if lastlogin > lastlogout:
					status = "Online!"
				else:
					status = "Offline!"
				try:
					rank = player.getRank()['rank']
				except Exception:
					rank = None
				if rank == "MVP+":
					if rankcolor == "RED":
						rankimg = "https://firediscordbot.tk/pickleranks/MVPplusone.png"
					if rankcolor == "GOLD":
						rankimg = "https://firediscordbot.tk/pickleranks/MVPplustwo.png"
					if rankcolor == "GREEN":
						rankimg = "https://firediscordbot.tk/pickleranks/MVPplusthree.png"
					if rankcolor == "YELLOW":
						rankimg = "https://firediscordbot.tk/pickleranks/MVPplusfour.png"
					if rankcolor == "LIGHT_PURPLE":
						rankimg = "https://firediscordbot.tk/pickleranks/MVPplusfive.png"
					if rankcolor == "WHITE":
						rankimg = "https://firediscordbot.tk/pickleranks/MVPplussix.png"
					if rankcolor == "BLUE":
						rankimg = "https://firediscordbot.tk/pickleranks/MVPplusseven.png"
					if rankcolor == "DARK_GREEN":
						rankimg = "https://firediscordbot.tk/pickleranks/MVPpluseight.png"
					if rankcolor == "DARK_RED":
						rankimg = "https://firediscordbot.tk/pickleranks/MVPplusnine.png"
					if rankcolor == "DARK_AQUA":
						rankimg = "https://firediscordbot.tk/pickleranks/MVPplusten.png"
					if rankcolor == "DARK_PURPLE":
						rankimg = "https://firediscordbot.tk/pickleranks/MVPpluseleven.png"
					if rankcolor == "GREY":
						rankimg = "https://firediscordbot.tk/pickleranks/MVPplustwelve.png"
					if rankcolor == "BLACK":
						rankimg = "https://firediscordbot.tk/pickleranks/MVPplusthirteen.png"
				if rank == "MVP":
					rankimg = "https://firediscordbot.tk/pickleranks/MVP.png"
				if rank == "VIP+":
					rankimg = "https://firediscordbot.tk/pickleranks/VIPplus.png"
				if rank == "VIP":
					rankimg = "https://firediscordbot.tk/pickleranks/VIP.png"
				try:
					monthlyrank = p['monthlyPackageRank']
				except Exception:
					monthlyrank = None
				if monthlyrank == "SUPERSTAR":
					if prefixcolor == "GOLD":
						if rankcolor ==  "Default (Red)":
							rankimg = "https://firediscordbot.tk/pickleranks/SUPERSTARlred.png"
						if rankcolor ==  "GOLD":
							rankimg = "https://firediscordbot.tk/pickleranks/SUPERSTARgold.png"
						if rankcolor ==  "GREEN":
							rankimg = "https://firediscordbot.tk/pickleranks/SUPERSTARlgreen.png"
						if rankcolor ==  "YELLOW":
							rankimg = "https://firediscordbot.tk/pickleranks/SUPERSTARyellow.png"
						if rankcolor ==  "LIGHT_PURPLE":
							rankimg = "https://firediscordbot.tk/pickleranks/SUPERSTARlpurple.png"
						if rankcolor ==  "WHITE":
							rankimg = "https://firediscordbot.tk/pickleranks/SUPERSTARwhite.png"
						if rankcolor ==  "BLUE":
							rankimg = "https://firediscordbot.tk/pickleranks/SUPERSTARblue.png"
						if rankcolor ==  "DARK_GREEN":
							rankimg = "https://firediscordbot.tk/pickleranks/SUPERSTARdgreen.png"
						if rankcolor ==  "DARK_RED":
							rankimg = "https://firediscordbot.tk/pickleranks/SUPERSTARdred.png"
						if rankcolor ==  "DARK_AQUA":
							rankimg = "https://firediscordbot.tk/pickleranks/SUPERSTARdaqua.png"
						if rankcolor ==  "DARK_PURPLE":
							rankimg = "https://firediscordbot.tk/pickleranks/SUPERSTARdpurple.png"
						if rankcolor ==  "GREY":
							rankimg = "https://firediscordbot.tk/pickleranks/SUPERSTARgrey.png"
						if rankcolor ==  "BLACK":
							rankimg = "https://firediscordbot.tk/pickleranks/SUPERSTARblack.png"
					if prefixcolor == "AQUA":
						if rankcolor ==  "Default (Red)":
							rankimg = "https://firediscordbot.tk/pickleranks/threeRED.png"
						if rankcolor ==  "GOLD":
							rankimg = "https://firediscordbot.tk/pickleranks/threeGOLD.png"
						if rankcolor ==  "GREEN":
							rankimg = "https://firediscordbot.tk/pickleranks/threeGREEN.png"
						if rankcolor ==  "YELLOW":
							rankimg = "https://firediscordbot.tk/pickleranks/threeYELLOW.png"
						if rankcolor ==  "LIGHT_PURPLE":
							rankimg = "https://firediscordbot.tk/pickleranks/threePURPLE.png"
						if rankcolor ==  "WHITE":
							rankimg = "https://firediscordbot.tk/pickleranks/threeWHITE.png"
						if rankcolor ==  "BLUE":
							rankimg = "https://firediscordbot.tk/pickleranks/threeBLUE.png"
						if rankcolor ==  "DARK_GREEN":
							rankimg = "https://firediscordbot.tk/pickleranks/threeDGREEN.png"
						if rankcolor ==  "DARK_RED":
							rankimg = "https://firediscordbot.tk/pickleranks/threeDRED.png"
						if rankcolor ==  "DARK_AQUA":
							rankimg = "https://firediscordbot.tk/pickleranks/threeDAQUA.png"
						if rankcolor ==  "DARK_PURPLE":
							rankimg = "https://firediscordbot.tk/pickleranks/threeDPURPLE.png"
						if rankcolor ==  "GREY":
							rankimg = "https://firediscordbot.tk/pickleranks/threeGREY.png"
						if rankcolor ==  "BLACK":
							rankimg = "https://firediscordbot.tk/pickleranks/threeBLACK.png"
				if rank == "Non":
					rankimg = "https://firediscordbot.tk/pickleranks/NON.png"
				if rank == "YouTube":
					rankimg = "https://firediscordbot.tk/pickleranks/YOUTUBE.png"
				if rank == "Helper":
					rankimg = "https://firediscordbot.tk/pickleranks/HELPER.png"
				if rank == "Moderator":
					rankimg = "https://firediscordbot.tk/pickleranks/MOD.png"
				if rank == "Admin":
					rankimg = "https://firediscordbot.tk/pickleranks/ADMIN.png"
				if arg2 == None:
					msg = await ctx.send(f"Retrieving {p['displayname']}'s info...")
					uuid = player.UUID
					embed = discord.Embed(title=f"{p['displayname']}'s Info", colour=color, timestamp=datetime.datetime.now())
					if rankimg != None:
						embed.set_image(url=rankimg)
					embed.set_thumbnail(url=f"https://crafatar.com/avatars/{uuid}?overlay=true")
					embed.set_footer(text="Want more integrations? Use the suggest command to suggest some")
					embed.add_field(name="Online Status", value=status, inline=True)
					try:
						language = p['userLanguage']
					except Exception:
						language = "Not Set"
					embed.add_field(name="Language", value=language, inline=True)
					try:
						channel = p['channel']
					except Exception:
						channel = "ALL"
					embed.add_field(name="Chat Channel", value=channel, inline=True)
					try:
						ver = p['mcVersionRp']
					except Exception:
						ver = "Unknown"
					embed.add_field(name="Version", value=ver, inline=True)
					embed.add_field(name="Level", value=level, inline=True)
					embed.add_field(name="Karma", value=format(p['karma'], ',d'), inline=True)
					try:
						twitter = p['socialMedia']['TWITTER']
					except Exception:
						twitter = "Not Set"
					try:
						yt = p['socialMedia']['links']['YOUTUBE']
					except Exception:
						yt = "Not Set"
					try:
						insta = p['socialMedia']['INSTAGRAM']
					except Exception:
						insta = "Not Set"
					try:
						twitch = p['socialMedia']['TWITCH']
					except Exception:
						twitch = "Not Set"
					try:
						beam = p['socialMedia']['BEAM']
					except Exception:
						beam = "Not Set"
					try:
						dscrd = p['socialMedia']['links']['DISCORD']
					except Exception:
						dscrd = "Not Set"
					embed.add_field(name="Social Media", value=f"Twitter: {twitter}\nYouTube: {yt}\nInstagram: {insta}\nTwitch: {twitch}\nBeam: {beam}\nDiscord: {dscrd}", inline=True)
					if tributes != 0:
						embed.add_field(name="Tournament Tributes", value=tributes, inline=False)
					await msg.edit(embed=embed)

def setup(bot):
	bot.add_cog(pickle(bot))