"""Envia texto para o WhatsApp via Evolution API (sendText).

Irmão do wpp_media.py: mesmo cofre, mesma instância, mesmos destinos nomeados.
Existe porque relatório é texto, não imagem — e relatório desta marca vai para o
WhatsApp, não para arquivo que ninguém abre.

Uso:
    python wpp_texto.py --para=miqueias "texto da mensagem"
    python wpp_texto.py --para=miqueias,izana --arquivo relatorio.md

O WhatsApp quebra mensagem muito longa, então texto acima de 4000 caracteres é
enviado em partes, na ordem.
"""
import json, os, sys, time
import requests

CREDS = json.load(open(os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")),
                                    ".claude", "credentials.json"), encoding="utf-8"))
BASE = CREDS["evolution"]["url"].rstrip("/")
KEY = CREDS["evolution"]["api_key"]
INSTANCE = "esim-miqueias"
LIMITE = 4000

# Destinos nomeados, lidos do cofre (bloco "whatsapp_destinos"), nunca do código —
# são dados pessoais e este arquivo vive num repositório.
DESTINOS = {k: v for k, v in CREDS.get("whatsapp_destinos", {}).items()
            if not k.startswith("_")}
if not DESTINOS:
    sys.exit('credentials.json precisa do bloco "whatsapp_destinos", '
             'por exemplo {"miqueias": "<jid>@g.us"}')


def _partes(texto, limite=LIMITE):
    """Quebra em parágrafos inteiros quando dá, para não cortar frase no meio."""
    if len(texto) <= limite:
        return [texto]
    partes, atual = [], ""
    for bloco in texto.split("\n\n"):
        if len(atual) + len(bloco) + 2 > limite and atual:
            partes.append(atual.rstrip())
            atual = ""
        while len(bloco) > limite:
            partes.append(bloco[:limite])
            bloco = bloco[limite:]
        atual += bloco + "\n\n"
    if atual.strip():
        partes.append(atual.rstrip())
    return partes


def enviar(texto, destino):
    """Devolve (ok, mensagem). Nunca levanta exceção."""
    resultados = []
    for i, parte in enumerate(_partes(texto), 1):
        try:
            r = requests.post(
                f"{BASE}/message/sendText/{INSTANCE}",
                headers={"apikey": KEY, "Content-Type": "application/json"},
                json={"number": destino, "text": parte},
                timeout=60,
            )
            ok = 200 <= r.status_code < 300
            try:
                ident = r.json().get("key", {}).get("id", "?")
            except Exception:
                ident = "?"
            resultados.append((ok, f"HTTP {r.status_code} {ident}"
                                   f"{'' if ok else ' | ' + r.text[:200]}"))
        except Exception as e:
            resultados.append((False, str(e)[:200]))
        time.sleep(1.2)
    todas_ok = all(ok for ok, _ in resultados)
    return todas_ok, " ; ".join(m for _, m in resultados)


if __name__ == "__main__":
    args = sys.argv[1:]
    alvos, texto, arquivo = ["miqueias"], [], None
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--para="):
            alvos = [x.strip() for x in a.split("=", 1)[1].split(",") if x.strip()]
        elif a == "--arquivo":
            i += 1
            arquivo = args[i]
        else:
            texto.append(a)
        i += 1

    if arquivo:
        corpo = open(arquivo, encoding="utf-8").read()
    else:
        corpo = " ".join(texto)
    if not corpo.strip():
        sys.exit("nada para enviar: passe o texto ou --arquivo <caminho>")

    for nome in alvos:
        if nome not in DESTINOS:
            sys.exit(f"destino desconhecido: {nome} (use {', '.join(DESTINOS)})")

    for nome in alvos:
        ok, msg = enviar(corpo, DESTINOS[nome])
        print(f"{'OK ' if ok else 'FALHA'} {nome:9s} {len(corpo):5d} chars  {msg}")
