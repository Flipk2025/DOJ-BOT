import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
import traceback

class Rozprawa(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
        # Natychmiast potwierdź otrzymanie interakcji, aby zapobiec jej wygaśnięciu
        # Używamy defer, aby Discord wiedział, że będziemy odpowiadać później
        await interaction.response.defer(ephemeral=True)
        print(f"🔔 /rozprawa callback - ID interakcji: {interaction.id}")
        
        try:
            allowed_role_id = 1334892405035372564
            if allowed_role_id not in [r.id for r in interaction.user.roles]:
                await interaction.followup.send("Nie masz uprawnień.", ephemeral=True)
                return
                
            try:
                dt_obj = datetime.strptime(f"{data} {godzina}", "%d/%m/%Y %H:%M")
                timestamp = int(dt_obj.replace(tzinfo=timezone.utc).timestamp())
            except ValueError:
                await interaction.followup.send("Błędny format daty/godziny.", ephemeral=True)
                return
            
            court_channel = self.bot.get_channel(1370809492283064350)
            if not court_channel:
                await interaction.followup.send("Brak kanału.", ephemeral=True)
                return
            
            # Przygotuj treść wiadomości
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
            
            # Wyślij wiadomość na kanał sądu
            await court_channel.send(content)
            
            # Odpowiedź dla użytkownika używając followup zamiast response
            await interaction.followup.send(
                f"Rozprawa ogłoszona na {court_channel.mention}.",
                ephemeral=True
            )
            
        except Exception as e:
            # Pełne logowanie błędu
            error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            print(f"❌ Błąd podczas przetwarzania komendy /rozprawa:\n{error_msg}")
            
            try:
                # Próba poinformowania użytkownika o błędzie
                await interaction.followup.send(
                    "Wystąpił błąd podczas przetwarzania komendy. Zgłoś to administracji.",
                    ephemeral=True
                )
            except:
                # Jeśli nawet to się nie powiedzie, po prostu zaloguj
                print("❌ Nie udało się wysłać komunikatu o błędzie do użytkownika")

async def setup(bot: commands.Bot):
    await bot.add_cog(Rozprawa(bot))