#! /usr/bin/env python3

"""
 The Memeonaut will bring peace and love to the universe by sending memes from reddit on discord!

    Copyright (C) 2021 Jan Raab et al.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

	### VERSION HISTORY ###
	# 0.1: 		how it started
	# 0.3: 		further updates (@Jonas)
	# 0.42: 	official first release
	# 0.69:		major new update after Klausurenphase WS20/21 (@Simon)
	# 1.69: 	major upgrade to structure 
	###
"""

### imports
import discord
from discord.ext import commands
from io import BytesIO
import sys, os, re
import json
import random
import asyncpraw
import requests, subprocess
import logging as log

# reduce startup time by for example not getting new reddit data on startup
dev_mode = False

log.basicConfig(level=log.INFO, stream=sys.stdout)

### configuration
try:
	with open('configuration.json', 'r') as configuration:
		global config
		config = json.load(configuration)
		sentmemes = config["files"]["sentmemes"]
		emojis = config.get("emojis")
		desc = config.get("commands")
		log.info("Configuration got loaded: {}".format(config))
except Exception:
	log.exception("Configuration (configuration.json) was not found or couldn't be opened")
	sys.exit()
try:
	with open('token.json', 'r') as tkn:
		global token
		token = json.load(tkn)
		log.info("Token got loaded")
except Exception:
	log.exception("Token (token.json) was not found or couldn't be opened!")
	sys.exit()

### global variables
memelist = [] # store memes we will send here
lewdlist = [] # store nsfw-content we will send here
spoiler = True # default: nsfw set spoiler

#### create a reddit instance
try:
	reddit = asyncpraw.Reddit(client_id = token["reddit_id"], client_secret = token["reddit_tkn"], user_agent = 'Mozilla/5.0')
except Exception:
	log.exception("No usage of REDDIT API is possible! Wrong token/id?")
	sys.exit()

### backend functions
# update the memelist  
async def update_list():

	log.info("Updating Memelist...")
	# reset the current list to prevent :reeee:posts
	global memelist, lewdlist
	memelist = []
	lewdlist = []

	# save already sent memes as list (performance)
	try:
		with open(sentmemes, 'r') as sm:
			already_sent = sm.readlines()
	except:
		with open(sentmemes, 'a') as sm:
			sm.write("Start of already sent memes. Format is title;image_url")
			log.warning("Starting a new anti-repost list. Expect to get some memes you have already seen.")
	try:
		for sub in config.get("subreddits", None): # go through subreddits
			subreddit = await reddit.subreddit(sub)
			log.info("Searching in subreddit: {0}".format(sub))
			async for post in subreddit.hot(limit=30): # go through posts
				image_url = post.url
				image_title = post.title
				#print("Image Title: {0} \t Image URL: {1}".format(image_title,image_url)) #debug
				line = "{};{}\n".format(image_title, image_url)
				if image_url.split('.')[-1] in config["extensions"]:	# has right extension
					if line not in already_sent: # meme not sent already
						if not post.over_18:	# decide if nsfw or not
							memelist.append(line)
						else:
							lewdlist.append(line)
	except:
		log.exception("Something went wrong while getting a meme.")
		log.debug("Memelist: {}\nNSFW-List: {}".format(memelist,lewdlist))
	log.debug("Done... Memes to send: " + str(len(memelist)) + " | NSFW to send: " +  str(len(lewdlist)))

def get_comic(whattype=None):
	ret = None
	possible_sites = list(config["comics"].keys())
	if whattype is None:
		whattype = random.choice(possible_sites)
	log.info("Searching for a {} comic.".format(whattype))

	try:
		req = requests.get(url = config["comics"].get(whattype))
	except:
		return ret
	# only xkdc for now - change for other sites
	id = ""
	for l in req.text.split('\n'):
		if "id" in l:
			try:
				id = l.split('"')[1]
			except:
				pass
		if id == 'comic' and "img src" in l: 
			ret =  "http:" + l.split('"')[1]

	return ret

def get_meme(nsfw=False):
	log.debug("Searching for a {}meme.".format("nsfw " if nsfw else ''))
	try:
		if nsfw:
			line = lewdlist.pop(random.randint(0, len(lewdlist)-1))
		else:
			line = memelist.pop(random.randint(0, len(memelist)-1))
	except Exception:
		log.info("No meme found!")
		return None
	# write meme we want to send in sentmemes
	with open(sentmemes, 'a') as sent_memes:
		log.info("Writing meme in sentmemes: {}".format(line.replace('\n', '')))
		sent_memes.write(line)

	title = line.split(';')[0]
	url = line.split(';')[1]
	return [title, url]

### Here starts the discord API

'''
Define a new command as such:
@bot.command(name="command_name", help=config["command_name"]["help"], brief=config["command_name"]["brief"])
async def new_command_name(ctx):
	# do stuff here
	# use ctx to interact
	# define and use backend functions
	# log.info("basic functionality")
	# log.debug("debug message")
	# log.error("hefty error occured")

'''
intents = discord.Intents.default()
# allow the bot to access the member list
# !!! This has to be enabled explicitly in the Discord Developer Settings!
# Enable it in Bot > Priviledged Gateway Intents > Server Members Intent
intents.members = True
bot = commands.Bot(command_prefix='!', description=config["bot_description"], case_insensitive=True, intents=intents)

@bot.event
async def on_ready():
	log.info("Logged on as {} ID#{}!".format(bot.user.name, bot.user.id))
	if not dev_mode:
		await update_list()
	print("ready")

@bot.command(name='meme', help=desc["meme"]["help"], brief=desc["meme"]["brief"])
async def meme(ctx):
	log.info("Got a Meme-Request from {0}!".format(ctx.author))
	await ctx.message.delete() # delete old message
	ret = get_meme()
	if ret is None: # try refresh and get new meme
		await update_list()
		ret = get_meme()
	if ret is None: # still not? then error
		log.error("No meme found! (╯°□°）╯︵ ┻━┻")
		await ctx.send("No Me Me found! (╯°□°）╯︵ ┻━┻")

	else: 
		title = ret[0]
		url = ret[1]

	await ctx.send(url)

@bot.command(name='refresh',help=desc["refresh"]["help"], brief=desc["refresh"]["brief"])
async def refresh(ctx):
	log.debug("Request to update Memelist")
	await ctx.message.add_reaction('👍')
	await update_list()
	await ctx.message.delete(delay=10)

@bot.command(name='comic',help=desc["comic"]["help"], brief=desc["comic"]["brief"])
async def comic(ctx, comictype=None):
	log.debug("Request to get a comic")
	ret = get_comic(comictype)
	if ret is None:
		ret = get_comic(comictype)
		if ret is None:
			ret = "No comic found! :("
	await ctx.message.delete()
	await ctx.send(ret)

@bot.command(name='nsfw',help=desc["nsfw"]["help"], brief=desc["nsfw"]["brief"])
async def not_safe_for_work(ctx, arg=None):
		log.debug("Request to get a not safe for work image")

		if ctx.message.channel.is_nsfw():
			try:
				splr = arg.split('=')[-1]
				global spoiler
				if splr == "on" or splr.lower() == "true":
					spoiler = True
				elif splr == "off" or splr.lower == "false":
					spoiler = False
			except:
				pass
			ret = get_meme(nsfw=True)
			await ctx.message.delete() # delete old message

			if ret is None: # try refresh and get new nsfw
				await update_list()
				ret = get_meme(nsfw=True)
			if ret is None: # still not? then error
				log.error("No nsfw image found! (╯°□°）╯︵ ┻━┻")
				await ctx.send("No naugthy pic found! Gotta stay horny *bonk*")

			else: 
				title = ret[0]
				url = ret[1]
				if spoiler:
					url = "||" + url + "||"
				await ctx.send(url)
		else:
			await ctx.send("Go to Honry-Jail! Thats not the place to send those pictures...")

@bot.command(name='info',help=desc["info"]["help"], brief=desc["info"]["brief"])
async def info(ctx):
	mc = len(open(config['files']['sentmemes'], 'r').readlines()) # number of memes
	helptext= [	config['bot_description'],
				"On version {}:{} right now. \n".format(config["version_nmbr_high"], config["version_nmbr_low"]),
				"Stats:\nTill now, {} memes were sent!".format(mc)
				]
	await ctx.send("\n".join(helptext))


@bot.command(name='bonk',help=desc["bonk"]["help"], brief=desc["bonk"]["brief"])
async def bonk(ctx, *, who=None):
	from bonk import create_bonk_gif

	if not who:
		await ctx.message.channel.send("tip: !bonk <Name>")
		return
	
	# attempt to convert to member
	try:
		who = await commands.MemberConverter().convert(ctx, who)
	except commands.MemberNotFound:
		await ctx.message.channel.send(f"Sorry, I couldn't find {who}.")
		return

	log.info(f"Received bonk request {ctx.message.content.lower()} with arg {who}")

	avatar = who.avatar_url_as(size=256)

	# download avatar of user
	file_obj = BytesIO(requests.get(avatar).content)
	# create bonked gif - will be saved under bonk_gif_path because this stupid library can only save GIFs as files
	bonk_gif_path = create_bonk_gif(file_obj)

	string_to_send = "Get bonked, " + who.mention
	await ctx.message.channel.send(content=string_to_send, file=discord.File(bonk_gif_path))
	# remove bonk gif after sending
	os.remove(bonk_gif_path)


@bot.listen('on_message')
async def react(message):
	if message.author == bot.user:
		return
	# here we can define stuff we want to do on every message
	log.info("Got a message from {0}! It says {1}".format(message.author, message.content))

bot.run(token['discord_tkn'])

# lul
