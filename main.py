import discord
from discord.ext import commands
import asyncio
from flask import Flask
from threading import Thread
import random
import os

# ==================== 1. WEB DASHBOARD ====================
app = Flask('')

@app.route('/')
def home():
    return """
    <div style='text-align:center; padding:50px; font-family:sans-serif;'>
        <h1>AuraBot Ultimate Dashboard</h1>
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

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="!help | 24/7 Online"))

# ==================== 3. MODERATION COMMANDS ====================
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

# ==================== 4. UTILITY & UTILS COMMANDS ====================
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
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%m"), inline=True)
    embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(member.display_avatar.url)

# ==================== 5. COMMUNITY & FUN ====================
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

# ==================== 6. RUN BOT & DASHBOARD ====================
keep_alive()

BOT_TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(BOT_TOKEN)
