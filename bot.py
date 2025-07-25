import os
import discord
from discord.ext import commands
from PIL import Image
import requests
from io import BytesIO
from collections import Counter
import threading
from flask import Flask

# === Fake serveur web pour Render ===
app = Flask('')

@app.route('/')
def home():
    return "Le bot tourne !"

def run_web():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_web).start()

# === Bot Discord ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# === Couleurs nommées de base ===
BASIC_COLORS = {
    "rouge": (255, 0, 0),
    "vert": (0, 255, 0),
    "bleu": (0, 0, 255),
    "jaune": (255, 255, 0),
    "orange": (255, 165, 0),
    "violet": (128, 0, 128),
    "rose": (255, 192, 203),
    "noir": (0, 0, 0),
    "blanc": (255, 255, 255),
    "gris": (128, 128, 128),
    "marron": (139, 69, 19),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255)
}

def closest_color_name(rgb):
    def distance(c):
        return sum((c[i] - rgb[i]) ** 2 for i in range(3))
    return min(BASIC_COLORS, key=lambda name: distance(BASIC_COLORS[name]))

def get_dominant_color(image):
    image = image.resize((50, 50))
    pixels = list(image.getdata())
    pixels = [p for p in pixels if len(p) == 3]
    most_common = Counter(pixels).most_common(1)[0][0]
    return most_common

def generate_color_image(rgb, size=(100, 100)):
    img = Image.new("RGB", size, rgb)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

@bot.command()
async def couleur(ctx):
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        try:
            response = requests.get(attachment.url)
            img = Image.open(BytesIO(response.content))
            dominant = get_dominant_color(img)
            name = closest_color_name(dominant)

            # Générer une image de la couleur dominante
            color_img = generate_color_image(dominant)

            file = discord.File(fp=color_img, filename="couleur.png")
            embed = discord.Embed(title="🎨 Couleur dominante", color=discord.Color.from_rgb(*dominant))
            embed.add_field(name="Nom approximatif", value=name, inline=True)
            embed.add_field(name="Valeur RGB", value=str(dominant), inline=True)
            embed.set_image(url="attachment://couleur.png")

            await ctx.send(file=file, embed=embed)
        except Exception as e:
            print(e)
            await ctx.send("❌ Erreur lors du traitement de l'image.")
    else:
        await ctx.send("🖼️ Envoie une image avec la commande `!couleur`.")

@bot.event
async def on_ready():
    print(f"{bot.user} est prêt.")
