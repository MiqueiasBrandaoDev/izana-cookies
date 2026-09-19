"""Captura e destrincha uma referência visual, de qualquer fonte.

Aceita URL (Instagram, TikTok, YouTube, Facebook, Pinterest, Kwai, site com vídeo) ou
um arquivo local de vídeo ou imagem. Baixa, extrai os frames, monta um mosaico para
localizar o que interessa e transcreve o áudio.

Uso:
    python referencia.py <url-ou-arquivo> [--saida PASTA] [--fps 1] [--sem-audio]

Depois de rodar, abra o mosaico para achar o segundo certo e extraia o frame cheio com:
    python referencia.py --frame <video> <segundos> [--saida PASTA]

Sem dependência de yt-dlp no PATH: usa o módulo Python.
"""
import argparse
import json
import os
import subprocess
import sys

CREDS = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")),
                     ".claude", "credentials.json")

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}
IMAGEM_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def baixar(origem, saida):
    """Baixa de URL via yt-dlp, ou devolve o caminho se já for arquivo local."""
    if os.path.exists(origem):
        return origem
    if not origem.lower().startswith(("http://", "https://")):
        sys.exit(f"nao encontrei o arquivo nem reconheci como URL: {origem}")

    alvo = os.path.join(saida, "origem.%(ext)s")
    print(f"baixando: {origem}")
    r = run([sys.executable, "-m", "yt_dlp", origem, "-o", alvo, "--no-warnings"])
    if r.returncode != 0:
        # fallback: pagina comum com imagem ou video direto
        print(r.stderr[-800:])
        sys.exit("yt-dlp nao deu conta. Se for uma imagem solta, baixe e passe o arquivo.")

    achados = [f for f in os.listdir(saida) if f.startswith("origem.")]
    if not achados:
        sys.exit("download terminou mas nao achei o arquivo")
    return os.path.join(saida, achados[0])


def sondar(video):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height,r_frame_rate,nb_frames",
             "-show_entries", "format=duration",
             "-of", "json", video])
    try:
        j = json.loads(r.stdout)
    except Exception:
        return {}
    st = (j.get("streams") or [{}])[0]
    fmt = j.get("format", {})
    info = {"largura": st.get("width"), "altura": st.get("height"),
            "fps": st.get("r_frame_rate"), "frames": st.get("nb_frames"),
            "duracao": fmt.get("duration")}
    print(f"  {info['largura']}x{info['altura']} · {info['duracao']}s · {info['frames']} frames")

    larg = info.get("largura") or 0
    if larg and larg < 1080:
        print(f"  AVISO: {larg}px de largura. Serve como referencia de angulo, "
              f"mas NAO serve como arte final para impressao.")
    return info


def extrair_frames(video, saida, fps):
    pasta = os.path.join(saida, "frames")
    os.makedirs(pasta, exist_ok=True)
    run(["ffmpeg", "-y", "-v", "error", "-i", video,
         "-vf", f"fps={fps}", "-q:v", "2", os.path.join(pasta, "f_%04d.jpg")])
    n = len([f for f in os.listdir(pasta) if f.endswith(".jpg")])
    print(f"  {n} frames em frames/ (a {fps} fps)")
    return pasta, n


def mosaico(video, saida, fps, n):
    """Mosaico para localizar o trecho. Sem drawtext: o ffmpeg local quebra com Fontconfig.
    A posicao do quadro ja da o tempo: quadro n = (n-1)/fps segundos."""
    cols = 6 if n <= 36 else 9
    linhas = max(1, -(-n // cols))
    destino = os.path.join(saida, "mosaico.jpg")
    run(["ffmpeg", "-y", "-v", "error", "-i", video,
         "-vf", f"fps={fps},scale=180:-1,tile={cols}x{linhas}:margin=4:padding=4",
         "-frames:v", "1", destino])
    if os.path.exists(destino):
        print(f"  mosaico.jpg ({cols} por linha; quadro n = (n-1)/{fps} s)")
    return destino


def transcrever(video, saida):
    try:
        cred = json.load(open(CREDS, encoding="utf-8"))
        key = [k for k in cred["openai"]["keys"] if k["name"] == "core-resumefy"][0]["key"]
    except Exception as e:
        print(f"  sem transcricao (cofre): {e}")
        return None

    audio = os.path.join(saida, "audio.mp3")
    run(["ffmpeg", "-y", "-v", "error", "-i", video, "-vn",
         "-acodec", "libmp3lame", "-ar", "16000", "-ac", "1", "-b:a", "64k", audio])
    if not os.path.exists(audio) or os.path.getsize(audio) < 2000:
        print("  sem audio no video")
        return None

    destino = os.path.join(saida, "transcricao.json")
    r = run(["curl.exe", "-s", "https://api.openai.com/v1/audio/transcriptions",
             "-H", f"Authorization: Bearer {key}",
             "-F", f"file=@{audio}", "-F", "model=whisper-1",
             "-F", "language=pt", "-F", "response_format=verbose_json",
             "-o", destino])
    if not os.path.exists(destino):
        print(f"  transcricao falhou: {r.stderr[-300:]}")
        return None

    try:
        j = json.load(open(destino, encoding="utf-8"))
    except Exception:
        print("  transcricao voltou invalida")
        return None

    txt = os.path.join(saida, "transcricao.txt")
    with open(txt, "w", encoding="utf-8") as fh:
        for s in j.get("segments", []):
            fh.write(f"[{s['start']:.1f}s] {s['text'].strip()}\n")
    print("  transcricao.txt com marcacao de tempo")
    return txt


def frame_cheio(video, segundos, saida):
    os.makedirs(saida, exist_ok=True)
    destino = os.path.join(saida, f"frame_{str(segundos).replace('.', '_')}s.jpg")
    run(["ffmpeg", "-y", "-v", "error", "-ss", str(segundos), "-i", video,
         "-frames:v", "1", "-q:v", "2", destino])
    print(destino)
    return destino


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("origem", help="URL ou caminho do video/imagem")
    ap.add_argument("segundos", nargs="?", help="com --frame: instante a extrair")
    ap.add_argument("--saida", default="referencia")
    ap.add_argument("--fps", type=float, default=1)
    ap.add_argument("--sem-audio", action="store_true")
    ap.add_argument("--frame", action="store_true",
                    help="extrai um unico frame em resolucao cheia")
    a = ap.parse_args()

    os.makedirs(a.saida, exist_ok=True)

    if a.frame:
        if not a.segundos:
            sys.exit("com --frame, informe os segundos")
        frame_cheio(a.origem, a.segundos, a.saida)
        return

    arq = baixar(a.origem, a.saida)
    ext = os.path.splitext(arq)[1].lower()

    if ext in IMAGEM_EXT:
        print(f"imagem: {arq}")
        print("  referencia estatica, nada a fatiar")
        return

    if ext not in VIDEO_EXT:
        print(f"aviso: extensao {ext} nao reconhecida, tentando como video")

    print(f"video: {arq}")
    sondar(arq)
    _, n = extrair_frames(arq, a.saida, a.fps)
    mosaico(arq, a.saida, a.fps, n)
    if not a.sem_audio:
        transcrever(arq, a.saida)

    print(f"\npronto em {os.path.abspath(a.saida)}")
    print("abra mosaico.jpg, ache o segundo e rode:")
    print(f'  python referencia.py --frame "{arq}" <segundos> --saida "{a.saida}"')


if __name__ == "__main__":
    main()
