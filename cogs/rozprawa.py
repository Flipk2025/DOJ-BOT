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
        # 1) sprawdzenie roli
        allowed = 1334892405035372564
        if allowed not in [r.id for r in interaction.user.roles]:
            return await interaction.response.send_message("Brak uprawnień.", ephemeral=True)

        # 2) parsowanie czasu
        try:
            dt = datetime.strptime(f"{data} {godzina}", "%d/%m/%Y %H:%M")
            ts = int(dt.replace(tzinfo=timezone.utc).timestamp())
        except:
            return await interaction.response.send_message("Nieprawidłowy format daty/godziny.", ephemeral=True)

        # 3) kanał sądowy
        chan = self.bot.get_channel(1364172834183708693)
        if not chan:
            return await interaction.response.send_message("Nie znalazłem kanału.", ephemeral=True)

        # 4) opis jako blok kodu
        desc = (
            "```"
            "\n# TERMIN ROZPRAWY\n\n"
            f"### Data: {data} (<t:{ts}:R>)\n"
            f"### Godzina: {godzina}\n"
            f"### Sędzia prowadzący: {sedzia_prowadzacy}\n"
            f"### Sędzia pomocniczy: {sedzia_pomocniczy}\n"
            f"### Tryb Rozprawy: {tryb}\n"
            f"### Oskarżony: {oskarzeni}\n"
            "```"
        )

        # 5) budujemy embed z logo obok tytułu
        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name="📅 TERMIN ROZPRAWY", icon_url="attachment://sąd.png")
        embed.description = desc
        embed.set_footer(text="Sąd Stanowy San Andreas")

        # 6) załączamy plik i wysyłamy JEDNYM send()
        plik = discord.File("sąd.png", filename="sąd.png")
        await chan.send(embed=embed, file=plik)

        # 7) potwierdzenie
        await interaction.response.send_message(f"Ogłoszono rozprawę na {chan.mention}.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Rozprawa(bot))
