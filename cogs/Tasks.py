import discord
from discord.ext import commands, tasks

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.update_channel = 1305085207917105172
        self.update_count.start()
        
    
    @tasks.loop(minutes=5)
    async def update_count(self):
        role_to_track = "Viewers"
        count_channel = self.bot.get_channel(self.update_channel)
        
        if not count_channel:
            print("Count channel not found!")
            return

        guild = count_channel.guild
        role = discord.utils.get(guild.roles, name= role_to_track)
        
        if not role:
            print(f"{role_to_track} was not found.")
            return
        
        member_count = sum(1 for member in guild.members if role in member.roles)
        
        await count_channel.edit(name=f"Chads: {member_count}")
        print(f"Updated count to {member_count}.")
        
        
    @update_count.before_loop
    async def before_update_count(self):
        await self.bot.wait_until_ready()
        
    
async def setup(bot):
        cog = Tasks(bot)
        await bot.add_cog(cog)