# Contexto da marca — fonte única da verdade

Este arquivo é o **único** lugar onde os dados da marca ficam escritos. Nenhuma outra parte
da skill, nenhum script e nenhum prompt pode ter nome, cor ou fonte cravados: tudo é lido daqui.

O que estiver **PENDENTE** não pode ser inventado. Pergunte ao Miquéias.

---

## 0. A marca pode mudar a qualquer momento

O nome, a tipografia, as cores e o logo **estão sujeitos a troca sem aviso**, por decisão da
Izana. Quando isso acontecer:

1. Atualize a tabela da seção 1 aqui, com a data da decisão.
2. **Não** saia refazendo peça antiga por conta própria. Pergunte o que ele quer regerar.
3. As peças já geradas continuam em `assets/` como histórico, não como referência de marca.

Nunca escreva o nome da marca dentro de um script, de um prompt fixo ou do `SKILL.md`.
O nome sempre vem desta tabela, em tempo de execução.

Histórico de nome: `Cookies da Izana` → **`Izana Cookies`** (19/09/2026, decidido pela Izana).

---

## 1. Identidade

| Item | Valor | Estado |
|------|-------|--------|
| Nome | **Izana Cookies** (nessa ordem) | Decidido 19/09/2026, sujeito a troca |
| Tipografia do nome | a da logo: sans arredondada pesada, tipo groovy/retrô | arquivo em mãos desde 19/09/2026; 10 alternativas em `assets/banners/v4-fontes/` |
| Símbolo / logo desenhado | não há símbolo separado — a logo é wordmark, com os dois "o" de "cookies" virando cookies | **temporária** (19/09/2026) |
| Cor da marca (azul) | `#BADCFF` azul-claro | adotado 19/09/2026, aguarda confirmação escrita da Izana |
| Cor da marca (traço) | `#622F2E` vinho escuro | adotado 19/09/2026, é a cor da letra da logo |
| Cor de apoio | `#F6E8D8` creme | usada no kit v2 |
| Cor de apoio | `#8B5A3C` chocolate médio | usada nas gotas e ilustrações |
| Cidade / praça | — | **PENDENTE** |
| @ do Instagram | — | **PENDENTE** |

Registro no INPI: **fora de escopo** por decisão do Miquéias (19/09/2026). Não levantar de novo.

### 1.1 A logo — **temporária**

Arquivo recebido da Ana Carla em 19/09/2026 e salvo em
`assets/logo/logo-izana-cookies-temporaria.jpg` (1280×1280, JPG).
Continua **temporária**: vai ser trocada, não é identidade fechada e não se gera aplicação
definitiva em cima dela sem perguntar.

Composição do arquivo recebido — **é um wordmark, sem símbolo desenhado**:

- **"IZANA"** na primeira linha, caixa alta, sans-serif muito pesada, arredondada, de bojo
  largo e cantos cheios — tipo *groovy/retrô*, com as hastes engrossando nas pontas.
- **"cookies"** na segunda linha, menor, caixa baixa, mesma família arredondada.
- Os dois **"o"** de "cookies" são **cookies desenhados** — disco claro com gotas de
  chocolate e contorno marrom. É o único elemento ilustrado da logo.
- **Não é serif, não é manuscrita** — bate com a direção já aprovada.

Cores medidas no arquivo:

| Papel | Hex |
|---|---|
| Fundo da versão recebida | `#BADCFF` azul-claro |
| Letra e traço | `#622F2E` vinho escuro |

**PENDENTE:** versão com fundo transparente; versão monocromática para aplicação em uma
cor só.

**Histórico — logo anterior (descrita em 19/09/2026, substituída no mesmo dia):** duas
meninas de rosto colado segurando juntas um cookie grande, traço de contorno grosso, sobre
fundo preto, com respingos azul e vermelho. O arquivo dela nunca chegou. A duas irmãs de
mãos no mesmo cookie voltou no kit v2, como ilustração de linha, não como logo.

### 1.2 Logo v2 — mordida e gotas em coração (19/09/2026)

Pedido da Ana Carla: manter o wordmark e os dois "o" de cookies virando cookies, com duas
mudanças:

- o **segundo cookie leva uma mordida** arredondada na borda superior direita, continuando
  legível como letra "o"; o primeiro fica inteiro;
- **toda gota de chocolate vira um coraçãozinho**, na logo e em todo o material derivado.

Três versões em `marketing/marca/identidade-v2/` (op1, op2, op3), aguardando a escolha dela.
A **op1** foi a base usada para gerar o resto do kit.

O **azul `#BADCFF` entra na paleta** por essa mesma decisão — ela pediu o kit inteiro a
partir da logo azul. Confirmação escrita ainda pendente.

**O cookie mordido virou assinatura curta da marca:** serve para assinar peça pequena sem a
logo inteira (plaquinha da fachada, adesivo, padronagem).

**Mascote:** duas propostas geradas, ambas o próprio cookie com rosto, bochecha rosada e
gotas em coração — uma inteira e uma mordida. Escolha **PENDENTE**.

### 1.2.1 Mexer na logo é editar o arquivo, não redesenhar (19/09/2026)

Pedido da Ana Carla: os cookies da logo têm de continuar **exatamente** como estão, mudando
só as gotas e a mordida. Por isso a versão v3 não é gerada por modelo de imagem — o script
`marketing/marca/identidade-v2/_logo_v3.py` abre o arquivo original, troca as 14 gotas por
corações no mesmo centro e tamanho, recorta a mordida, e deixa **o resto pixel a pixel
igual**. Cores e espessura são medidas do próprio arquivo.

Modelo de imagem serve para aplicação — mockup, foto, peça. Para a marca em si ele aproxima,
e aproximar uma logo é perdê-la.

Três versões em `marketing/marca/identidade-v2/logo-v3-mordida-{1-menor,2-media,3-maior}.png`,
aguardando a escolha dela.

### 1.2.2 A padronagem miúda (19/09/2026)

A família de desenhinhos de linha — cookies, as duas irmãs, pilha com laço, flores, corações
e os pacotes de ingrediente — é a **textura da marca**. Aparece miúda e repetida na lateral
da sacola, no adesivo comprido e no papel manteiga, sempre no vinho `#622F2E`, nunca no
chocolate claro. Em miniatura os pacotes vão **sem rótulo**: texto minúsculo é onde a grafia
quebra, e naquela escala não se lê mesmo.

### 1.3 Embalagem — regra permanente (19/09/2026)

Embalagem de cookie **não esconde e não encosta no recheio de cima**. Base baixa de papelão
segurando o cookie e tampa transparente alta, com folga de ar entre o swirl e o plástico.
Vale para qualquer embalagem futura: o topo brilhante é o produto.

### Dona e decisão
Izana é a dona e decide — inclusive operando a skill sozinha, na máquina dela.
O Miquéias opera também e aprova a copy antes de virar arte.
Toda peça pronta vai para os dois pelo WhatsApp.

Quando a Izana decidir algo (nome, fonte, cor, sabor novo, preço), registre aqui na hora,
com a data, e avise o Miquéias na próxima conversa com ele.

---

## 2. Texto aprovado para peça impressa

```
Aqui tem
cookie recheado
<NOME DA MARCA>
```

A marca é o maior elemento da peça; as duas linhas de cima são subordinadas a ela.

### Regras de copy — todas vieram de reprovação real

- **Sem frase de impacto.** Reprovadas em bloco: "Grosso, macio e cheio por dentro",
  "Os cookies mais recheados da cidade", "O recheio faz a diferença", "Aqui o recheio não é
  enfeite". O que funciona é **nomear o produto**, não vendê-lo com adjetivo.
- **Sem marca de terceiros.** Nada de Nutella nem Notella em peça impressa.
- **Sem escassez inventada.** Nada de "edição limitada", quantidade por dia, data ou preço
  numa peça permanente.
- **Sem claim de processo.** Não é feito na hora; não escrever que é.
- **Genérico e permanente.** A banca troca de sabor; a peça não pode depender de um.
- **Copy nova é aprovada pelo Miquéias ANTES de virar imagem.**
- **O que foi dito para a legenda NÃO entra na arte.** (19/09/2026) Quando ele escrever o
  texto do post na conversa — "Hoje tem feira", endereço, horário, o que for — aquilo é
  **legenda**. A imagem fica só com a fotografia. Ele não precisa repetir "isso é legenda"
  a cada peça: se o texto veio ditado no pedido, o lugar dele é a legenda.
  **Motivo:** a foto sem data e sem endereço serve na semana seguinte; a legenda se
  reescreve em dez segundos. Texto cravado na imagem joga a peça fora junto com o recado.
  Peça impressa (banner, cardápio, etiqueta) é outra coisa e segue a seção 2.

---

## 3. Produto

Argumento de venda: **a maioria dos cookies tem recheio dentro.**

### Sabores confirmados — vistos em foto ou vídeo reais

| Sabor | Descrição | Referência real |
|-------|-----------|-----------------|
| Chocolate com creme de avelã | massa de chocolate, swirl brilhante no topo, gotas de chocolate | `assets/referencias/foto-real-cookie-nutella.jpg` |
| Creme branco | massa dourada com gotas, recheio branco cremoso e abundante, polvilhado por cima | `assets/referencias/foto-real-cookie-creme-branco.jpg` |
| Chocolate com wafer branco | massa de chocolate, barra de wafer branco e chocolate ao leite no topo | só em vídeo de baixa resolução |
| Cookies e creme | massa clara com pedaço de biscoito preto e gotas de chocolate; dentro, biscoito inteiro, chocolate branco e creme branco que escorre | entrou em 19/09/2026 por decisão da Ana Carla, a partir de `marketing/referencias/ref-02/`; ficha em `marketing/produto/fichas-tecnicas/cookie-cookies-e-creme.md`. Nome comercial **PENDENTE** |

**PENDENTE:** catálogo completo com o nome comercial de cada sabor.

**Sabores que a IA inventou e NÃO existem:** pistache, red velvet, biscoito tipo Lotus.
Apareceram sozinhos em gerações de composição e foram removidos. Nunca reintroduzir.

---

## 4. Referência estrutural da peça

Nasceu do banner do stand **Berry Dubai BC** (`assets/referencias/ref-banner-berry-dubai.jpg`),
achado num reel do Instagram e destrinchado frame a frame.

Estrutura em 5 níveis, de cima para baixo:

1. Linha pequena em serif, caixa mista
2. Linha grande em serif, na cor de destaque
3. Linha pequena em sans caixa alta, tracking largo, com filete de cada lado
4. Nome grande — no original é o produto; **no nosso caso é a marca**
5. Foto grande do produto ocupando a metade de baixo, com elementos sangrando nas laterais

O que faz a peça funcionar não é a frase: é **nomear o produto e mostrá-lo grande**.

---

## 5. Histórico

Sessão de 19/09/2026: 18 fotos de produto e 44 gerações de banner, em 6 rodadas.
As pastas de reprovados em `assets/banners/` são propositais — cada uma registra um erro
que não deve voltar:

| Pasta | O erro registrado |
|-------|-------------------|
| `v1-reprovados` | marca de terceiros, escassez, "feito na hora", sabor único |
| `v2-reprovados` | cookies abertos, secos e esfarelados |
| `v3-texto-aprovado` | frases de impacto forçadas |
| `v4-fontes` | as 10 opções de tipografia, aguardando escolha |
