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

| Item | Para quê | Obrigatório | Como conferir |
|------|----------|-------------|---------------|
| Python 3 | scripts | sim | `python --version` |
| `requests` | geração | sim | `pip install requests` |
| Chave da OpenAI no cofre | gerar imagem e transcrever | sim | ver abaixo |
| `ffmpeg` e `ffprobe` no PATH | fatiar vídeo, montar mosaico | só para referência em vídeo | `ffmpeg -version` |
| `yt_dlp` (módulo) | baixar referência de URL | só para referência de link | `python -m yt_dlp --version` |
| `curl` | transcrição | só para transcrever | já vem no Windows 10+ |
| `Pillow` | envio por WhatsApp | só para o envio | `pip install pillow` |
| Evolution no cofre | envio por WhatsApp | só para o envio | ver abaixo |

### Cofre

O cofre **não** vai neste repositório. Fica em `~/.claude/credentials.json`
(`%USERPROFILE%\.claude\credentials.json` no Windows). O mínimo para a skill funcionar:

```json
{
  "openai": {
    "keys": [
      { "name": "core-resumefy", "key": "sk-proj-...", "used_in": ["izana-cookies"] }
    ]
  }
}
```

Para habilitar também o envio por WhatsApp, acrescente:

```json
{
  "evolution": { "url": "https://...", "api_key": "..." },
  "whatsapp_destinos": { "miqueias": "<jid>@g.us", "izana": "<jid>@s.whatsapp.net" }
}
```

Sem esses dois blocos a skill continua funcionando: ela gera normalmente e entrega os
arquivos localmente, sem tentar enviar.

Se o arquivo já existir na máquina, **mescle os blocos** em vez de substituir.
Salve como **UTF-8 sem BOM** — com BOM o Python não lê o cofre. No PowerShell, não use
`Out-File` nem `Set-Content` para editá-lo: eles gravam BOM.

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
