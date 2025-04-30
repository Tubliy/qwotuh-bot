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
        self.doublecoins = None
        
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
    async def coins(self,ctx, member : discord.Member = None):
        member = member or ctx.author
        coins = self.get_balance(member.id)
        now = datetime.now()
        date_string = now.strftime("%B %d, %Y")
        
        coin_embed = discord.Embed(title="Bank💲", description=f"{member.mention} has a total of {coins} {self.coin_emoji}", color=
        discord.Color.green())
        coin_embed.set_footer(text=f"Requested by {ctx.author.display_name},  {date_string}")
        
        await ctx.send(embed=coin_embed)
        
    @commands.command()
    async def qgive(self, ctx, member: discord.Member, amount: int):
        giver = str(ctx.author.id)
        receiver = str(member.id)

        if ctx.author.id == member.id:
            try:
             await ctx.send(embed=self.error_embed)
             await ctx.author.send(f"{ctx.author.mention}, you can't give Q Coins to yourself.")
            except discord.Forbidden:
                await ctx.send(f"{ctx.author.mention}, I'm unable to DM you. Please change your privacy settings.")
            return
            

        if amount <= 0:
          try:
              await ctx.send(embed=self.error_embed)
              await ctx.author.send("Invalid number of coins, please enter a positive value.")
          except discord.Forbidden:
                await ctx.send(f"{ctx.author.mention}, I'm unable to DM you. Please change your privacy settings.")
          return

        if self.get_balance(giver) < amount:
         try:
             await ctx.send(embed=self.error_embed)
             await ctx.author.send("You don't have sufficient coins to send that amount.")
         except discord.Forbidden:
             await ctx.send(f"{ctx.author.mention}, I'm unable to DM you. Please change your privacy settings.")
         return

        self.add_qcoins(giver, -amount)
        self.add_qcoins(receiver, amount)

        sent_embed = discord.Embed(
          title="Bank💲",
             description=f"{ctx.author.mention}, you have given {amount} {self.coin_emoji} to {member.mention}",
                color=discord.Color.green()
            )

        await ctx.send(embed=sent_embed)

        
    async def collect_coins(self, message):
        if message.author.bot:
            return
        if not self.doublecoins:
         self.add_qcoins(message.author.id, 10)
        self.doublecoins()
        
        
    @commands.command()
    async def gamble(self,ctx,amount : int):
        user_id = str(ctx.author.id)
        
        random_amount = [0.5, 1.5, 1, 2, 2.24, 3.45, 5, 5.7, 10]
        
        if amount <= 0:
            try:
                await ctx.send(embed=self.error_embed)
                await ctx.author.send("Invalid number of coins, please enter a positive value")
            except discord.Forbidden:
               await ctx.send(f"{ctx.author.mention}, I'm unable to DM you please change your privacy settings.")
            return
        
        balance = self.get_balance(user_id)
        gamble_amount = round(amount * random.choice(random_amount))
        
        success_gamble = discord.Embed(title="Bank💲", description=f"{ctx.author.mention}, you have won {gamble_amount} {self.coin_emoji} 🎰!", color=
        discord.Color.green())
        failed_gamble = discord.Embed(title="Bank💲", description=f"{ctx.author.mention}, you have lost {amount} {self.coin_emoji} 💀 !", color=
        discord.Color.red())
        
        
        if balance < amount:
            try:
                await ctx.send(self.error_embed)
                await ctx.author.send("You don't have sufficient coins to gamble that amount.")
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
            await ctx.send(embed=self.error_embed)
            return
        
        reciever = str(member.id)
        self.data[reciever] = amount
        self.saveqcoins()
        
        
        embed = discord.Embed(
        title="✅ Coins Set",
        description=f"{member.mention} now has **{amount}** {self.coin_emoji}",
        color=discord.Color.green()
            )
        embed.set_footer(text="Admin command")
        await ctx.send(embed=embed)

        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def doublecoins(self,ctx):
        self.doublecoins = True
        self.add_qcoins(ctx.author.id, 40)
        
        double_embed = discord.Embed(title="Bank💲", description="Double coins is now activate!", color=
        discord.Color.gold())
        double_embed.set_footer(text="Admin command")

        await ctx.send(embed=double_embed)

async def setup(bot):
    cog = QCoins(bot)
    await bot.add_cog(cog)
    bot.qcoins = cog
        
        
        
            
            
        
    