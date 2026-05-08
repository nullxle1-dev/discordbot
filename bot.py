 import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="0", intents=intents)

# =========================
# MEMORY (simple in-file storage)
# =========================
warnings = {}

# =========================
# HELPER FUNCTIONS
# =========================
def parse_time(time_str):
    if "h" in time_str:
        return timedelta(hours=int(time_str.replace("h", "")))
    if "m" in time_str:
        return timedelta(minutes=int(time_str.replace("m", "")))
    if "d" in time_str:
        return timedelta(days=int(time_str.replace("d", "")))
    return timedelta(minutes=0)

# =========================
# READY EVENT
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(e)

# =========================
# PREFIX COMMANDS (0)
# =========================

# CLEAR
@bot.command()
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"Cleared {amount} messages", delete_after=3)

# KICK
@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"Kicked {member}")

# BAN
@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"Banned {member}")

# UNBAN
@bot.command()
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"Unbanned {user}")

# MUTE (TEMP)
@bot.command()
async def mute(ctx, member: discord.Member, time: str = "10m"):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted")

    await member.add_roles(role)
    await ctx.send(f"Muted {member} for {time}")

    await asyncio.sleep(parse_time(time).total_seconds())
    await member.remove_roles(role)

# UNMUTE
@bot.command()
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(role)
    await ctx.send(f"Unmuted {member}")

# WARN SYSTEM
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    warnings.setdefault(member.id, []).append(reason)
    await ctx.send(f"{member} warned: {reason}")

# CHECK WARNS
@bot.command()
async def warns(ctx, member: discord.Member):
    w = warnings.get(member.id, [])
    await ctx.send(f"{member} has {len(w)} warnings")

# SLOWMODE
@bot.command()
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"Slowmode set to {seconds}s")

# LOCK CHANNEL
@bot.command()
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("Channel locked")

# UNLOCK
@bot.command()
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("Channel unlocked")

# PURGE USER MESSAGES
@bot.command()
async def purgeuser(ctx, member: discord.Member, limit: int = 20):
    def check(m):
        return m.author == member
    await ctx.channel.purge(limit=limit, check=check)
    await ctx.send(f"Deleted messages from {member}")

# MASS BAN (basic)
@bot.command()
async def massban(ctx, limit: int):
    count = 0
    async for member in ctx.guild.fetch_members(limit=limit):
        try:
            await member.ban()
            count += 1
        except:
            pass
    await ctx.send(f"Mass banned {count} users")

# ROLE ADD
@bot.command()
async def addrole(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send("Role added")

# ROLE REMOVE
@bot.command()
async def removerole(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send("Role removed")

# NICKNAME
@bot.command()
async def nick(ctx, member: discord.Member, *, name):
    await member.edit(nick=name)
    await ctx.send("Nickname changed")

# TEMPMUTE
@bot.command()
async def tempmute(ctx, member: discord.Member, time: str):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted")

    await member.add_roles(role)
    await ctx.send(f"Tempmuted {member} for {time}")

    await asyncio.sleep(parse_time(time).total_seconds())
    await member.remove_roles(role)

# TEMPBAN
@bot.command()
async def tempban(ctx, member: discord.Member, time: str):
    await member.ban()
    await ctx.send(f"Temporarily banned {member}")

    await asyncio.sleep(parse_time(time).total_seconds())
    await ctx.guild.unban(member)

# =========================
# SLASH COMMANDS (/)
# =========================

@bot.tree.command(name="clear")
async def slash_clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"Cleared {amount}", ephemeral=True)

@bot.tree.command(name="mute")
async def slash_mute(interaction: discord.Interaction, member: discord.Member, time: str):
    role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not role:
        role = await interaction.guild.create_role(name="Muted")

    await member.add_roles(role)
    await interaction.response.send_message(f"Muted {member} for {time}", ephemeral=True)

# =========================
# RUN BOT
# =========================
bot.rimport os
bot.run(os.getenv("TOKEN"))
