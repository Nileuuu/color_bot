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
    "noir": (0, 0, 0),
    "gris foncé": (64, 64, 64),
    "gris": (128, 128, 128),
    "gris clair": (192, 192, 192),
    "blanc": (255, 255, 255),
    "rouge foncé": (139, 0, 0),
    "rouge": (255, 0, 0),
    "rouge clair": (255, 102, 102),
    "orange foncé": (255, 140, 0),
    "orange": (255, 165, 0),
    "jaune doré": (255, 215, 0),
    "jaune": (255, 255, 0),
    "jaune clair": (255, 255, 153),
    "vert foncé": (0, 100, 0),
    "vert": (0, 128, 0),
    "vert clair": (144, 238, 144),
    "vert menthe": (152, 255, 152),
    "cyan foncé": (0, 139, 139),
    "cyan": (0, 255, 255),
    "bleu foncé": (0, 0, 139),
    "bleu": (0, 0, 255),
    "bleu clair": (173, 216, 230),
    "bleu ciel": (135, 206, 235),
    "bleu roi": (65, 105, 225),
    "violet foncé": (75, 0, 130),
    "violet": (128, 0, 128),
    "lavande": (230, 230, 250),
    "magenta": (255, 0, 255),
    "rose foncé": (255, 20, 147),
    "rose": (255, 192, 203),
    "marron foncé": (101, 67, 33),
    "marron": (139, 69, 19),
    "beige": (245, 245, 220),
    "ocre": (204, 119, 34),
    "saumon": (250, 128, 114),
    "corail": (255, 127, 80),
    "or": (255, 215, 0),
    "argent": (192, 192, 192),
    "bronze": (205, 127, 50),
    "olive": (128, 128, 0),
    "turquoise": (64, 224, 208),
    "indigo": (75, 0, 130),
    "prune": (112, 28, 28),
    "cramoisi": (220, 20, 60),
    "bordeaux": (128, 0, 32),
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
