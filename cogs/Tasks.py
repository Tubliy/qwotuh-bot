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
        
        
    async def check_live_message(self,message):
        if message.author.bot:
            return
        
        tubliy_user_id = 400402306836856833
        qwotuh_user_id = 795417945105891352
        
        if message.author.id != qwotuh_user_id or tubliy_user_id:
            return
        
        if "LIVE" not in message.content.upper():
            return
        
        guild = message.guild
        announcement_channel = discord.utils.get(guild.text_channels, name="announcements")
        
        if not announcement_channel:
            print("Announcement channel not found.")
            return
        
        live_message = ("🔴 **Qwotuh** is now live on tiktok. \n"
        "tiktok.com/qwotuh")
        
        file = discord.File("images/qwotuh.gif",filename="qwotuh.gif")
        
        live_embed = discord.Embed(description=live_message, color=discord.Color.green())
        live_embed.set_image(url="attachment://qwotuh.gif")
        
        try:
                await message.delete()
                await announcement_channel.send(live_embed, file=file)
                
        except discord.Forbidden:
                print("Bot lacks permission to send such message.")
        except Exception as e:
                print(f"Error handling live message: {e}")
                
        
    @update_count.before_loop
    async def before_update_count(self):
        await self.bot.wait_until_ready()
        
        
    
async def setup(bot):
        cog = Tasks(bot)
        await bot.add_cog(cog)
        bot.tasks = cog