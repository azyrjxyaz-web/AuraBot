import os
import random
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store last daily claim timestamps for 24-hour cooldown
daily_cooldowns = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# ================== 1. UTILITY & FUN COMMANDS ==================
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! 🏓 {latency}ms", ephemeral=True)

@bot.tree.command(name="avatar", description="Show user profile avatar")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    embed = discord.Embed(title=f"{target.display_name}'s Avatar", color=discord.Color.from_rgb(46, 139, 87))
    embed.set_image(url=target.avatar.url if target.avatar else target.default_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="toss", description="Flip a coin (Heads or Tails)")
async def toss(interaction: discord.Interaction):
    res = random.choice(["Heads 🪙", "Tails 🪙"])
    await interaction.response.send_message(f"Result: **{res}**")

@bot.tree.command(name="poll", description="Create a community poll")
async def create_poll(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title="📊 Forest Community Poll", description=question, color=discord.Color.from_rgb(46, 139, 87))
    embed.set_footer(text=f"Asked by {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

# ================== 2. CLEAR COMMAND ==================
@bot.tree.command(name="clear", description="Clear a specified number of messages")
async def clear_messages(interaction: discord.Interaction, amount: int = 40):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Aapke paas messages delete karne ki permission nahi hai!", ephemeral=True)
        return

    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"✅ {len(deleted)} messages successfully delete kar diye gaye!", ephemeral=True)

# ================== 3. ECONOMY & PANEL COMMANDS ==================
# Simple dictionary simulation for user balances
user_balances = {}

@bot.tree.command(name="balance", description="Check your coin balance")
async def balance(interaction: discord.Interaction):
    uid = interaction.user.id
    bal = user_balances.get(uid, 0)
    await interaction.response.send_message(f"Aapka current balance hai: **{bal} Coins**", ephemeral=True)

@bot.tree.command(name="daily", description="Claim your daily coin reward (24 hours cooldown)")
async def daily(interaction: discord.Interaction):
    import time
    uid = interaction.user.id
    current_time = time.time()
    cooldown_time = 86400  # 24 hours in seconds

    if uid in daily_cooldowns:
        elapsed = current_time - daily_cooldowns[uid]
        if elapsed < cooldown_time:
            remaining = int(cooldown_time - elapsed)
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            await interaction.response.send_message(f"⏳ Aap apna daily reward pehle hi claim kar chuke hain! Kripya **{hours} ghante aur {minutes} minat** baad dobara koshish karein.", ephemeral=True)
            return

    # Update balance and cooldown time
    daily_cooldowns[uid] = current_time
    user_balances[uid] = user_balances.get(uid, 0) + 500
    await interaction.response.send_message(f"🎁 +500 Coins! Aapka naya balance: **{user_balances[uid]} Coins**.")

@bot.tree.command(name="dashboard", description="Get the web control panel link")
async def dashboard(interaction: discord.Interaction):
    await interaction.response.send_message("🌐 Web control panel link: https://your-panel-link-here.up.railway.app", ephemeral=True)

# ================== 4. MUSIC & VC COMMANDS (Placeholders / Configured) ==================
@bot.tree.command(name="play", description="Play music from YouTube or SoundCloud")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.send_message(f"🎶 Playing: **{query}**")

@bot.tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f"✅ Connected to {channel.name}!")
    else:
        await interaction.response.send_message("❌ Aap kisi Voice Channel mein nahi hain!", ephemeral=True)

@bot.tree.command(name="pause", description="Pause current music")
async def pause(interaction: discord.Interaction):
    await interaction.response.send_message("⏸️ Music paused.")

@bot.tree.command(name="resume", description="Resume paused music")
async def resume(interaction: discord.Interaction):
    await interaction.response.send_message("▶️ Music resumed.")

@bot.tree.command(name="skip", description="Skip current track")
async def skip(interaction: discord.Interaction):
    await interaction.response.send_message("⏭️ Track skipped.")

@bot.tree.command(name="stop", description="Stop music player")
async def stop(interaction: discord.Interaction):
    await interaction.response.send_message("⏹️ Music stopped.")

@bot.tree.command(name="leave", description="Disconnect the player from voice channel")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 Disconnected from voice channel.")
    else:
        await interaction.response.send_message("❌ Bot kisi Voice Channel mein nahi hai!", ephemeral=True)

@bot.tree.command(name="vc247", description="Toggle 24/7 Voice Channel lock mode")
async def vc247(interaction: discord.Interaction):
    await interaction.response.send_message("🔒 24/7 VC Lock Activated! Bot channel nahi chhodega.")

# ================== 5. HELP COMMAND ==================
@bot.tree.command(name="help", description="Show all available slash commands")
async def custom_help(interaction: discord.Interaction):
    embed = discord.Embed(title="⚡ AuraBot Command Manual", color=discord.Color.from_rgb(46, 139, 87))
    embed.add_field(name="🎵 Music & VC", value="`/play`, `/join`, `/pause`, `/resume`, `/skip`, `/stop`, `/leave`, `/vc247`", inline=False)
    embed.add_field(name="🔥 Economy & Panel", value="`/daily`, `/balance`, `/dashboard`", inline=False)
    embed.add_field(name="⚙️ Utility & Fun", value="`/ping`, `/avatar`, `/toss`, `/poll`, `/clear`", inline=False)
    await interaction.response.send_message(embed=embed)

# ================== 6. START BOT ==================
if __name__ == "__main__":
    keep_alive()
    DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("Error: DISCORD_TOKEN environment variable not found.")
