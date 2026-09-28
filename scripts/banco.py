"""Puxa as imagens que chegaram no grupo "Banco De Dados - IZANA" do WhatsApp.

A Ana Carla manda as fotos no grupo e diz "mandei no banco de dados". Este script
busca o que ela mandou e salva em disco para o Claude abrir e analisar.

Ele só enxerga aquele grupo. Não fala com a Evolution nem com o banco do Resumefy:
fala com um portão (webhook) que já sabe qual é o grupo e barra qualquer outro chat.
O endereço e o token do portão ficam no cofre, bloco "izana_banco".

Cada imagem tem um estado: nova ou lida. Imagem lida sai da lista de novas, mas pode
ser relida a qualquer momento com `reler`.

Uso:
    python banco.py novas              baixa as que ainda não foram lidas e marca como lidas
    python banco.py lista              mostra as não lidas, numeradas, sem baixar
    python banco.py lista --todas      mostra todas, com quantas vezes cada uma foi lida
    python banco.py reler 3 5          baixa de novo as de número 3 e 5 (numeração do `lista --todas`)
    python banco.py reler <id>         também aceita o id da mensagem
    python banco.py reler --ultimas 4  baixa de novo as 4 mais recentes

    --saida <pasta>   onde salvar (padrão: banco/ dentro da skill)
    --nao-marcar      baixa sem marcar como lida
"""
import base64, json, os, sys
from datetime import datetime
import requests

sys.stdout.reconfigure(encoding="utf-8")

CREDS = json.load(open(os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")),
                                    ".claude", "credentials.json"), encoding="utf-8"))
CFG = CREDS.get("izana_banco")
if not CFG or not CFG.get("url") or not CFG.get("token"):
    sys.exit('credentials.json precisa do bloco "izana_banco": {"url": "...", "token": "..."}')

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/heic": ".heic"}


def portao(acao, **corpo):
    r = requests.post(CFG["url"], headers={"x-izana-token": CFG["token"]},
                      json={"acao": acao, **corpo}, timeout=180)
    if r.status_code == 403:
        sys.exit("o portão recusou o token: confira o bloco izana_banco do cofre")
    r.raise_for_status()
    j = r.json()
    if not j.get("ok"):
        raise RuntimeError(j.get("erro") or "resposta sem ok")
    return j


def quando(iso):
    return datetime.fromisoformat(iso).astimezone().strftime("%d/%m %H:%M") if iso else "?"


def baixar(img, pasta):
    d = portao("baixar", id=img["message_id"])
    if not d.get("base64"):
        raise RuntimeError("o WhatsApp não devolveu o arquivo (a mídia pode ter expirado)")
    carimbo = datetime.fromisoformat(img["enviada_em"]).astimezone().strftime("%Y-%m-%d_%H%M%S")
    nome = f"{carimbo}_{img['message_id'][-6:]}{EXT.get(d.get('mimetype'), '.jpg')}"
    caminho = os.path.join(pasta, nome)
    with open(caminho, "wb") as f:
        f.write(base64.b64decode(d["base64"]))
    return caminho


def imprimir(imagens, numeros=True):
    for n, i in enumerate(imagens, 1):
        estado = f"lida {i['vezes_lida']}x" if i.get("lida_em") else "NOVA"
        legenda = f' | "{i["legenda"]}"' if i.get("legenda") else ""
        print(f"{n:3d}. {quando(i['enviada_em'])}  {estado:9s} {i.get('remetente') or '?'}"
              f"  id={i['message_id']}{legenda}")


def puxar(alvos, pasta, marcar):
    os.makedirs(pasta, exist_ok=True)
    ok = []
    for img in alvos:
        try:
            caminho = baixar(img, pasta)
            ok.append(img["message_id"])
            legenda = f' | legenda: "{img["legenda"]}"' if img.get("legenda") else ""
            print(f"OK    {quando(img['enviada_em'])}  {caminho}{legenda}")
        except Exception as e:
            print(f"FALHA {quando(img['enviada_em'])}  id={img['message_id']}  {e}")
    if marcar and ok:
        portao("marcar", ids=ok)
    print(f"\n{len(ok)} de {len(alvos)} baixada(s)" + (" e marcada(s) como lida(s)" if marcar and ok else ""))


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        sys.exit(__doc__)
    cmd, resto = args[0], args[1:]
    pasta = os.path.join(SKILL, "banco")
    marcar, todas, ultimas, escolhidos = True, False, None, []
    i = 0
    while i < len(resto):
        a = resto[i]
        if a == "--saida":
            i += 1; pasta = resto[i]
        elif a == "--nao-marcar":
            marcar = False
        elif a == "--todas":
            todas = True
        elif a == "--ultimas":
            i += 1; ultimas = int(resto[i])
        else:
            escolhidos.append(a)
        i += 1

    if cmd == "lista":
        imagens = portao("listar", todas=todas)["imagens"]
        if not imagens:
            print("nenhuma imagem " + ("no grupo" if todas else "nova no grupo"))
        imprimir(imagens)

    elif cmd == "novas":
        imagens = portao("listar")["imagens"]
        if not imagens:
            print("nenhuma imagem nova no grupo")
        else:
            puxar(imagens, pasta, marcar)

    elif cmd == "reler":
        imagens = portao("listar", todas=True)["imagens"]
        if ultimas:
            alvos = imagens[-ultimas:]
        else:
            por_id = {x["message_id"]: x for x in imagens}
            alvos = []
            for e in escolhidos:
                if e.isdigit() and 1 <= int(e) <= len(imagens):
                    alvos.append(imagens[int(e) - 1])
                elif e in por_id:
                    alvos.append(por_id[e])
                else:
                    print(f"não achei a imagem {e} (rode `lista --todas` para ver os números)")
        if alvos:
            puxar(alvos, pasta, marcar)

    else:
        sys.exit(f"comando desconhecido: {cmd}\n{__doc__}")
