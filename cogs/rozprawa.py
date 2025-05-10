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
        data="Data rozprawy w formacie DD/MM/RRRR",
        godzina="Godzina rozprawy w formacie HH:MM (24h)",
        sedzia_prowadzacy="Sędzia prowadzący",
        sedzia_pomocniczy="Sędzia pomocniczy",
        tryb="Tryb rozprawy (np. Zwykły, Przyspieszony)",
        oskarzeni="Wzmiankuj oskarżonych (oddziel spacją, użyj @mention)"
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
        # 1) Sprawdzenie uprawnień
        allowed_role_id = 1334892405035372564
        if allowed_role_id not in [r.id for r in interaction.user.roles]:
            return await interaction.response.send_message(
                "Nie masz uprawnień do użycia tej komendy.",
                ephemeral=True
            )

        # 2) Parsowanie daty i godziny oraz timestamp
        try:
            dt_obj = datetime.strptime(f"{data} {godzina}", "%d/%m/%Y %H:%M")
            timestamp = int(dt_obj.replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            return await interaction.response.send_message(
                "Błąd formatu. Użyj `DD/MM/RRRR` i `HH:MM`.",
                ephemeral=True
            )

        # 3) Pobranie kanału sądowego
        court_channel = self.bot.get_channel(1364172834183708693)
        if not court_channel:
            return await interaction.response.send_message(
                "Nie znaleziono kanału sądowego.",
                ephemeral=True
            )

        # 4) Przygotowanie opisu embed (blok kodu)
        opis = (
            "```"
            "\n# TERMIN ROZPRAWY\n\n"
            f"### Data: {data} (<t:{timestamp}:R>)\n"
            f"### Godzina: {godzina}\n"
            f"### Sędzia prowadzący: {sedzia_prowadzacy}\n"
            f"### Sędzia pomocniczy: {sedzia_pomocniczy}\n"
            f"### Tryb Rozprawy: {tryb}\n"
            f"### Oskarżony: {oskarzeni}\n"
            "```"
        )

        # 5) Budowa embedu
        embed = discord.Embed(
            title="📅 TERMIN ROZPRAWY",
            description=opis,
            color=discord.Color.dark_red()
        )
        # <-- logo w embedzie jako thumbnail
        embed.set_thumbnail(url="attachment://sąd.png")
        embed.set_footer(text="Sąd Stanowy San Andreas")

        # 6) Załączenie pliku i wysłanie raz
        plik = discord.File("sąd.png", filename="sąd.png")
        await court_channel.send(
            content=oskarzeni,
            embed=embed,
            file=plik
        )

        # 7) Feedback dla wywołującego
        await interaction.response.send_message(
            f"Rozprawa ogłoszona na {court_channel.mention}.",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Rozprawa(bot))
