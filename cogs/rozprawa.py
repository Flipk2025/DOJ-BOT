import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone, timedelta
import traceback
import hashlib
import asyncio

class Rozprawa(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Słownik przechowujący informacje o ostatnio wysłanych wiadomościach
        # Klucz: hash treści, Wartość: (timestamp, channel_id)
        self.recent_messages = {}
        # Interwał czasu (w sekundach) w ramach którego uznajemy wiadomości za duplikaty
        self.duplicate_window = 5

    def _generate_content_hash(self, data, godzina, sedzia_prowadzacy, sedzia_pomocniczy, tryb, oskarzeni):
        """Generuje unikalny hash na podstawie parametrów rozprawy"""
        content = f"{data}-{godzina}-{sedzia_prowadzacy}-{sedzia_pomocniczy}-{tryb}-{oskarzeni}"
        return hashlib.md5(content.encode()).hexdigest()

    def _is_duplicate(self, content_hash, channel_id):
        """Sprawdza, czy ta sama wiadomość została niedawno wysłana na dany kanał"""
        now = datetime.now()
        if content_hash in self.recent_messages:
            timestamp, msg_channel_id = self.recent_messages[content_hash]
            if msg_channel_id == channel_id:
                # Sprawdź czy wiadomość została wysłana w ciągu ostatnich X sekund
                if (now - timestamp) < timedelta(seconds=self.duplicate_window):
                    return True
        
        # Zapisz informację o aktualnej wiadomości
        self.recent_messages[content_hash] = (now, channel_id)
        
        # Usuwanie starych wpisów (starszych niż minuta)
        to_remove = []
        for hash_key, (msg_time, _) in self.recent_messages.items():
            if (now - msg_time) > timedelta(minutes=1):
                to_remove.append(hash_key)
        
        for key in to_remove:
            del self.recent_messages[key]
            
        return False

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

        # Opóźnienie, aby uniknąć problemów z wyścigiem
        await asyncio.sleep(0.1)

        try:
            # Sprawdź uprawnienia
            allowed_role_id = 1334892405035372564
            if allowed_role_id not in [r.id for r in interaction.user.roles]:
                await interaction.response.send_message(
                    "Nie masz uprawnień.", ephemeral=True
                )
                return

            # Spróbuj sparsować datę i godzinę
            try:
                # Parsujemy datę jako lokalną (UTC+2), a następnie odejmujemy offset
                # by uzyskać prawidłowy czas UTC
                dt_obj = datetime.strptime(f"{data} {godzina}", "%d/%m/%Y %H:%M")

                # Tworzony jest czas lokalny, trzeba odjąć 2 godziny, by uzyskać poprawny UTC
                # dla Discord timestamp
                poland_offset = timedelta(hours=2)  # UTC+2 dla czasu polskiego
                utc_time = dt_obj - poland_offset

                # Konwersja na timestamp
                timestamp = int(utc_time.replace(tzinfo=timezone.utc).timestamp())
            except ValueError:
                await interaction.response.send_message(
                    "Błędny format daty/godziny.", ephemeral=True
                )
                return

            # Sprawdź czy kanał sądu istnieje
            court_channel_id = 1370809492283064350
            court_channel = self.bot.get_channel(court_channel_id)
            if not court_channel:
                await interaction.response.send_message(
                    "Brak kanału.", ephemeral=True
                )
                return

            # Generuj hash dla tej wiadomości
            content_hash = self._generate_content_hash(
                data, godzina, sedzia_prowadzacy, sedzia_pomocniczy, tryb, oskarzeni
            )

            # Sprawdź czy to nie duplikat
            if self._is_duplicate(content_hash, court_channel_id):
                print(f"⚠️ Wykryto duplikat wiadomości [hash: {content_hash}] - ignoruję")
                await interaction.response.send_message(
                    f"Rozprawa już została ogłoszona na {court_channel.mention}.",
                    ephemeral=True
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
            try:
                await interaction.response.send_message(
                    f"Rozprawa ogłoszona na {court_channel.mention}.",
                    ephemeral=True
                )
            except discord.errors.InteractionResponded:
                # Jeśli interakcja już została obsłużona, spróbuj użyć followup
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
                try:
                    await interaction.response.send_message(
                        "Wystąpił błąd podczas przetwarzania komendy. Zgłoś to administracji.",
                        ephemeral=True
                    )
                except discord.errors.InteractionResponded:
                    await interaction.followup.send(
                        "Wystąpił błąd podczas przetwarzania komendy. Zgłoś to administracji.",
                        ephemeral=True
                    )
            except:
                # Jeśli nawet to się nie powiedzie, po prostu zaloguj
                print("❌ Nie udało się wysłać komunikatu o błędzie do użytkownika")

async def setup(bot: commands.Bot):
    await bot.add_cog(Rozprawa(bot))