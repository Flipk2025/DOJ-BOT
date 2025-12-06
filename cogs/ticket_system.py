import discord
from discord import app_commands
from discord.ext import commands
import re

# Stałe role
VIEWER_ROLE_ID = 1334881150858035290  # dostęp tylko, bez pisania
WRITER_ROLE_ID = 1334881150925275194  # dostęp i pisanie

# Kanały i kategorie
TICKET_CHANNEL_ID = 1334881151935840325  # ID kanału z formularzem
TICKET_CATEGORY_ID = 1334881156574871582  # ID kategorii dla ticketów
# ID kategorii, do której będą przenoszone zamknięte tickety
# --> WPISZ TUTAJ ID KATEGORII, np. CLOSED_TICKET_CATEGORY_ID = 133488999999999999
CLOSED_TICKET_CATEGORY_ID = 1446958394341593282

# Konfiguracja typów ticketów
TICKET_TYPES = {
	"ranga": {
		"label": "Wniosek o przyznanie rangi",
		"handler_roles": [1342200180052590642],  # pingowane
		"viewer_roles": [1334881150828806188], # tylko dostęp
		"fields": [
			("Imię i nazwisko (IC)", "np. John Doe", True),
			("Data urodzenia", "np. 20-02-1997", True),
			("Ranga do dodania", "np. Właściciel Firmy, LSPD, USMS, Adwokat, DOJ", True),
			("Numer odznaki/legitymacni (Jeśli dotyczy)", "Napisz swój nr. odznaki/legitymacji jeśli masz", False),
			("Inne uwagi", "POLE NIEOBOWIĄSKOWE", False)
		]
	},
	"dane": {
		"label": "Zmiana Danych",
		"handler_roles": [1368498015702351954],  # pingowane
		"viewer_roles": [],                      # tylko dostęp
		"fields": [
			("Imię i nazwisko (IC)", "np. John Doe", True),
			("Data urodzenia", "np. 20-02-1997", True),
			("Wnioskowene Imię i naziwsko", "np. John Smith", True),
			("Powód zmiany", "Opisz co jest powodem zmiany danych", True),
			("Inne uwagi", "POLE NIEOBOWIĄSKOWE", False)
		]
	},
	"sad": {
		"label": "Sprawa do Sądu",
		"handler_roles": [1334888295154319522],
		"viewer_roles": [1334892405035372564],
		"fields": [
			("Imię i nazwisko (IC)", "np. John Doe", True),
			("Data urodzenia", "np. 20-02-1997", True),
			("Inne uwagi/Załączniki", "POLE NIEOBOWIĄSKOWE", False),
			("Inne uwagi", "POLE NIEOBOWIĄSKOWE", False),
			
		]
	},
	"prawo": {
		"label": "Pomoc Prawna",
		"handler_roles": [1334881150925275187],
		"viewer_roles": [],
		"fields": [
			("Imię i nazwisko (IC)", "np. John Doe", True),
			("Data urodzenia", "np. 20-02-1997", True),
			("Opis sprawy", "Opisz sprawę", True),
			("Inne uwagi", "POLE NIEOBOWIĄSKOWE", False)
		]
	},
	"prokuratura": {
		"label": "Sprawa do prokuratury",
		"handler_roles": [1359162624889065512],
		"viewer_roles": [1334891241002893312],
		"fields": [
			("Imię i nazwisko (IC)", "np. John Doe", True),
			("Data urodzenia", "np. 20-02-1997", True),
			("Opis sprawy", "Opisz jaką masz sprawę do prokuratury", True),
			("Inne uwagi/Załączniki", "POLE NIEOBOWIĄSKOWE", False)
		]
	},
	"zarzad": {
		"label": "Prośba o rozmowę z zarządem",
		"handler_roles": [1342200180052590642],
		"viewer_roles": [1342200179478233159, 1334881150828806188],
		"fields": [
			("Imię i nazwisko (IC)", "np. John Doe", True),
			("Data urodzenia", "np. 20-02-1997", True),
			("Cel rozmowy", "W jakiej sprawie chcesz rozmawiać?", True)
		]
	},
	"skarga": {
		"label": "Skarga na urzędnika/funkcjonariusza",
		"handler_roles": [1359162624889065512],
		"viewer_roles": [1334891241002893312, 1334892405035372564, 1342200179478233159],
		"fields": [
			("Imię i nazwisko (IC)", "np. John Doe", True),
			("Numer SSN", "np. 54175", True),
			("Dane funkcjonariusza/urzędnika", "np. Samuel King", True),
			("Nr. odznaki/legitymaci i Jednoska/Wydział", "np. 145 - LSPD, 14 - FIB, 31 - DOJ", True),
			("Powód skargi", "Opisz co jest powodem skargi", True),
			("Załączniki (Opcjonalnie)", "np. nagrania itp.", True)
		]
	},
	"zatarcie": {
		"label": "Wniosek o zatarcie Wyroku/Mandatu",
		"handler_roles": [1334888295154319522],
		"viewer_roles": [1334892405035372564, 1334895667189125222, 1359162624163578127, 1359162626793279672],
		"fields": [
			("Imię i nazwisko (IC)", "np. John Doe", True),
			("Numer SSN", "np. 54175", True),
			("Powód wniosku:", "np. Dostanie się do pracy.", True),
			("Dokładne zarzuty/wykroczenia:", "Napisz co chcesz by zostało zatarte.", True),
			("Załączniki (Opcjonalnie)", "np. nagrania itp.", True)
		]
	},
	"inne": {
		"label": "Inna sprawa",
		"handler_roles": [1334881150828806188],
		"viewer_roles": [1342200180052590642, 1342200179478233159],
			"fields": [
				("Imię i nazwisko (IC)", "np. John Doe", True),
				("Opis", "Napisz w czym możemy pomóc", True)
			]
	}
}

# Helper: parsowanie claimed_by z topic
CLAIMED_RE = re.compile(r"claimed_by:(\d+)")

class TicketSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
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

class TicketModal(discord.ui.Modal):
    def __init__(self, topic_key):
        title = f"{TICKET_TYPES[topic_key]['label'][:45]}"
        super().__init__(title=title)
        self.topic_key = topic_key
        self.inputs = []
        for i, (label, placeholder, required) in enumerate(TICKET_TYPES[topic_key]["fields"]):
            if i >= 5:
                break
            inp = discord.ui.TextInput(label=label, placeholder=placeholder, required=required)
            # store the label text to avoid accessing deprecated attribute later
            setattr(inp, "_label_text", label)
            self.inputs.append(inp)
            self.add_item(inp)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        cfg = TICKET_TYPES[self.topic_key]

        # Budowanie overwrite permissions
        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        # Zawsze dodaj role VIEWER_ROLE_ID (tylko czytanie) i WRITER_ROLE_ID
        if guild.get_role(VIEWER_ROLE_ID):
            overwrites[guild.get_role(VIEWER_ROLE_ID)] = discord.PermissionOverwrite(view_channel=True, send_messages=False)
        if guild.get_role(WRITER_ROLE_ID):
            overwrites[guild.get_role(WRITER_ROLE_ID)] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        # Role handler:
        for role_id in cfg['handler_roles']:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        # Role viewer:
        for role_id in cfg['viewer_roles']:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=False)
        # Użytkownik:
        overwrites[interaction.user] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        # Tworzenie kanału ticket
        channel_name = f"ticket-{interaction.user.name}".replace(" ", "-").lower()
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"{cfg['label']} zgłoszenie od {interaction.user.name} | claimed_by:{interaction.user.id}"
        )

        # Przygotowanie embed i view kontrolnego
        # Use stored label text to avoid deprecated access to TextInput.label
        embed_desc = "\n".join(f"**{getattr(inp, '_label_text', getattr(inp, 'label', 'Pole'))}:** {inp.value}" for inp in self.inputs)
        view = TicketControlView(cfg['handler_roles'] + [WRITER_ROLE_ID])
        embed = discord.Embed(
            title="📩 Nowe zgłoszenie",
            description=embed_desc,
            color=discord.Color.green()
        )
        mentions = f"{interaction.user.mention} | " + " ".join(f"<@&{rid}>" for rid in cfg['handler_roles'])
        await ticket_channel.send(content=mentions, embed=embed, view=view)
        await interaction.response.send_message(f"✅ Zgłoszenie utworzone: {ticket_channel.mention}", ephemeral=True)

class TicketControlView(discord.ui.View):
    def __init__(self, allowed_roles):
        super().__init__(timeout=None)
        self.allowed_roles = allowed_roles  # list of role IDs that may manage ticket

    # helper: sprawdź czy user ma prawo zarządzać ticketem
    async def _has_permission(self, interaction: discord.Interaction) -> bool:
        # check writer role
        if any(role.id == WRITER_ROLE_ID for role in interaction.user.roles):
            return True
        # check handler roles
        if any(role.id in self.allowed_roles for role in interaction.user.roles):
            return True
        # check claimed_by in topic
        topic = interaction.channel.topic or ""
        m = CLAIMED_RE.search(topic)
        if m:
            try:
                claimer_id = int(m.group(1))
                if interaction.user.id == claimer_id:
                    return True
            except:
                pass
        return False

    async def _set_channel_claim(self, channel: discord.TextChannel, user: discord.Member):
        topic = channel.topic or ""
        # remove old claimed_by if present
        topic = re.sub(r"claimed_by:\d+", "", topic).strip()
        if topic and not topic.endswith("|"):
            topic = topic + " | "
        topic = f"{topic}claimed_by:{user.id}"
        await channel.edit(topic=topic)

        # also ensure user has send permission explicitly
        await channel.set_permissions(user, view_channel=True, send_messages=True)

    @discord.ui.button(label="Przejmij zgłoszenie", style=discord.ButtonStyle.success)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Allow if handler/writer OR if no claimed_by yet and user has handler/writer role
        if not await self._has_permission(interaction):
            await interaction.response.send_message("Brak uprawnień do przejęcia zgłoszenia.", ephemeral=True)
            return

        # Set claimed_by in topic and adjust permissions
        await self._set_channel_claim(interaction.channel, interaction.user)

        # Update button display
        button.disabled = True
        # mark visually who claimed it
        button.label = f"Przejęte przez {interaction.user.display_name}"
        try:
            button.style = discord.ButtonStyle.secondary
        except Exception:
            pass
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(f"Zgłoszenie przejął: {interaction.user.mention}")

    @discord.ui.button(label="Zamknij zgłoszenie", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._has_permission(interaction):
            await interaction.response.send_message("Brak uprawnień.", ephemeral=True)
            return

        channel: discord.TextChannel = interaction.channel  # type: ignore
        guild = channel.guild

        # Build closed overwrites: only VIEWER_ROLE_ID, WRITER_ROLE_ID and handler roles can view (but not write)
        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}

        # allow viewer role to view but not send
        viewer_role = guild.get_role(VIEWER_ROLE_ID)
        if viewer_role:
            overwrites[viewer_role] = discord.PermissionOverwrite(view_channel=True, send_messages=False)
        # allow writer role to view but not send (if you want writer to still write after close, change send_messages=True)
        writer_role = guild.get_role(WRITER_ROLE_ID)
        if writer_role:
            overwrites[writer_role] = discord.PermissionOverwrite(view_channel=True, send_messages=False)

        # handler roles: allow view only
        for rid in self.allowed_roles:
            role = guild.get_role(rid)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=False)

        # clear individual user perms and make all final edits in a single request to avoid rate-limits
        # annotate topic as closed
        topic = channel.topic or ""
        topic = re.sub(r"claimed_by:\d+", "", topic).strip()
        topic = (topic + " | " if topic and not topic.endswith("|") else topic)
        topic = f"{topic}status:closed"

        # rename and move channel to closed category (if configured)
        original_name = channel.name
        if not original_name.startswith("closed-"):
            new_name = f"closed-{original_name}"
        else:
            new_name = original_name

        closed_category = None
        if CLOSED_TICKET_CATEGORY_ID and CLOSED_TICKET_CATEGORY_ID != 0:
            closed_category = guild.get_channel(CLOSED_TICKET_CATEGORY_ID)

        try:
            await channel.edit(overwrites=overwrites, topic=topic, name=new_name, category=closed_category)
        except Exception as e:
            # jeśli edycja nazwy/przeniesienie się nie powiodło, logujemy błąd ale nie przerywamy
            print(f"Błąd przy przenoszeniu/zamykaniu kanału: {e}")

        # disable buttons
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        await interaction.response.edit_message(view=self)
        await channel.send("🔒 Zgłoszenie zamknięte — kanał przemianowany i przeniesiony (jeśli podano kategorię).")

    # Slash commands are added in the Cog (below) — tutaj tylko przyciski

class TicketManagementCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def is_ticket_channel(self, channel: discord.abc.GuildChannel) -> bool:
        return isinstance(channel, discord.TextChannel) and channel.name.startswith("ticket-")

    async def _get_claimed_id(self, channel: discord.TextChannel):
        topic = channel.topic or ""
        m = CLAIMED_RE.search(topic)
        if m:
            try:
                return int(m.group(1))
            except:
                return None
        return None

    async def _has_manage_permission(self, user: discord.Member, channel: discord.TextChannel):
        # writer role
        if any(r.id == WRITER_ROLE_ID for r in user.roles):
            return True
        # handler roles: check roles allowed from topic? Simpler: check if any role in TICKET_TYPES handler_roles
        user_role_ids = {r.id for r in user.roles}
        handler_role_ids = set()
        for cfg in TICKET_TYPES.values():
            handler_role_ids.update(cfg.get("handler_roles", []))
        if user_role_ids & handler_role_ids:
            return True
        # claimed
        claimed = await self._get_claimed_id(channel)
        if claimed and user.id == claimed:
            return True
        return False

    @app_commands.command(name="przekaz", description="Przekaż ticket innej osobie")
    @app_commands.describe(member="Osoba, której chcesz przekazać ticket")
    async def przekaz(self, interaction: discord.Interaction, member: discord.Member):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel) or not self.is_ticket_channel(channel):
            await interaction.response.send_message("To polecenie można użyć tylko w kanale ticket.", ephemeral=True)
            return
        if not await self._has_manage_permission(interaction.user, channel):
            await interaction.response.send_message("Brak uprawnień do przekazania ticketu.", ephemeral=True)
            return

        # set new claimer, update permission
        await channel.set_permissions(member, view_channel=True, send_messages=True)
        # remove send rights from previous claimed user (if any)
        old_claim = await self._get_claimed_id(channel)
        if old_claim and old_claim != member.id:
            old_member = channel.guild.get_member(old_claim)
            if old_member:
                await channel.set_permissions(old_member, view_channel=True, send_messages=False)

        # update topic
        topic = channel.topic or ""
        topic = re.sub(r"claimed_by:\d+", "", topic).strip()
        if topic and not topic.endswith("|"):
            topic = topic + " | "
        topic = f"{topic}claimed_by:{member.id}"
        await channel.edit(topic=topic)

        await interaction.response.send_message(f"✅ Ticket przekazany do {member.mention}.", ephemeral=True)

    @app_commands.command(name="dodaj-os", description="Dodaj osobę do ticketu (dostęp/wysłanie wiadomości)")
    @app_commands.describe(member="Osoba do dodania")
    async def dodaj_os(self, interaction: discord.Interaction, member: discord.Member):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel) or not self.is_ticket_channel(channel):
            await interaction.response.send_message("To polecenie można użyć tylko w kanale ticket.", ephemeral=True)
            return
        if not await self._has_manage_permission(interaction.user, channel):
            await interaction.response.send_message("Brak uprawnień do dodania osoby.", ephemeral=True)
            return

        await channel.set_permissions(member, view_channel=True, send_messages=True)
        await interaction.response.send_message(f"✅ {member.mention} otrzymał dostęp do ticketu.", ephemeral=True)

    @app_commands.command(name="usun-os", description="Usuń osobę z ticketu (cofnij dostęp)")
    @app_commands.describe(member="Osoba do usunięcia")
    async def usun_os(self, interaction: discord.Interaction, member: discord.Member):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel) or not self.is_ticket_channel(channel):
            await interaction.response.send_message("To polecenie można użyć tylko w kanale ticket.", ephemeral=True)
            return
        if not await self._has_manage_permission(interaction.user, channel):
            await interaction.response.send_message("Brak uprawnień do usunięcia osoby.", ephemeral=True)
            return

        await channel.set_permissions(member, overwrite=None)  # usuń indywidualne overwrite
        await interaction.response.send_message(f"✅ Dostęp {member.mention} został cofnięty.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(TicketSystem(bot))
    # rejestrujemy cog z komendami zarządzania ticketami
    mgmt = TicketManagementCog(bot)
    await bot.add_cog(mgmt)
    # opcjonalnie: zarejestruj komendy globalnie / na serwerze — discord.py automatycznie zarejestruje app_commands z cogów
