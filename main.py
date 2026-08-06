import static_ffmpeg
static_ffmpeg.add_paths()

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
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AuraBot Control Center</title>
        <style>
            body { background: #0b0f19; color: #f3f4f6; font-family: sans-serif; text-align: center; padding: 50px; }
            h1 { color: #a855f7; }
            .status { color: #4ade80; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🤖 AuraBot 24/7 Control Center</h1>
        <p class="status">● System Online & Active</p>
    </body>
    </html>
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

vc_247_id = None
economy = {}

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'extract_flat': False
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="!help | 24/7 All-in-One Bot"))
    if not check_247_vc.is_running():
        check_247_vc.start()

# 24/7 VC Auto-Reconnect Loop
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
                    await channel.connect(reconnect=True, timeout=30.0)
                except Exception as e:
                    print(f"24/7 VC Reconnect Error: {e}")

# ==================== 3. MUSIC & 24/7 COMMANDS ====================
@bot.command(name="vc247")
async def _vc247(ctx, channel_id: int = None):
    global vc_247_id
    if channel_id:
        vc_247_id = channel_id
    elif ctx.author.voice:
        vc_247_id = ctx.author.voice.channel.id
    else:
        return await ctx.send("❌ Pehle kisi Voice Channel me join karo ya Channel ID do!")

    channel = bot.get_channel(vc_247_id)
    if channel:
        if not ctx.voice_client:
            await channel.connect(reconnect=True, timeout=30.0)
        elif ctx.voice_client.channel.id != vc_247_id:
            await ctx.voice_client.move_to(channel)
        await ctx.send(f"🔒 **24/7 Mode Activated!** Bot ab **{channel.name}** VC me hamesha rahega.")
    else:
        await ctx.send("❌ Voice Channel nahi mila.")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect(reconnect=True, timeout=30.0)
        await ctx.send(f"🔊 Joined **{channel.name}**!")
    else:
        await ctx.send("❌ Pehle kisi Voice Channel me join karo!")

@bot.command()
async def leave(ctx):
    global vc_247_id
    vc_247_id = None
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Voice channel se disconnect ho gaya (24/7 mode disabled).")
    else:
        await ctx.send("❌ Main kisi Voice Channel me nahi hoon.")

@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Pehle kisi Voice Channel me join karo!")

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect(reconnect=True, timeout=30.0)
    elif ctx.voice_client.channel != ctx.author.voice.channel:
        await ctx.voice_client.move_to(ctx.author.voice.channel)

    async with ctx.typing():
        try:
            # Direct URL vs Song Name Search
            if not (search.startswith("http://") or search.startswith("https://")):
                query = f"ytsearch:{search}"
            else:
                query = search

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
            await ctx.send(f"❌ Song play karne me error aaya: `{e}`")

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

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Song skip kar diya gaya!")
    else:
        await ctx.send("❌ Abhi koi song play nahi ho raha hai.")

@bot.command()
async def volume(ctx, vol: int):
    if ctx.voice_client and ctx.voice_client.source:
        try:
            ctx.voice_client.source.volume = vol / 100
            await ctx.send(f"🔊 Volume set kardi gayi: **{vol}%**")
        except Exception:
            await ctx.send("❌ Is source par volume adjust nahi ho sakti.")
    else:
        await ctx.send("❌ Bot kisi VC me song play nahi kar raha.")

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

@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"❌ **{role.name}** role **{member.display_name}** se hata diya gaya.")

@bot.command()
@commands.has_permissions(mute_members=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    await member.edit(muted=True, reason=reason)
    await ctx.send(f"🔇 **{member.display_name}** ko voice mute kar diya gaya.")

@bot.command()
@commands.has_permissions(mute_members=True)
async def unmute(ctx, member: discord.Member):
    await member.edit(muted=False)
    await ctx.send(f"🔊 **{member.display_name}** ka voice unmute kar diya gaya.")

# ==================== 5. ECONOMY & FUN COMMANDS ====================
@bot.command()
async def balance(ctx, member: discord.Member = None):
    member = member or ctx.author
    bal = economy.get(member.id, 100)
    await ctx.send(f"💰 **{member.display_name}** ka balance: **{bal} AuraCoins**")

@bot.command()
async def daily(ctx):
    user_id = ctx.author.id
    current = economy.get(user_id, 100)
    economy[user_id] = current + 500
    await ctx.send(f"🎁 {ctx.author.mention}, aapko apne daily **500 AuraCoins** mil gaye hain!")

@bot.command()
async def coinflip(ctx, guess: str, amount: int):
    user_id = ctx.author.id
    bal = economy.get(user_id, 100)
    if amount > bal or amount <= 0:
        return await ctx.send("❌ Aapke paas itne coins nahi hain ya amount invalid hai!")
    
    result = random.choice(["heads", "tails"])
    guess = guess.lower()

    if guess not in ["heads", "tails"]:
        return await ctx.send("❌ Sahi guess likho: `!coinflip heads 50` ya `!coinflip tails 50`")

    if guess == result:
        economy[user_id] += amount
        await ctx.send(f"🎉 Jeet gaye! Coin aaya: **{result.upper()}**. Aapne jeete **{amount} coins**!")
    else:
        economy[user_id] -= amount
        await ctx.send(f"😢 Haar gaye! Coin aaya: **{result.upper()}**. Aapne khoye **{amount} coins**.")

# ==================== 6. COMMUNITY & UTILITY COMMANDS ====================
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Bot Latency: **{latency}ms**")

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
    embed.add_field(name="Total Roles", value=len(guild.roles), inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(member.display_avatar.url)

@bot.command()
async def giveaway(ctx, seconds: int, *, prize: str):
    embed = discord.Embed(title="🎉 GIVEAWAY!", description=f"Prize: **{prize}**\nReact 🎁 karke enter karo!\nTime: **{seconds}** seconds", color=discord.Color.gold())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎁")

    await asyncio.sleep(seconds)

    new_msg = await ctx.channel.fetch_message(msg.id)
    users = [user async for user in new_msg.reactions[0].users() if not user.bot]

    if users:
        winner = random.choice(users)
        await ctx.send(f"🎉 Mubarak ho {winner.mention}! Aapne jeeta hai: **{prize}**!")
    else:
        await ctx.send("😞 Koi valid giveaway entry nahi mili.")

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
        await ctx.send(f"🎲 Dice Roll: **{', '.join(map(str, results))}** (Total: {sum(results)})")
    except Exception:
        await ctx.send("❌ Format galat hai! Use karo: `!roll 1d6`")

@bot.command()
async def toss(ctx):
    outcome = random.choice(["Heads 🪙", "Tails 🪙"])
    await ctx.send(f"Coin toss result: **{outcome}**")

@bot.command(name="8ball")
async def _8ball(ctx, *, question):
    responses = [
        "Haan, bilkul!", "Puri tarah se sambhav hai.", "Isme koi shak nahi.",
        "Baad me poochna.", "Abhi batana mushkil hai.", "Nahi, bilkul nahi.",
        "Kayi chances kam hain.", "Mera jawab 'Nahi' hai."
    ]
    await ctx.send(f"🎱 Sawaal: {question}\nJawab: **{random.choice(responses)}**")

# ==================== 7. RUN BOT & WEB SERVER ====================
keep_alive()

BOT_TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(BOT_TOKEN)
