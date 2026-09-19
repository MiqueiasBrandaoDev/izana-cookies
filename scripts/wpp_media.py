"""Envia imagens para o WhatsApp do Miquéias via Evolution API (sendMedia).

Uso: python wpp_media.py <arquivo>::<legenda> [<arquivo>::<legenda> ...]
Instância: esim-miqueias | Destino: grupo "Avisos Claude Code".
"""
import base64, json, os, sys, time
import requests
from PIL import Image

CREDS = json.load(open(r"C:\Users\mique\.claude\credentials.json", encoding="utf-8"))
BASE = CREDS["evolution"]["url"].rstrip("/")
KEY = CREDS["evolution"]["api_key"]
INSTANCE = "esim-miqueias"

# Destinos nomeados, lidos do cofre (bloco "whatsapp_destinos"), nunca do código —
# são dados pessoais e este arquivo vive num repositório.
# Use --para=miqueias,izana (padrão: miqueias).
DESTINOS = {k: v for k, v in CREDS.get("whatsapp_destinos", {}).items()
            if not k.startswith("_")}
if not DESTINOS:
    sys.exit('credentials.json precisa do bloco "whatsapp_destinos", '
             'por exemplo {"miqueias": "<jid>@g.us"}')

TMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wpp_tmp")
os.makedirs(TMP, exist_ok=True)


def preparar(path):
    """Converte para JPG com lado maior <= 1600px, para aliviar o payload."""
    im = Image.open(path).convert("RGB")
    if max(im.size) > 1600:
        r = 1600 / max(im.size)
        im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    out = os.path.join(TMP, os.path.splitext(os.path.basename(path))[0] + ".jpg")
    im.save(out, "JPEG", quality=88, optimize=True)
    return out


def enviar(path, caption, destino):
    jpg = preparar(path)
    b64 = base64.b64encode(open(jpg, "rb").read()).decode()
    payload = {
        "number": destino,
        "mediatype": "image",
        "mimetype": "image/jpeg",
        "media": b64,
        "fileName": os.path.basename(jpg),
        "caption": caption,
    }
    r = requests.post(
        f"{BASE}/message/sendMedia/{INSTANCE}",
        headers={"apikey": KEY, "Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )
    try:
        j = r.json()
    except Exception:
        j = r.text
    ok = 200 <= r.status_code < 300
    ident = (j.get("key", {}).get("id", "?") if isinstance(j, dict) else "?")
    detalhe = "" if ok else f" | {str(j)[:300]}"
    return ok, f"HTTP {r.status_code} {ident}{detalhe}"


if __name__ == "__main__":
    args = sys.argv[1:]
    alvos = ["miqueias"]
    itens = []
    for arg in args:
        if arg.startswith("--para="):
            alvos = [a.strip() for a in arg.split("=", 1)[1].split(",") if a.strip()]
        else:
            itens.append(arg)

    for nome in alvos:
        if nome not in DESTINOS:
            sys.exit(f"destino desconhecido: {nome} (use {', '.join(DESTINOS)})")

    for arg in itens:
        path, _, caption = arg.partition("::")
        for nome in alvos:
            ok, msg = enviar(path, caption, DESTINOS[nome])
            print(f"{'OK ' if ok else 'FALHA'} {nome:9s} {os.path.basename(path):28s} {msg}")
            time.sleep(1.5)
