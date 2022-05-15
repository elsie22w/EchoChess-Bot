# IMPORTING
import discord
import uuid
import requests
import shutil
import os

# IMPORT FUNCTIONS 
from dotenv import load_dotenv
from discord.ext import commands

# LOADS THE .ENV FILE THAT RESIDES ON THE SAME LEVEL AS THE SCRIPT.
load_dotenv()

# GRAB THE API TOKEN FROM THE .ENV FILE.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# GETS THE CLIENT OBJECT FROM DISCORD.PY. CLIENT IS SYNONYMOUS WITH BOT.
bot = discord.Client()
bot = commands.Bot(command_prefix = "!")

# FILE SCANNER
@bot.command(name="file-scanner", help = 'scans image with written moves and inputs them into pgn')
async def scan(ctx):
        try:
                url = ctx.message.attachments[0].url            
        except IndexError:
                await ctx.send("No attachments detected!")
        else:
                if url[0:26] == "https://cdn.discordapp.com":   
                    r = requests.get(url, stream=True)
                    imageName = 'moves.jpg'      
                    with open(imageName, 'wb') as out_file:
                        shutil.copyfileobj(r.raw, out_file)
                        
        #DOES STUFF AOIDSJKL

        await ctx.channel.send(file=discord.File("moves.pgn"))



# FIND TATICS
@bot.command(name="find-tactics", help = 'finds possible strategies and possible moves')
async def analyze(ctx):
        global username, games
        await ctx.channel.send("Please enter your username")
        
        def check(username):
                return username.author == ctx.author and username.channel == ctx.channel
        username = (await bot.wait_for("message", check=check)).content

        #GET RID OF THIS PART VVV
        await ctx.channel.send(username.content)
        
        await ctx.channel.send("Please enter the number of games you would like to review")

        def check(games):
                return games.author == ctx.author and games.channel == ctx.channel
        games = (await bot.wait_for("message", check=check)).content

        #GET RID OF THIS PART VVV
        await ctx.channel.send(games.content)
        
        await ctx.channel.send(file=discord.File("tactics.pgn"))



# ANALYZE GAME
@bot.command(name="analyze-game", help = 'provides an analysis of most recent game')
async def analyze(ctx):
        global username2
        await ctx.channel.send("Please enter your username")
        
        def check(username2):
                return username2.author == ctx.author and username2.channel == ctx.channel
        username2 = (await bot.wait_for("message", check=check)).content

        #GET RID OF THIS PART VVV
        await ctx.channel.send(username2)

        await ctx.channel.send(file=discord.File("analysis.pgn"))

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
print(DISCORD_TOKEN)
bot.run(DISCORD_TOKEN)
