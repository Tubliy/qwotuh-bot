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
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor
import time
import logging
import os
import sys


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

COUNT_CHANNEL_ID = 1305085207917105172
ROLE_TO_TRACK = "Viewers"

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
    # Define the role by its name
    role = discord.utils.get(member.guild.roles, name="Viewers")

    # Add the role to the new member
    if role:
        await member.add_roles(role)
        print(f'Assigned {role.name} to {member.name}')
    else:
        print("Role not found!")

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


async def check_tiktok_live():
    return await asyncio.get_running_loop().run_in_executor(executor, sync_check_tiktok_live)

    
    
def sync_check_tiktok_live():
    try:
        # Your TikTok username
        tiktok_username = "qwotuh"  # Replace with your actual TikTok username
        tiktok_url = f"https://www.tiktok.com/@{tiktok_username}"

        # Path to your ChromeDriver (use the full path to chromedriver.exe)
        chrome_driver_path = '/usr/local/bin/chromedriver'

        # Set up Chrome options (running without headless mode for testing)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Commented out to run in non-headless mode for debugging
        #chrome_options.add_argument("--no-sandbox")
        #chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    
        
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.delete_all_cookies()
        # Open TikTok profile page
        driver.get(tiktok_url)

        # Scroll down the page to load dynamic content
        print("Scrolling to load dynamic content...")
        body = driver.find_element(By.TAG_NAME, 'body')
        for _ in range(3):  # Scroll 3 times, adjust this number as needed
            body.send_keys(Keys.PAGE_DOWN)
            

        # Wait for the live badge to appear (using CSS selector)
        try:
            live_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".css-1n3ab5j-SpanLiveBadge.e1vl87hj3"))
            )
            print("User is live!")
            return True
        except TimeoutException:
            print("Timeout: Live badge not found. User is not live.")
        finally:
            driver.quit()  # Ensure the driver always quits

        return False

    except Exception as e:
        print(f"Error occurred while checking TikTok live status: {e}")
        return False

# Background task to check if you're live on TikTok every 5 minutes

@tasks.loop(minutes=5)
async def live_tiktokcheck():
    global was_live_tiktok  # Access the global live status variable
    channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)

    # Check if the channel was found correctly
    if channel is None:
        print("Channel not found. Make sure ANNOUNCEMENT_CHANNEL_ID is correct.")
        return

    # Check if the user is live
    is_live = await check_tiktok_live()
    print(f"Live status: {is_live}")  # Print the live status for debugging

    # If the user is live and hasn't been announced yet, post the announcement
    if is_live and not was_live_tiktok:
        print(f"Announcing live status in {channel.name}")
        await channel.send(f"<@&{ROLE_IDS['Notifications']}> \n🚨 **I'm live on TikTok!** 🚨\nCome watch: {TIKTOK_URL}")
        was_live_tiktok = True  # Set the flag to True, so it doesn't post again until live status changes
    elif not is_live and was_live_tiktok:
        print("User went offline.")
        was_live_tiktok = False
    else:
        print("No change in live status.")
        
        
async def check_twitch_live():
    return await asyncio.get_running_loop().run_in_executor(executor, sync_check_twitch_live)

        
def sync_check_twitch_live():
    try:
       
        twitch_username = "qwotuh"  
        twitch_url = f"https://www.twitch.tv/{twitch_username}"

        # Path to your ChromeDriver (use the full path to chromedriver.exe)
        chrome_driver_path = '/usr/local/bin/chromedriver'

        # Set up Chrome options (running without headless mode for testing)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Commented out to run in non-headless mode for debugging
        #chrome_options.add_argument("--no-sandbox")
        #chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    
        
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.delete_all_cookies()
    
        driver.get(twitch_url)

        # Scroll down the page to load dynamic content
        print("Scrolling to load dynamic content...")
        body = driver.find_element(By.TAG_NAME, 'body')
        for _ in range(3):  # Scroll 3 times, adjust this number as needed
            body.send_keys(Keys.PAGE_DOWN)
        

        # Wait for the live badge to appear (using CSS selector)
        try:
            live_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'LIVE')]"))
            )
            print("User is live!")
            return True
        except TimeoutException:
            print("Timeout: Live badge not found. User is not live.")
        finally:
            driver.quit()  # Ensure the driver always quits

        return False

    except Exception as e:
        print(f"Error occurred while checking TikTok live status: {e}")
        return False

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

@bot.event
async def on_ready():
    print(f'{bot.user.name} is online!')
    if not update_count.is_running():
        print("Starting upate_count task...")
        update_count.start()
    else:
        print("update_count task is already running.")

    # Start the live check task if it's not already running
    if not live_twitchcheck.is_running():
        print("Starting live_twitchcheck task...")
        live_twitchcheck.start()
    else:
        print("live_twitchcheck task is already running.")

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
    is_live = await check_tiktok_live()
    is_live2 = await check_twitch_live()

    # Check if both are live first
    if is_live and is_live2:
        await ctx.send(f"🚨 **I'm currently live on both** 🚨\nCome watch:\nTikTok: {TIKTOK_URL}\nTwitch: {TWITCH_URL}")
    elif is_live:
        await ctx.send(f"🚨 **I'm live on TikTok!** 🚨\nCome watch: {TIKTOK_URL}")
    elif is_live2:
        await ctx.send(f"🚨 **I'm live on Twitch!** 🚨\nCome watch: {TWITCH_URL}")
    else:
        await ctx.send("I'm not live on TikTok or Twitch right now.")
   

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




    
@bot.event
async def on_message(message):
    # Check if the message is sent by a bot to prevent bot loops
    if message.author.bot:
        return

    # Check for any banned words in the message content
    for word in banned_words:
        if word.lower() in message.content.lower():
            await message.author.ban(reason=f'Used banned word: {word}')
            await message.channel.send(f'```\n{message.author.name} has been banned for an inappropriate word.```')
            return  # Return here to stop further processing for this message if banned

    # Make sure to process other bot commands
    await bot.process_commands(message)

bot.remove_command('help')

# Command to display custom help information
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Help", description="Here are the available commands:", color=discord.Color.blue())
    
    # Add fields for each command
    embed.add_field(name="!livetest", value="Checks if you're live on TikTok.", inline=False)
    embed.add_field(name="!play <url>", value="Plays music from a given URL.", inline=False)
    embed.add_field(name="!socials", value="Displays social media links.", inline=False)
    embed.add_field(name="!ppsize", value="Displays your pp size", inline=False)
    embed.add_field(name="!roll", value="Rolls a dice (#d#) Example: 2d6", inline=False)
    embed.add_field(name="!rps", value="Allows you to play rock paper scissors.", inline=False)
    embed.add_field(name="!coinflip", value="Allows you to flip a coin.", inline=False)

    # Add more commands as needed
    
    # Send the embed with help information
    await ctx.send(embed=embed)


# Run the bot with your token
bot.run('MTI5NzA2MDU0OTIwNDUxMjgzOQ.GfV15z._yiVFaa2DF83VRld8V6EXdQuwHN72DComXJKuo')
