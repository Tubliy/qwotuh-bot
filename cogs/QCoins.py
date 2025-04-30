import discord
from discord.ext import commands
import json
import os
from datetime import datetime

class QCoins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = 'qcoins.json'
        self.data = self.loadqcoins()
        self.coin_emoji = "<:qcoin:1367163106282963066>"
        
    def loadqcoins(self):
        if not os.path.exists(self.file):
            return {}
        with open(self.file, 'r') as f:
            return json.load(f)
        
    def saveqcoins(self):
        with open(self.file, 'w') as f:
            json.dump(self.data,f, indent=4)
            
    def get_balance(self, user_id):
        return self.data.get(str(user_id),0)
    
    def add_qcoins(self,user_id, amount):
        user_id = str(user_id)
        self.data[user_id] = self.data.get(str(user_id),0) + amount
        self.saveqcoins()
        
    @commands.command()
    async def coins(self,ctx):
        coins = self.get_balance(ctx.author.id)
        now = datetime.now()
        date_string = now.strftime("%B %d, %Y")
        
        coin_embed = discord.Embed(title="Bank💲", description=f"You have a total of {coins} {self.coin_emoji}", color=
        discord.Color.green())
        coin_embed.set_footer(text=f"{ctx.author.id},  {date_string}")
        
        await ctx.send(embed=coin_embed)
        
    @commands.command()
    async def qgive(self, ctx, member : discord.Member, amount : int):
        error_embed = discord.Embed(title="Bank💲", description=f"Error: Not able to proceed with action", color=
        discord.Color.red())
        
        
        if amount <= 0:
            await ctx.send(embed=error_embed)
            await ctx.author.send("Invalid number of coins please enter a positive value.")
            return
        
        giver = str(ctx.author.id)
        receiver = str(member.id)
        
        if self.get_balance(giver) < amount:
            await
            
            
        
    