import discord
from discord.ext import commands
import asyncio
from flask import Flask
from threading import Thread
import random

# ================= 1. WEB DASHBOARD =================
app = Flask('')

@app.route('/')
def home():
    return """
    <div style='text-align:center; padding:50px; font-family:sans-serif; background:#0f172a; color:white;'>
        <h1>🚀 AuraBot Ultimate Dashboard</h1>
        <p style='color:#10b981; font-weight:bold;'>Status: 100% Operational & All-Rounder Active</p>
        <p>Features Enabled: Moderation | Music | Tickets | Leveling | Giveaways | Welcome</p>
    </div>
    """

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run_web, daemon=True).start()

# ================= 2. BOT INITIALIZATION =================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Simulated XP database
user_xp = {}

@bot.event
async def on_ready():
    print(f"🔥 {bot.user.name} Ultimate All-in-One Bot Online Ho Gaya Hai!")
    await bot.change_presence(activity=discord.Game(name="!help | Everything Automated"))

# ================= 3. WELCOME & LEVELING SYSTEM =================
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="welcome") or member.guild.system_channel
    if channel:
        embed = discord.Embed(
            title=f"🎉 Welcome to {member.guild.name}!",
            description=f"Hey {member.mention}, server me aapka swagat hai! Rules channel check karna mat bhoolna.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Leveling Logic
    author_id = message.author.id
    user_xp[author_id] = user_xp.get(author_id, 0) + 5
    
    await bot.process_commands(message)

# ================= 4. MODERATION COMMANDS =================
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Koi karan nahi diya"):
    await member.kick(reason=reason)
    await ctx.send(f"🚫 **{member.display_name}** ko kick kar diya. Reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Koi karan nahi diya"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 **{member.display_name}** ko ban kar diya. Reason: {reason}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 `{amount}` messages delete ho gaye!", delete_after=3)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int = 10):
    duration = discord.utils.utcnow() + discord.utils.timedelta(minutes=minutes)
    await member.timeout(duration, reason="Muted by Moderator")
    await ctx.send(f"🔇 **{member.display_name}** ko {minutes} minute ke liye mute kar diya.")

# ================= 5. TICKET SUPPORT SYSTEM =================
@bot.command()
async def ticket(ctx):
    guild = ctx.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    channel = await guild.create_text_channel(f'ticket-{ctx.author.name}', overwrites=overwrites)
    await channel.send(f"🎟️ Hey {ctx.author.mention}, aapka support ticket create ho gaya hai. Admin jald hi help karenge!\nTicket close karne ke liye `!closeticket` type karein.")
    await ctx.send(f"✅ Ticket channel bana diya gaya hai: {channel.mention}", delete_after=5)

@bot.command()
async def closeticket(ctx):
    if "ticket-" in ctx.channel.name:
        await ctx.send("🔒 Ticket channel 5 seconds me close ho raha hai...")
        await asyncio.sleep(5)
        await ctx.channel.delete()

# ================= 6. MUSIC COMMANDS =================
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"🔊 **{channel.name}** voice channel me join ho gaya!")
    else:
        await ctx.send("❌ Aapko pehle kisi Voice Channel me join hona padega!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Voice channel chhod diya.")

# ================= 7. UTILITY, GIVEAWAY & FUN =================
@bot.command()
async def level(ctx, member: discord.Member = None):
    member = member or ctx.author
    xp = user_xp.get(member.id, 0)
    lvl = xp // 50
    await ctx.send(f"📊 **{member.display_name}** | Level: `{lvl}` | XP: `{xp}`")

@bot.command()
@commands.has_permissions(administrator=True)
async def giveaway(ctx, seconds: int, *, prize: str):
    embed = discord.Embed(title="🎁 GIVEAWAY!", description=f"Prize: **{prize}**\nReact 🎉 to enter!\nTime: `{seconds}` seconds", color=discord.Color.gold())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")
    
    await asyncio.sleep(seconds)
    
    new_msg = await ctx.channel.fetch_message(msg.id)
    users = [user async for user in new_msg.reactions[0].users() if not user.bot]
    
    if users:
        winner = random.choice(users)
        await ctx.send(f"🎊 Mubarak ho {winner.mention}! Aapne jeeta: **{prize}**!")
    else:
        await ctx.send("😞 Koi valid entry nahi mili.")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="📊 Community Poll", description=question, color=discord.Color.blue())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

# ================= 8. RUN BOT & DASHBOARD =================
keep_alive()

BOT_TOKEN = "MTUzNDg4NzQzNjEzNDUxODg5Ng.GwOomE.0IgO4oCADAx3vTLPwxh_iccLFyqYtwRtbb1190"
bot.run(BOT_TOKEN)