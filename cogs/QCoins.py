import discord
from discord.ext import commands
import json
import os
import time
from datetime import datetime, timedelta
import random

class QCoins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = 'qcoins.json'
        self.data = self.loadqcoins()
        self.coin_emoji = "<:qcoin:1367163106282963066>"
        self.random_amount = [0.5, 1.5, 1, 2, 2.24, 3.45, 5, 5.7, 10]
        self.dailycoins_cooldown = {}
        
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
        if getattr(self, "doublecoins_active", False):
            self.add_qcoins(message.author.id, 40)
        else:
            self.add_qcoins(message.author.id,20)
        
        
    @commands.command()
    async def gamble(self,ctx,amount : int):
        user_id = str(ctx.author.id)
        
        
        if amount <= 0:
            try:
                await ctx.send(embed=self.error_embed)
                await ctx.author.send("Invalid number of coins, please enter a positive value")
            except discord.Forbidden:
               await ctx.send(f"{ctx.author.mention}, I'm unable to DM you please change your privacy settings.")
            return
        
        balance = self.get_balance(user_id)
        gamble_amount = round(amount * random.choice(self.random_amount))
        
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
        if getattr(self, "doublecoins_active", False):
         self.doublecoins_active = False
         embed = discord.Embed(title="Bank💲", description="Double coins has been deactivated.", color=
         discord.Color.gold())
        else:
            self.doublecoins_active = True
            embed = discord.Embed(title="Bank💲", description="Double coins has been activated!", color=
            discord.Color.gold())

        embed.set_footer(text="Admin command")
        await ctx.send(embed=embed)
        
    @commands.command()
    async def daily(self,ctx):
        now = time.time()
        cooldown = 86400
        user_id = ctx.author.id
        
        last_used = self.dailycoins_cooldowns.get(user_id,0)
        remaining = int(cooldown - (now - last_used))
        
        balance = self.get_balance(user_id)
        daily_amount = round(balance *random.choice(self.random_amount))
        
        if remaining > 0:
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            seconds = remaining % 60
            await ctx.send(embed=self.error_embed)
            await ctx.author.send(
            f"⏳ You need to wait **{hours}h {minutes}m {seconds}s** before using this again."
             )
            return
        
        self.add_qcoins(user_id,daily_amount)
        self.dailycoins_cooldowns[user_id] = now
        
        embed = discord.Embed(title="Bank💲", description=f"You have been given your daily {daily_amount} {self.coin_emoji}", color=
         discord.Color.green())
        
        await ctx.send(embed=embed)

async def setup(bot):
    cog = QCoins(bot)
    await bot.add_cog(cog)
    bot.qcoins = cog
        
        
        
            
            
        
    