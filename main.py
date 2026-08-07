import os
import asyncio
import random
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

ADMIN_USERNAME = "AMIT"
ADMIN_PASSWORD = "AMIT"

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

# ==================== 1. LOGIN & DASHBOARD TEMPLATES ====================
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AuraBot Login</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); width: 320px; border-top: 4px solid #38bdf8; }
        h2 { color: #38bdf8; text-align: center; margin-top: 0; }
        label { display: block; margin-bottom: 8px; font-size: 14px; color: #cbd5e1; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; margin-bottom: 15px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; box-sizing: border-box; }
        button { background: #0284c7; color: white; border: none; padding: 10px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; font-size: 15px; }
        button:hover { background: #0369a1; }
        .error { color: #ef4444; font-size: 13px; text-align: center; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>🔒 Admin Login</h2>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        <form method="POST" action="/login">
            <label>Username:</label>
            <input type="text" name="username" required>
            <label>Password:</label>
            <input type="password" name="password" required>
            <button type="submit">Login</button>
        </form>
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
    <title>AuraBot Control Panel</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 850px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        .header { display: flex; justify-content: space-between; align-items: center; }
        h1 { color: #38bdf8; margin: 0; }
        .logout-btn { background: #ef4444; padding: 8px 15px; border-radius: 6px; color: white; text-decoration: none; font-weight: bold; font-size: 13px; }
        .logout-btn:hover { background: #dc2626; }
        .subtitle { color: #94a3b8; margin-bottom: 30px; font-size: 14px; }
        .card { background: #334155; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #38bdf8; }
        h3 { margin-top: 0; color: #38bdf8; }
        label { display: block; margin-bottom: 8px; font-weight: bold; font-size: 14px; color: #cbd5e1; }
        input[type="text"] { width: 100%; padding: 10px; margin-bottom: 15px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; box-sizing: border-box; }
        textarea { width: 100%; padding: 10px; margin-bottom: 15px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; box-sizing: border-box; height: 120px; resize: vertical; }
        button { background: #0284c7; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; font-size: 15px; transition: background 0.2s; }
        button:hover { background: #0369a1; }
        .status-badge { display: inline-block; padding: 6px 12px; border-radius: 20px; background: #22c55e; color: white; font-weight: bold; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AuraBot Control Panel</h1>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
        <p class="subtitle">Protected Admin Dashboard</p>
        
        <div class="card">
            <h3>🤖 Bot Status</h3>
            <p>Current State: <span class="status-badge">Online & Active</span></p>
        </div>

        <div class="card">
            <h3>⚙️ Change Bot Activity / Playing Status</h3>
            <form action="/update-status" method="POST">
                <label for="status_text">Status Activity Message:</label>
                <input type="text" id="status_text" name="status_text" placeholder="e.g. /help | High Performance Music" required>
                <button type="submit">Update Status</button>
            </form>
        </div>

        <div class="card">
            <h3>🌿 Customize Forest Welcome Message & Banner</h3>
            <form action="/update-welcome" method="POST">
                <label for="welcome_msg">Welcome Text / Description:</label>
                <textarea id="welcome_msg" name="welcome_msg" required>{{ current_msg }}</textarea>
                <label for="welcome_img">Welcome Banner Image URL:</label>
                <input type="text" id="welcome_img" name="welcome_img" value="{{ current_img }}" required>
                <button type="submit">Save Welcome Settings</button>
            </form>
        </div>

        <div class="card">
            <h3>📢 Send Announcement / Broadcast</h3>
            <form action="/broadcast" method="POST">
                <label for="channel_id">Discord Text Channel ID:</label>
                <input type="text" id="channel_id" name="channel_id" placeholder="Enter channel ID..." required>
                <label for="message">Announcement Message:</label>
                <input type="text" id="message" name="message" placeholder="Type your message here..." required>
                <button type="submit">Send Broadcast</button>
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
    return render_template_string(DASHBOARD_TEMPLATE, current_msg=bot_settings["welcome_message"], current_img=bot_settings["welcome_image"])

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

async def send_discord_message(channel_id, message):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(f"📢 **Announcement:** {message}")

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

@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user.name} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Sync error: {e}")
    await bot.change_presence(activity=discord.Game(name="/help | Forest Vibes 🍄"))

# ==================== 3. FOREST WELCOME EVENT ====================
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

# ==================== 4. SLASH COMMANDS (MUSIC & VC) ====================

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

# ==================== 5. SLASH COMMANDS (ECONOMY & DASHBOARD) ====================

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

@bot.tree.command(name="dashboard", description="Get the web control panel link")
async def dashboard_link(interaction: discord.Interaction):
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://render.com")
    
    embed = discord.Embed(
        title="🌐 AuraBot Control Panel",
        description="Aapke bot ko manage karne, forest welcome message badalne aur status update karne ke liye niche diye gaye button par click karein!",
        color=discord.Color.from_rgb(46, 139, 87)
    )
    
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Open Dashboard", style=discord.ButtonStyle.link, url=render_url))
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# ==================== 6. SLASH COMMANDS (UTILITY & FUN) ====================

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

@bot.tree.command(name="help", description="Show all available slash commands")
async def custom_help(interaction: discord.Interaction):
    embed = discord.Embed(title="⚡ AuraBot Command Manual", color=discord.Color.from_rgb(46, 139, 87))
    embed.add_field(name="🎵 Music & VC", value="`/play`, `/join`, `/pause`, `/resume`, `/skip`, `/stop`, `/leave`, `/vc247`", inline=False)
    embed.add_field(name="💰 Economy & Panel", value="`/daily`, `/balance`, `/dashboard`", inline=False)
    embed.add_field(name="⚙️ Utility & Fun", value="`/ping`, `/avatar`, `/toss`, `/poll`", inline=False)
    await interaction.response.send_message(embed=embed)

# ==================== 7. START BOT ====================
if __name__ == "__main__":
    keep_alive()
    DISCORD_TOKEN = "MTUzNDg4NzQzNjEzNDUxODg5Gimde5.Sd0kyos2HVqYGRk63nJw0rnnSjYDbdQP5ttCY"
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("ERROR: Discord token is missing!")
