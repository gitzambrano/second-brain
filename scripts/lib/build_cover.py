"""Assa o retrato estático do mapa que ilustra a capa do Atlas.

O enfeite da capa precisa ser o mapa de verdade, não uma imitação. A versão
anterior baixava `graph.json` (851 KB) na página inicial e refazia o desenho em
JavaScript a partir de uma amostra de 300 nós — outro layout, outro contorno,
metade das arestas. Era mais pesado que o mapa que representava e não se
parecia com ele.

Aqui o retrato é capturado do próprio `graph.html` já construído, num navegador
headless, com o mesmo código de desenho, o mesmo layout e as mesmas arestas.
Sai um PNG por tema. O fundo é opaco e igual ao da página, então a imagem
assenta sem costura nenhuma e dispensa transparência — que só serviria para
recortar as bordas anti-aliased dos nós.

Sem Playwright instalado a função não é um erro: devolve `None` e o build
mantém o PNG anterior. Assar a capa é passo de publicação, não pré-requisito
para gerar o site.
"""
from pathlib import Path

# Tem de bater com o fundo real das duas superfícies, senão a moldura opaca
# aparece. Verificado no navegador: body e canvas pintam a mesma cor.
FUNDOS = {"light": "#ffffff", "dark": "#090909"}

# O <canvas> some por baixo de tudo o que é interface: painel, botões, o
# seletor de mapa. A captura é só do desenho.
CHROME = "#panel, #panel-toggle, #export-svg-popover, #modal-overlay, #reader-overlay, #sb-back, #sb-map-switch"

# Captura num viewport de desktop e reduz: o mapa se enquadra sozinho ao
# viewport, então capturar direto na caixinha da capa engordaria os nós até
# virarem bolhas. Capturar grande e reduzir preserva a forma real e a malha
# inteira de arestas.
LARGURA, ALTURA = 2200, 1376  # 16:10, a proporção da caixa na capa
SAIDA = (1100, 688)           # 550x344 CSS em tela retina
CORES = 192                   # paleta indexada, generosa: o degradê dos nós
                              # e o cinza fino das arestas não fecham em 64
FOLGA = 0.03                  # respiro em volta do desenho, em fração do lado


def render(site_root, largura=LARGURA, altura=ALTURA, saida=SAIDA, espera=6000):
    """Grava assets/cover-<tema>.png a partir de site/graph.html.

    Devolve a lista de (nome, KB) gravados, ou None se o navegador headless
    não estiver disponível.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    origem = Path(site_root) / "graph.html"
    if not origem.is_file():
        return None
    destino = Path(site_root) / "assets"
    destino.mkdir(parents=True, exist_ok=True)

    escritos = []
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        try:
            for tema, fundo in FUNDOS.items():
                ctx = navegador.new_context(
                    viewport={"width": largura, "height": altura},
                )
                ctx.add_init_script(
                    "try{localStorage.setItem('sb-theme',%r)}catch(e){}" % tema
                )
                # A interface é escondida ANTES da carga, e não depois: o
                # `fitToScreen` do mapa enquadra contando com o painel lateral
                # ocupando a tela, e capturar com ele oculto depois do
                # enquadramento jogava o desenho para a direita.
                ctx.add_init_script(
                    "document.addEventListener('DOMContentLoaded',function(){"
                    "var e=document.createElement('style');"
                    "e.textContent=%r+'{display:none!important}';"
                    "document.head.appendChild(e)})" % CHROME
                )
                pagina = ctx.new_page()
                pagina.goto(origem.resolve().as_uri(), wait_until="load")
                # O layout chega pronto do Python (compute_layout, seed fixa),
                # mas o enquadramento é feito por ticks da simulação: a espera
                # é para capturar o mapa já assentado, que é o que o leitor vê
                # ao abrir a página.
                pagina.wait_for_timeout(espera)
                alvo = destino / f"cover-{tema}.png"
                pagina.locator("canvas#graph").screenshot(path=str(alvo))
                ctx.close()
                _enxugar(alvo, saida, fundo)
                escritos.append((alvo.name, alvo.stat().st_size / 1024))
        finally:
            navegador.close()
    return escritos


def _enxugar(caminho, saida, fundo):
    """Recorta no desenho, recentraliza no quadro e indexa a paleta.

    O recorte pelo conteúdo é o que garante o centro: não depende de o
    enquadramento do mapa ter acertado a margem, e de quebra devolve ao desenho
    o espaço que sobrava nas bordas.

    Sem dithering de propósito — num mapa, que é fundo chapado com pontos, o
    ruído do dithering destrói a compressão do PNG sem ganho visível.
    """
    from PIL import Image, ImageChops

    imagem = Image.open(caminho).convert("RGB")
    cor = tuple(int(fundo[i:i + 2], 16) for i in (1, 3, 5))
    caixa = ImageChops.difference(imagem, Image.new("RGB", imagem.size, cor)).getbbox()
    if caixa:
        imagem = imagem.crop(caixa)

    largura, altura = saida
    folga = 1 - 2 * FOLGA
    escala = min(largura * folga / imagem.width, altura * folga / imagem.height)
    desenho = imagem.resize(
        (max(1, round(imagem.width * escala)), max(1, round(imagem.height * escala))),
        Image.LANCZOS,
    )
    quadro = Image.new("RGB", saida, cor)
    quadro.paste(desenho, ((largura - desenho.width) // 2,
                           (altura - desenho.height) // 2))
    quadro.quantize(colors=CORES, method=Image.MEDIANCUT, dither=Image.NONE).save(
        caminho, optimize=True
    )


def main():
    from repo_paths import SITE_ROOT

    resultado = render(SITE_ROOT)
    if resultado is None:
        print("cover: SKIP — Playwright indisponível ou graph.html ausente")
        return 0
    for nome, kb in resultado:
        print(f"  assets/{nome} ({kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
