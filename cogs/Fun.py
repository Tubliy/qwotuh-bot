import discord
from discord.ext import commands
import random
import aiohttp
import asyncio

class Fun(commands.Cog):
    def __init__(self, bot):
       self.bot = bot
       
       
       
    @commands.command(name="ppsize")
    async def ppsize(self, ctx):
        size = random.randint(1,12)
        
        if not ctx.message.mentions:
            await ctx.send(f"{ctx.author.mention}'s penis is {size} inches long.")
            return
        
        tagged_user = ctx.message.mentions[0]
        
        await ctx.send(f"{tagged_user.mention}'s penis is {size} inches long.")
        
    @commands.command(name="rps")
    async def rps(self, ctx, *, message : str):
        rps_choices = ["rock", "paper", "scissors"]
        try:
            if message.lower() not in rps_choices:
                raise ValueError("Invalid Input")
            
            rps = random.choice(rps_choices)
             
            embed = discord.Embed(title="Command: rps", description=f"I choose {rps}.")
            await ctx.send(embed=embed)
             
            await asyncio.sleep(1)

            if rps.lower() == message.lower():
               await ctx.send("It's a tie!")
            elif (rps == "Rock" and message.lower() == "scissors") or \
            (rps == "Paper" and message.lower() == "scissors") or \
            (rps == "Scissors" and message.lower() == "rock"):
               await ctx.send("You win!")
            else:
                await ctx.send("I win!")
        except ValueError:
            await ctx.send("Invalid input: Please choose rock, paper, or scissors.")

    @commands.command(name="coinflip")
    async def coinflip(self, ctx):
     coinflip = random.choice(["heads", "tails"])
     embed = discord.Embed(title="Command: coinflip",description=f"The coin landed on {coinflip}.", color=discord.Color.brand_red())
     await ctx.send(embed=embed)
     
    @commands.command(name="meme")
    async def meme(self, ctx):
        async with aiohttp.ClientSession() as session:
         async with session.get("https://meme-api.com/gimme") as response:
            if response.status == 200:
             meme_data = await response.json()
             title = meme_data["title"]
             url = meme_data["url"]
             post_link = meme_data["postLink"]
             subreddit = meme_data["subreddit"]
        
             embed = discord.Embed(title=title, url=post_link, color=discord.Color.random())
             embed.set_image(url=url)
             embed.set_footer(text=f"From r/{subreddit}")
            
             await ctx.send(embed=embed)
            else:
             await ctx.send("Not able to fetch a meme!")
        
        
        
async def setup(bot):
    cog = Fun(bot)
    await bot.add_cog(cog)