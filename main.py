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
app.secret_key = "amit_super_secret_key_ultimate_bot"

ADMIN_USERNAME = "AMIT"
ADMIN_PASSWORD = "AMIT"

bot_settings = {
    "welcome_message": """🍃 ━━━━━━━━━━━━━━━━━━━━━━━━━━ 🍃
Welcome to the Forest, <@user>! 🍄

Humare cozy community garden mein aapka swaagat hai! ✨

🌷 ┆ *Rules:* <#1478807408342995098>
🌿 ┆ *Main Chat:* <#1478807408867414171>
🌸 ┆ *Self Roles:* <#1478807408342995099>

Chill karo, music suno aur naye dosto se milo! 🎧💖
🍃 ━━━━━━━━━━━━━━━━━━━━━━━━🍃""",
    "welcome_image": "https://images.unsplash.com/photo-1511497584788-876761102341?q=80&w=1000&auto=format&fit=crop"
}

# ==================== 1. ULTIMATE LOGIN & DASHBOARD TEMPLATES ====================
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AuraBot Ultimate Login</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #0f172a, #1e1b4b); color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: rgba(30, 41, 59, 0.9); padding: 40px; border-radius: 16px; box-shadow: 0 15px 35px rgba(0,0,0,0.6); width: 350px; border-top: 5px solid #38bdf8; backdrop-filter: blur(10px); }
        h2 { color: #38bdf8; text-align: center; margin-top: 0; font-weight: 800; letter-spacing: 1px; }
        label { display: block; margin-bottom: 8px; font-size: 13px; color: #cbd5e1; font-weight: 600; text-transform: uppercase; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px; margin-bottom: 20px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: white; box-sizing: border-box; font-size: 15px; }
        input:focus { border-color: #38bdf8; outline: none; box-shadow: 0 0 10px rgba(56, 189, 248, 0.3); }
        button { background: linear-gradient(135deg, #0284c7, #0369a1); color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; font-size: 16px; transition: 0.3s; }
        button:hover { background: linear-gradient(135deg, #0369a1, #075985); transform: translateY(-2px); box-shadow: 0 5px 15px rgba(2, 132, 199, 0.4); }
        .error { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #fca5a5; padding: 10px; border-radius: 6px; font-size: 13px; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>⚡ AuraBot Master</h2>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        <form method="POST" action="/login">
            <label>Admin Username:</label>
            <input type="text" name="username" placeholder="Enter username..." required>
            <label>Admin Password:</label>
            <input type="password" name="password" placeholder="Enter password..." required>
            <button type="submit">Unlock Dashboard</button>
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
    <title>AuraBot Ultimate Command Center</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0b0f19; color: #f8fafc; margin: 0; padding: 25px; }
        .container { max-width: 900px; margin: 0 auto; background: #111827; padding: 35px; border-radius: 16px; box-shadow: 0 20px 40px rgba(0,0,0,0.7); border: 1px solid #1f2937; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #1f2937; padding-bottom: 20px; margin-bottom: 25px; }
        h1 { color: #38bdf8; margin: 0; font-size: 26px; font-weight: 800; display: flex; align-items: center; gap: 10px; }
        .logout-btn { background: #ef4444; padding: 10px 20px; border-radius: 8px; color: white; text-decoration: none; font-weight: bold; font-size: 13px; transition: 0.3s; }
        .logout-btn:hover { background: #dc2626; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4); }
        .grid { display: grid; grid-template-columns: 1fr; gap: 20px; }
        .card { background: #1f2937; padding: 25px; border-radius: 12px; border-left: 5px solid #38bdf8; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        h3 { margin-top: 0; color: #38bdf8; font-size: 18px; display: flex; align-items: center; gap: 8px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; font-size: 14px; color: #cbd5e1; }
        input[type="text"] { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #374151; background: #0b0f19; color: white; box-sizing: border-box; font-size: 14px; }
        textarea { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #374151; background: #0b0f19; color: white; box-sizing: border-box; height: 130px; resize: vertical; font-family: monospace; font-size: 13px; }
        input:focus, textarea:focus { border-color: #38bdf8; outline: none; }
        button { background: linear-gradient(135deg, #0284c7, #0369a1); color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; font-size: 15px; transition: 0.3s; }
        button:hover { background: linear-gradient(135deg, #0369a1, #075985); box-shadow: 0 5px 15px rgba(2, 132, 199, 0.4); }
        .status-badge { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 20px; background: rgba(34, 197, 94, 0.2); border: 1px solid #22c55e; color: #4ade80; font-weight: bold; font-size: 13px; }
        .dot { height: 8px; width: 8px; background-color: #4ade80; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #4ade80; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ AuraBot Master Control Panel</h1>
            <a href="/logout" class="logout-btn">Logout Securely</a>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🤖 Bot Operational Status</h3>
                <p style="margin: 0;">Live System State: <span class="status-badge"><span class="dot"></span> Online & Fully Operational</span></p>
            </div>

            <div class="card">
                <h3>⚙️ Live Presence & Status Changer</h3>
                <form action="/update-status" method="POST">
                    <label for="status_text">Custom Playing Status Message:</label>
                    <input type="text" id="status_text" name="status_text" placeholder="e.g. /help | Forest Vibes 🍄" required>
                    <button type="submit">Push Status to Discord</button>
                </form>
            </div>

            <div class="card">
                <h3>🌿 Forest Welcome Message & Banner Studio</h3>
                <form action="/update-welcome" method="POST">
                    <label for="welcome_msg">Welcome Embed Content (Supports Markdown & <@user>):</label>
                    <textarea id="welcome_msg" name="welcome_msg" required>{{ current_msg }}</textarea>
                    <label for="welcome_img">Welcome Embed Banner Image URL:</label>
                    <input type="text" id="welcome_img" name="welcome_img" value="{{ current_img }}" required>
                    <button type="submit">Save & Apply Welcome Config</button>
                </form>
            </div>

            <div class="card">
                <h3>📢 Global Broadcast Announcement</h3>
                <form action="/broadcast" method="POST">
                    <label for="channel_id">Target Discord Text Channel ID:</label>
                    <input type="text" id="channel_id" name="channel_id" placeholder="Paste Channel ID here..." required>
                    <label for="message">Announcement Message Text:</label>
                    <input type="text" id="message" name="message" placeholder="Type your broadcast message..." required>
                    <button type="submit">Broadcast Instantly</button>
                </form>
            </div>
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
            error = "⚠️ Galat Username ya Password hai! Dobara koshish karein."
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
    try:
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Flask server error: {e}")

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
    'default_search': 'ytsearch', # Yeh pehle se hai, ise yehi rehne dein
    'extract_flat': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'no_warnings': True,
    'source_address': '0.0.0.0',
    'extractor-args': {'youtube': {'player-client': ['ios', 'android', 'web']}},
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
    render_url = "https://web-production-7df4a.up.railway.app/login"
    
    embed = discord.Embed(
        title="🌐 AuraBot Master Control Panel",
        description="Aapke bot ko manage karne, forest welcome message badalne aur status update karne ke liye niche diye gaye button par click karein!",
        color=discord.Color.from_rgb(46, 139, 87)
    )
    
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Open Control Panel", style=discord.ButtonStyle.link, url=render_url))
    
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
    DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
    if DISCORD_TOKEN:
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            print(f"Bot start error: {e}")
    else:
        print("ERROR: DISCORD_TOKEN environment variable is missing!")
