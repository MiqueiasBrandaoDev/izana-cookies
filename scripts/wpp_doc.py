"""Envia arquivo (PDF de impressão, ficha) para o WhatsApp via Evolution API.

Imagem vai por `wpp_media.py`, que reduz e converte para JPG. Arquivo de gráfica
não pode passar por isso: o que vale nele é justamente estar intacto. Aqui o
arquivo sobe como documento, byte a byte.

Uso: python wpp_doc.py --para=miqueias,izana <arquivo>::<legenda> [...]
"""
import base64, json, os, sys, time
import requests

CREDS = json.load(open(os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")),
                                    ".claude", "credentials.json"), encoding="utf-8"))
BASE = CREDS["evolution"]["url"].rstrip("/")
KEY = CREDS["evolution"]["api_key"]
INSTANCE = "esim-miqueias"

# Destinos nomeados, lidos do cofre — são dados pessoais e este arquivo vive num
# repositório público.
DESTINOS = {k: v for k, v in CREDS.get("whatsapp_destinos", {}).items()
            if not k.startswith("_")}
if not DESTINOS:
    sys.exit('credentials.json precisa do bloco "whatsapp_destinos"')

TIPOS = {".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg",
         ".md": "text/markdown", ".txt": "text/plain", ".csv": "text/csv"}


def enviar(path, caption, destino):
    ext = os.path.splitext(path)[1].lower()
    payload = {
        "number": destino,
        "mediatype": "document",
        "mimetype": TIPOS.get(ext, "application/octet-stream"),
        "media": base64.b64encode(open(path, "rb").read()).decode(),
        "fileName": os.path.basename(path),
        "caption": caption,
    }
    r = requests.post(f"{BASE}/message/sendMedia/{INSTANCE}",
                      headers={"apikey": KEY, "Content-Type": "application/json"},
                      json=payload, timeout=180)
    try:
        j = r.json()
    except Exception:
        j = r.text
    ok = 200 <= r.status_code < 300
    ident = j.get("key", {}).get("id", "?") if isinstance(j, dict) else "?"
    return ok, f"HTTP {r.status_code} {ident}" + ("" if ok else f" | {str(j)[:300]}")


if __name__ == "__main__":
    alvos, itens = ["miqueias"], []
    for arg in sys.argv[1:]:
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
            print(f"{'OK ' if ok else 'FALHA'} {nome:9s} {os.path.basename(path):34s} {msg}")
            time.sleep(1.5)
