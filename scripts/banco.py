"""Puxa o que chegou no grupo "Banco De Dados - IZANA" do WhatsApp.

A Ana Carla manda no grupo o que tiver na mão, inclusive na rua: foto, áudio,
recado de texto, vídeo, PDF. Depois diz "mandei no banco de dados". Este script
traz tudo na ordem em que ela mandou, como uma conversa:

    texto      aparece direto
    áudio      aparece transcrito
    imagem     salva em disco, com a legenda e uma descrição do que tem nela
    vídeo      salvo em disco (fatie com referencia.py se precisar)
    documento  salvo em disco com o nome original

Ele só enxerga aquele grupo. Não fala com a Evolution nem com os bancos do
Resumefy: fala com um portão (webhook) que conhece só aquele grupo e barra
qualquer outro chat. Endereço e token do portão ficam no cofre, bloco "izana_banco".

Cada item é novo ou lido. Item lido sai de `novas`, mas pode ser relido com `reler`.

Uso:
    python banco.py novas              traz o que ainda não foi lido e marca como lido
    python banco.py lista              mostra o que não foi lido, numerado, sem baixar
    python banco.py lista --todas      mostra tudo, com quantas vezes cada item foi lido
    python banco.py reler 3 5          traz de novo os itens 3 e 5 (numeração do `lista --todas`)
    python banco.py reler <id>         também aceita o id da mensagem
    python banco.py reler --ultimas 4  traz de novo os 4 mais recentes

    --saida <pasta>   onde salvar arquivos (padrão: banco/ dentro da skill)
    --nao-marcar      traz sem marcar como lido
"""
import base64, json, os, re, sys
from datetime import datetime
import requests

sys.stdout.reconfigure(encoding="utf-8")

CREDS = json.load(open(os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")),
                                    ".claude", "credentials.json"), encoding="utf-8"))
CFG = CREDS.get("izana_banco")
if not CFG or not CFG.get("url") or not CFG.get("token"):
    sys.exit('credentials.json precisa do bloco "izana_banco": {"url": "...", "token": "..."}')

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/heic": ".heic",
       "video/mp4": ".mp4", "audio/ogg": ".ogg", "audio/mpeg": ".mp3", "audio/mp4": ".m4a",
       "application/pdf": ".pdf"}
ROTULO = {"texto": "TEXTO", "audio": "ÁUDIO", "imagem": "IMAGEM", "video": "VÍDEO",
          "documento": "DOCUMENTO"}


def portao(acao, **corpo):
    r = requests.post(CFG["url"], headers={"x-izana-token": CFG["token"]},
                      json={"acao": acao, **corpo}, timeout=300)
    if r.status_code == 403:
        sys.exit("o portão recusou o token: confira o bloco izana_banco do cofre")
    r.raise_for_status()
    j = r.json()
    if not j.get("ok"):
        raise RuntimeError(j.get("erro") or "resposta sem ok")
    return j


def quando(iso):
    return datetime.fromisoformat(iso).astimezone().strftime("%d/%m %H:%M") if iso else "?"


def duracao(s):
    return f" {s // 60}:{s % 60:02d}" if s else ""


def baixar(item, pasta):
    d = portao("baixar", id=item["message_id"])
    if not d.get("base64"):
        raise RuntimeError("o WhatsApp não devolveu o arquivo (a mídia pode ter expirado)")
    carimbo = datetime.fromisoformat(item["enviada_em"]).astimezone().strftime("%Y-%m-%d_%H%M%S")
    mime = (d.get("mimetype") or item.get("mimetype") or "").split(";")[0].strip()
    if item.get("nome_arquivo"):
        base = re.sub(r'[<>:"/\\|?*]', "_", item["nome_arquivo"])
        nome = f"{carimbo}_{base}"
    else:
        nome = f"{carimbo}_{item['message_id'][-6:]}{EXT.get(mime, '.bin')}"
    caminho = os.path.join(pasta, nome)
    with open(caminho, "wb") as f:
        f.write(base64.b64decode(d["base64"]))
    return caminho


def transcrever_local(caminho):
    """Reserva: o hub costuma já ter transcrito. Só roda quando não transcreveu."""
    key = [k for k in CREDS["openai"]["keys"] if k["name"] == "core-resumefy"][0]["key"]
    with open(caminho, "rb") as f:
        r = requests.post("https://api.openai.com/v1/audio/transcriptions",
                          headers={"Authorization": f"Bearer {key}"},
                          files={"file": (os.path.basename(caminho), f)},
                          data={"model": "whisper-1", "language": "pt"}, timeout=300)
    r.raise_for_status()
    return r.json().get("text", "").strip()


def cabecalho(n, item):
    estado = f"lido {item['vezes_lida']}x" if item.get("lida_em") else "novo"
    return (f"\n── nº {n}  {quando(item['enviada_em'])}  {item.get('remetente') or '?'}  "
            f"{ROTULO.get(item['tipo'], item['tipo'].upper())}{duracao(item.get('duracao_s'))}  ({estado})")


def mostrar(n, item, pasta):
    """Imprime o item e devolve True se ele pôde ser entregue por inteiro."""
    print(cabecalho(n, item))
    tipo, texto = item["tipo"], item.get("texto")
    if tipo == "texto":
        print(f"   {texto}")
        return True
    try:
        if tipo == "audio":
            transcricao = item.get("transcricao")
            if not transcricao:
                caminho = baixar(item, pasta)
                transcricao = transcrever_local(caminho)
                portao("transcricao", id=item["message_id"], texto=transcricao)
            print(f'   transcrição: "{transcricao}"')
            return True
        caminho = baixar(item, pasta)
        print(f"   arquivo: {caminho}")
        if texto:
            print(f'   legenda: "{texto}"')
        if item.get("descricao"):
            print(f"   descrição automática (confira na imagem): {item['descricao']}")
        if tipo == "video":
            print("   para ver os quadros e ouvir: python <skill>/scripts/referencia.py "
                  f'"{caminho}" --saida <pasta>')
        return True
    except Exception as e:
        print(f"   FALHA: {e}")
        return False


def entregar(itens, numeros, pasta, marcar):
    os.makedirs(pasta, exist_ok=True)
    ok = [it["message_id"] for n, it in zip(numeros, itens) if mostrar(n, it, pasta)]
    if marcar and ok:
        portao("marcar", ids=ok)
    print(f"\n{len(ok)} de {len(itens)} item(ns) entregue(s)"
          + (" e marcado(s) como lido(s)" if marcar and ok else ""))


def listar(itens):
    for n, it in enumerate(itens, 1):
        resumo = it.get("texto") or it.get("transcricao") or it.get("nome_arquivo") or ""
        resumo = " ".join(resumo.split())
        resumo = f' | "{resumo[:80]}{"…" if len(resumo) > 80 else ""}"' if resumo else ""
        print(cabecalho(n, it).strip() + resumo)


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
        itens = portao("listar", todas=todas)["itens"]
        if not itens:
            print("nada " + ("no grupo" if todas else "novo no grupo"))
        listar(itens)

    elif cmd == "novas":
        itens = portao("listar")["itens"]
        if not itens:
            print("nada novo no grupo")
        else:
            entregar(itens, range(1, len(itens) + 1), pasta, marcar)

    elif cmd == "reler":
        itens = portao("listar", todas=True)["itens"]
        if ultimas:
            base = len(itens) - ultimas
            alvos = [(base + k + 1, it) for k, it in enumerate(itens[-ultimas:])]
        else:
            por_id = {x["message_id"]: (k, x) for k, x in enumerate(itens, 1)}
            alvos = []
            for e in escolhidos:
                if e.isdigit() and 1 <= int(e) <= len(itens):
                    alvos.append((int(e), itens[int(e) - 1]))
                elif e in por_id:
                    alvos.append(por_id[e])
                else:
                    print(f"não achei o item {e} (rode `lista --todas` para ver os números)")
        if alvos:
            entregar([a[1] for a in alvos], [a[0] for a in alvos], pasta, marcar)

    else:
        sys.exit(f"comando desconhecido: {cmd}\n{__doc__}")
