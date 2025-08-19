import os
import logging
import instaloader
import discord
from discord.ext import commands
import random
import shutil
from dotenv import load_dotenv  # <-- added

# Load .env file (only needed locally)
load_dotenv()

# Load token from environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

# If no token found, stop
if not TOKEN:
    raise ValueError("❌ No Discord token found. Please set DISCORD_TOKEN in .env (local) or dash.daki environment variables.")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize Instaloader
L = instaloader.Instaloader()

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# GIF URLs for different states
START_GIFS = [
    "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif",
    "https://media.giphy.com/media/26tn33aiTi1jkl6H6/giphy.gif"
]

PROCESSING_GIFS = [
    "https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif",
    "https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif",
    "https://media.giphy.com/media/xTkcEQACH24SMPxIQg/giphy.gif"
]

# Bot ready event
@bot.event
async def on_ready():
    print(f'Bot is running as {bot.user}')
    print("=" * 50)
    print("Developer: Syed Rehan • @9yrs")
    print("Instagram Downloader Bot v2.0")
    print("=" * 50)

# Start command
@bot.command(name='start')
async def start(ctx):
    embed = discord.Embed(
        title="🚀 Instagram Downloader Bot",
        description="Send me an Instagram link (Reel, Story, or Post), and I'll download it for you!",
        color=0xE4405F
    )
    embed.add_field(
        name="📱 Supported Content",
        value="• Instagram Reels\n• Instagram Posts\n• Instagram Stories",
        inline=True
    )
    embed.add_field(
        name="💡 How to Use",
        value="Just paste any Instagram URL in the chat!",
        inline=True
    )
    embed.set_footer(
        text="Developer: Syed Rehan • @9yrs",
        icon_url="https://cdn.discordapp.com/emojis/741243683378602085.png"
    )
    embed.set_image(url=random.choice(START_GIFS))
    await ctx.send(embed=embed)

# Developer info command
@bot.command(name='dev', aliases=['developer', 'about'])
async def developer_info(ctx):
    embed = discord.Embed(
        title="👨‍💻 Developer Information",
        color=0x00ff00
    )
    embed.add_field(name="Developer", value="**Syed Rehan**", inline=True)
    embed.add_field(name="Experience", value="**9+ Years**", inline=True)
    embed.add_field(name="Contact", value="@9yrs", inline=True)
    embed.add_field(
        name="🔧 Technologies Used",
        value="• Python\n• Discord.py\n• Instaloader\n• Instagram API",
        inline=False
    )
    embed.set_thumbnail(url="https://media.giphy.com/media/L1R1tvI9svkIWwpVYr/giphy.gif")
    embed.set_footer(text="Thanks for using my bot! ❤️")
    await ctx.send(embed=embed)

# Function to download Instagram content
def download_instagram_content(instagram_url: str) -> str:
    try:
        if 'reel' in instagram_url:
            shortcode = instagram_url.split('/')[-2]
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(post, target=shortcode)
        elif 'stories' in instagram_url or '/p/' in instagram_url:
            username = instagram_url.split('/')[3]
            profile = instaloader.Profile.from_username(L.context, username)
            if 'stories' in instagram_url:
                for story in profile.get_stories():
                    L.download_story(story, target=username)
            else:
                shortcode = instagram_url.split('/')[-1]
                post = instaloader.Post.from_shortcode(L.context, shortcode)
                L.download_post(post, target=shortcode)
        else:
            return None

        folder = shortcode if 'reel' in instagram_url else username
        video_file = next((f for f in os.listdir(folder) if f.endswith('.mp4')), None)
        image_file = next((f for f in os.listdir(folder) if f.endswith(('.jpg', '.png'))), None)
        if video_file:
            return os.path.join(folder, video_file)
        elif image_file:
            return os.path.join(folder, image_file)
    except Exception as e:
        logging.error(f"Failed to download: {e}")
    return None

# Handle Instagram links in chat
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

    if "instagram.com" in message.content:
        processing_embed = discord.Embed(
            title="⏳ Processing your Instagram link...",
            description="Please wait while I download your content!",
            color=0xffaa00
        )
        processing_embed.set_image(url=random.choice(PROCESSING_GIFS))
        processing_embed.set_footer(text="Developer: Syed Rehan • @9yrs")
        
        processing_msg = await message.channel.send(embed=processing_embed)
        file_path = download_instagram_content(message.content)
        await processing_msg.delete()
        
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    success_embed = discord.Embed(
                        title="✅ Download Successful!",
                        description="Here's your Instagram content:",
                        color=0x00ff00
                    )
                    success_embed.set_footer(text="Developer: Syed Rehan • @9yrs")
                    
                    if file_path.endswith('.mp4'):
                        await message.channel.send(embed=success_embed, file=discord.File(file, filename='content.mp4'))
                    else:
                        await message.channel.send(embed=success_embed, file=discord.File(file, filename='content.jpg'))
                
                shutil.rmtree(os.path.dirname(file_path))
            except Exception as e:
                error_embed = discord.Embed(
                    title="❌ Error Occurred",
                    description=f"An error occurred: {e}",
                    color=0xff0000
                )
                error_embed.set_footer(text="Developer: Syed Rehan • @9yrs")
                await message.channel.send(embed=error_embed)
        else:
            error_embed = discord.Embed(
                title="❌ Download Failed",
                description="Couldn't download. Link might be invalid, private, or unsupported.",
                color=0xff0000
            )
            error_embed.set_footer(text="Developer: Syed Rehan • @9yrs")
            await message.channel.send(embed=error_embed)

# Run the bot
def main():
    print("=" * 50)
    print("Instagram Downloader Bot v2.0")
    print("Developer: Syed Rehan • @9yrs")
    print("Starting bot...")
    print("=" * 50)
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
