import discord
from discord.ext import commands
from discord import app_commands, ui
import os
from flask import Flask
import threading

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    # Render.com utilise la variable d'environnement PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

# ----------------------------
# IDS RÔLES BLOODS
# ----------------------------
STAFF_ROLE_IDS = [
    1419411125090517124,  # Og
    1419418542171885783,  # Chef
    1454556993137410184,  # Co chef
    1462083431814139967,  # Vvi
    1438280877221085307,  # Ags
    1419415301694558308   # Staff Elite
]

ROOKIE_ROLE_ID = 1419421022469361675
OFFICIEL_ROLE_ID = 1430669476809937027

# ----------------------------
# CHECKS
# ----------------------------
def is_staff(interaction: discord.Interaction) -> bool:
    if not isinstance(interaction.user, discord.Member): return False
    return any(role.id in STAFF_ROLE_IDS for role in interaction.user.roles)

def is_rookie(interaction: discord.Interaction) -> bool:
    if not isinstance(interaction.user, discord.Member): return False
    return any(role.id == ROOKIE_ROLE_ID for role in interaction.user.roles)

# ----------------------------
# ON READY
# ----------------------------
@bot.event
async def on_ready():
    print(f"🔴 BLOODS PANEL - Connecté en tant que {bot.user}")
    await bot.tree.sync()

# ----------------------------
# COLORS BLOODS GRADIENT
# ----------------------------
BLOODS_COLORS = [
    discord.Color.red(),
    discord.Color.dark_red(),
    discord.Color.from_rgb(139,0,0),     # Dark Blood
    discord.Color.from_rgb(255,69,0),    # Orange Red
    discord.Color.from_rgb(178,34,34),   # Fire Brick
]

def get_color(index: int) -> discord.Color:
    return BLOODS_COLORS[index % len(BLOODS_COLORS)]

# ----------------------------
# PANEL VOCAL BLOODS
# ----------------------------
class BloodsVoicePanel(ui.View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel = channel

    @ui.button(label="🔇 Mute All", style=discord.ButtonStyle.danger)
    async def mute_all(self, interaction: discord.Interaction, button: ui.Button):
        if not is_staff(interaction):
            await interaction.response.send_message("❌ Commande réservée aux OG/BLOODS.", ephemeral=True)
            return
        await interaction.response.defer()
        for member in self.channel.members:
            if member.bot or any(role.id in STAFF_ROLE_IDS for role in member.roles):
                continue
            try:
                await member.edit(mute=True)
            except discord.HTTPException:
                pass
        await interaction.followup.send(f"🔴 Tous les membres ont été mute (staff immunisé).")

    @ui.button(label="🔊 Unmute All", style=discord.ButtonStyle.success)
    async def unmute_all(self, interaction: discord.Interaction, button: ui.Button):
        if not is_staff(interaction):
            await interaction.response.send_message("❌ Commande réservée aux OG/BLOODS.", ephemeral=True)
            return
        await interaction.response.defer()
        for member in self.channel.members:
            if member.bot or any(role.id in STAFF_ROLE_IDS for role in member.roles):
                continue
            try:
                await member.edit(mute=False)
            except discord.HTTPException:
                pass
        await interaction.followup.send("🔴 Tous les membres ont été unmute (staff immunisé).")

# ----------------------------
# /panelvocals
# ----------------------------
@bot.tree.command(name="panelvocals", description="Ouvre le panneau vocal BLOODS 🔴")
async def panelvocals(interaction: discord.Interaction):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Tu n’as pas le droit.", ephemeral=True)
        return
    if not getattr(interaction.user, 'voice', None):
        await interaction.response.send_message("❌ Tu dois être dans un vocal.", ephemeral=True)
        return
    view = BloodsVoicePanel(interaction.user.voice.channel)
    color = get_color(0)
    embed = discord.Embed(
        title="🔴 BLOODS VOICE PANEL",
        description="Boutons interactifs pour mute/unmute tous les membres sauf staff. 🩸",
        color=color
    )
    embed.set_footer(text="💀 Respecte les OG, reste rouge.")
    await interaction.response.send_message(embed=embed, view=view)

# ----------------------------
# /roles BLOODS
# ----------------------------
@bot.tree.command(name="roles", description="Affiche tous les rôles du serveur BLOODS")
async def roles(interaction: discord.Interaction):
    if not is_rookie(interaction):
        await interaction.response.send_message("❌ Rookie only.", ephemeral=True)
        return
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message("❌ Cette commande doit être exécutée sur un serveur.", ephemeral=True)
        return
    roles = sorted([r for r in guild.roles if r.name != "@everyone"], key=lambda r: r.position, reverse=True)
    lines = []
    for idx, r in enumerate(roles):
        color_hex = f"{r.color.value:06X}"
        lines.append(f"🔴 {r.name} | ID: {r.id} | Couleur: #{color_hex}")
    embed_color = get_color(1)
    embed = discord.Embed(title=f"🎭 Rôles BLOODS sur {guild.name}", description="\n".join(lines), color=embed_color)
    embed.set_footer(text=f"Total : {len(roles)} rôle(s) 🩸")
    await interaction.response.send_message(embed=embed)

# ----------------------------
# /listofficiel BLOODS
# ----------------------------
@bot.tree.command(name="listofficiel", description="Liste tous les membres OFFICIEL 🔴")
async def listofficiel(interaction: discord.Interaction):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Commande réservée aux OG/BLOODS.", ephemeral=True)
        return
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message("❌ Cette commande doit être exécutée sur un serveur.", ephemeral=True)
        return
    role = guild.get_role(OFFICIEL_ROLE_ID)
    if not role:
        await interaction.response.send_message("❌ Rôle introuvable.", ephemeral=True)
        return
    members = [m.mention for m in role.members]
    embed_color = get_color(2)
    embed = discord.Embed(title="📋 Membres OFFICIEL 🔴", description="\n".join(members) if members else "Aucun", color=embed_color)
    embed.set_footer(text=f"Total : {len(members)} 🩸")
    await interaction.response.send_message(embed=embed)

# ----------------------------
# /informations BLOODS
# ----------------------------
@bot.tree.command(name="informations", description="Infos d’un membre BLOODS 🔴")
@app_commands.describe(membre="Choisis le membre")
async def informations(interaction: discord.Interaction, membre: discord.Member):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Commande réservée aux OG/BLOODS.", ephemeral=True)
        return
    embed_color = get_color(3)
    embed = discord.Embed(title=f"ℹ️ {membre}", color=embed_color)
    embed.add_field(name="Nom complet", value=str(membre), inline=False)
    embed.add_field(name="ID", value=str(membre.id), inline=False)
    joined = membre.joined_at.strftime("%d/%m/%Y %H:%M:%S") if getattr(membre, 'joined_at', None) else "Inconnu"
    embed.add_field(name="Date de join", value=joined, inline=False)
    embed.add_field(name="Roles", value=", ".join([r.mention for r in getattr(membre, 'roles', []) if r.name != "@everyone"]), inline=False)
    embed.set_footer(text="💀 Toujours respecter les OG 🩸")
    await interaction.response.send_message(embed=embed)




# ---------------- COMMANDES ---------------- #

# WARN
@bot.tree.command(name="warn", description="Warn un membre")
@app_commands.describe(member="La personne à warn", reason="Raison du warn")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "Non spécifiée"):
    if not any(role.id in staff_roles for role in interaction.user.roles):
        await interaction.response.send_message("❌ Tu n'as pas la permission.", ephemeral=True)
        return

    warns[member.id] = warns.get(member.id, 0) + 1
    nb_warns = warns[member.id]

    embed = discord.Embed(
        title="⚠️ Nouveau Warn",
        description=f"{member.mention} a été warn par {interaction.user.mention}\nRaison: {reason}",
        color=0xFF0000
    )
    embed.add_field(name="Points rouges", value="🔴" * nb_warns)
    embed.set_footer(text=f"Total warns: {nb_warns}")
    log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
    await log_channel.send(embed=embed)

    try:
        await member.send(f"Tu as reçu un warn dans {interaction.guild.name} pour : {reason}\nPoints rouges: {'🔴'*nb_warns}")
    except:
        pass

    if nb_warns >= 3:
        mention_roles = " ".join([f"<@&{r}>" for r in ROLES_ALERT])
        await log_channel.send(f"⚠️ {mention_roles} {member.mention} a 3 warns ou plus !")

    await interaction.response.send_message(f"✅ {member.display_name} a été warn. Points rouges: {'🔴'*nb_warns}", ephemeral=True)


# UNWARN
@bot.tree.command(name="unwarn", description="Enlève un warn à un membre")
@app_commands.describe(member="La personne à unwarn")
async def unwarn(interaction: discord.Interaction, member: discord.Member):
    if not any(role.id in staff_roles for role in interaction.user.roles):
        await interaction.response.send_message("❌ Tu n'as pas la permission.", ephemeral=True)
        return

    if member.id not in warns or warns[member.id] == 0:
        await interaction.response.send_message(f"❌ {member.display_name} n'a aucun warn.", ephemeral=True)
        return

    warns[member.id] -= 1
    nb_warns = warns[member.id]
    if nb_warns == 0:
        del warns[member.id]

    embed = discord.Embed(
        title="✅ Warn retiré",
        description=f"{interaction.user.mention} a retiré un warn à {member.mention}",
        color=0x00FF00
    )
    embed.add_field(name="Points rouges restants", value="🔴" * nb_warns if nb_warns > 0 else "Aucun", inline=False)
    log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
    await log_channel.send(embed=embed)

    await interaction.response.send_message(f"✅ {member.display_name} a maintenant {nb_warns} point(s) rouge(s).", ephemeral=True)


# WARNS_LIST
@bot.tree.command(name="warns_list", description="Affiche la liste de tous les membres avec des warns")
async def warns_list(interaction: discord.Interaction):
    if not any(role.id in staff_roles for role in interaction.user.roles):
        await interaction.response.send_message("❌ Tu n'as pas la permission.", ephemeral=True)
        return

    if not warns:
        await interaction.response.send_message("Aucun membre n'a de warns pour le moment.", ephemeral=True)
        return

    embed = discord.Embed(
        title="⚠️ Liste des warns",
        description="Voici tous les membres avec des warns et leurs points rouges",
        color=0xFF0000
    )

    for member_id, nb_warns in warns.items():
        member = interaction.guild.get_member(member_id)
        if member:
            embed.add_field(name=member.display_name, value="🔴" * nb_warns, inline=False)

    embed.set_footer(text=f"Total membres warnés: {len(warns)}")
    await interaction.response.send_message(embed=embed, ephemeral=True)
# ----------------------------
# RUN
# ----------------------------

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    keep_alive()
    bot.run(TOKEN)
else:
    print("❌ ERREUR : Le token n'est pas défini dans les variables d'environnement (DISCORD_TOKEN).")
