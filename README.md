# izana-cookies

Skill única do Claude Code para operar a marca de cookies: imagens de produto, banners
impressos, posts, logo, copy e estratégia. Todo o contexto da marca mora dentro dela.

## Instalar em outra máquina

```bash
git clone <url-do-repo> ~/.claude/skills/izana-cookies
```

No Windows:

```powershell
git clone <url-do-repo> "$env:USERPROFILE\.claude\skills\izana-cookies"
```

Abra o Claude Code e chame `/izana-cookies`. A skill também dispara sozinha quando o
assunto for a marca.

Para atualizar depois:

```bash
git -C ~/.claude/skills/izana-cookies pull
```

## O que a máquina precisa ter

| Item | Para quê | Como conferir |
|------|----------|---------------|
| Python 3 | scripts | `python --version` |
| `requests`, `Pillow` | geração e envio | `pip install requests pillow` |
| `yt_dlp` (módulo) | baixar referência de URL | `python -m yt_dlp --version` |
| `ffmpeg` e `ffprobe` no PATH | fatiar vídeo, montar mosaico | `ffmpeg -version` |
| `curl` | transcrição | já vem no Windows 10+ |
| Cofre de credenciais | chave da OpenAI e da Evolution | `~/.claude/credentials.json` |

O cofre **não** vai neste repositório. Na máquina nova ele precisa ter a chave
`openai.core-resumefy` e o bloco `evolution` com `url` e `api_key`.

Para o envio pelo WhatsApp, a máquina também precisa de `~/.claude/scripts/wpp_media.py`.

## Estrutura

```
SKILL.md                        entrada e modos de operação
references/marca.md             fonte única da verdade da marca
references/producao-imagem.md   o método inteiro, passo a passo
scripts/referencia.py           baixa e fatia referência de qualquer fonte
scripts/gerar.py                gera imagem com gpt-image
```

Os assets (fotos, banners, referências, cerca de 150 MB) ficam **fora** do repositório,
em `izana-cookies/assets/` na pasta de projetos. Não versione imagem pesada aqui.

## Aviso

A marca pode mudar a qualquer momento. Nome, fonte, cor e logo vivem apenas em
`references/marca.md` — nunca cravados em script ou prompt.
