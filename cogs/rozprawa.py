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
        allowed_role_id = 1334892405035372564
        if allowed_role_id not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("Nie masz uprawnień do użycia tej komendy.", ephemeral=True)
            return

        # Parsowanie daty i godziny
        try:
            dt_obj = datetime.strptime(f"{data} {godzina}", "%d/%m/%Y %H:%M")
            timestamp = int(dt_obj.replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            await interaction.response.send_message("Błąd formatu daty lub godziny. Użyj DD/MM/RRRR i HH:MM.", ephemeral=True)
            return

        # Pobieranie kanału
        target_channel = self.bot.get_channel(1370809492283064350)
        if target_channel is None:
            await interaction.response.send_message("Nie znaleziono kanału sądowego.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📅 TERMIN ROZPRAWY",
            color=discord.Color.dark_red()
        )
        embed.add_field(name="📌 Data", value=f"{data} (<t:{timestamp}:R>)", inline=False)
        embed.add_field(name="⏰ Godzina", value=godzina, inline=False)
        embed.add_field(name="⚖️ Sędzia prowadzący", value=sedzia_prowadzacy, inline=False)
        embed.add_field(name="🧑‍⚖️ Sędzia pomocniczy", value=sedzia_pomocniczy, inline=False)
        embed.add_field(name="📂 Tryb Rozprawy", value=tryb, inline=False)
        embed.add_field(name="👤 Oskarżony", value=oskarzeni, inline=False)
        embed.set_thumbnail(url="attachment://sąd.png")
        embed.set_footer(text="Sąd Stanowy San Andreas")

        embed.set_thumbnail(url="attachment://sąd.png")

        await target_channel.send(content="``` ```", embed=embed, file=file)
        await target_channel.send("``` ```")

        await interaction.response.send_message(
            f"Rozprawa ogłoszona na kanale {target_channel.mention}.",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Rozprawa(bot))
