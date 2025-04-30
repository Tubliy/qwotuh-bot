import discord
from discord.ext import commands
import time
import asyncio

class Moderation(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.bad_words = self.load_bad_words()
        self.bad_words_warnings = {}
        self.spam_warnings = {}
        self.messagelog = {}
        
        
        self.time_window = 5
        self.max_messages = 5
        self.last_spam_trigger = {}
        
        self.log_channel = 1365098636064591944
        
        
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
        
    async def spam_check(self, message, user_id):
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
        
        user_id = message.author.id
        bad_word_used = next((word for word in self.bad_words if word in message.content.lower()), None)

        await self.spam_check(message, user_id)
        
        if bad_word_used:
            await message.delete()
            
            
            self.bad_words_warnings[user_id] = self.bad_words_warnings.get(user_id, 0) + 1
            
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