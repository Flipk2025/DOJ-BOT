import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone

class Rozprawa(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Flaga do śledzenia, czy już obsłużyliśmy interakcję
        self._already_responded = set()

    @app_commands.command(name="rozprawa", description="Ogłasza termin rozprawy sądowej")
    @app_commands.describe(
        data="Data w formacie DD/MM/RRRR",
        godzina="Godzina w formacie HH:MM (24h)",
        sedzia_prowadzacy="Sędzia prowadzący",
        sedzia_pomocniczy="Sędzia pomocniczy",
        tryb="Tryb rozprawy",
        oskarzeni="Wzmiankuj oskarżonych"
    )
    async def rozprawa(
        self, interaction: discord.Interaction,
        data: str, godzina: str,
        sedzia_prowadzacy: str, sedzia_pomocniczy: str,
        tryb: str, oskarzeni: str
    ):
        print(f"🔔 /rozprawa callback - ID interakcji: {interaction.id}")
        
        # Sprawdź, czy już obsłużyliśmy tę interakcję
        if interaction.id in self._already_responded:
            print(f"⚠️ Interakcja {interaction.id} już została obsłużona - ignorowanie")
            return
            
        # Zaznacz, że obsługujemy tę interakcję
        self._already_responded.add(interaction.id)
        
        # Limit wielkości zbioru, aby uniknąć wycieków pamięci
        if len(self._already_responded) > 1000:
            self._already_responded.clear()
        
        allowed_role_id = 1334892405035372564
        if allowed_role_id not in [r.id for r in interaction.user.roles]:
            return await interaction.response.send_message(
                "Nie masz uprawnień.", ephemeral=True
            )
        try:
            dt_obj = datetime.strptime(f"{data} {godzina}", "%d/%m/%Y %H:%M")
            timestamp = int(dt_obj.replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            return await interaction.response.send_message(
                "Błędny format daty/godziny.", ephemeral=True
            )
        
        court_channel = self.bot.get_channel(1370809492283064350)
        if not court_channel:
            return await interaction.response.send_message(
                "Brak kanału.", ephemeral=True
            )
        
        # Your content with ANSI-empty blocks if you want
        content = (
            "``` ```\n"
            "# TERMIN ROZPRAWY\n\n"
            f"### Data: {data} (<t:{timestamp}:R>)\n"
            f"### Godzina: {godzina}\n"
            f"### Sędzia prowadzący: {sedzia_prowadzacy}\n"
            f"### Sędzia pomocniczy: {sedzia_pomocniczy}\n"
            f"### Tryb: {tryb}\n"
            f"### Oskarżony: {oskarzeni}\n"
            "``` ```\n"
            "||<@&1370830123523379210>||"
        )
        await court_channel.send(content)
        return await interaction.response.send_message(
            f"Rozprawa ogłoszona na {court_channel.mention}.",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Rozprawa(bot))