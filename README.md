# Discord Meme Bot

My name is Memeonaut™, I scavange Reddit on the search for new memes for your Discord server. Here is the link to invite me:  
https://discord.com/api/oauth2/authorize?client_id=840923794087477248&permissions=59456&scope=bot

We use discord.py: https://discordpy.readthedocs.io/en/latest/index.html
As well as the Reddit API asyncpraw: https://asyncpraw.readthedocs.io/en/latest/

Join our Discord: https://discord.gg/YuW4tsT3hH

# How can you start

Clone this repo.

Build your own token*

Make run.

(*)
With the Discord Developer Portal you can make your own bot: https://discord.com/developers/applications
- "New application" - Choose name (i.e. "<YOURNAME>'s bot")
- Bot -> Add a bot ==> There is the DISCORD_TOKEN
- OAuth -> OAuth2 URL Generator -> choose "bot", copy link and invite to your server.
- Check the bot's permissions  

Then you can create a Reddit-"App": https://old.reddit.com/prefs/apps/
- create application
- script
- redirect url "http://localhost:8080

From here, you can add those values to the token.json file and you are ready to rock!

# Version History

## RELEASE 0.1
Now live on GitHub! 
This project was originally developed for a private server but the author decided it would be best served public.
