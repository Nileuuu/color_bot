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
    "gris": (128, 128, 128),
    "blanc": (255, 255, 255),
    "rouge": (255, 0, 0),
    "vert": (0, 128, 0),
    "bleu": (0, 0, 255),
    "jaune": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "orange": (255, 165, 0),
    "rose": (255, 192, 203),
    "marron": (139, 69, 19),
    "violet": (128, 0, 128),
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
