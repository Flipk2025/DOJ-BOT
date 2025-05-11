import discord
from discord.ext import commands
from discord import app_commands
import traceback
import asyncio

class RoleMenu(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # ID kanału, na który ma być wysłane osadzenie
        self.target_channel_id = 1234567890123456789  # Zmień na właściwe ID kanału

        # ID ról do zarządzania
        self.role_ids = {
            "ping_rozprawy": 1370830123523379210,  # ID dla roli @Ping Rozprawy
            "zmiany_prawne": 1371009145796562974,  # ID dla roli @Zmiany Prawne - zmień na właściwe ID
            "listy_goncze": 1371009146295685242,   # ID dla roli @Listy Gończe - zmień na właściwe ID
        }

        # Dodaj widok z persistent buttons (przyciski działające po restarcie bota)
        self.bot.add_view(RoleView(self.role_ids))

    @app_commands.command(name="role", description="Wysyła panel do zarządzania rolami")
    async def role_command(self, interaction: discord.Interaction):
        """Komenda wysyłająca menu z przyciskami do zarządzania rolami"""
        try:
            # Opóźnienie, aby uniknąć problemów z wyścigiem
            await asyncio.sleep(0.1)

            # Pobranie docelowego kanału
            target_channel = self.bot.get_channel(self.target_channel_id)
            if not target_channel:
                await interaction.response.send_message(
                    "Nie znaleziono kanału docelowego dla panelu ról. Skontaktuj się z administracją.",
                    ephemeral=True
                )
                return

            # Sprawdzenie, czy na kanale jest już osadzenie z przyciskami
            try:
                # Pobierz ostatnie 50 wiadomości z kanału
                messages = [message async for message in target_channel.history(limit=50)]

                # Sprawdź czy któraś wiadomość to nasze osadzenie z rolami
                panel_exists = False
                for message in messages:
                    # Sprawdź czy wiadomość ma osadzenia i czy tytuł osadzenia to "Wybierz Powiadomienia"
                    if message.embeds and message.embeds[0].title == "Wybierz Powiadomienia":
                        panel_exists = True
                        break

                if panel_exists:
                    await interaction.response.send_message(
                        f"Panel ról już istnieje na kanale {target_channel.mention}!",
                        ephemeral=True
                    )
                    return
            except Exception as e:
                print(f"❌ Błąd podczas sprawdzania istniejącego panelu: {e}")
                # Kontynuuj wykonanie, jeśli nie można sprawdzić historii

            # Tworzenie osadzenia (embed)
            embed = discord.Embed(
                title="Wybierz Powiadomienia",
                description="Kliknij przycisk, aby otrzymać lub usunąć rolę. \n"
                            "Wybierz kategorie powiadomień, które Cię interesują.",
                color=discord.Color.blue()
            )

            # Dodawanie pól do osadzenia dla każdej roli
            embed.add_field(
                name="🔔 Ping Rozprawy",
                value="Otrzymuj powiadomienia o nowych rozprawach sądowych",
                inline=False
            )
            embed.add_field(
                name="📜 Zmiany Prawne",
                value="Otrzymuj powiadomienia o zmianach w prawie",
                inline=False
            )
            embed.add_field(
                name="🚨 Listy Gończe",
                value="Otrzymuj powiadomienia o nowych listach gończych",
                inline=False
            )

            embed.set_footer(text="Kliknij przycisk ponownie, aby usunąć rolę")

            # Tworzenie przycisków
            view = RoleView(self.role_ids)

            # Informujemy użytkownika, że panel jest tworzony
            await interaction.response.send_message(
                f"Tworzę panel wyboru ról na kanale {target_channel.mention}...",
                ephemeral=True
            )

            # Wysyłanie osadzenia z przyciskami na docelowy kanał
            await target_channel.send(embed=embed, view=view)

            # Aktualizacja informacji dla użytkownika
            await interaction.edit_original_response(
                content=f"Panel wyboru ról został utworzony na kanale {target_channel.mention}!"
            )

        except Exception as e:
            error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            print(f"❌ Błąd podczas przetwarzania komendy /role:\n{error_msg}")

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

class RoleButton(discord.ui.Button):
    def __init__(self, role_id: int, label: str, emoji: str, style: discord.ButtonStyle):
        super().__init__(
            label=label,
            emoji=emoji,
            style=style,
            custom_id=f"role_button_{role_id}"  # Dodanie custom_id dla persistent views
        )
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        """Funkcja wywoływana po kliknięciu przycisku"""
        # Pobierz rolę z serwera
        role = interaction.guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message(
                f"Nie znaleziono roli o ID {self.role_id}. Skontaktuj się z administracją.",
                ephemeral=True
            )
            return

        try:
            # Sprawdź czy użytkownik ma już tę rolę
            if role in interaction.user.roles:
                # Użytkownik ma rolę - usuń ją
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    f"Usunięto rolę {role.mention}.",
                    ephemeral=True
                )
            else:
                # Użytkownik nie ma roli - dodaj ją
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    f"Dodano rolę {role.mention}.",
                    ephemeral=True
                )
        except discord.Forbidden:
            await interaction.response.send_message(
                "Bot nie ma uprawnień do zarządzania rolami. Skontaktuj się z administracją.",
                ephemeral=True
            )
        except Exception as e:
            error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            print(f"❌ Błąd podczas obsługi przycisku roli:\n{error_msg}")
            await interaction.response.send_message(
                "Wystąpił błąd podczas przetwarzania żądania.",
                ephemeral=True
            )

class RoleView(discord.ui.View):
    def __init__(self, role_ids: dict):
        super().__init__(timeout=None)  # Brak timeout - przyciski będą działać zawsze

        # Przycisk dla Ping Rozprawy
        self.add_item(RoleButton(
            role_id=role_ids["ping_rozprawy"],
            label="Ping Rozprawy",
            emoji="🔔",
            style=discord.ButtonStyle.primary
        ))

        # Przycisk dla Zmiany Prawne
        self.add_item(RoleButton(
            role_id=role_ids["zmiany_prawne"],
            label="Zmiany Prawne",
            emoji="📜",
            style=discord.ButtonStyle.success
        ))

        # Przycisk dla Listy Gończe
        self.add_item(RoleButton(
            role_id=role_ids["listy_goncze"],
            label="Listy Gończe",
            emoji="🚨",
            style=discord.ButtonStyle.danger
        ))

async def setup(bot: commands.Bot):
    await bot.add_cog(RoleMenu(bot))