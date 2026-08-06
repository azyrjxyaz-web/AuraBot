import discord
from discord.ext import commands, tasks
import asyncio
from flask import Flask
from threading import Thread
import random
import os
import yt_dlp

# ==================== 1. WEB DASHBOARD ====================
app = Flask('')

@app.route('/')
def home():
    return """
    <div style='text-align:center; padding:50px; font-family:sans-serif;'>
        <h1>AuraBot Ultimate All-in-One Dashboard</h1>
        <p>Status: <b style='color:green;'>ONLINE 24/7</b></p>
    </div>
    """

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# ==================== 2. BOT CONFIGURATION ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 24/7 VC tracking variable
vc_247_id = None

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="!help | 24/7 Online"))
    if not check_247_vc.is_running():
        check_247_vc.start()

# 24/7 VC Auto-Reconnect Loop (Checks every 15 seconds)
@tasks.loop(seconds=15)
async def check_247_vc():
    global vc_247_id
    if vc_247_id:
        channel = bot.get_channel(vc_247_id)
        if channel:
            guild = channel.guild
            voice_client = guild.voice_client
            if not voice_client or not voice_client.is_connected():
                try:
                    await channel.connect()
                except Exception as e:
                    print(f"24/7 VC Reconnect Error: {e}")

# ==================== 3. VOICE, MUSIC & 24/7 COMMANDS ====================
@bot.command()
async def vc247(ctx, channel_id: int = None):
    global vc_247_id
    if channel_id:
        vc_247_id = channel_id
    elif ctx.author.voice:
        vc_247_id = ctx.author.voice.channel.id
    else:
        return await ctx.send("❌ Pehle kisi Voice Channel me join karo ya Channel ID provide karo!")

    channel = bot.get_channel(vc_247_id)
    if channel:
        if not ctx.voice_client:
            await channel.connect()
        elif ctx.voice_client.channel.id != vc_247_id:
            await ctx.voice_client.move_to(channel)
        await ctx.send(f"🔒 **24/7 Mode Activated!** Bot ab **{channel.name}** VC me 24/7 rahega.")
    else:
        await ctx.send("❌ Voice Channel nahi mila.")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"🔊 Joined **{channel.name}**!")
    else:
        await ctx.send("❌ Pehle kisi Voice Channel me join karo!")

@bot.command()
async def leave(ctx):
    global vc_247_id
    vc_247_id = None  # Disable 24/7 mode on manual leave
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Voice channel se disconnect ho gaya (24/7 mode deactivated).")
    else:
        await ctx.send("❌ Main kisi Voice Channel me nahi hoon.")

@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Pehle kisi Voice Channel me join karo!")

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    async with ctx.typing():
        info = ytdl.extract_info(search, download=False)
        if 'entries' in info:
            info = info['entries'][0]
        url = info['url']
        title = info.get('title', 'Audio')

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
        ctx.voice_client.play(source)

    await ctx.send(f"🎵 Now Playing: **{title}**")

@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Music pause kar diya.")

@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Music resume kar diya.")

@bot.command()
async def stop(ctx):
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop()
        await ctx.send("⏹️ Music stop kar diya.")

# ==================== 4. MODERATION COMMANDS ====================
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"👢 **{member.display_name}** ko kick kar diya gaya. Reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 **{member.display_name}** ko ban kar diya gaya. Reason: {reason}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 **{amount}** messages delete kar diye gaye!")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"✅ **{role.name}** role **{member.display_name}** ko de diya gaya.")

# ==================== 5. UTILITY COMMANDS ====================
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: **{latency}ms**")

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"User Info - {member.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.green())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Total Members", value=guild.member_count, inline=True)
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(member.display_avatar.url)

# ==================== 6. COMMUNITY, FUN & GAMES ====================
@bot.command()
async def giveaway(ctx, seconds: int, *, prize: str):
    embed = discord.Embed(title="🎉 GIVEAWAY!", description=f"Prize: **{prize}**\nReact 🎁 to enter!\nTime: **{seconds}** seconds", color=discord.Color.gold())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎁")

    await asyncio.sleep(seconds)

    new_msg = await ctx.channel.fetch_message(msg.id)
    users = [user async for user in new_msg.reactions[0].users() if not user.bot]

    if users:
        winner = random.choice(users)
        await ctx.send(f"🎉 Mubarak ho {winner.mention}! Aapne jeeta: **{prize}**!")
    else:
        await ctx.send("😞 Koi valid entry nahi mili.")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="📊 Community Poll", description=question, color=discord.Color.blue())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@bot.command()
async def roll(ctx, dice: str = "1d6"):
    try:
        rolls, limit = map(int, dice.split('d'))
        results = [random.randint(1, limit) for _ in range(rolls)]
        await ctx.send(f"🎲 Dice Result: **{', '.join(map(str, results))}** (Total: {sum(results)})")
    except Exception:
        await ctx.send("❌ Format galat hai! Use karo: `!roll 1d6` ya `!roll 2d20`")

@bot.command()
async def toss(ctx):
    outcome = random.choice(["Heads 🪙", "Tails 🪙"])
    await ctx.send(f"Coin flip result: **{outcome}**")

# ==================== 7. RUN BOT & DASHBOARD ====================
keep_alive()

BOT_TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(BOT_TOKEN)
