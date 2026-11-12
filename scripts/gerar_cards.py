#!/usr/bin/env python3
"""Gera os cards SVG animados do README, nas versões clara e escura.

Uso:  python scripts/gerar_cards.py

Tudo o que aparece nos cards está na seção "Conteúdo" logo abaixo. Edite ali,
rode o script de novo e faça commit da pasta cards/. Não precisa instalar nada:
o script só usa a biblioteca padrão do Python.
"""
from html import escape
from pathlib import Path

# --------------------------------------------------------------------------
# Conteúdo
# --------------------------------------------------------------------------

PERFIL = {
    "nome": "Henrique Godoy",
    "cargo": "Software Engineer",
    "janela": "henrique@github: ~",
    "sobre": [
        "19 anos · estudante de Engenharia de Software na Unaerp",
        "Apaixonado por tecnologia e focado em aplicações modernas.",
    ],
}

# Monograma em matriz de pontos no canto do hero ("#" = ponto aceso).
MONOGRAMA = [
    "#...#..###.",
    "#...#.#...#",
    "#...#.#....",
    "#####.#.###",
    "#...#.#...#",
    "#...#.#...#",
    "#...#..###.",
]

# (grupo, [(símbolo, nome, cor no tema escuro, cor no tema claro)])
STACK = [
    ("Front-end", [
        ("Js", "JavaScript", "#f7df1e", "#8a6d00"),
        ("Ts", "TypeScript", "#5b9df0", "#2f74c0"),
        ("Ht", "HTML5", "#f16529", "#d84a1b"),
        ("Cs", "CSS3", "#a56eff", "#663399"),
    ]),
    ("Back-end", [
        ("Py", "Python", "#4b8bbe", "#306998"),
        ("Nd", "Node.js", "#8cc84b", "#417e38"),
        ("C", "C", "#a8b9cc", "#5b6b80"),
    ]),
    ("Dados", [
        ("Sq", "SQL", "#2bb3c0", "#00758f"),
        ("Mg", "MongoDB", "#00ed64", "#00684a"),
    ]),
]

# (arquivo, rótulo, texto) -- os links ficam no README.md
CONTATOS = [
    ("linkedin", "LinkedIn", "/in/henrique-godoy-dos-santos"),
    ("instagram", "Instagram", "@henrique_godoy12"),
    ("email", "E-mail", "henriquegodoyds@gmail.com"),
]

# (repositório, descrição, linguagem) -- gera cards/repo-<repositório>-<tema>.svg
# Use o nome exato do repositório; o link de cada card fica no README.md.
PROJETOS = [
    ("Natacao_Unaerp",
     "Sistema do projeto de extensão Unaerp Esportes para acompanhar a evolução dos atletas de natação.",
     "TypeScript"),
    ("Portifolio",
     "Portfólio pessoal em PT/EN feito com Next.js, Tailwind CSS e Motion.",
     "TypeScript"),
    ("mobile-security",
     "App Android de sobremesas com catálogo via API, carrinho local e regras de segurança de rede.",
     "Kotlin"),
]

# --------------------------------------------------------------------------
# Visual
# --------------------------------------------------------------------------

TEMAS = {
    "dark": {
        "bg": "#0b0f14", "barra": "#10161d", "borda": "#232b36",
        "texto": "#e6edf3", "suave": "#8b949e", "fraco": "#2a333f",
        "acento": "#3ddc97",
    },
    "light": {
        "bg": "#ffffff", "barra": "#f6f8fa", "borda": "#d0d7de",
        "texto": "#1f2328", "suave": "#59636e", "fraco": "#d5dce3",
        "acento": "#0f7b53",
    },
}

CORES_LINGUAGEM = {  # (escuro, claro)
    "JavaScript": ("#f7df1e", "#8a6d00"), "TypeScript": ("#5b9df0", "#2f74c0"),
    "HTML": ("#f16529", "#d84a1b"), "CSS": ("#a56eff", "#663399"),
    "Python": ("#4b8bbe", "#306998"), "C": ("#a8b9cc", "#5b6b80"),
    "Java": ("#e76f00", "#b05800"), "C#": ("#9b6cd6", "#68217a"),
    "Kotlin": ("#a97bff", "#7f52ff"),
}

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

# O estado final de cada elemento é o estado "parado": quem pede menos
# movimento (prefers-reduced-motion) vê o card completo, sem animação.
CSS_BASE = (
    f".m{{font-family:{MONO}}}.s{{font-family:{SANS}}}"
    ".cur{opacity:0}"
    "@keyframes sobe{from{opacity:0;transform:translateY(8px)}}"
    "@keyframes surge{from{opacity:0}}"
    "@keyframes vis{from,to{opacity:1}}"
    "@keyframes pisca{0%,49%{opacity:1}50%,100%{opacity:0}}"
    "@keyframes pulsa{50%{opacity:.35}}"
    "@keyframes onda{0%,14%,100%{opacity:0}7%{opacity:1}}"
    "@keyframes cutuca{50%{transform:translate(2px,-2px)}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)

LARGURA = 880
RESPIRO = 12          # espaço transparente embaixo de cada card
CW = 9.0              # largura de um caractere no texto "digitado"
SUAVE = "cubic-bezier(.2,.7,.2,1)"


def svg(largura, altura, corpo, rotulo, css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura:.3f}" height="{altura}" '
        f'viewBox="0 0 {largura:.3f} {altura}" role="img" aria-label="{escape(rotulo, quote=True)}">'
        f"<title>{escape(rotulo)}</title><style>{CSS_BASE}{css}</style>{corpo}</svg>\n"
    )


def digitar(texto, x, y, inicio, chave, t, passo=0.075):
    """Texto que aparece letra por letra, com um cursor acompanhando.

    Cada letra tem posição fixa, então o efeito não depende da fonte de quem vê.
    Devolve (svg, css, instante em que termina).
    """
    n = len(texto)
    duracao = n * passo
    letras = "".join(
        f'<tspan x="{x + i * CW:g}" style="animation:surge .01s linear {inicio + i * passo:.2f}s both">'
        f"{escape(c)}</tspan>"
        for i, c in enumerate(texto) if c != " "
    )
    cursor = (
        f'<rect class="cur" x="{x:g}" y="{y - 14}" width="8" height="18" fill="{t["acento"]}" '
        f'style="animation:mv{chave} {duracao:.2f}s steps({n},start) {inicio:.2f}s both,'
        f'vis {duracao + 1:.2f}s linear {inicio - 0.6:.2f}s"/>'
    )
    corpo = f'<text y="{y}" class="m" font-size="15" fill="{t["texto"]}">{letras}</text>{cursor}'
    css = f"@keyframes mv{chave}{{to{{transform:translateX({n * CW:g}px)}}}}"
    return corpo, css, inicio + duracao


def hero(t):
    L, A = LARGURA, 380
    p, css = [], []

    # Janela de terminal
    p.append(f'<rect x=".5" y=".5" width="{L - 1}" height="{A - 1}" rx="14" fill="{t["bg"]}" stroke="{t["borda"]}"/>')
    p.append(f'<path d="M.5 40.5V14.5a14 14 0 0 1 14-14h{L - 29}a14 14 0 0 1 14 14v26z" '
             f'fill="{t["barra"]}" stroke="{t["borda"]}"/>')
    for cx, cor in ((24, "#ff5f57"), (44, "#febc2e"), (64, "#28c840")):
        p.append(f'<circle cx="{cx}" cy="20.5" r="6" fill="{cor}"/>')
    p.append(f'<text x="{L / 2:g}" y="25" text-anchor="middle" class="m" font-size="12" '
             f'fill="{t["suave"]}">{escape(PERFIL["janela"])}</text>')

    def prompt(y, estilo=""):
        return f'<text x="32" y="{y}" class="m" font-size="15" fill="{t["acento"]}"{estilo}>$</text>'

    # $ whoami
    p.append(prompt(80))
    corpo, k, fim = digitar("whoami", 50, 80, 0.8, 1, t)
    p.append(corpo)
    css.append(k)
    p.append(f'<text x="30" y="146" class="s" font-size="54" font-weight="800" letter-spacing="-1.5" '
             f'fill="{t["texto"]}" style="animation:sobe .7s {SUAVE} {fim + 0.25:.2f}s both">'
             f'{escape(PERFIL["nome"])}</text>')
    p.append(f'<text x="33" y="180" class="m" font-size="17" fill="{t["acento"]}" '
             f'style="animation:sobe .7s {SUAVE} {fim + 0.5:.2f}s both">{escape(PERFIL["cargo"])}</text>')

    # $ cat sobre.txt
    inicio = fim + 1.85
    p.append(prompt(232, f' style="animation:surge .01s linear {inicio - 0.6:.2f}s both"'))
    corpo, k, fim = digitar("cat sobre.txt", 50, 232, inicio, 2, t)
    p.append(corpo)
    css.append(k)
    for i, linha in enumerate(PERFIL["sobre"]):
        p.append(f'<text x="32" y="{266 + i * 25}" class="s" font-size="16" '
                 f'fill="{t["texto"] if i == 0 else t["suave"]}" '
                 f'style="animation:sobe .6s {SUAVE} {fim + 0.25 + i * 0.2:.2f}s both">{escape(linha)}</text>')

    # Prompt final, com o cursor piscando para sempre
    fim += 1.2
    y = 266 + len(PERFIL["sobre"]) * 25 + 24
    p.append(prompt(y, f' style="animation:surge .01s linear {fim:.2f}s both"'))
    p.append(f'<rect x="50" y="{y - 14}" width="8" height="18" fill="{t["acento"]}" '
             f'style="animation:surge .01s linear {fim:.2f}s both,pisca 1.1s linear {fim:.2f}s infinite"/>')

    # Monograma em matriz de pontos
    passo = 24
    colunas = len(MONOGRAMA[0])
    x0 = L - 36 - (colunas - 1) * passo
    y0 = 40 + (A - 40 - (len(MONOGRAMA) - 1) * passo) / 2
    for r, linha in enumerate(MONOGRAMA):
        for c, ponto in enumerate(linha):
            cx, cy = x0 + c * passo, y0 + r * passo
            if ponto == "#":
                p.append(f'<circle cx="{cx:g}" cy="{cy:g}" r="4.5" fill="{t["acento"]}" '
                         f'style="animation:surge .5s ease {0.4 + (c + r) * 0.07:.2f}s both,'
                         f'pulsa 4s ease-in-out {3 + (c + r) * 0.14:.2f}s infinite"/>')
            else:
                p.append(f'<circle cx="{cx:g}" cy="{cy:g}" r="2" fill="{t["fraco"]}"/>')

    rotulo = f'{PERFIL["nome"]}. {PERFIL["cargo"]}. ' + " ".join(PERFIL["sobre"])
    return svg(L, A + RESPIRO, "".join(p), rotulo, "".join(css))


def stack(t, tema):
    L, A = LARGURA, 212
    lado, alto, vao, vao_grupo = 80, 96, 8, 28
    p = [f'<rect x=".5" y=".5" width="{L - 1}" height="{A - 1}" rx="14" fill="{t["bg"]}" stroke="{t["borda"]}"/>']
    p.append(f'<text x="28" y="42" class="s" font-size="17" font-weight="700" fill="{t["texto"]}">'
             f"Linguagens e Tecnologias</text>")
    p.append(f'<text x="{L - 28}" y="41" text-anchor="end" class="m" font-size="12" fill="{t["suave"]}">'
             f'<tspan fill="{t["acento"]}">$</tspan> ls ~/stack</text>')

    x, y, i = 28, 64, 0
    for grupo, itens in STACK:
        inicio_grupo = x
        for simbolo, nome, escura, clara in itens:
            cor = escura if tema == "dark" else clara
            atraso = 0.15 + i * 0.09
            p.append(
                f'<g style="animation:sobe .6s {SUAVE} {atraso:.2f}s both">'
                f'<rect x="{x}.5" y="{y}.5" width="{lado - 1}" height="{alto - 1}" rx="10" '
                f'fill="{cor}" fill-opacity=".09" stroke="{cor}" stroke-opacity=".45"/>'
                f'<rect x="{x}.5" y="{y}.5" width="{lado - 1}" height="{alto - 1}" rx="10" fill="{cor}" '
                f'fill-opacity=".12" stroke="{cor}" stroke-width="1.5" opacity="0" '
                f'style="animation:onda 7s ease-in-out {2 + i * 0.16:.2f}s infinite"/>'
                f'<text x="{x + 9}" y="{y + 18}" class="m" font-size="10" fill="{t["suave"]}">{i + 1:02d}</text>'
                f'<text x="{x + lado / 2:g}" y="{y + 57}" text-anchor="middle" class="s" font-size="27" '
                f'font-weight="800" fill="{cor}">{escape(simbolo)}</text>'
                f'<text x="{x + lado / 2:g}" y="{y + 80}" text-anchor="middle" class="s" font-size="11" '
                f'fill="{t["texto"]}">{escape(nome)}</text></g>'
            )
            x += lado + vao
            i += 1
        fim_grupo = x - vao
        p.append(f'<path d="M{inicio_grupo}.5 {y + alto + 8}v5H{fim_grupo - 1}.5v-5" fill="none" stroke="{t["fraco"]}"/>')
        p.append(f'<text x="{(inicio_grupo + fim_grupo) / 2:g}" y="{y + alto + 32}" text-anchor="middle" '
                 f'class="m" font-size="11" fill="{t["suave"]}">{escape(grupo)}</text>')
        x += vao_grupo - vao

    nomes = ", ".join(nome for _, itens in STACK for _, nome, _, _ in itens)
    return svg(L, A + RESPIRO, "".join(p), f"Linguagens e Tecnologias: {nomes}")


def fatia(i):
    """Posição de um card numa fileira de três: (largura da imagem, x, largura do card)."""
    largura = LARGURA / 3
    return largura, (0, 4, 8)[i % 3], largura - 8


def seta(x, y, atraso, t):
    return (f'<g transform="translate({x:g} {y})"><path d="M1 11 11 1M4 1h7v7" fill="none" stroke="{t["acento"]}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
            f'style="animation:cutuca 2.4s ease-in-out {atraso:.2f}s infinite"/></g>')


def contato(t, i, rotulo, texto):
    largura, x, w = fatia(i)
    A = 84
    p = (
        f'<g style="animation:sobe .6s {SUAVE} {0.1 + i * 0.12:.2f}s both">'
        f'<rect x="{x}.5" y=".5" width="{w - 1:.3f}" height="{A - 1}" rx="12" fill="{t["bg"]}" stroke="{t["borda"]}"/>'
        f'<text x="{x + 18}" y="33" class="m" font-size="11" letter-spacing="1" fill="{t["suave"]}">'
        f"{escape(rotulo.upper())}</text>"
        f'<text x="{x + 18}" y="59" class="s" font-size="14.5" font-weight="600" fill="{t["texto"]}">'
        f"{escape(texto)}</text>"
        f"{seta(x + w - 32, 22, i * 0.3, t)}</g>"
    )
    return svg(largura, A + RESPIRO, p, f"{rotulo}: {texto}")


def titulo(t, texto, comando):
    """Título de seção, sem fundo, alinhado com o cabeçalho do card de stack."""
    L, A = LARGURA, 34
    p = (
        f'<text x="28" y="23" class="s" font-size="17" font-weight="700" fill="{t["texto"]}">{escape(texto)}</text>'
        f'<text x="{L - 28}" y="22" text-anchor="end" class="m" font-size="12" fill="{t["suave"]}">'
        f'<tspan fill="{t["acento"]}">$</tspan> {escape(comando)}</text>'
    )
    return svg(L, A + RESPIRO, p, texto)


def quebrar(texto, limite=36, linhas=3):
    saida, atual = [], ""
    for palavra in texto.split():
        if atual and len(atual) + 1 + len(palavra) > limite:
            saida.append(atual)
            atual = palavra
        else:
            atual = f"{atual} {palavra}".strip()
    saida.append(atual)
    if len(saida) > linhas:
        saida = saida[:linhas]
        saida[-1] = saida[-1][: limite - 1].rstrip() + "…"
    return saida


def projeto(t, tema, i, repo, descricao, linguagem):
    largura, x, w = fatia(i)
    A = 136
    escura, clara = CORES_LINGUAGEM.get(linguagem, (t["suave"], t["suave"]))
    cor = escura if tema == "dark" else clara
    linhas = "".join(
        f'<text x="{x + 18}" y="{60 + n * 19}" class="s" font-size="13" fill="{t["suave"]}">{escape(linha)}</text>'
        for n, linha in enumerate(quebrar(descricao))
    )
    p = (
        f'<g style="animation:sobe .6s {SUAVE} {0.1 + (i % 3) * 0.12:.2f}s both">'
        f'<rect x="{x}.5" y=".5" width="{w - 1:.3f}" height="{A - 1}" rx="12" fill="{t["bg"]}" stroke="{t["borda"]}"/>'
        f'<text x="{x + 18}" y="34" class="m" font-size="14" font-weight="600" fill="{t["acento"]}">{escape(repo)}</text>'
        f"{linhas}"
        f'<circle cx="{x + 23}" cy="{A - 21}" r="5" fill="{cor}" '
        f'style="animation:pulsa 3s ease-in-out {(i % 3) * 0.4:.2f}s infinite"/>'
        f'<text x="{x + 35}" y="{A - 17}" class="m" font-size="11" fill="{t["suave"]}">{escape(linguagem)}</text>'
        f"{seta(x + w - 32, 22, (i % 3) * 0.3, t)}</g>"
    )
    return svg(largura, A + RESPIRO, p, f"{repo}: {descricao}")


def main():
    pasta = Path(__file__).resolve().parent.parent / "cards"
    pasta.mkdir(exist_ok=True)
    arquivos = {}
    for tema, t in TEMAS.items():
        arquivos[f"hero-{tema}.svg"] = hero(t)
        arquivos[f"stack-{tema}.svg"] = stack(t, tema)
        for i, (arquivo, rotulo, texto) in enumerate(CONTATOS):
            arquivos[f"contato-{arquivo}-{tema}.svg"] = contato(t, i, rotulo, texto)
        if PROJETOS:
            arquivos[f"titulo-projetos-{tema}.svg"] = titulo(t, "Projetos em destaque", "ls ~/projetos")
        for i, (repo, descricao, linguagem) in enumerate(PROJETOS):
            arquivos[f"repo-{repo}-{tema}.svg"] = projeto(t, tema, i, repo, descricao, linguagem)
    for nome, conteudo in arquivos.items():
        (pasta / nome).write_text(conteudo, encoding="utf-8", newline="\n")
    print(f"{len(arquivos)} cards gerados em {pasta}")


if __name__ == "__main__":
    main()
