import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run("MTUwMjA4OTY4MDkxOTg1OTQwMA.GXrsdf.72F9jywR1Au0K5rliVUWhGv12H5vENmuVJpbX4")