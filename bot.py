import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="0", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Command 1
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Command 2
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.name}!")

# Command 3
@bot.command()
async def add(ctx, a: int, b: int):
    await ctx.send(f"Result: {a + b}")

import os
bot.run(os.getenv("TOKEN"))
