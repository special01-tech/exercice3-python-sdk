import asyncio
import base64
import os

import httpx
from rodiumai import RodiumAI
# Modèle utilisé si le SDK n'en reçoit pas (évite le retour à openai/gpt-4o)
os.environ.setdefault("RODIUMAI_DEFAULT_MODEL", "anthropic/claude-haiku-4-5-20251001")

# 1) Charger la clé depuis le fichier .env (ici ou dans le dossier au-dessus)
def charger_cle():
    if os.environ.get("RODIUMAI_API_KEY"):
        return
    dossier = os.path.dirname(os.path.abspath(__file__))
    for chemin in (os.path.join(dossier, ".env"), os.path.join(dossier, "..", ".env")):
        if os.path.isfile(chemin):
            with open(chemin, encoding="utf-8-sig") as f:
                for ligne in f:
                    ligne = ligne.strip().replace("export ", "", 1)
                    if ligne.startswith("RODIUMAI_API_KEY="):
                        os.environ["RODIUMAI_API_KEY"] = (
                            ligne.split("=", 1)[1].strip().strip('"').strip("'")
                        )
                        return


charger_cle()


# 2) Enregistrer un fichier à partir d'une réponse (base64 ou lien)
def enregistrer(item, nom_fichier):
    if item.b64_json:
        contenu = base64.b64decode(item.b64_json)
    else:
        contenu = httpx.get(item.url, timeout=120, follow_redirects=True).content
    with open(nom_fichier, "wb") as f:
        f.write(contenu)
    print("Fichier enregistré :", nom_fichier)


# 3) Les trois étapes, avec le SDK
async def etape_chat(client):
    rep = await client.model("anthropic/claude-haiku-4-5-20251001") \
        .temperature(0.7).chat("Écris une accroche pour un restaurant de quartier.")
    print(rep.choices[0].message.content)
    print("Coût (RODI) :", getattr(rep, "cost_rodi", None))


async def etape_image(client):
    rep = await client.images.generate(
        model="google/gemini-3.1-flash-lite-image",
        prompt="Un plat appétissant dans un restaurant de quartier, lumière naturelle",
        n=1,
        size="1024x1024",
        quality="low",
        timeout=180,
    )
    enregistrer(rep.data[0], "image.png")


async def etape_video(client):
    rep = await client.video(
        model="google/veo-3.1-fast",
        prompt="Un cuisinier prépare un plat, gros plan, ambiance chaleureuse",
        duration_seconds=8,
        aspect_ratio="9:16",
    )
    enregistrer(rep.data[0], "video.mp4")


# 4) Le menu : précédent / rester / suivant
async def main():
    client = RodiumAI()  # lit la clé dans RODIUMAI_API_KEY
    etapes = [("Chat", etape_chat), ("Image", etape_image), ("Vidéo", etape_video)]
    i = 0
    while i < len(etapes):
        nom, fonction = etapes[i]
        print(f"\n=== Étape {i + 1}/{len(etapes)} : {nom} ===")
        try:
            await fonction(client)
        except Exception as e:
            print("Erreur :", e)
        choix = ""
        while choix not in ("p", "r", "s"):
            choix = input("\n(p) précédent, (r) rester, (s) suivant ? ").strip().lower()
        if choix == "p":
            i = max(0, i - 1)
        elif choix == "s":
            i += 1
        # "r" : on reste sur la même étape et on la relance
    print("\nTerminé.")


asyncio.run(main())