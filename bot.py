import discord
from discord.ext import commands
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import io
import os
from math import sqrt
from flask import Flask
import threading

# ---- Flask keepalive ----
app = Flask('')

@app.route('/')
def home():
    return "Bot actif."

def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()

# ---- Couleurs connues ----
COLOR_NAMES = {
    # Noirs et Gris
    "noir": (0, 0, 0),
    "noir charbon": (20, 20, 20),
    "noir corbeau": (40, 40, 40),
    "gris foncé": (64, 64, 64),
    "gris ardoise": (112, 128, 144),
    "gris acier": (70, 70, 70),
    "gris": (128, 128, 128),
    "gris taupe": (72, 60, 50),
    "gris clair": (192, 192, 192),
    "gris perle": (200, 200, 200),
    "blanc": (255, 255, 255),
    "blanc cassé": (245, 245, 245),
    "blanc neige": (255, 250, 250),

    # Rouges
    "rouge foncé": (139, 0, 0),
    "rouge sang": (102, 0, 0),
    "rouge bordeaux": (128, 0, 32),
    "rouge": (255, 0, 0),
    "rouge rubis": (224, 17, 95),
    "rouge tomate": (255, 99, 71),
    "rouge clair": (255, 102, 102),
    "rouge pastel": (255, 105, 97),
    "rouge cerise": (222, 49, 99),

    # Oranges
    "orange brûlé": (204, 85, 0),
    "orange foncé": (255, 140, 0),
    "orange": (255, 165, 0),
    "orange corail": (255, 127, 80),
    "orange abricot": (251, 206, 177),
    "orange pêche": (255, 218, 185),
    "orange saumon": (250, 128, 114),

    # Jaunes
    "jaune moutarde": (204, 204, 0),
    "jaune doré": (255, 215, 0),
    "jaune citron": (255, 255, 0),
    "jaune": (255, 255, 0),
    "jaune pâle": (255, 255, 153),
    "jaune crème": (255, 253, 208),
    "jaune vanille": (243, 229, 171),
    "jaune maïs": (251, 236, 93),

    # Verts
    "vert foncé": (0, 100, 0),
    "vert forêt": (34, 139, 34),
    "vert sapin": (1, 50, 32),
    "vert olive": (128, 128, 0),
    "vert": (0, 128, 0),
    "vert pomme": (141, 182, 0),
    "vert menthe": (152, 255, 152),
    "vert clair": (144, 238, 144),
    "vert lime": (50, 205, 50),
    "vert émeraude": (80, 200, 120),
    "vert jade": (0, 168, 107),
    "vert printemps": (0, 255, 127),

    # Bleus
    "bleu marine": (0, 0, 128),
    "bleu foncé": (0, 0, 139),
    "bleu roi": (65, 105, 225),
    "bleu": (0, 0, 255),
    "bleu ciel": (135, 206, 235),
    "bleu clair": (173, 216, 230),
    "bleu turquoise": (64, 224, 208),
    "bleu acier": (70, 130, 180),
    "bleu azur": (0, 127, 255),
    "bleu canard": (0, 139, 139),
    "bleu pétrole": (0, 86, 86),
    "bleu outremer": (65, 102, 245),

    # Violets
    "violet foncé": (75, 0, 130),
    "violet": (128, 0, 128),
    "violet orchidée": (218, 112, 214),
    "lavande": (230, 230, 250),
    "violet pastel": (203, 153, 201),
    "violet prune": (112, 28, 28),
    "violet lilas": (200, 162, 200),
    "violet améthyste": (153, 102, 204),

    # Roses
    "rose foncé": (255, 20, 147),
    "rose vif": (255, 105, 180),
    "rose": (255, 192, 203),
    "rose bonbon": (255, 183, 197),
    "rose poudré": (255, 209, 220),
    "rose saumon": (244, 194, 194),
    "rose thé": (248, 195, 205),

    # Bruns et Terre
    "marron foncé": (101, 67, 33),
    "marron": (139, 69, 19),
    "marron chocolat": (123, 63, 0),
    "marron caramel": (175, 110, 75),
    "marron café": (111, 78, 55),
    "beige": (245, 245, 220),
    "beige sable": (194, 178, 128),
    "beige café au lait": (166, 138, 100),
    "ocre": (204, 119, 34),
    "terre de sienne": (160, 82, 45),
    "cuivre": (184, 115, 51),
    "bronze": (205, 127, 50),

    # Autres
    "magenta": (255, 0, 255),
    "fuchsia": (255, 0, 128),
    "indigo": (75, 0, 130),
    "cramoisi": (220, 20, 60),
    "corail": (255, 127, 80),
    "turquoise": (64, 224, 208),
    "cyan foncé": (0, 139, 139),
    "cyan": (0, 255, 255),
    "or": (255, 215, 0),
    "argent": (192, 192, 192),
    "platine": (229, 228, 226),
    "ivoire": (255, 255, 240),
    "crème": (255, 253, 208),
}


# ---- Détection couleur dominante ----
def get_dominant_color(image_bytes, k=3):
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGB")
    image = image.resize((100, 100))
    pixels = np.array(image).reshape(-1, 3)

    pixels = [p for p in pixels if not all(c > 245 for c in p)]
    if not pixels:
        pixels = np.array(image).reshape(-1, 3)

    kmeans = KMeans(n_clusters=k, n_init=10).fit(pixels)
    counts = np.bincount(kmeans.labels_)
    dominant = kmeans.cluster_centers_[np.argmax(counts)].astype(int)
    return tuple(dominant)

def closest_color_name(rgb):
    min_distance = float('inf')
    closest_name = None
    for name, ref_rgb in COLOR_NAMES.items():
        distance = sqrt(sum((rgb[i] - ref_rgb[i]) ** 2 for i in range(3)))
        if distance < min_distance:
            min_distance = distance
            closest_name = name
    return closest_name

# ---- Discord bot ----
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

@bot.command()
async def couleur(ctx):
    if not ctx.message.attachments:
        await ctx.send("❌ Tu dois envoyer une image en pièce jointe.")
        return

    attachment = ctx.message.attachments[0]
    image_bytes = await attachment.read()

    try:
        dominant_rgb = get_dominant_color(image_bytes)
        color_name = closest_color_name(dominant_rgb)
        hex_color = '#%02x%02x%02x' % dominant_rgb

        img = Image.new("RGB", (200, 200), dominant_rgb)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        await ctx.send(
            content=(
                f"🎨 **Couleur dominante détectée**\n"
                f"- RGB : {dominant_rgb}\n"
                f"- HEX : `{hex_color}`\n"
                f"- Nom approximatif : **{color_name.upper()}**"
            ),
            file=discord.File(img_bytes, filename="dominante.png")
        )
        print(f"[LOG] Image analysée. Dominante : {dominant_rgb} ≈ {color_name}")
    except Exception as e:
        await ctx.send("❌ Erreur lors du traitement de l'image.")
        print(f"[ERREUR] {e}")

bot.run(os.environ["DISCORD_TOKEN"])
