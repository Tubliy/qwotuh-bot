import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import os
import asyncio


class Main(commands.Bot):
    def __init__(self):
     intents = discord.Intents.default()
     intents.members = True
     intents.message_content = True
     super().__init__(command_prefix="!", intents=intents, help_command=None)
     self.add_command(self.help)
     
     self.owner = 400402306836856833
     self.moderation = None
     self.tasks = None
     self.qcoins = None
     
    
     
    async def setup_hook(self):
        owner_user = await self.fetch_user(self.owner)
        await owner_user.send("Cogs loaded:")
        for filename in os.listdir("./cogs"):
             if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")  
                await owner_user.send(f"\n{filename}")  
   
    async def on_message(self, message):
        if message.author == self.user:
          return
      
        if self.moderation:
            await self.moderation.check_message(message)
            
        if self.tasks:
            await self.tasks.check_live_message(message)
            
        if self.qcoins:
            await self.qcoins.collect_coins(message)
                
        await self.process_commands(message)
        
    
    async def on_member_join(self, member):
        if member.bot:
         return
    
        channel = discord.utils.get(member.guild.text_channels, name = "welcome")
        
        if not channel:
            print("Welcome channel not found!")
            return
        
        custom_image_url = "https://cdn.discordapp.com/attachments/1297471194861273150/1308363082728472576/qwotuh.png"
        
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        
        embed = discord.Embed(
            title="🎉 Welcome to the Server! 🎉",
            description=f"Hello {member.mention}, we're so glad you made it!",
            color=discord.Color.green()
        )
        embed.add_field(name="What to do next?", value="Check out the rules and introduce yourself", inline=False)
        embed.set_thumbnail(url=avatar_url)
        embed.set_image(url=custom_image_url)
        embed.set_footer(text=f"Welcome to {member.guild.name}!")
        
        
        try:
            await asyncio.sleep(5)
            await channel.send(embed=embed)
        except discord.Forbidden:
            print("Bot doesn't have permissions to welcome channel.")
            
        role = discord.utils.get(member.guild.roles, name = "Viewers")
        
        if role:
            try:
                await member.add_roles(role)
                owner_user = await self.fetch_user(self.owner)
                await owner_user.send(f"{member.mention}, has joined {member.guild.name}.")
            except discord.Forbidden:
                print("Bot doesn't have permission to manage roles.")
            except Exception as e:
                print(f"Error assigning roles {e}.")
        else:
            print("Role Viewers not found.")
               
        try:
           await member.send(
            f"Welcome to **{member.guild.name}**, {member.mention}! 🎉\n\n"
            "We're thrilled to have you here! Make sure to check out the rules and introduce yourself."
        )
        except discord.Forbidden:
            print(f"Could not send a DM to {member.name}.")
                
        
    async def on_ready(self):
        
        owner_user = await self.fetch_user(self.owner)
        if owner_user:
            try:
                await owner_user.send("Qwotuhbot is now online.")
            except discord.Forbidden:
                print("Couldn't dm the owner.")
    
    
    @commands.command(name="help")   
    async def help(self, ctx, type : str):
        
        user = ctx.author
        
        has_mod_role = discord.utils.get(user.roles, name="Moderator") is not None
        
        try:
            match type.lower():
            
             case "fun":
                funembed = discord.Embed(title="Fun Commands",
                                         color=discord.Color.blue())
                funembed.add_field(name="ppsize", value="Usage: !ppsize @user")
                funembed.add_field(name="rps", value="!rps (rock|paper|scissor)")
                funembed.add_field(name="coinflip", value="!coinflip")
                funembed.add_field(name="meme", value="!meme")
                funembed.set_footer(text="Fun Command Section")
                
                await ctx.send(embed=funembed)
                
             case "mod":
                if has_mod_role:
                    modembed = discord.Embed(title="Mod Commands", color=discord.Color.red())
                    
                    modembed.add_field(name="clear", value="!clear <amount>")
                    modembed.add_field(name="warnings", value="!warnings @user")
                    modembed.set_footer(text="Mod Command Section")
                    
                    await ctx.send(embed=modembed)
                else:
                    await ctx.send("You don't have permission to view these commands.")
                    
             case "qcoins":
                 qcoinsembed = discord.Embed("Qcoins Commands", color=discord.Color.gold())
                 
                 qcoinsembed.add_field(name="coins", value="!coins @user")
                 qcoinsembed.add_field(name="qgive", value="!qgive @user <amount>")
                 qcoinsembed.add_field(name="gamble", value="!gamble <amount>")
                 qcoinsembed.add_field(name="daily", value="!daily")
                 qcoinsembed.add_field(name="leaderboard", value="!leaderboard")
                 qcoinsembed.add_field(name="shop", value="!shop")
                 qcoinsembed.add_field(name="buy", value="!buy <int>")
                 
                 await ctx.send(embed=qcoinsembed)
             case _:
                await ctx.send("Options are fun, mod, and qcoins.")
        except Exception as e:
            await ctx.send(f"Error occured: {e}")
        
if __name__ == "__main__":
    bot = Main()
    bot.run('MTI5NzA2MDU0OTIwNDUxMjgzOQ.GfV15z._yiVFaa2DF83VRld8V6EXdQuwHN72DComXJKuo')
        
        
     

        