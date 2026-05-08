import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from datetime import timedelta

# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# =========================
# BOT SETUP
# =========================
bot = commands.Bot(
    command_prefix="0",
    intents=intents,
    help_command=None
)

# =========================
# STORAGE
# =========================
warnings = {}

# =========================
# TIME PARSER
# =========================
def parse_time(time_str):
    try:
        if time_str.endswith("s"):
            return timedelta(seconds=int(time_str[:-1]))
        elif time_str.endswith("m"):
            return timedelta(minutes=int(time_str[:-1]))
        elif time_str.endswith("h"):
            return timedelta(hours=int(time_str[:-1]))
        elif time_str.endswith("d"):
            return timedelta(days=int(time_str[:-1]))
    except:
        pass

    return timedelta(minutes=10)

# =========================
# READY EVENT
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(e)

# =========================
# HELP COMMAND
# =========================
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Moderation Commands",
        color=discord.Color.red()
    )

    embed.add_field(
        name="Moderation",
        value="""
0clear <amount>
0kick @user
0ban @user
0unban <user_id>
0mute @user 1h
0unmute @user
0warn @user reason
0warns @user
0slowmode <seconds>
0lock
0unlock
0nick @user name
0addrole @user @role
0removerole @user @role
0purgeuser @user 20
0tempban @user 1h
0tempmute @user 30m
        """,
        inline=False
    )

    await ctx.send(embed=embed)

# =========================
# CLEAR
# =========================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    msg = await ctx.send(f"Cleared {amount} messages")
    await asyncio.sleep(3)
    await msg.delete()

# =========================
# KICK
# =========================
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick(reason=reason)
    await ctx.send(f"Kicked {member}")

# =========================
# BAN
# =========================
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send(f"Banned {member}")

# =========================
# UNBAN
# =========================
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"Unbanned {user}")

# =========================
# MUTE
# =========================
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, time="10m"):

    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if role is None:
        role = await ctx.guild.create_role(name="Muted")

        for channel in ctx.guild.channels:
            await channel.set_permissions(
                role,
                send_messages=False,
                speak=False
            )

    await member.add_roles(role)

    await ctx.send(f"Muted {member} for {time}")

    await asyncio.sleep(parse_time(time).total_seconds())

    if role in member.roles:
        await member.remove_roles(role)

# =========================
# UNMUTE
# =========================
@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):

    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if role in member.roles:
        await member.remove_roles(role)

    await ctx.send(f"Unmuted {member}")

# =========================
# WARN
# =========================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="No reason"):

    if member.id not in warnings:
        warnings[member.id] = []

    warnings[member.id].append(reason)

    await ctx.send(f"{member} warned for: {reason}")

# =========================
# WARNS
# =========================
@bot.command()
async def warns(ctx, member: discord.Member):

    user_warnings = warnings.get(member.id, [])

    if not user_warnings:
        await ctx.send("No warnings")
        return

    text = "\n".join(user_warnings)

    embed = discord.Embed(
        title=f"Warnings for {member}",
        description=text,
        color=discord.Color.orange()
    )

    await ctx.send(embed=embed)

# =========================
# SLOWMODE
# =========================
@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):

    await ctx.channel.edit(slowmode_delay=seconds)

    await ctx.send(f"Slowmode set to {seconds}s")

# =========================
# LOCK
# =========================
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        send_messages=False
    )

    await ctx.send("Channel locked")

# =========================
# UNLOCK
# =========================
@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        send_messages=True
    )

    await ctx.send("Channel unlocked")

# =========================
# NICK
# =========================
@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, nickname):

    await member.edit(nick=nickname)

    await ctx.send(f"Changed nickname of {member}")

# =========================
# ADDROLE
# =========================
@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, role: discord.Role):

    await member.add_roles(role)

    await ctx.send("Role added")

# =========================
# REMOVEROLE
# =========================
@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):

    await member.remove_roles(role)

    await ctx.send("Role removed")

# =========================
# PURGE USER
# =========================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purgeuser(ctx, member: discord.Member, amount: int = 20):

    def check(message):
        return message.author == member

    await ctx.channel.purge(limit=amount, check=check)

    await ctx.send(f"Purged messages from {member}")

# =========================
# TEMPBAN
# =========================
@bot.command()
@commands.has_permissions(ban_members=True)
async def tempban(ctx, member: discord.Member, time="1h"):

    user = member

    await member.ban()

    await ctx.send(f"Banned {member} for {time}")

    await asyncio.sleep(parse_time(time).total_seconds())

    await ctx.guild.unban(user)

# =========================
# TEMPMUTE
# =========================
@bot.command()
@commands.has_permissions(manage_roles=True)
async def tempmute(ctx, member: discord.Member, time="30m"):

    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if role is None:
        role = await ctx.guild.create_role(name="Muted")

    await member.add_roles(role)

    await ctx.send(f"Muted {member} for {time}")

    await asyncio.sleep(parse_time(time).total_seconds())

    if role in member.roles:
        await member.remove_roles(role)

# =========================
# SLASH COMMANDS
# =========================
@bot.tree.command(name="clear")
@app_commands.describe(amount="How many messages to delete")
async def slash_clear(interaction: discord.Interaction, amount: int):

    await interaction.channel.purge(limit=amount)

    await interaction.response.send_message(
        f"Cleared {amount} messages",
        ephemeral=True
    )

@bot.tree.command(name="mute")
@app_commands.describe(member="Member to mute", time="Example: 1h")
async def slash_mute(
    interaction: discord.Interaction,
    member: discord.Member,
    time: str
):

    role = discord.utils.get(interaction.guild.roles, name="Muted")

    if role is None:
        role = await interaction.guild.create_role(name="Muted")

    await member.add_roles(role)

    await interaction.response.send_message(
        f"Muted {member} for {time}",
        ephemeral=True
    )

# =========================
# ERROR HANDLER
# =========================
@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments.")

    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Member not found.")

    else:
        await ctx.send(f"Error: {error}")

# =========================
# RUN
# =========================
bot.run(os.getenv("TOKEN"))
