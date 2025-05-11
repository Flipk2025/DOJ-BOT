import discord
from discord.ext import commands
import traceback
import asyncio

class RoleMenuCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # ID ról do zarządzania
        self.role_ids = {
            "ping_rozprawy": 1370830123523379210,  # ID dla roli @Ping Rozprawy
            "zmiany_prawne": 1371009145796562974,  # ID dla roli @Zmiany Prawne
            "listy_goncze": 1371009146295685242,   # ID dla roli @Listy Gończe
        }

        # ID kanału, na który ma być wysłane menu ról
        self.role_menu_channel_id = 1371007466535649320
        
        # Dodaj widok z persistent buttons (przyciski działające po restarcie bota)
        self.bot.add_view(RoleView(self.role_ids))
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ Moduł {self.__class__.__name__} jest gotowy!")
        
        # Poczekaj 5 sekund, aby bot miał czas na załadowanie wszystkich danych
        await asyncio.sleep(5)
        
        # Automatycznie wysyłaj menu ról przy starcie
        await self.send_role_menu()
    
    async def send_role_menu(self):
        """Funkcja wysyłająca menu z przyciskami do zarządzania rolami"""
        try:
            # Pobierz docelowy kanał
            target_channel = self.bot.get_channel(self.role_menu_channel_id)
            if not target_channel:
                print(f"❌ Nie mogę znaleźć kanału docelowego (ID: {self.role_menu_channel_id}).")
                return
            
            # Sprawdź, czy menu już istnieje na kanale
            # Przeszukaj ostatnie 100 wiadomości na kanale
            menu_exists = False
            async for message in target_channel.history(limit=100):
                # Jeśli wiadomość jest od bota i zawiera osadzenie z tytułem "Wybierz Powiadomienia"
                if message.author.id == self.bot.user.id and message.embeds:
                    if message.embeds[0].title == "Wybierz Powiadomienia":
                        print(f"✅ Menu ról już istnieje na kanale {target_channel.name}.")
                        menu_exists = True
                        break
            
            # Jeśli menu już istnieje, nie wysyłaj nowego
            if menu_exists:
                return
                
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
            
            # Wysyłanie osadzenia z przyciskami na określony kanał
            await target_channel.send(embed=embed, view=view)
            print(f"✅ Menu ról zostało utworzone na kanale {target_channel.name}.")
            
        except Exception as e:
            error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            print(f"❌ Błąd podczas wysyłania menu ról:\n{error_msg}")

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
    await bot.add_cog(RoleMenuCog(bot))