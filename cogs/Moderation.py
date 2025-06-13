import discord
from discord.ext import commands
import time
import asyncio
import re
import json
import os

class Moderation(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.bad_words = self.load_bad_words()
        self.fileName_badword = "badwordwarnings.json"
        self.fileName_spam = "spamwarnings.json"
        self.bad_words_warnings = self.load_badwordwarnings()
        self.spam_warnings = self.load_spamwarnings()
        self.messagelog = {}
        
        
        self.time_window = 5
        self.max_messages = 5
        self.last_spam_trigger = {}
        
        self.log_channel = 1365098636064591944
        
    def save_spamwarnings(self):
        with open(self.fileName_spam,"w") as f:
            json.dump({str(k): v for k,v in self.spam_warnings.items()}, f)
    
    def load_spamwarnings(self):
        if os.path.exists(self.fileName_spam):
            with open(self.fileName_spam, "r") as f:
                return json.load(f)
        return {}
        
    def save_badwordwarnings(self):
        with open(self.fileName_badword, "w") as f:
            json.dump({str(k): v for k,v in self.bad_words_warnings.items()}, f)
    
    def load_badwordwarnings(self):
        if os.path.exists(self.fileName_badword):
            with open(self.fileName_badword, "r") as f:
                return json.load(f)
        return {}
    
    
    @commands.command(name="warnings")
    async def warnings(self, ctx, member : discord.Member = None):
        member = member or ctx.author
        user_id = str(member.id)
        
        mod = discord.utils.get(member.roles, name="Moderator") is not None
        
        bad_word_warnings = self.bad_words_warnings.get(user_id, 0)
        spam_warnings = self.spam_warnings.get(user_id,0)
        
        if mod:
         embed = discord.Embed(title=f"Warnings for {member.display_name}",
                color=discord.Color.orange()
         )
         embed.add_field(name="Bad Word Warnings", value=str(bad_word_warnings), inline=False)
         embed.add_field(name="Spam Warnings" , value=str(spam_warnings), inline=False)
        
         await ctx.send(embed=embed)
        else:
           await ctx.send("You don't have permission for this command!")
        
    @commands.command(name="setwarnings")
    @commands.has_permissions(administrator=True)
    async def setwarnings(self, ctx, member : discord.Member = None, type: str = None, amount: int = 0):
        member = member or ctx.author
        user_id = str(member.id)
        author = ctx.author.display_name
        
        if amount < 0:
            await ctx.send("⚠ The number has to be a positive number.")
        
        if amount > 3:
            await ctx.send("⚠ The number can't be greater than 3.")
        if type not in ["spam", "badwords"]:
            return await ctx.send("⚠ Type must be either `spam` or `badwords`.")
            
        embed = discord.Embed(title=f"Set warnings for {member.display_name}."
        , color=discord.Color.blue())
        embed.set_footer(text="Admin Command.")
        
        log_channel = self.bot.get_channel(self.log_channel)
        
    
        try:
          if type == "spam":
              self.spam_warnings[user_id] = amount
              self.save_spamwarnings()
              embed.add_field(name="Spam Warning:", value=amount)
              await log_channel.send(f"{member.display_name}, spam warnings has been set to {amount} by `{author}`")
          elif type == "badwords":
              self.bad_words_warnings[user_id] = amount
              self.save_badwordwarnings()
              embed.add_field(name="Bad Word warning:", value=amount)
              await log_channel.send(f"{member.display_name}, bad word warnings has been set to {amount} by `{author}`")
        except Exception:
           await ctx.send("Invalid type.")
            
        await ctx.send(embed=embed)
    
        
    
        
    @commands.command(name="clear")
    @commands.has_permissions(administrator=True)
    
    async def clear(self, ctx, amount: int):
        
        if amount <= 0:
            await ctx.send("Please specify a positive number to clear.")
            return
        
        deleted = await ctx.channel.purge(limit=amount+1)
        
        await ctx.send(f"{ctx.author.mention}, Deleted {len(deleted) - 1} messages!", delete_after = 10)
    
    @clear.error
    async def clear_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You are missing the permissions to use this command!")
            
            
    def load_bad_words(self):
        try:
            with open("badwords.txt", "r") as f:
                return [line.strip().lower() for line in f if line.strip()]
        except FileNotFoundError:
            print("badwords.txt file not found!")
            return []
        
    async def spam_check(self, message):
        
        user_id = str(message.author.id)
        now = time.time()
        cooldown = 15  # seconds of cooldown after a warning

        # ⏱ Cooldown check
        last_trigger = self.last_spam_trigger.get(user_id)
        if last_trigger and now - last_trigger < cooldown:
            return  # Still in cooldown, skip

        # 🧠 Filter and store recent message timestamps
        timestamps = self.messagelog.get(user_id, [])
        timestamps = [t for t in timestamps if now - t < self.time_window]
        timestamps.append(now)
        self.messagelog[user_id] = timestamps

        messages_sent = len(timestamps)

        if messages_sent > self.max_messages:
            # ⚠️ Increment warning count
            self.spam_warnings[user_id] = self.spam_warnings.get(user_id, 0) + 1
            warning_count = self.spam_warnings[user_id]
            
            self.save_spamwarnings()

            log_channel = self.bot.get_channel(self.log_channel)

            await message.channel.send(f"{message.author.mention}, please stop spamming!")

            if log_channel:
                await log_channel.send(
                    f"{message.author.mention} has sent {messages_sent} messages (limit: {self.max_messages}). "
                    f"Spam violation.\nWarning count: {warning_count}"
                )

            try:
                await message.delete()
            except discord.Forbidden:
                pass

            self.messagelog[user_id] = []  # Reset counter
            
            self.last_spam_trigger[user_id] = now  # Start cooldown

            # ⛔ Mute after 3 warnings
            if warning_count == 3:
                reason = "Reached the three warning limit. (Spam Violation)"
                if log_channel:
                    await log_channel.send(f"{message.author.mention} has been muted for: {reason}")
                await self.mute(member=message.author, reason=reason, duration=600)  # 10 minutes
                self.spam_warnings[user_id] = 0  # Reset warnings after mute
                
                self.save_spamwarnings()
    
    async def mute(self, member : discord.Member, reason = "Spamming", duration: int = 600):
        guild = member.guild
        muted_role = discord.utils.get(guild.roles, name="Muted")
        
        if not muted_role:
            try:
                muted_role = await guild.create_role(name="Muted", reason="To mute users.")
                for channel in guild.channels:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False)
            except discord.Forbidden:
                print("Cannot create the muted role.")
                return
        
        try:
            await member.add_roles(muted_role, reason=reason)
            await member.send(f"You've been muted in {guild.name} for reason: {reason} \n"
            f"Ends in {duration // 60} minutes")
        except discord.Forbidden:
            print(f"Wasn't able to add Muted Role to {member}")
            return
        
        await asyncio.sleep(duration)
        
        try:
            await member.remove_roles(muted_role, reason="Mute expired")
            await member.send(f"You've been unmuted in {guild.name}.")
        except discord.Forbidden:
            print(f"Wasn't able to remove muted role from {member}")
            
    async def check_message(self, message):
            
        if message.author.bot:
            return
        
        user_id = str(message.author.id)
        message_content = message.content.lower()
        bad_word_used = next((word for word in self.bad_words if re.search(rf"\b{re.escape(word)}\b", message_content)), None
                             
        )

        await self.spam_check(message)
        
        if bad_word_used:
            await message.delete()
            
            
            self.bad_words_warnings[user_id] = self.bad_words_warnings.get(user_id, 0) + 1
            self.save_badwordwarnings()
            
            warning_count = self.bad_words_warnings[user_id]
            log_channel = self.bot.get_channel(self.log_channel)
            
            
            await message.channel.send(f"{message.author.mention}, watch what you say! \n Warning count: {warning_count}")
            
            if log_channel and warning_count <=2:
             
                await log_channel.send(f"{message.author.mention}, has said '{bad_word_used}' in {message.channel.mention} \n Warning count: {warning_count}")
                
            elif warning_count == 3:
                reason = f"Reached the three warning limit. And said {bad_word_used}"
                await message.author.ban(reason=reason)
                await log_channel.send(f"{message.author.mention} was banned for: {reason}")
                
async def setup(bot):
    cog = Moderation(bot)
    await bot.add_cog(cog)
    bot.moderation = cog