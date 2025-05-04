import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from keep_alive import keep_alive

# Load environment variables
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
	print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
async def ping(ctx):
	await ctx.send("Pong!")

# Auto ładowanie cogów
@bot.event
async def setup_hook():
	for filename in os.listdir("./cogs"):
		if filename.endswith(".py") and not filename.startswith("__"):
			await bot.load_extension(f"cogs.{filename[:-3]}")
	try:
		synced = await bot.tree.sync()
		print(f"🔁 Slash commands synced ({len(synced)} komend)")
	except Exception as e:
		print(f"❌ Błąd synchronizacji komend: {e}")
	print("🧩 Wszystkie cogi załadowane")

# Start
keep_alive()
bot.run(os.getenv("TOKEN"))
