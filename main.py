import os
import asyncio
import random
import discord
from discord.ext import commands
import yt_dlp
import static_ffmpeg

# Automatic FFmpeg Setup
static_ffmpeg.add_paths()

# ==================== 1. BOT CONFIGURATION ====================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -probesize 1000000 -analyzeduration 0',
    'options': '-vn -ac 2 -ar 48000 -b:a 64k'
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
user_balances = {}

@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user.name} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Sync error: {e}")
    await bot.change_presence(activity=discord.Game(name="/help | Forest Vibes 🍄"))

# ==================== 2. SLASH COMMANDS (MUSIC & VC) ====================

@bot.tree.command(name="join", description="Join your current voice channel")
async def join_vc(interaction: discord.Interaction):
    if not interaction.user.voice:
        return await interaction.response.send_message("❌ Pehle kisi Voice Channel me join karein!", ephemeral=True)
    channel = interaction.user.voice.channel
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.move_to(channel)
    else:
        await channel.connect(reconnect=True, timeout=30.0)
    await interaction.response.send_message(f"🔊 Joined **{channel.name}**!")

@bot.tree.command(name="play", description="Play music from YouTube or SoundCloud")
async def play_music(interaction: discord.Interaction, search: str):
    if not interaction.user.voice:
        return await interaction.response.send_message("❌ Pehle kisi Voice Channel me join karein!", ephemeral=True)

    await interaction.response.defer()

    vc = interaction.guild.voice_client
    if not vc:
        vc = await interaction.user.voice.channel.connect(reconnect=True, timeout=30.0)
    elif vc.channel != interaction.user.voice.channel:
        await vc.move_to(interaction.user.voice.channel)

    try:
        query = search if (search.startswith("http://") or search.startswith("https://")) else f"scsearch:{search}"
        info = ytdl.extract_info(query, download=False)
        if 'entries' in info and len(info['entries']) > 0:
            info = info['entries'][0]

        url = info['url']
        title = info.get('title', 'Audio Stream')

        if vc.is_playing():
            vc.stop()

        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
        vc.play(source)
        await interaction.followup.send(f"🎵 **Now Playing:** {title}")
    except Exception as e:
        await interaction.followup.send(f"❌ Play error: `{e}`")

@bot.tree.command(name="pause", description="Pause the currently playing music")
async def pause_music(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.pause()
        await interaction.response.send_message("⏸️ Music paused.")
    else:
        await interaction.response.send_message("❌ Koi music play nahi ho raha hai!", ephemeral=True)

@bot.tree.command(name="resume", description="Resume paused music")
async def resume_music(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
        interaction.guild.voice_client.resume()
        await interaction.response.send_message("▶️ Music resumed.")
    else:
        await interaction.response.send_message("❌ Music paused nahi hai!", ephemeral=True)

@bot.tree.command(name="skip", description="Skip the current song")
async def skip_music(interaction: discord.Interaction):
    if interaction.guild.voice_client and (interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused()):
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏭️ Song skipped.")
    else:
        await interaction.response.send_message("❌ Skip karne ke liye kuch play nahi ho raha!", ephemeral=True)

@bot.tree.command(name="stop", description="Stop music playback")
async def stop_music(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏹️ Music stopped.")
    else:
        await interaction.response.send_message("❌ Bot kisi voice channel me nahi hai!", ephemeral=True)

@bot.tree.command(name="leave", description="Disconnect bot from the voice channel")
async def leave_vc(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 Disconnected from Voice Channel.")
    else:
        await interaction.response.send_message("❌ Bot kisi voice channel me nahi hai!", ephemeral=True)

@bot.tree.command(name="vc247", description="Activate 24/7 Voice Channel lock")
async def vc247_toggle(interaction: discord.Interaction):
    if not interaction.user.voice:
        return await interaction.response.send_message("❌ Pehle kisi Voice Channel me join karein!", ephemeral=True)
    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect(reconnect=True, timeout=30.0)
    await interaction.response.send_message("🔒 **24/7 VC Lock Activated!** Bot channel nahi chhodega.")

# ==================== 3. SLASH COMMANDS (ECONOMY) ====================

@bot.tree.command(name="daily", description="Claim your daily coin reward")
async def daily_reward(interaction: discord.Interaction):
    uid = interaction.user.id
    reward = 500
    user_balances[uid] = user_balances.get(uid, 0) + reward
    await interaction.response.send_message(f"💰 **+{reward} Coins!** Aapka naya balance: **{user_balances[uid]} Coins**.")

@bot.tree.command(name="balance", description="Check your coin balance")
async def check_balance(interaction: discord.Interaction):
    uid = interaction.user.id
    bal = user_balances.get(uid, 0)
    await interaction.response.send_message(f"💳 **{interaction.user.display_name}**, Aapka Balance: **{bal} Coins**.")

# ==================== 4. SLASH COMMANDS (UTILITY & FUN) ====================

@bot.tree.command(name="ping", description="Check bot latency")
async def ping_bot(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 **Pong!** Latency: `{round(bot.latency * 1000)}ms`")

@bot.tree.command(name="avatar", description="Show user profile avatar")
async def show_avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"{member.display_name}'s Avatar", color=discord.Color.from_rgb(46, 139, 87))
    embed.set_image(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="toss", description="Flip a coin")
async def coin_toss(interaction: discord.Interaction):
    res = random.choice(["Heads 🪙", "Tails 🪙"])
    await interaction.response.send_message(f"🎲 Result: **{res}**")

@bot.tree.command(name="poll", description="Create a community poll")
async def create_poll(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title="📊 Forest Community Poll", description=question, color=discord.Color.from_rgb(46, 139, 87))
    embed.set_footer(text=f"Asked by {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@bot.tree.command(name="clear", description="Clear a specified number of messages")
async def clear_messages(interaction: discord.Interaction, amount: int = 40):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Aapke paas messages delete karne ki permission nahi hai!", ephemeral=True)
        return

    try:
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ Successfully **{len(deleted)}** messages delete kar diye gaye!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Messages delete karte samay error aaya: `{e}`", ephemeral=True)

@bot.tree.command(name="help", description="Show all available slash commands")
async def custom_help(interaction: discord.Interaction):
    embed = discord.Embed(title="⚡ AuraBot Command Manual", color=discord.Color.from_rgb(46, 139, 87))
    embed.add_field(name="🎵 Music & VC", value="`/play`, `/join`, `/pause`, `/resume`, `/skip`, `/stop`, `/leave`, `/vc247`", inline=False)
    embed.add_field(name="💰 Economy", value="`/daily`, `/balance`", inline=False)
    embed.add_field(name="⚙️ Utility & Fun", value="`/ping`, `/avatar`, `/toss`, `/poll`, `/clear`", inline=False)
    await interaction.response.send_message(embed=embed)

# ==================== 5. START BOT ====================
if __name__ == "__main__":
    DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
    if DISCORD_TOKEN:
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            print(f"Bot start error: {e}")
    else:
        print("ERROR: DISCORD_TOKEN environment variable is missing!")
