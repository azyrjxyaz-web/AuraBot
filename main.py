import os
import asyncio
import random
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import yt_dlp
import static_ffmpeg

# Automatic FFmpeg Setup
static_ffmpeg.add_paths()

# Flask Server for Render 24/7 Uptime Keep-Alive
app = Flask('')

@app.route('/')
def home():
    return "AuraBot Ultimate Edition is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# Discord Bot Setup with All Intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# FFmpeg & YTDL Audio Configurations
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'scsearch',
    'extract_flat': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'no_warnings': True,
    'source_address': '0.0.0.0'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

# In-Memory Storage for Economy System
user_balances = {}

@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user.name} ({bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="!help | Ultimate Music & Utility"))

# ----------------- MUSIC COMMANDS -----------------

@bot.command(name="join")
async def join_vc(ctx):
    """Joins the user's voice channel."""
    if not ctx.author.voice:
        return await ctx.send("❌ Pehle kisi Voice Channel me join karein!")
    channel = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect(reconnect=True, timeout=30.0)
    await ctx.send(f"🔊 Joined **{channel.name}**!")

@bot.command(name="play")
async def play_music(ctx, *, search: str):
    """Plays audio from SoundCloud/Search URL."""
    if not ctx.author.voice:
        return await ctx.send("❌ Pehle kisi Voice Channel me join karein!")

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect(reconnect=True, timeout=30.0)
    elif ctx.voice_client.channel != ctx.author.voice.channel:
        await ctx.voice_client.move_to(ctx.author.voice.channel)

    async with ctx.typing():
        try:
            query = search if (search.startswith("http://") or search.startswith("https://")) else f"scsearch:{search}"
            info = ytdl.extract_info(query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                info = info['entries'][0]

            url = info['url']
            title = info.get('title', 'Audio Stream')

            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()

            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source)
            await ctx.send(f"🎵 **Now Playing:** {title}")
        except Exception as e:
            await ctx.send(f"❌ Play error: `{e}`")

@bot.command(name="pause")
async def pause_music(ctx):
    """Pauses current playback."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Music paused.")

@bot.command(name="resume")
async def resume_music(ctx):
    """Resumes paused music."""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Music resumed.")

@bot.command(name="skip")
async def skip_music(ctx):
    """Skips current song."""
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop()
        await ctx.send("⏭️ Song skipped.")

@bot.command(name="stop")
async def stop_music(ctx):
    """Stops music and clears player."""
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ Music stopped.")

@bot.command(name="leave")
async def leave_vc(ctx):
    """Disconnects bot from Voice Channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Disconnected from Voice Channel.")

@bot.command(name="vc247")
async def vc247_toggle(ctx):
    """Locks bot to current Voice Channel for 24/7 staying."""
    if not ctx.author.voice:
        return await ctx.send("❌ Pehle kisi Voice Channel me join karein!")
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect(reconnect=True, timeout=30.0)
    await ctx.send("🔒 **24/7 VC Lock Activated!** Bot channel nahi chhodega.")

# ----------------- ECONOMY COMMANDS -----------------

@bot.command(name="daily")
async def daily_reward(ctx):
    """Claims daily coins."""
    uid = ctx.author.id
    reward = 500
    user_balances[uid] = user_balances.get(uid, 0) + reward
    await ctx.send(f"💰 **+{reward} Coins!** Aapka naya balance: **{user_balances[uid]} Coins**.")

@bot.command(name="balance")
async def check_balance(ctx):
    """Checks wallet balance."""
    uid = ctx.author.id
    bal = user_balances.get(uid, 0)
    await ctx.send(f"💳 **{ctx.author.display_name}**, Aapka Balance: **{bal} Coins**.")

# ----------------- UTILITY & FUN COMMANDS -----------------

@bot.command(name="ping")
async def ping_bot(ctx):
    """Latency test."""
    await ctx.send(f"🏓 **Pong!** Latency: `{round(bot.latency * 1000)}ms`")

@bot.command(name="avatar")
async def show_avatar(ctx, member: discord.Member = None):
    """Displays user avatar."""
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.display_name}'s Avatar", color=discord.Color.blue())
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="toss")
async def coin_toss(ctx):
    """Flips a coin."""
    res = random.choice(["Heads 🪙", "Tails 🪙"])
    await ctx.send(f"🎲 Result: **{res}**")

@bot.command(name="poll")
async def create_poll(ctx, *, question: str):
    """Creates a quick voting poll."""
    embed = discord.Embed(title="📊 Community Poll", description=question, color=discord.Color.gold())
    embed.set_footer(text=f"Asked by {ctx.author.display_name}")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@bot.command(name="help")
async def custom_help(ctx):
    """Displays command manual."""
    embed = discord.Embed(title="⚡ AuraBot Command Manual", color=discord.Color.purple())
    embed.add_field(name="🎵 Music & VC", value="`!play <song>`, `!join`, `!pause`, `!resume`, `!skip`, `!stop`, `!leave`, `!vc247`", inline=False)
    embed.add_field(name="💰 Economy", value="`!daily`, `!balance`", inline=False)
    embed.add_field(name="⚙️ Utility & Fun", value="`!ping`, `!avatar`, `!toss`, `!poll <question>`", inline=False)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_TOKEN environment variable not set!")
