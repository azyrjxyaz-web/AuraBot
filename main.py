import os
import asyncio
import random
import time
import discord
from discord.ext import commands
from flask import Flask, render_template_string, request, redirect, url_for, session
from threading import Thread
import yt_dlp
import static_ffmpeg

# Automatic FFmpeg Setup
static_ffmpeg.add_paths()

# ==================== SECURITY & SETTINGS ====================
app = Flask('')
app.secret_key = "amit_secret_key_change_this"

ADMIN_USERNAME = "AuraBot"
ADMIN_PASSWORD = "AMITRATHOD"

bot_settings = {
    "welcome_message": """🍃 ━━━━━━━━━━━━━━━━━━━━━━━━━━ 🍃
Welcome to the Forest, <@user>! 🍄

Humare cozy community garden mein aapka swaagat hai! ✨

🌷 ┆ **Rules:** <#1478807408342995098>
🌿 ┆ **Main Chat:** <#1478807408867414171>
🌸 ┆ **Self Roles:** <#1478807408342995099>

Chill karo, music suno aur naye dosto se milo! 🎧💖
🍃 ━━━━━━━━━━━━━━━━━━━━━━━━🍃""",
    "welcome_image": "https://images.unsplash.com/photo-1511497584788-876761102341?q=80&w=1000&auto=format&fit=crop"
}

# ==================== 1. POWERFUL ADVANCED LOGIN & DASHBOARD ====================
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AuraBot Ultimate Login</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #0b0f19; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: #111827; padding: 40px; border-radius: 16px; box-shadow: 0 20px 40px rgba(0,0,0,0.7); width: 350px; border-top: 5px solid #38bdf8; border: 1px solid #1f2937; }
        h2 { color: #38bdf8; text-align: center; margin-top: 0; font-size: 24px; }
        label { display: block; margin-bottom: 8px; font-size: 13px; color: #94a3b8; font-weight: 600; text-transform: uppercase; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px; margin-bottom: 18px; border-radius: 8px; border: 1px solid #374151; background: #0b0f19; color: white; box-sizing: border-box; font-size: 15px; }
        button { background: #0ea5e9; color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; font-size: 16px; transition: 0.2s; }
        button:hover { background: #0284c7; }
        .error { background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #ef4444; padding: 10px; border-radius: 6px; font-size: 13px; text-align: center; margin-bottom: 15px; }
        .hint { text-align: center; color: #64748b; font-size: 12px; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>🔒 AuraBot Secure</h2>
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST" action="/login">
            <label>Username:</label>
            <input type="text" name="username" placeholder="Enter AuraBot" required>
            <label>Password:</label>
            <input type="password" name="password" placeholder="Enter Password" required>
            <button type="submit">Access Control Panel</button>
        </form>
        <p class="hint">Default: AuraBot / AMITRATHOD</p>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AuraBot Ultimate Control Panel</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0b0f19; color: #f8fafc; margin: 0; padding: 30px; }
        .container { max-width: 950px; margin: 0 auto; background: #111827; padding: 35px; border-radius: 16px; box-shadow: 0 20px 45px rgba(0,0,0,0.8); border: 1px solid #1f2937; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1f2937; padding-bottom: 20px; margin-bottom: 25px; }
        h1 { color: #38bdf8; margin: 0; font-size: 26px; }
        .logout-btn { background: #ef4444; padding: 10px 20px; border-radius: 8px; color: white; text-decoration: none; font-weight: bold; font-size: 14px; transition: 0.2s; }
        .logout-btn:hover { background: #dc2626; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .card { background: #1f2937; padding: 22px; border-radius: 12px; border-left: 5px solid #38bdf8; border: 1px solid #374151; }
        .card.full { grid-column: span 2; }
        h3 { margin-top: 0; color: #38bdf8; font-size: 18px; margin-bottom: 15px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; font-size: 13px; color: #94a3b8; text-transform: uppercase; }
        input[type="text"], textarea { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #374151; background: #0b0f19; color: white; box-sizing: border-box; font-size: 14px; }
        textarea { height: 140px; resize: vertical; font-family: monospace; }
        button { background: #0ea5e9; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; font-size: 15px; transition: 0.2s; }
        button:hover { background: #0284c7; }
        .danger-btn { background: #ef4444 !important; }
        .danger-btn:hover { background: #dc2626 !important; }
        .status-badge { display: inline-block; padding: 6px 14px; border-radius: 20px; background: #22c55e; color: white; font-weight: bold; font-size: 12px; }
        .info-text { color: #cbd5e1; font-size: 14px; margin: 5px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ AuraBot Ultimate Command Center</h1>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🤖 Bot Live Status</h3>
                <p class="info-text">State: <span class="status-badge">Online & Active 24/7</span></p>
                <p class="info-text">Latency: <b>{{ bot_latency }}ms</b></p>
                <p class="info-text">Active Voice Channels: <b>{{ active_vc_count }}</b></p>
            </div>

            <div class="card">
                <h3>🔊 Voice Management</h3>
                <p class="info-text">Connected VC: <b>{{ current_vc_name }}</b></p>
                <form action="/disconnect-vc" method="POST" style="margin-top: 15px;">
                    <button type="submit" class="danger-btn">Force Disconnect Bot from VC</button>
                </form>
            </div>
        </div>

        <div class="card full">
            <h3>⚙️ Change Bot Activity / Playing Status</h3>
            <form action="/update-status" method="POST">
                <label>Status Message (Activity):</label>
                <input type="text" name="status_text" placeholder="e.g. /help | Forest Vibes 🍄" required>
                <button type="submit">Update Bot Status</button>
            </form>
        </div>

        <div class="card full">
            <h3>🌿 Customize Forest Welcome Message & Banner</h3>
            <form action="/update-welcome" method="POST">
                <label>Welcome Text / Embed Description:</label>
                <textarea name="welcome_msg" required>{{ current_msg }}</textarea>
                <label>Welcome Banner Image URL:</label>
                <input type="text" name="welcome_img" value="{{ current_img }}" required>
                <button type="submit">Save Welcome Settings</button>
            </form>
        </div>

        <div class="card full">
            <h3>📢 Send Global Announcement / Broadcast</h3>
            <form action="/broadcast" method="POST">
                <label>Discord Text Channel ID:</label>
                <input type="text" name="channel_id" placeholder="Enter target channel ID..." required>
                <label>Announcement Message:</label>
                <input type="text" name="message" placeholder="Type your high-priority announcement here..." required>
                <button type="submit">Send Broadcast Message</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USERNAME and request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            error = "Galat Username ya Password hai!"
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    latency = round(bot.latency * 1000) if bot.latency else 0
    vc_count = len(bot.voice_clients)
    vc_name = bot.voice_clients[0].channel.name if vc_count > 0 and bot.voice_clients[0].channel else "None"

    return render_template_string(
        DASHBOARD_TEMPLATE, 
        current_msg=bot_settings["welcome_message"], 
        current_img=bot_settings["welcome_image"],
        bot_latency=latency,
        active_vc_count=vc_count,
        current_vc_name=vc_name
    )

@app.route('/update-status', methods=['POST'])
def update_status():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    new_status = request.form.get('status_text')
    if new_status:
        asyncio.run_coroutine_threadsafe(bot.change_presence(activity=discord.Game(name=new_status)), bot.loop)
    return redirect(url_for('home'))

@app.route('/update-welcome', methods=['POST'])
def update_welcome():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    w_msg = request.form.get('welcome_msg')
    w_img = request.form.get('welcome_img')
    if w_msg:
        bot_settings["welcome_message"] = w_msg
    if w_img:
        bot_settings["welcome_image"] = w_img
    return redirect(url_for('home'))

@app.route('/broadcast', methods=['POST'])
def broadcast():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    channel_id = request.form.get('channel_id')
    msg = request.form.get('message')
    if channel_id and msg:
        try:
            ch_id = int(channel_id)
            asyncio.run_coroutine_threadsafe(send_discord_message(ch_id, msg), bot.loop)
        except ValueError:
            pass
    return redirect(url_for('home'))

@app.route('/disconnect-vc', methods=['POST'])
def disconnect_vc():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    async def leave_all_vc():
        for vc in bot.voice_clients:
            await vc.disconnect()
    asyncio.run_coroutine_threadsafe(leave_all_vc(), bot.loop)
    return redirect(url_for('home'))

async def send_discord_message(channel_id, message):
    channel = bot.get_channel(channel_id)
    if channel:
        embed = discord.Embed(
            title="📢 Forest Official Announcement",
            description=message,
            color=discord.Color.from_rgb(46, 139, 87)
        )
        embed.set_footer(text="Sent via AuraBot Secure Control Panel")
        await channel.send(embed=embed)

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==================== 2. BOT CONFIGURATION ====================
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
daily_cooldowns = {}

@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user.name} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Sync error: {e}")
    await bot.change_presence(activity=discord.Game(name="/help | Forest Vibes 🍄"))

@bot.event
async def on_member_join(member):
    WELCOME_CHANNEL_ID = 1478807408342995096
    target_channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    
    if not target_channel:
        for channel in member.guild.text_channels:
            if "welcome" in channel.name.lower():
                target_channel = channel
                break
        if not target_channel:
            target_channel = member.guild.system_channel

    if target_channel:
        custom_desc = bot_settings['welcome_message'].replace("<@user>", member.mention)

        embed = discord.Embed(
            description=custom_desc,
            color=discord.Color.from_rgb(46, 139, 87)
        )
        embed.set_image(url=bot_settings['welcome_image'])
        embed.set_footer(text=f"Total Members: {member.guild.member_count}")
        
        await target_channel.send(embed=embed)

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

@bot.tree.command(name="daily", description="Claim your daily 24-hour coin reward")
async def daily_reward(interaction: discord.Interaction):
    uid = interaction.user.id
    current_time = time.time()
    cooldown_period = 86400

    if uid in daily_cooldowns:
        elapsed_time = current_time - daily_cooldowns[uid]
        if elapsed_time < cooldown_period:
            remaining_time = cooldown_period - elapsed_time
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            return await interaction.response.send_message(
                f"⏳ Aapne aaj ka daily reward pehle hi claim kar liya hai! Agla reward aap **{hours} ghante aur {minutes} minat** baad claim kar payenge.", 
                ephemeral=True
            )

    daily_cooldowns[uid] = current_time
    reward = 500
    user_balances[uid] = user_balances.get(uid, 0) + reward
    
    await interaction.response.send_message(f"💰 **+{reward} Coins added!** Aapka naya balance: **{user_balances[uid]} Coins**.")

@bot.tree.command(name="balance", description="Check your coin balance")
async def check_balance(interaction: discord.Interaction):
    uid = interaction.user.id
    bal = user_balances.get(uid, 0)
    await interaction.response.send_message(f"💳 **{interaction.user.display_name}**, Aapka Balance: **{bal} Coins**.")

@bot.tree.command(name="dashboard", description="Get the web control panel link")
async def dashboard_link(interaction: discord.Interaction):
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://apka-bot-naam.onrender.com")
    
    embed = discord.Embed(
        title="🌐 AuraBot Control Panel",
        description="Aapke bot ko manage karne, forest welcome message badalne aur status update karne ke liye niche diye gaye button par click karein!",
        color=discord.Color.from_rgb(46, 139, 87)
    )
