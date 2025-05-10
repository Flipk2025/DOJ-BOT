import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone

class Rozprawa(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="rozprawa",
        description="Ogłasza termin rozprawy sądowej"
    )
    @app_commands.describe(
        data="Data w formacie DD/MM/RRRR",
        godzina="Godzina w formacie HH:MM (24h)",
        sedzia_prowadzacy="Sędzia prowadzący",
        sedzia_pomocniczy="Sędzia pomocniczy",
        tryb="Tryb rozprawy",
        oskarzeni="Wzmiankuj oskarżonych"
    )
    async def rozprawa(
        self,
        interaction: discord.Interaction,
        data: str,
        godzina: str,
        sedzia_prowadzacy: str,
        sedzia_pomocniczy: str,
        tryb: str,
        oskarzeni: str
    ):
        # ✅ Defer — zabezpiecza przed błędem 40060
        await interaction.response.defer(ephemeral=True)

        # Sprawdzenie uprawnień
        allowed_role_id = 1334892405035372564
        if allowed_role_id not in [r.id for r in interaction.user.roles]:
            return await interaction.followup.send("Nie masz uprawnień do użycia tej komendy.", ephemeral=True)

        # Parsowanie daty i godziny
        try:
            dt_obj = datetime.strptime(f"{data} {godzina}", "%d/%m/%Y %H:%M")
            timestamp = int(dt_obj.replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            return await interaction.followup.send("Błąd formatu daty lub godziny. Użyj `DD/MM/RRRR` i `HH:MM`.", ephemeral=True)

        # Kanał sądowy
        court_channel = self.bot.get_channel(1370809492283064350)
        if not court_channel:
            return await interaction.followup.send("Nie znaleziono kanału sądowego.", ephemeral=True)

        # Komponujemy jedną wiadomość z blokiem kodu i pingiem roli jako spoiler
        content = (
            "```\n"
            "# TERMIN ROZPRAWY\n\n"
            f"### Data: {data} (<t:{timestamp}:R>)\n"
            f"### Godzina: {godzina}\n"
            f"### Sędzia prowadzący: {sedzia_prowadzacy}\n"
            f"### Sędzia pomocniczy: {sedzia_pomocniczy}\n"
            f"### Tryb Rozprawy: {tryb}\n"
            f"### Oskarżony: {oskarzeni}\n"
            "```\n"
            f"||<@&1370830123523379210>||"
        )

        await court_channel.send(content)
        await interaction.followup.send(f"Rozprawa ogłoszona na {court_channel.mention}.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Rozprawa(bot))
