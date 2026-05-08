import discord
from discord.ext import commands
import os
import logging
import asyncio
from datetime import datetime

# ─── Setup Logging ───
# Railway logs everything, so this helps you debug crashes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('discord')

# ─── Intents ───
# You already got this right! message_content is required for prefix commands
intents = discord.Intents.default()
intents.message_content = True
# Add these ONLY if your bot needs them later:
# intents.members = True      # For welcome messages, user info
# intents.presences = True    # For status tracking (needs verification)

# ─── Bot Setup ───
# case_insensitive=True: "Ping", "PING", and "ping" all work
# help_command=None: We'll use a custom help or slash commands later
bot = commands.Bot(
    command_prefix="0",
    intents=intents,
    case_insensitive=True,
    help_command=None
)

# ─── Event: On Ready ───
@bot.event
async def on_ready():
    logger.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info(f"📊 Connected to {len(bot.guilds)} guilds")
    # Optional: Set a status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"0help | {len(bot.guilds)} servers"
        )
    )

# ─── Event: Command Error Handling ───
# Without this, errors silently fail in chat. This tells users what went wrong.
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Silently ignore unknown commands (prevents spam)
    
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"⚠️ Missing argument: `{error.param.name}`")
    
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Wait {error.retry_after:.1f}s before using this again.")
    
    else:
        logger.error(f"Unhandled error: {error}")
        await ctx.send("💥 An unexpected error occurred. Devs have been notified.")

# ─── Event: On Guild Join ───
# Logs when the bot joins a new server (useful for tracking growth)
@bot.event
async def on_guild_join(guild):
    logger.info(f"➕ Joined guild: {guild.name} (ID: {guild.id})")

# ─── Commands ───
@bot.command(name="ping", aliases=["pong", "latency"])
async def ping_command(ctx):
    """Check bot latency and API response time"""
    # Calculate round-trip time
    api_latency = round(bot.latency * 1000, 2)
    
    # Measure message send time
    start = discord.utils.utcnow()
    msg = await ctx.send("🏓 Pong! Calculating...")
    end = discord.utils.utcnow()
    
    msg_latency = round((end - start).total_seconds() * 1000, 2)
    
    embed = discord.Embed(
        title="🏓 Pong!",
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="API Latency", value=f"`{api_latency}ms`", inline=True)
    embed.add_field(name="Message Latency", value=f"`{msg_latency}ms`", inline=True)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
    
    await msg.edit(content=None, embed=embed)

@bot.command(name="help", aliases=["h", "commands"])
async def help_command(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="📖 Bot Commands",
        description="Here are all available commands:",
        color=discord.Color.blue()
    )
    embed.add_field(name="`0ping`", value="Check bot latency", inline=False)
    embed.add_field(name="`0help`", value="Show this message", inline=False)
    embed.set_footer(text=f"Prefix: 0 | Total servers: {len(bot.guilds)}")
    await ctx.send(embed=embed)

# ─── Slash Command (Modern Discord) ───
# Slash commands are the modern standard and don't need message_content intent
@bot.tree.command(name="ping", description="Check bot latency")
async def slash_ping(interaction: discord.Interaction):
    api_latency = round(bot.latency * 1000, 2)
    await interaction.response.send_message(f"🏓 Pong! `{api_latency}ms`")

# ─── Sync Slash Commands ───
# Run this once when adding new slash commands, then remove
@bot.command(hidden=True)
@commands.is_owner()
async def sync(ctx):
    """Sync slash commands (owner only)"""
    synced = await bot.tree.sync()
    await ctx.send(f"✅ Synced {len(synced)} slash command(s)")

# ─── Run Bot ───
def main():
    token = os.getenv("Bot_Token")
    if not token:
        logger.error("❌ Bot_Token environment variable not found!")
        logger.error("   Set it in Railway Variables or create a .env file locally")
        return
    
    try:
        bot.run(token, log_handler=None)  # log_handler=None prevents duplicate logs
    except discord.LoginFailure:
        logger.error("❌ Invalid token. Check your Bot_Token in Railway.")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
