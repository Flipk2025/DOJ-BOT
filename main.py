import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from keep_alive import keep_alive

# Start serwera keep-alive
keep_alive()

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Intencje
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Tworzymy instancję bota
bot = commands.Bot(command_prefix="!", intents=intents)

# Event on_ready
@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

# Prosta komenda ping
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Auto ładowanie coga
@bot.event
async def setup_hook():
    # Ładujemy wszystkie cogi w folderze "cogs"
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Załadowano coga: {filename}")
            except Exception as e:
                print(f"❌ Błąd ładowania coga {filename}: {e}")

    # Synchronizowanie komend
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Slash commands synced ({len(synced)} komend)")
    except Exception as e:
        print(f"❌ Błąd synchronizacji komend: {e}")

    print("🧩 Wszystkie cogi załadowane")

# Pobranie tokenu i uruchomienie bota
token = os.getenv("TOKEN")

if __name__ == "__main__":
    bot.run(token)
