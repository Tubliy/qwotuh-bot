import discord
from discord.ext import commands
import json
import os
from datetime import datetime
import random

class QCoins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = 'qcoins.json'
        self.data = self.loadqcoins()
        self.coin_emoji = "<:qcoin:1367163106282963066>"
        
        self.error_embed = discord.Embed(title="Bank💲", description="Error: Not able to proceed with action", color=
        discord.Color.red())
        
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
        coin_embed.set_footer(text=f"{ctx.author.mention},  {date_string}")
        
        await ctx.send(embed=coin_embed)
        
    @commands.command()
    async def qgive(self, ctx, member : discord.Member, amount : int):
        
        
        sent_embed = discord.Embed(title="Bank💲", description=f"{ctx.author.mention}, you have given {amount} {self.coin_emoji} to {member.mention}", color=
        discord.Color.green())
        
        giver = str(ctx.author.id)
        receiver = str(member.id)
        
        if amount <= 0:
            try:
                await ctx.send(embed=self.error_embed)
                await ctx.author.send("Invalid number of coins, please enter a positive value.")
            except discord.Forbidden:
                ctx.send(f"{ctx.author.mention}, I'm unable to DM you please change your privacy settings.")
            return
        
        
        
        if self.get_balance(giver) < amount:
            try:
                await ctx.send(self.error_embed)
                await ctx.author.send("You don't have efficient coins to send that amount.")
            except discord.Forbidden:
                ctx.send(f"{ctx.author.mention}, I'm unable to DM you please change your privacy settings.")
            return
        
        self.add_qcoins(giver, -amount)
        self.add_qcoins(receiver, amount)
        
        await ctx.send(sent_embed)
        
    async def collect_coins(self, message):
        if message.author.bot:
            return
        
        self.add_qcoins(message.author.id, 10)
        
        
    @commands.command()
    async def gamble(self,ctx,amount : int):
        user_id = str(ctx.author.id)
        
        if amount <= 0:
            try:
                await ctx.send(embed=self.error_embed)
                await ctx.author.send("Invalid number of coins, please enter a positive value")
            except discord.Forbidden:
                ctx.send(f"{ctx.author.mention}, I'm unable to DM you please change your privacy settings.")
            return
        
        balance = self.get_balance(user_id)
        gamble_amount = amount * 3.5
        
        success_gamble = discord.Embed(title="Bank💲", description=f"{ctx.author.mention}, you have won {gamble_amount} {self.coin_emoji} 🎰!", color=
        discord.Color.green())
        failed_gamble = discord.Embed(title="Bank💲", description=f"{ctx.author.mention}, you have lost {amount} {self.coin_emoji} 💀 !", color=
        discord.Color.red())
        
        
        if balance < amount:
            try:
                await ctx.send(self.error_embed)
                await ctx.author.send("You don't have efficient coins to gamble that amount.")
            except discord.Forbidden:
                ctx.send(f"{ctx.author.mention}, I'm unable to DM you please change your privacy settings.")
            return
        
        if random.choice([True,False]):
            self.add_qcoins(user_id, gamble_amount)
            await ctx.send(embed=success_gamble)
        else:
            self.add_qcoins(user_id, -amount)
            await ctx.send(embed=failed_gamble)
        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def qset(self,ctx, member: discord.Member, amount : int):
        
        
                                    
        if amount <= 0:
            ctx.send(embed=self.error_embed)
            return
        
        reciever = str(member.id)
        self.data[reciever] = amount
        self.saveqcoins()
        
        
        admin_embed = discord.Embed(title="Bank💲", description=f"You sucessfully set {member.mention}'s coins to {amount} {self.coin_emoji}", color=discord.Color.dark_blue)
        admin_embed.set_footer(text="Admin command")
        
        
        await ctx.send(embed=admin_embed)
        
    

async def setup(bot):
    cog = QCoins(bot)
    await bot.add_cog(cog)
    bot.qcoins = cog
        
        
        
            
            
        
    