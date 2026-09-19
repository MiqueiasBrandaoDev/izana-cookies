"""Gera imagens da marca com gpt-image, usando as fotos reais como referência.

O nome, as cores e a fonte NUNCA ficam escritos aqui: vêm do prompt que o agente monta
depois de ler references/marca.md. Este script só executa.

Uso como biblioteca (preferido — o agente monta os prompts):

    from gerar import gerar, gerar_lote
    gerar("saida.png", prompt, referencias=["foto1.jpg"], size="1024x1536")
    gerar_lote([("a.png", p1, refs1), ("b.png", p2, refs2)])

Uso pela linha de comando, para um teste rápido:

    python gerar.py saida.png "prompt..." foto1.jpg foto2.png --size 1024x1536

Blocos prontos para compor prompts estão no fim do arquivo (TEXTURA, INTEIRO, SEM_TEXTO...).
Eles carregam os erros já cometidos; use-os sempre.
"""
import base64
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests

CREDS = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")),
                     ".claude", "credentials.json")
MODELO = "gpt-image-2.5-sunburst"
ENDPOINT = "https://api.openai.com/v1/images/edits"
TAMANHOS = {"1024x1024", "1024x1536", "1536x1024"}


def _chave():
    cred = json.load(open(CREDS, encoding="utf-8"))
    return [k for k in cred["openai"]["keys"] if k["name"] == "core-resumefy"][0]["key"]


def _mime(p):
    return "image/png" if p.lower().endswith(".png") else "image/jpeg"


def gerar(destino, prompt, referencias=(), size="1024x1536", tentativas=3, modelo=MODELO):
    """Gera uma imagem. Devolve (ok, mensagem). Nunca levanta exceção."""
    if size not in TAMANHOS:
        return False, f"tamanho invalido: {size} (use {', '.join(sorted(TAMANHOS))})"
    faltando = [p for p in referencias if not os.path.exists(p)]
    if faltando:
        return False, f"referencia inexistente: {faltando[0]}"

    key = _chave()
    for n in range(tentativas):
        arquivos = [("image[]", (os.path.basename(p), open(p, "rb"), _mime(p)))
                    for p in referencias]
        try:
            r = requests.post(
                ENDPOINT,
                headers={"Authorization": f"Bearer {key}"},
                files=arquivos,
                data={"model": modelo, "size": size, "quality": "high", "prompt": prompt},
                timeout=900,
            )
            j = r.json()
            if "error" in j:
                if n < tentativas - 1:
                    time.sleep(8)
                    continue
                return False, "API: " + j["error"]["message"][:220]
            os.makedirs(os.path.dirname(os.path.abspath(destino)), exist_ok=True)
            with open(destino, "wb") as fh:
                fh.write(base64.b64decode(j["data"][0]["b64_json"]))
            return True, f"{os.path.getsize(destino) // 1024} KB"
        except Exception as e:
            if n < tentativas - 1:
                time.sleep(8)
                continue
            return False, str(e)[:200]
        finally:
            for _, (_, fh, _) in arquivos:
                try:
                    fh.close()
                except Exception:
                    pass
    return False, "falhou"


def gerar_lote(jobs, paralelas=4, size="1024x1536"):
    """jobs: lista de (destino, prompt, referencias) ou (destino, prompt, referencias, size).
    Gera em paralelo e imprime o resultado de cada um."""
    def _um(job):
        destino, prompt, refs = job[0], job[1], job[2]
        tam = job[3] if len(job) > 3 else size
        ok, msg = gerar(destino, prompt, refs, size=tam)
        return destino, ok, msg

    resultados = []
    with ThreadPoolExecutor(max_workers=paralelas) as ex:
        for destino, ok, msg in ex.map(_um, jobs):
            print(f"{'ok   ' if ok else 'FALHA'} {os.path.basename(destino):32s} {msg}")
            resultados.append((destino, ok, msg))
    return resultados


# --------------------------------------------------------------------------
# Blocos de prompt. Cada um existe por causa de uma reprovação real.
# --------------------------------------------------------------------------

TEXTURA = (
    "CRITICAL TEXTURE DIRECTION: the cookies must look MOIST, SOFT and FRESH — glossy "
    "toppings catching the light, melted chocolate glistening and slowly running down the "
    "side, a soft fudgy surface. They must NOT look dry, sandy, crumbly or over-baked. "
    "Do NOT scatter loose crumbs around the scene. Keep the surface around the cookies "
    "clean. Rich saturated colour, appetising highlights, food-magazine quality."
)

INTEIRO = (
    "Every cookie is WHOLE and UNBROKEN — do not break, split or cut any cookie open. "
    "Show them from the top-front so the glossy topping is the hero."
)

SABORES_TRAVADOS = (
    "Only show the cookie flavours present in the reference images. Do NOT invent other "
    "flavours, no pistachio, no red velvet, no biscuit toppings."
)

SEM_TEXTO = "No hands, no text, no logos, no packaging."

ESPACO_TIPOGRAFIA = (
    "Leave generous empty background in the TOP HALF of the frame for typography."
)

SEM_MANUSCRITO = (
    "NEVER use handwritten, script, cursive or brush lettering for any word."
)

POSTER = (
    "Flat graphic-design poster artwork for a printed piece, no mockup, no room, no stand, "
    "no people, no hands. Fill the whole frame edge to edge. Brazilian Portuguese, correct "
    "accents, spelled exactly as given."
)


def so_este_texto(itens):
    """Fecha a porta para slogan inventado. itens: lista de strings, na ordem da peça."""
    linhas = "\n".join(f"  ({chr(97 + i)}) \"{t}\"" for i, t in enumerate(itens))
    return (
        "THE ONLY TEXT ON THE WHOLE PIECE IS THESE ITEMS, nothing else:\n" + linhas + "\n"
        "No slogan, no tagline, no extra sentence, no descriptions, no prices, no flavours "
        "listed, no dates, no phone numbers, no social handles, no QR codes. If you are "
        "tempted to add any other words, leave the space empty instead."
    )


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    size = "1024x1536"
    if "--size" in args:
        i = args.index("--size")
        size = args[i + 1]
        del args[i:i + 2]
    if len(args) < 2:
        sys.exit(__doc__)
    destino, prompt, refs = args[0], args[1], args[2:]
    ok, msg = gerar(destino, prompt, refs, size=size)
    print(("ok " if ok else "FALHA ") + msg)
    sys.exit(0 if ok else 1)
