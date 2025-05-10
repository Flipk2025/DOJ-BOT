import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from keep_alive import keep_alive

# Start serwera keep-alive
keep_alive()

# Ładowanie zmiennych środowiskowych
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Intencje
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class SupremeCourtBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            # wyłączamy automatyczne syncowanie cogs,
            # będziemy robić to ręcznie w setup_hook
            help_command=None  
        )

    async def setup_hook(self):
        # 1) Ładujemy cogi
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                ext = f"cogs.{filename[:-3]}"
                try:
                    await self.load_extension(ext)
                    print(f"✅ Załadowano coga: {ext}")
                except Exception as e:
                    print(f"❌ Błąd ładowania coga {ext}: {e}")

        # 2) Synchronizujemy slash-komendy
        try:
            synced = await self.tree.sync()
            print(f"🔁 Slash commands synced: {len(synced)} komend")
        except Exception as e:
            print(f"❌ Błąd synchronizacji komend: {e}")

        print("🧩 Setup complete — bot is ready to serve!")

    async def on_ready(self):
        print(f"🚀 Zalogowano jako {self.user} (ID: {self.user.id})")

# Tworzymy i uruchamiamy bota
if __name__ == "__main__":
    bot = SupremeCourtBot()

    # zwykła tekstowa komenda dla testów
    @bot.command(name="ping")
    async def ping(ctx):
        await ctx.send("Pong!")

    bot.run(TOKEN)
