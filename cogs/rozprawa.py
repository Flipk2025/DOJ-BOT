import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
import traceback

class Rozprawa(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Słownik przechowujący informacje o kanałach, na które wysłano wiadomości
        self.processed_interactions = {}

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
        interaction_id = interaction.id
        print(f"🔔 /rozprawa callback - ID interakcji: {interaction_id}")

        # Sprawdź, czy już przetwarzamy tę interakcję
        if interaction_id in self.processed_interactions:
            print(f"⚠️ Interakcja {interaction_id} jest już przetwarzana - ignoruję")
            return

        # Oznacz interakcję jako przetwarzaną
        self.processed_interactions[interaction_id] = True

        # Czyść starsze wpisy, aby uniknąć wycieków pamięci
        if len(self.processed_interactions) > 100:
            old_keys = list(self.processed_interactions.keys())[:-50]
            for key in old_keys:
                del self.processed_interactions[key]

        try:
            # Sprawdź uprawnienia
            allowed_role_id = 1334892405035372564
            if allowed_role_id not in [r.id for r in interaction.user.roles]:
                # Użyj response.send_message tylko raz, bez wcześniejszego defer
                await interaction.response.send_message(
                    "Nie masz uprawnień.", ephemeral=True
                )
                return

            # Spróbuj sparsować datę i godzinę
            try:
                dt_obj = datetime.strptime(f"{data} {godzina}", "%d/%m/%Y %H:%M")
                timestamp = int(dt_obj.replace(tzinfo=timezone.utc).timestamp())
            except ValueError:
                await interaction.response.send_message(
                    "Błędny format daty/godziny.", ephemeral=True
                )
                return

            # Sprawdź czy kanał sądu istnieje
            court_channel = self.bot.get_channel(1370809492283064350)
            if not court_channel:
                await interaction.response.send_message(
                    "Brak kanału.", ephemeral=True
                )
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

            # Odpowiedź dla użytkownika
            await interaction.response.send_message(
                f"Rozprawa ogłoszona na {court_channel.mention}.",
                ephemeral=True
            )

        except discord.errors.HTTPException as e:
            # Specjalna obsługa dla błędu "już potwierdzonej interakcji"
            if e.code == 40060:  # Interaction has already been acknowledged
                print(f"⚠️ Interakcja {interaction_id} została już potwierdzona")
                try:
                    # Spróbuj użyć followup zamiast response
                    await interaction.followup.send(
                        f"Rozprawa ogłoszona na {court_channel.mention}.",
                        ephemeral=True
                    )
                except Exception as follow_error:
                    print(f"❌ Błąd przy próbie followup: {follow_error}")
            else:
                print(f"❌ Błąd HTTP: {e}")
                
        except Exception as e:
            # Ogólna obsługa błędów
            error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            print(f"❌ Błąd podczas przetwarzania komendy /rozprawa:\n{error_msg}")
            
            try:
                # Próba poinformowania użytkownika o błędzie
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "Wystąpił błąd podczas przetwarzania komendy. Zgłoś to administracji.",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "Wystąpił błąd podczas przetwarzania komendy. Zgłoś to administracji.",
                        ephemeral=True
                    )
            except:
                # Jeśli nawet to się nie powiedzie, po prostu zaloguj
                print("❌ Nie udało się wysłać komunikatu o błędzie do użytkownika")

async def setup(bot: commands.Bot):
    await bot.add_cog(Rozprawa(bot))