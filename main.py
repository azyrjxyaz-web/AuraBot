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

# ==================== FLASK APP SETUP ====================
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

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AuraBot Login</title>
    <style>
        body { font-family: sans-serif; background-color: #0b0f19; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #111827; padding: 30px; border-radius: 12px; width: 320px; border: 1px solid #1f2937; }
        input { width: 100%; padding: 10px; margin: 10px 0; background: #0b0f19; border: 1px solid #374151; color: white; border-radius: 6px; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: #0ea5e9; border: none; color: white; font-weight: bold; border-radius: 6px; cursor: pointer; }
        .error { color: #ef4444; font-size: 13px; text-align: center; }
    </style>
</head>
<body>
    <div class="card">
        <h2 style="color: #38bdf8; text-align: center;">🔒 AuraBot Login</h2>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
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
    <title>AuraBot Dashboard</title>
    <style>
        body { font-family: sans-serif; background-color: #0b0f19; color: #fff; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: #111827; padding: 25px; border-radius: 12px; border: 1px solid #1f2937; }
        h1 { color: #38bdf8; font-size: 22px; }
        .logout { float: right; background: #ef4444; color: white; padding: 6px 12px; text-decoration: none; border-radius: 6px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/logout" class="logout">Logout</a>
        <h1>⚡ AuraBot Control Center</h1>
        <p>Status: <span style="color: #22c55e; font-weight: bold;">Online & Running 24/7</span></p>
        <p>Bot Latency: <b>{{ bot_latency }}ms</b></p>
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
    return render_template_string(DASHBOARD_TEMPLATE, bot_latency=latency)

def run_flask():
    # Render ke diye gaye dynamic PORT ko bind karna zaroori hai
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==================== DISCORD BOT SETUP ====================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user.name}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Sync error: {e}")

@bot.tree.command(name="ping", description="Check bot latency")
async def ping_bot(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! `{latency}ms`")

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ ERROR: 'DISCORD_TOKEN' environment variable is missing!")
