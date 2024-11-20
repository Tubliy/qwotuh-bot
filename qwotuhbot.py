import discord
import random
import yt_dlp
import asyncio
import requests
from discord.ext import commands, tasks
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor
import time
import logging
import os
import sys
import traceback
import re
import math
import json

logging.basicConfig(level=logging.INFO, filename='/home/tubliy/qwotuh-bot/bot.log')
# Define intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
intents.members = True

# Set up the bot with the defined intents
bot = commands.Bot(command_prefix='!', intents=intents)

ROLE_IDS = {
  "Notifications" : 1300696449687748700
}

# List of banned words
banned_words = ["nigger", "kkk", "faggot", "coon", "chink"]
warnings = {}
ANNOUNCEMENT_CHANNEL_ID = 1262467818171928789
TIKTOK_URL = 'https://www.tiktok.com/@qwotuh'
TWITCH_URL = 'https://www.twitch.com/qwotuh'
was_live_tiktok = False
was_live_twitch = False
executor = ThreadPoolExecutor(max_workers=2)
USERNAME = 'qwotuh'

COUNT_CHANNEL_ID = 1305085207917105172
ROLE_TO_TRACK = "Viewers"
try:
    with open("xp_data.json", "r") as f:
        xp_data = json.load(f)
except FileNotFoundError:
    xp_data = {}

# Prestige ranks
prestige_ranks = {
    1: "Prestige 1",
    2: "Prestige 2",
    3: "Prestige 3",
    4: "Prestige 4",
    5: "Prestige 5",
    6: "Prestige 6",
    7: "Prestige 7",
    8: "Prestige 8",
    9: "Prestige 9",
    10: "Master Prestige"
}
prestige_icons = {
    1: "https://cdn.discordapp.com/attachments/1306125326124060682/1306125654647111730/Prestige_1.png",
    2: "https://cdn.discordapp.com/attachments/1306125326124060682/1306126835125584052/Prestige_2.png",
    3: "https://cdn.discordapp.com/attachments/1306125326124060682/1306128540663812127/Prestige_3.png",
    4: "https://cdn.discordapp.com/attachments/1306125326124060682/1306128564109971466/Prestige_4.png",
    5: "https://cdn.discordapp.com/attachments/1306125326124060682/1306128596280147968/Prestige_5.png",
    6: "https://cdn.discordapp.com/attachments/1306125326124060682/1306130743130591243/Prestige_6.png",
    7: "https://cdn.discordapp.com/attachments/1306125326124060682/1306131015038668850/Prestige_7.png",
    8: "https://cdn.discordapp.com/attachments/1306125326124060682/1306131052435214366/Prestige_8.png",
    9: "https://cdn.discordapp.com/attachments/1306125326124060682/1306131076384555051/Prestige_9.png",
    10: "https://cdn.discordapp.com/attachments/1306125326124060682/1306131105413333013/Master_Prestige.png"
}

# XP bar function to show progress towards the next level
def xp_bar(current_xp, level_up_xp, bar_length=20):
    progress = min(current_xp / level_up_xp, 1)
    filled_length = int(bar_length * progress)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    return f"[{bar}] {int(progress * 100)}%"

# List of user IDs or usernames to exclude from the leaderboard
# Replace these with your actual Discord user IDs
excluded_user_ids = ["400402306836856833", "795417945105891352"]

@bot.command()
async def leaderboard(ctx):
    # Filter out excluded users by checking their IDs
    filtered_users = {
        user_id: data for user_id, data in xp_data.items() if user_id not in excluded_user_ids
    }
    
    # Sort the filtered users by level (and by XP as a secondary sort) in descending order
    sorted_users = sorted(
        filtered_users.items(),
        key=lambda item: (item[1]["level"], item[1]["xp"]),
        reverse=True
    )

    # Create the leaderboard embed
    embed = discord.Embed(title="🏆 Leaderboard 🏆", color=discord.Color.gold())
    embed.set_footer(text="Top players based on level and XP")

    # Limit to top 10 users and format each entry
    for idx, (user_id, data) in enumerate(sorted_users[:10], start=1):
        user = await bot.fetch_user(int(user_id))  # Fetch the user by ID
        level = data["level"]
        xp = data["xp"]
        prestige = data["prestige"]
        embed.add_field(
            name=f"{idx}. {user.display_name}",
            value=f"Level: {level} | XP: {xp} | Prestige: {prestige}",
            inline=False
        )

    # Send the leaderboard
    await ctx.send(embed=embed)


async def level_up_announcement(message, level, prestige):

    guild = message.guild  # The Discord server (guild) where the bot is active

    # Determine the prestige rank and role name
    if prestige == 10 and level == 1:  # Master Prestige at Prestige 10, Level 1
        prestige_rank_name = "Master Prestige"
    elif level == 55 and prestige < 10:  # Reaching level 55 before max prestige
        prestige_rank_name = f"Prestige {prestige + 1}"  # Next prestige rank
    else:
        prestige_rank_name = prestige_ranks.get(prestige, f"Prestige {prestige}")

    # Assign the role if it exists and hasn't already been assigned
    role = discord.utils.get(guild.roles, name=prestige_rank_name)
    if role and role not in message.author.roles:
        await message.author.add_roles(role)
        await message.channel.send(f"{message.author.mention} has been granted the **{prestige_rank_name}** rank!")

    # Build the level-up announcement embed
    embed = discord.Embed(
        title="🎉 Level Up! 🎉",
        description=f"Congratulations {message.author.mention}, you've reached **Level {level}**!",
        color=discord.Color.gold()
    )
    
    if prestige > 0:  # Add prestige information if applicable
        embed.set_footer(text=f"Prestige Rank: {prestige_rank_name}")
    
    embed.set_thumbnail(url=message.author.avatar.url)  # Display the user's avatar
    embed.add_field(
        name="Keep going!", 
        value="Each message brings you closer to the next level.", 
        inline=False
    )
    
    # Send the announcement to the channel
    await message.channel.send(embed=embed)




def add_xp(user_id):
    if user_id not in xp_data:
        xp_data[user_id] = {"xp": 0, "level": 1, "prestige": 0}

    xp_data[user_id]["xp"] += 10  # Adjust XP gain per message

    level_up = False  # Flag to track level-up
    while True:
        # Progressive XP required for each level
        level_up_xp = 100 * (1.5 ** (xp_data[user_id]["level"] - 1))

        # Check for level-up
        if xp_data[user_id]["xp"] >= level_up_xp:
            xp_data[user_id]["xp"] -= level_up_xp  # Carry over excess XP
            xp_data[user_id]["level"] += 1
            level_up = True

            # Check for prestige
            if xp_data[user_id]["level"] > 55:
                xp_data[user_id]["level"] = 1
                if xp_data[user_id]["prestige"] < 10:
                    xp_data[user_id]["prestige"] += 1
        else:
            break

    # Save updated XP data
    with open("xp_data.json", "w") as f:
        json.dump(xp_data, f)

    return level_up  # Indicates whether a level-up occurred


@bot.command()
async def rank(ctx, member: discord.Member = None):
    target = member or ctx.author
    user_id = str(target.id)
    
    if user_id in xp_data:
        current_xp = xp_data[user_id]["xp"]
        level = xp_data[user_id]["level"]
        prestige = xp_data[user_id]["prestige"]
        level_up_xp = 100 * (1.5 ** (level - 1))  # Adjusted XP for the next level
        
        # Determine prestige display and icon
        if prestige == 0:
            prestige_display = "Prestige 0"  # Text for non-prestiged users
            icon_url = None  # No icon
        else:
            prestige_display = prestige_ranks.get(prestige, f"Prestige {prestige}")  # Defaults to "Prestige X" if missing
            icon_url = prestige_icons.get(prestige, prestige_icons.get(10))  # Uses Master Prestige icon as final fallback

        # Create XP bar
        bar = xp_bar(current_xp, level_up_xp)
        
        # Embed rank information with badge icon if available
        embed = discord.Embed(
            title=f"{target.display_name}'s Rank",
            color=discord.Color.blue()
        )
        if icon_url:  # Only set thumbnail if prestige is 1 or higher
            embed.set_thumbnail(url=icon_url)
        embed.add_field(name="Level", value=f"{level}", inline=True)
        embed.add_field(name="Prestige", value=prestige_display, inline=True)
        embed.add_field(name="XP", value=f"{current_xp}/{int(level_up_xp)}", inline=True)
        embed.add_field(name="Progress", value=bar, inline=False)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"{target.display_name} has no levels yet. Start chatting to gain XP!")
      
@bot.command()
@commands.has_permissions(administrator=True)  # Restrict this command to administrators
async def setlevel(ctx, member: discord.Member, level: int):
    user_id = str(member.id)
    
    # Calculate prestige and level within that prestige
    max_level = 55
    prestige = min(level // max_level, 10)  # Cap prestige at 10 for Master Prestige
    adjusted_level = level % max_level if prestige < 10 else max_level  # Keep level within 1-55 for non-master prestige
    
    # Ensure xp_data is initialized for the user
    if user_id not in xp_data:
        xp_data[user_id] = {"xp": 0, "level": 1, "prestige": 0}
    
    # Set the level and prestige
    xp_data[user_id]["level"] = adjusted_level
    xp_data[user_id]["prestige"] = prestige

    # Save updated data with error handling
    try:
        with open("xp_data.json", "w") as f:
            json.dump(xp_data, f)
    except Exception as e:
        await ctx.send(f"Failed to save data: {e}")
        return
    
    # Determine the appropriate prestige role
    if prestige == 10 and adjusted_level == max_level:  # Only assign Master Prestige at Level 55, Prestige 10
        prestige_name = "Master Prestige"
    elif prestige > 0:
        prestige_name = prestige_ranks.get(prestige, f"Prestige {prestige}")
    else:
       prestige_name = None
    
    role = discord.utils.get(ctx.guild.roles, name=prestige_name)
    if role:
        # Remove existing prestige roles explicitly
        for prestige_role_name in prestige_ranks.values():
            existing_role = discord.utils.get(ctx.guild.roles, name=prestige_role_name)
            if existing_role and existing_role in member.roles:
                await member.remove_roles(existing_role)
        
        # Add the new prestige role
        await member.add_roles(role)
        await ctx.send(f"{member.mention}'s level has been set to {adjusted_level} with prestige rank: {prestige_name}. Role has been updated.")
    elif prestige_name == None:
        await ctx.send(f"{member.mention}'s level has been set to {adjusted_level} with prestige rank: {prestige_name}. Role has been updated.")
    else:
        await ctx.send(f"The role '{prestige_name}' does not exist on this server. Please create it to assign roles properly.")

    # Announce the new level and rank
    await ctx.send(f"{member.mention}'s level is now set to **{adjusted_level}** and prestige to **{prestige}**.")


@tasks.loop(minutes=5)
async def update_count():
    guild = bot.guilds[0]
    count_channel = bot.get_channel(COUNT_CHANNEL_ID)

    if not count_channel:
        print("Count channel not found. Check the channel ID.")
        return
    role = discord.utils.get(guild.roles, name = ROLE_TO_TRACK)

    if not role:
        print(f"Role '{ROLE_TO_TRACK}' not found in the server.")
        return
    
    member_count = sum(1 for member in guild.members if role in member.roles)

    await count_channel.edit(name = f"Chads: {member_count}")
    print(f"Currently updated Chads: to {member_count}")


@bot.event
async def on_member_join(member):
    # Define the welcome channel
    channel = discord.utils.get(member.guild.text_channels, name="welcome")

    if not channel:
        print("Welcome channel not found!")
        return

    # Custom picture URL
    custom_image_url = "https://cdn.discordapp.com/attachments/1297471194861273150/1308363082728472576/qwotuh.png"

    # Determine the avatar to use (custom or default)
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

    # Create the embed
    embed = discord.Embed(
        title="🎉 Welcome to the Server! 🎉",
        description=f"Hello {member.mention}, we're so glad to have you here! 🌟",
        color=discord.Color.green()
    )
    embed.add_field(name="What to do next?", value="Check out the rules and introduce yourself!", inline=False)
    embed.set_thumbnail(url=avatar_url)  # Use the new member's avatar or default avatar
    embed.set_image(url=custom_image_url)  # Custom image for the embed
    embed.set_footer(text=f"Welcome to {member.guild.name}!")

    # Send the embed in the welcome channel
    try:
        await channel.send(embed=embed)
    except discord.Forbidden:
        print("Bot does not have permission to send messages in the welcome channel.")

    # Assign the default role
    role = discord.utils.get(member.guild.roles, name="Viewers")
    if role:
        try:
            await member.add_roles(role)
            print(f'Assigned {role.name} to {member.name}')
        except discord.Forbidden:
            print("Bot does not have permission to manage roles.")
        except Exception as e:
            print(f"Error assigning role: {e}")
    else:
        print("Role 'Viewers' not found!")

    # Optional: Send a private DM to the new member
    try:
        await member.send(
            f"Welcome to **{member.guild.name}**, {member.mention}! 🎉\n\n"
            "We're thrilled to have you here! Make sure to check out the rules and introduce yourself."
        )
    except discord.Forbidden:
        print(f"Could not send a DM to {member.name}.")

@bot.command()
async def socials(ctx):
   
   
    yt_emoji = "<:qwotuheYoutube:1305101450757672970>"
    tiktok_emoji = "<:qwotuhTiktok:1305101796045230112>"
    twitch_emoji = "<:qwotuhTwitch:1305101582823718944>"
    x_emoji = "<:qwotuhX:1305101681847042068>"
    youtube = "https://youtube.com/@qwotuh"
    twitch = "https://www.twitch.tv/qwotuh"
    tiktok = "https://tiktok.com/@qwotuh"
    x = "https://x.com/qwotuhh"

    
    embed = discord.Embed(
        title="Check Out My Socials!",
        description="Follow me on these platforms:",
        color=0x1DA1F2  # Optional: Set a color for the embed
    )

    # Add fields for each social platform with clickable links
    embed.add_field(name=f"{yt_emoji} YouTube", value=f"[Subscribe on YouTube]({youtube})", inline=False)
    embed.add_field(name=f"{x_emoji} X", value=f"[Follow on X]({x})", inline=False)
    embed.add_field(name=f"{twitch_emoji} Twitch", value=f"[Watch on Twitch]({twitch})", inline=False)
    embed.add_field(name=f" {tiktok_emoji} TikTok", value=f"[Follow on TikTok]({tiktok})", inline=False)

    # Send the embed
    await ctx.send(embed=embed)

@bot.command()
async def eightball(ctx, *, question):
    responses = [
        "Yes.", "No.", "Maybe.", "Ask again later.", 
        "Definitely!", "I don't think so.", 
        "Absolutely not!", "It is certain."
    ]
    await ctx.send(f"🎱  {random.choice(responses)}")

    
@bot.command()
async def roll(ctx, dice: str):
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN (e.g., 2d6).')
        return

    result = ', '.join(str(random.randint(1, limit)) for _ in range(rolls))
    await ctx.send(result)
    

@bot.command()
async def poll(ctx, *, question):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have permission to create a poll. Only admins can use this command.")
        return
    embed = discord.Embed(title="Poll", description=question, color=discord.Color.gold())
    message = await ctx.send(embed=embed)
    await message.add_reaction("👍")
    await message.add_reaction("👎")


def check_tiktok_live(username):
    """Check if the TikTok user is live by looking for the live badge."""
    tiktok_url = f"https://www.tiktok.com/@{username}"
    logging.info(f"Attempting to check live status for {username} at {tiktok_url}")
    print(f"[INFO] Checking live status for {username} at {tiktok_url}")

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Define ChromeDriver path from environment
    chrome_driver_path = os.getenv("chrome_driver_path", "/usr/local/bin/chromedriver")
    
    # Set up the ChromeDriver Service
    service = Service(chrome_driver_path)

    # Create WebDriver instance
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info("WebDriver initialized successfully.")
        print("[INFO] WebDriver initialized successfully.")

        # Open the TikTok URL
        driver.get(tiktok_url)
        logging.info(f"Page loaded for {username}")
        print(f"[INFO] Page loaded for {username}")

        # Wait for the live badge element to load
        try:
            live_badge = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".css-1n3ab5j-SpanLiveBadge"))
            )
            logging.info("Live badge found.")
            print("[INFO] Live badge found.")
            return True  # User is live
        except TimeoutException:
            # If the live badge does not appear
            logging.info(f"{username} is not live on TikTok.")
            print(f"[INFO] {username} is not live on TikTok.")
            return False

    except WebDriverException as e:
        logging.error(f"WebDriver error while checking live status for {username}: {e}")
        print(f"[ERROR] WebDriver error: {e}")
        return False

    except Exception as e:
        logging.error(f"Unexpected error while checking live status for {username}: {e}")
        print(f"[ERROR] Unexpected error: {e}")
        return False

    finally:
        # Quit the driver if it was created
        if 'driver' in locals():
            try:
                driver.quit()
                logging.info("WebDriver session ended.")
                print("[INFO] WebDriver session ended.")
            except Exception as quit_error:
                logging.error(f"Error quitting WebDriver: {quit_error}")
                print(f"[ERROR] Error quitting WebDriver: {quit_error}")



async def async_check_tiktok_live(username):
    """Asynchronous wrapper to check if the TikTok user is live."""
    return await asyncio.to_thread(check_tiktok_live, username)

# Background task to check if the TikTok user is live every 5 minutes
@tasks.loop(minutes=5)
async def live_tiktokcheck():
    """Checks if the TikTok user is live and sends a notification if status changes."""
    global was_live_tiktok
    channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)

    if channel is None:
        logging.error("Channel not found. Check ANNOUNCEMENT_CHANNEL_ID.")
        return

    try:
        # Check live status asynchronously
        is_live = await async_check_tiktok_live(USERNAME)
        logging.info(f"Live status for {USERNAME}: {is_live}")

        # Send notification if the user has just gone live
        if is_live and not was_live_tiktok:
            if "Notifications" in ROLE_IDS:
                try:
                    await channel.send(
                        f"<@&{ROLE_IDS['Notifications']}> \n🚨 **I'm live on TikTok!** 🚨\n"
                        f"Come watch: https://www.tiktok.com/@{USERNAME}"
                    )
                    logging.info("Live notification sent.")
                    print("Live notification sent.")
                except Exception as send_error:
                    logging.error(f"Failed to send live notification: {send_error}")
            else:
                logging.warning("Notification role ID not found.")
            was_live_tiktok = True

        # Update live status if the user has gone offline
        elif not is_live and was_live_tiktok:
            was_live_tiktok = False
            logging.info(f"{USERNAME} is now offline.")
            print(f"{USERNAME} is now offline.")
        else:
            logging.info("No change in live status.")
            print("No change in live status.")

    except Exception as e:
        logging.error(f"Error in live_tiktokcheck task: {e}")
        print(f"Error in live_tiktokcheck task: {e}")

'''
async def check_twitch_live():
    return await asyncio.get_running_loop().run_in_executor(executor, sync_check_twitch_live)

        
logging.basicConfig(filename='twitch_live_check.log', level=logging.INFO)

def sync_check_twitch_live():
    driver = None 
    try:
        # Your Twitch username
        twitch_username = "kaicenat"  # Replace with your actual Twitch username
        twitch_url = f"https://www.twitch.tv/{twitch_username}"

        # Path to your ChromeDriver
        chrome_driver_path = '/usr/local/bin/chromedriver'

        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--no-sandbox")
        #chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--window-size=1920,1080")

        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.delete_all_cookies()
        # Open Twitch profile page
        driver.get(twitch_url)

       # Scroll down the page to load dynamic content
        print("Scrolling to load dynamic content...")
        body = driver.find_element(By.TAG_NAME, 'body')
        for _ in range(3):  # Scroll 3 times, adjust this number as needed
            body.send_keys(Keys.PAGE_DOWN)

        # Wait for the live badge to appear
        try:
            live_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ScThumbnailBrowse-featured__live-badge"))
            )
            print("User is live!")
            return True
        except TimeoutException:
            print("Timeout: Live badge not found. User is not live.")
            logging.error("Timeout: Live badge not found.")
            return False
    except Exception as e:
        print(f"Error occurred while checking Twitch live status: {e}")
        logging.error(f"Error occurred: {e}")
        return False
    finally:
        if driver is not None:
            driver.quit()

      
@tasks.loop(minutes=7)
async def live_twitchcheck():
    global was_live_twitch  # Access the global live status variable
    channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)

    # Check if the channel was found correctly
    if channel is None:
        print("Channel not found. Make sure ANNOUNCEMENT_CHANNEL_ID is correct.")
        return

    # Check if the user is live
    is_live = await check_twitch_live()
    print(f"Live status: {is_live}")  # Print the live status for debugging

    # If the user is live and hasn't been announced yet, post the announcement
    if is_live and not was_live_twitch:
        print(f"Announcing live status in {channel.name}")
        await channel.send(f"<@&{ROLE_IDS['Notifications']}> \n🚨 **I'm live on Twitch!** 🚨\nCome watch: {TWITCH_URL}")
        was_live_twitch = True  # Set the flag to True, so it doesn't post again until live status changes
    elif not is_live and was_live_twitch:
        print("User went offline.")
        was_live_twitch = False
    else:
        print("No change in live status.")
'''
@bot.event
async def on_ready():
    print(f'{bot.user.name} is online!')
    if not update_count.is_running():
        print("Starting upate_count task...")
        update_count.start()
    else:
        print("update_count task is already running.")
    '''
    # Start the live check task if it's not already running
    if not live_twitchcheck.is_running():
        print("Starting live_twitchcheck task...")
        live_twitchcheck.start()
    else:
        print("live_twitchcheck task is already running.")
    '''
    if not live_tiktokcheck.is_running():
        print("Starting live_tiktokcheck task...")
        live_tiktokcheck.start()
    else:
        print("live_tiktokcheck task is already running.")
        

@bot.command()
@commands.is_owner()
async def restart(ctx):
    await ctx.send("Restarting the bot...")
    await bot.close()

    os.execv(sys.executable, ['python'] + sys.argv)

@restart.error
async def restart_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You aren't the owner of the bot, so you can't restart it!")
        
# Command to manually check live status
@bot.command()
async def livetest(ctx):
    # Make sure to pass the username when calling the async wrapper
    is_live = await async_check_tiktok_live(USERNAME)  # Pass the `USERNAME` variable here
    if is_live:
        await ctx.send(f"{USERNAME} is currently live on TikTok!")
    else:
        await ctx.send(f"{USERNAME} is not live on TikTok.")


@bot.command()
async def ppsize(ctx):
    user = ctx.author
    size = random.randint(1, 12)
    if not ctx.message.mentions:
        await ctx.send(f"{user.name}'s pp size is: 8{'=' * size}D or {size} inches! 🍆")
        return
    
    # Get the first mentioned user
    tagged_user = ctx.message.mentions[0]
    

    # Send the response mentioning the tagged user
    await ctx.send(f"{tagged_user.mention}'s pp size is: 8{'=' * size}D or {size} inches! 🍆")



@bot.command()
async def rps(ctx, *, message: str):
    # Check if the input is valid
    try:
        if message.lower() not in ["rock", "paper", "scissors"]:
            raise ValueError("Invalid input")

        # Bot's random choice
        rps = random.choice(["Rock", "Paper", "Scissors"])
        
        # Send the bot's choice
        await ctx.send(f"I chose {rps}!")
        
        # Determine and send the result
        if rps.lower() == message.lower():
            await ctx.send("It's a tie!")
        elif (message.lower() == "rock" and rps == "Scissors") or \
             (message.lower() == "paper" and rps == "Rock") or \
             (message.lower() == "scissors" and rps == "Paper"):
            await ctx.send("You win!")
        else:
            await ctx.send("I win!")
            
    except ValueError:
        await ctx.send("Invalid input: Please use rock, paper, or scissors.")
        
@bot.command()
async def coinflip(ctx):
    flip = random.choice(["Heads","Tails"])
    await ctx.send(flip)
    
song_queue = []

@bot.command()
async def play(ctx, url: str):
    voice_channel = ctx.author.voice.channel
    if not voice_channel:
        await ctx.send("You're not connected to a voice channel!")
        return

    # Check if the bot is already connected to a voice channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client or not voice_client.is_connected():
        voice_client = await voice_channel.connect()

    # Extract audio stream using yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': 'True',
        'quiet': True,
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        song_title = info['title']
        audio_url = info['url']

    # Add song to queue
    song_queue.append((song_title, audio_url))
    await ctx.send(f'```\nAdded to queue: {song_title}```')

    # If nothing is currently playing, start the first song
    if not voice_client.is_playing():
        await play_next_song(ctx, voice_client)

async def play_next_song(ctx, voice_client):
    if song_queue:
        song_title, audio_url = song_queue.pop(0)
        
        def after_playing(error):
            if error:
                print(f"Error occurred: {error}")
            asyncio.run_coroutine_threadsafe(play_next_song(ctx, voice_client), bot.loop)

        # Play the next song in the queue
        voice_client.play(discord.FFmpegPCMAudio(audio_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", 
                                                 options="-vn"), after=after_playing)
        await ctx.send(f'```\nNow playing: {song_title}```')
    else:
        await voice_client.disconnect()

@bot.command()
async def skip(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()  # Stops the current song and triggers after_playing

@bot.command()
async def queue(ctx):
    if song_queue:
        queue_text = '\n'.join(f"{i+1}. {song[0]}" for i, song in enumerate(song_queue))
        await ctx.send(f"**Current Queue:**\n{queue_text}")
    else:
        await ctx.send("The queue is currently empty.")


@bot.command()
async def meme(ctx):
    # Fetch a random meme from the Meme API
    response = requests.get("https://meme-api.com/gimme")
    if response.status_code == 200:
        meme_data = response.json()
        title = meme_data["title"]
        url = meme_data["url"]
        post_link = meme_data["postLink"]
        subreddit = meme_data["subreddit"]

        # Create an embed for the meme
        embed = discord.Embed(title=title, url=post_link, color=discord.Color.random())
        embed.set_image(url=url)
        embed.set_footer(text=f"From r/{subreddit}")

        # Send the meme embed
        await ctx.send(embed=embed)
    else:
        # Handle API errors
        await ctx.send("❌ Couldn't fetch a meme. Try again later!")




@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"User Info: {member}", color=discord.Color.blue())
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Display Name", value=member.display_name, inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)


@bot.command()
async def remindme(ctx, time: int, *, reminder: str):
    await ctx.send(f"⏰ Reminder set for {time} seconds!")
    await asyncio.sleep(time)
    await ctx.send(f"🔔 {ctx.author.mention}, here's your reminder: **{reminder}**")


@bot.command()
async def hug(ctx, member: discord.Member):
    # List of hug GIFs
    hug_gifs = [
    "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
    "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
    "https://media.giphy.com/media/3bqtLDeiDtwhq/giphy.gif",
    "https://media.giphy.com/media/xT39D7ubkIUIrgX5XO/giphy.gif",
    "https://media.giphy.com/media/sUIZWMnfd4Mb6/giphy.gif",
    "https://media.giphy.com/media/2GnS81AihShS8/giphy.gif",
    "https://media.giphy.com/media/wnsgren9NtITS/giphy.gif",
    "https://media.giphy.com/media/BXrwTdoho6hkQ/giphy.gif",
    "https://media.giphy.com/media/49mdjsMrH7oze/giphy.gif",
    "https://media.giphy.com/media/yziFo5qYAOgY8/giphy.gif"
    ]   


    # Pick a random GIF
    selected_gif = random.choice(hug_gifs)

    # Create an embed with the GIF
    embed = discord.Embed(
        title="A warm hug! 🤗",
        description=f"{ctx.author.mention} gives a big hug to {member.mention}!",
        color=discord.Color.purple()
    )
    embed.set_image(url=selected_gif)

    # Send the embed
    await ctx.send(embed=embed)

@bot.command
async def kiss(ctx, member: discord.Member):
    kiss_gifs = [
        "https://tenor.com/view/peach-and-goma-gif-16302490032000255283",
    ]

    selected_gif = random.choice(kiss_gifs)

    embed = discord.Embed(
        title = "A sweet kiss! 💋",
        description= f"{ctx.author.mention} gives a big kiss to {member.mention}!",
        color= discord.Color.pink()
    )
    embed.set_image(url=selected_gif)
    
    await ctx.send(embed=embed)
    
@bot.event
async def on_message(message):
    # Check if the message is sent by a bot to prevent bot loops
    if message.author.bot:
        return

    # Check for any banned words in the message content
    for word in banned_words:
        # Use regular expression to match whole words only
        if re.search(rf'\b{re.escape(word)}\b', message.content, re.IGNORECASE):
            await message.author.ban(reason=f'Used banned word: {word}')
            await message.channel.send(f'```\n{message.author.name} has been banned for an inappropriate word.```')
            return  # Stop further processing if banned

  # Add XP and check for level-up
    user_id = str(message.author.id)
    leveled_up = add_xp(user_id)  # This will set leveled_up to True if they leveled up

    # Announce level-up if applicable
    if leveled_up:
        # Pass the full `message` object to `level_up_announcement`
        await level_up_announcement(message, xp_data[user_id]["level"], xp_data[user_id]["prestige"])
    
    await bot.process_commands(message)
  

bot.remove_command('help')

class HelpView(discord.ui.View):
    def __init__(self, bot, ctx, pages):
        super().__init__(timeout=60)
        self.bot = bot
        self.ctx = ctx
        self.pages = pages
        self.current_page = 0
        self.message = None

    async def update_embed(self):
        """Update the embed message and button states."""
        embed = self.pages[self.current_page]
        # Update button states
        self.children[0].disabled = self.current_page == 0  # Disable Previous on the first page
        self.children[1].disabled = self.current_page == len(self.pages) - 1  # Disable Next on the last page
        await self.message.edit(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the previous page."""
        self.current_page -= 1
        await self.update_embed()
        await interaction.response.defer()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the next page."""
        self.current_page += 1
        await self.update_embed()
        await interaction.response.defer()

    async def start(self):
        """Send the initial help message."""
        embed = self.pages[self.current_page]
        self.message = await self.ctx.send(embed=embed, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensure only the command user can interact with the buttons."""
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("This help menu isn't for you!", ephemeral=True)
            return False
        return True

@bot.command()
async def help(ctx):
    """Help command with categories."""
    pages = [
        # Page 1: General Commands
        discord.Embed(title="Help - General Commands", color=discord.Color.blue())
        .add_field(name="!livetest", value="Checks if you're live on TikTok.", inline=False)
        .add_field(name="!socials", value="Displays social media links.", inline=False)
        .add_field(name="!rank", value="Allows you to check your rank.", inline=False)
        .add_field(name="!leaderboard", value="Check the ranking leaderboard.", inline=False),

        # Page 2: Fun Commands
        discord.Embed(title="Help - Fun Commands", color=discord.Color.green())
        .add_field(name="!ppsize", value="Displays your pp size.", inline=False)
        .add_field(name="!hug", value="Give someone a hug.", inline=False)
        .add_field(name="!meme", value="Display a random meme.", inline=False)
        .add_field(name="!eightball", value="Test the magic 8ball.", inline=False),

        # Page 3: Game Commands
        discord.Embed(title="Help - Game Commands", color=discord.Color.purple())
        .add_field(name="!roll", value="Rolls a dice (#d#) Example: 2d6.", inline=False)
        .add_field(name="!rps", value="Allows you to play rock paper scissors.", inline=False)
        .add_field(name="!coinflip", value="Allows you to flip a coin.", inline=False),

        # Page 4: Music Commands
        discord.Embed(title="Help - Music Commands", color=discord.Color.orange())
        .add_field(name="!play <url>", value="Plays music from a given URL.", inline=False),
    ]

    # Start the paginated help menu
    view = HelpView(bot, ctx, pages)
    await view.start()


    
# Run the bot with your token
bot.run('MTI5NzA2MDU0OTIwNDUxMjgzOQ.GfV15z._yiVFaa2DF83VRld8V6EXdQuwHN72DComXJKuo')
