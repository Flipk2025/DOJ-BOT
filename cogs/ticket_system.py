import discord
from discord import app_commands
from discord.ext import commands

# Stałe role
VIEWER_ROLE_ID = 1334881150858035290  # dostęp tylko, bez pisania
WRITER_ROLE_ID = 1334881150925275194  # dostęp i pisanie

# Kanały i kategorie
TICKET_CHANNEL_ID = 1334881151935840325  # ID kanału z formularzem
TICKET_CATEGORY_ID = 1334881156574871582  # ID kategorii dla ticketów

# Konfiguracja typów ticketów
TICKET_TYPES = {
	"dane": {
		"label": "Zmiana Danych",
		"handler_roles": [1368498015702351954],  # pingowane
		"viewer_roles": [],                      # tylko dostęp
		"fields": [
			("Imię i nazwisko (IC)", "np. John Doe", True),
			("Numer SSN", "np. 54175", True),
			("Data urodzenia", "np. 20-02-1997", True),
			("Wnioskowene Imię i naziwsko", "np. John Smith", True),
			("Powód zmiany", "Opisz co jest powodem zmiany danych", True),
			("Inne uwagi", "POLE NIEOBOWIĄSKOWE", False)
		]
	},
	"pozew": {
		"label": "Złóż pozew do Sądu",
		"handler_roles": [1334888295154319522],
		"viewer_roles": [1334892405035372564],
		"fields": [
			("Imię i nazwisko (IC)", "np. John Doe", True),
			("Numer SSN", "np. 54175", True),
			("Data urodzenia", "np. 20-02-1997", True),
			("Link do pozwu", "MUSI BYĆ W GOOGLE DOCS", True)
		]
	},
	"prawo": {
		"label": "Pomoc Prawna",
		"handler_roles": [1334888295154319522],
		"viewer_roles": [],
		"fields": [
			("Imię i nazwisko (IC)", "np. John Doe", True),
			("Numer SSN", "np. 54175", True),
			("Data urodzenia", "np. 20-02-1997", True),
			("Opis sprawy", "Opisz sprawę", True)
		]
	},
	"prokuratura": {
		"label": "Sprawa do prokuratury",
		"handler_roles": [1359162624889065512],
		"viewer_roles": [1334891241002893312],
		"fields": [
			("Imię i nazwisko (IC)", "np. John Doe", True),
			("Numer SSN", "np. 54175", True),
			("Data urodzenia", "np. 20-02-1997", True),
			("Opis sprawy", "Opisz jaką masz sprawę do prokuratury", True),
			("Inne uwagi/Załączniki", "POLE NIEOBOWIĄSKOWE", False)
		]
	},
	"zarzad": {
		"label": "Prośba o rozmowę z zarządem",
		"handler_roles": [1342200180052590642],
		"viewer_roles": [1334881150925275194],
		"fields": [
			("Imię i nazwisko (IC)", "np. John Doe", True),
			("Cel rozmowy", "W jakiej sprawie chcesz rozmawiać?", True)
		]
	},
	"skarga": {
		"label": "Skarga na urzędnika/funkcjonariusza",
		"handler_roles": [1359162624889065512],
		"viewer_roles": [1334892405035372564, 1334891241002893312],
		"fields": [
			("Imię i nazwisko (IC)", "np. John Doe", True),
			("Numer SSN", "np. 54175", True),
			("Dane funkcjonariusza/urzędnika", "np. Samuel King", True),
			("Nr. odznaki/legitymaci i Jednoska/Wydział", "np. Samuel King LSPD, Mateo Smith FIB", True),
			("Powód skargi", "Opisz co jest powodem skargi", True),
			("Załączniki (Opcjonalnie)", "np. nagrania itp.", True)
		]
	},
	"inne": {
		"label": "Inna sprawa",
		"handler_roles": [1334881150828806188],
		"viewer_roles": [],
			"fields": [
				("Imię i nazwisko (IC)", "np. John Doe", True),
				("Opis", "Napisz w czym możemy pomóc", True)
			]
	}
}

class TicketSystem(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print("TicketSystem cog załadowany.")
		await self.send_ticket_message()

	async def send_ticket_message(self):
		channel = self.bot.get_channel(TICKET_CHANNEL_ID)
		if channel is None:
			return
		existing = [msg async for msg in channel.history(limit=10)]
		if any(msg.author == self.bot.user for msg in existing):
			return

		view = TicketDropdownView()
		embed = discord.Embed(
			title="🎫 Otwórz zgłoszenie",
			description="Wybierz temat, a następnie wypełnij formularz zgłoszenia.",
			color=discord.Color.blurple()
		)
		await channel.send(embed=embed, view=view)

class TicketDropdown(discord.ui.Select):
	def __init__(self):
		options = [discord.SelectOption(label=data["label"], value=key)
				   for key, data in TICKET_TYPES.items()]
		super().__init__(placeholder="Wybierz temat zgłoszenia...", min_values=1, max_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		topic_key = self.values[0]
		modal = TicketModal(topic_key)
		await interaction.response.send_modal(modal)

class TicketDropdownView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(TicketDropdown())

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(TICKET_CHANNEL_ID)
        if not channel:
            return
        # Pobierz wiadomości jako listę
        msgs = [msg async for msg in channel.history(limit=10)]
        if any(msg.author == self.bot.user for msg in msgs):
            return
        embed = discord.Embed(
            title="🎫 Otwórz zgłoszenie",
            description="Wybierz temat zgłoszenia", color=discord.Color.blurple()
        )
        options = [discord.SelectOption(label=topic) for topic in guild_ticket_config.keys()]
        view = discord.ui.View(timeout=None)
        view.add_item(discord.ui.Select(
            placeholder="Wybierz temat...",
            options=options,
            custom_id="ticket_topic_select",
            min_values=1, max_values=1
        ))
        await channel.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        custom_id = interaction.data.get('custom_id')
        if custom_id == 'ticket_topic_select':
            topic = interaction.data['values'][0]
            config = guild_ticket_config.get(topic)
            if not config:
                await interaction.response.send_message("Nieznany temat.", ephemeral=True)
                return
            class DynamicModal(discord.ui.Modal, title=f"Zgłoszenie: {topic}"):
                def __init__(self):
                    super().__init__()
                    for field in config['fields']:
                        self.add_item(discord.ui.TextInput(
                            custom_id=field['custom_id'], label=field['label'], style=field['style'], required=True
                        ))
            # zapisz temat
            self.bot._current_ticket_topic = topic
            await interaction.response.send_modal(DynamicModal())
            return

        # Obsługa przycisków
        if custom_id in ('take_ticket', 'close_ticket'):
            topic = getattr(self.bot, '_current_ticket_topic', None)
            config = guild_ticket_config.get(topic)
            if not config:
                await interaction.response.send_message("Brak tematu zgłoszenia.", ephemeral=True)
                return
            allowed_role = config['role_id']
            if allowed_role not in [r.id for r in interaction.user.roles]:
                await interaction.response.send_message("Brak uprawnień.", ephemeral=True)
                return
            channel = interaction.channel
            if custom_id == 'take_ticket':
                await channel.send(f"🔔 Zgłoszenie przejął: {interaction.user.mention}")
                await interaction.response.defer()
                return
            if custom_id == 'close_ticket':
                await channel.send("✅ Zgłoszenie zamknięte.")
                perms = channel.overwrites
                perms[channel.guild.default_role] = discord.PermissionOverwrite(view_channel=False)
                await channel.edit(overwrites=perms)
                await interaction.response.defer()
                return

    @commands.Cog.listener()
    async def on_modal_submit(self, interaction: discord.Interaction):
        topic = getattr(self.bot, '_current_ticket_topic', None)
        config = guild_ticket_config.get(topic)
        category = interaction.guild.get_channel(TICKET_CATEGORY_ID)
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        overwrites[interaction.guild.get_role(config['role_id'])] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        ticket_channel = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name}", category=category, overwrites=overwrites
        )
        desc = "\n".join(
            f"**{field['label']}:** {interaction.data['components'][i]['components'][0]['value']}"
            for i, field in enumerate(config['fields'])
        )
        embed = discord.Embed(title=f"Nowe zgłoszenie: {topic}", description=desc, color=discord.Color.green())
        view = discord.ui.View(timeout=None)
        view.add_item(discord.ui.Button(label="Przejmij Zgłoszenie", style=discord.ButtonStyle.green, custom_id="take_ticket"))
        view.add_item(discord.ui.Button(label="Zamknij Zgłoszenie", style=discord.ButtonStyle.red, custom_id="close_ticket"))
        await ticket_channel.send(content=f"{interaction.user.mention} <@&{config['role_id']}", embed=embed, view=view)
        await interaction.response.send_message(f"Utworzono kanał: {ticket_channel.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))