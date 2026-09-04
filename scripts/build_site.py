#!/usr/bin/env python3
"""
Compila o Jardim Digital público em SITE_ROOT a partir da allowlist de publicação.

O site é uma projeção de mão única. O catálogo e o mapa cobrem a base inteira;
só um essay autorizado com ``visibility: public`` (ou o legado ``publish:
true``) tem o texto renderizado, indexado para busca ou linkado. Nada mais do
repositório privado de dados é copiado, nunca.

Default sem argumentos: reconstruir o site inteiro.
    --manifest   imprime o que seria publicado, não escreve nada
    --check      confere um site existente contra a allowlist atual
    --no-render  pula a renderização do Pandoc (só estrutura e índice)
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

import build_public_map
from repo_paths import CODE_ROOT, OUTPUT_DIR, SITE_ROOT, SITE_SRC_DIR
from site_common import (
    collect_all,
    collect_public,
    plain_text,
    public_body_for_index,
)

GENERATED_ROOT_FILES = {
    "index.html", "graph.html", "sphere.html", "404.html",
    "graph.json", "search-index.json", "site-manifest.json",
}
GENERATED_DIRS = {"essays", "assets"}
FRONTEND_ASSETS = ("site.css", "theme.js", "site.js", "essay.js")

# O ícone do Atlas, assado por `build_favicons.py` a partir da arte-mestra em
# `site_src/brand/`. Copiado como está: são binários versionados, não gerados
# no build — assar exige Pillow e a arte de 1024px, e nenhum dos dois deveria
# ser pré-requisito para publicar.
BRAND_ASSETS = (
    "favicon.ico",
    "icon-16.png",
    "icon-32.png",
    "icon-32-dark.png",
    "icon-light-192.png",
    "icon-dark-192.png",
    "icon-light-512.png",
    "icon-dark-512.png",
    "apple-touch-icon.png",
)

# The essay template loads MathJax from a local asset so the reader never
# depends on a third-party CDN (blocked on some mobile networks/ad-blockers,
# which left equations as raw LaTeX). The source is the same single copy shared
# by the graph/HTML readers; it is fetched at build time, not at read time.
MATHJAX_URL = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg-full.js"
MATHJAX_SHARED_CACHE = OUTPUT_DIR / "graph" / "_mathjax_cache.js"
MATHJAX_DEST = "assets/mathjax/tex-svg.js"


def ensure_site_mathjax(root: Path) -> bool:
    """Serve a local MathJax bundle under SITE_ROOT/assets/mathjax/tex-svg.js.

    Reuses the shared graph/HTML reader cache when present, otherwise downloads
    from the CDN. Returns False (with a warning) only when neither is available,
    in which case equations fall back to raw LaTeX — same tolerated behaviour as
    the standalone HTML export.
    """
    if (root / MATHJAX_DEST).exists() and (root / MATHJAX_DEST).stat().st_size > 100_000:
        return True
    try:
        if MATHJAX_SHARED_CACHE.exists() and MATHJAX_SHARED_CACHE.stat().st_size > 100_000:
            src = MATHJAX_SHARED_CACHE.read_text(encoding="utf-8", errors="replace")
        else:
            with urllib.request.urlopen(MATHJAX_URL, timeout=60) as resp:
                src = resp.read().decode("utf-8", errors="replace")
            MATHJAX_SHARED_CACHE.parent.mkdir(parents=True, exist_ok=True)
            MATHJAX_SHARED_CACHE.write_text(src, encoding="utf-8")
    except Exception as e:  # noqa: BLE001 - offline build degrades gracefully
        print(f"  aviso: MathJax local indisponível ({e}); fórmulas ficarão como LaTeX cru.")
        return False
    dest = root / MATHJAX_DEST
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(src, encoding="utf-8")
    return True

# Fields that would turn a map node into readable body content or into a pointer
# at the private repository. `htmlFile` is the read link and is checked on its own.
GRAPH_PRIVATE_FIELDS = ("file", "body", "text", "path")


def require_site_root(root: Path) -> None:
    """Refuse to write anywhere that is not a marked site checkout."""
    if not root.is_dir():
        raise SystemExit(f"SITE_ROOT does not exist: {root}")
    if not (root / ".second-brain-site").exists():
        raise SystemExit(f"refusing to write without .second-brain-site marker: {root}")


def _unlink(path: Path, attempts: int = 5) -> None:
    """Delete a file, retrying briefly through a sync tool's transient lock."""
    for attempt in range(attempts):
        try:
            if path.exists():
                path.unlink()
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.3)


def _empty(directory: Path) -> None:
    """Remove everything inside a directory, keeping the directory itself.

    The checkout usually lives in a syncing folder (OneDrive/Dropbox) that holds
    a handle on directories it is watching, so `rmtree` fails on the folder even
    after its contents are gone. Emptying is equivalent here — the build
    repopulates the directory immediately — and never trips on that handle.
    """
    if not directory.is_dir():
        return
    for child in sorted(directory.iterdir(), key=lambda p: len(p.parts), reverse=True):
        if child.is_dir():
            _empty(child)
            try:
                child.rmdir()
            except OSError:
                pass
        else:
            _unlink(child)


def clean(root: Path) -> None:
    require_site_root(root)
    for name in GENERATED_ROOT_FILES:
        _unlink(root / name)
    for name in GENERATED_DIRS:
        _empty(root / name)


def ensure_site_fonts(root: Path) -> str:
    """Auto-hospeda a Inter variável e devolve os blocos `@font-face`.

    `--sans` do site sempre começou em Inter, mas nada nunca a servia: a página
    caía em Segoe UI ou Roboto, onde o eixo de peso é discreto e 500, 550 e 600
    renderizam exatamente o mesmo Semibold. Não havia como pedir um negrito
    intermediário porque a fonte que o tem nunca chegava.

    Sem rede o passo é pulado e o site volta ao comportamento anterior — a
    fonte é melhoria de tipografia, não pré-requisito de build.
    """
    from fetch_fonts import SITE_CSS_URL, ensure_local_fonts

    css_path = ensure_local_fonts(root / "assets", css_url=SITE_CSS_URL, dirname="fonts")
    if css_path is None:
        print("  fontes: SKIP (sem rede); o site usa a fonte do sistema")
        return ""
    return css_path.read_text(encoding="utf-8")


def font_face_css(blocks: str, prefix: str) -> str:
    """Reescreve `url(x.woff2)` para o caminho relativo de quem vai usar.

    O `fonts.css` do cache guarda referências relativas a si mesmo. A folha do
    catálogo é servida como `assets/site.css` (base: `assets/`), e a do essay é
    embutida em `essays/<slug>.html` (base: `essays/`). Dois prefixos, mesmos
    blocos.
    """
    if not blocks:
        return ""
    return re.sub(r"url\(([^)/][^)]*\.woff2)\)", lambda m: f"url({prefix}{m.group(1)})", blocks)


def copy_frontend(root: Path, fonts: str = "") -> dict[str, str]:
    """Copy the frontend and return a content fingerprint per asset.

    A browser that has visited before will happily keep serving the previous
    CSS and JS after a redeploy. Versioning each URL by content makes a changed
    asset a different URL, so a stale mix can never happen.
    """
    assets = root / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    fingerprints = {}
    for name in FRONTEND_ASSETS:
        source = SITE_SRC_DIR / name
        payload = source.read_bytes()
        if name == "site.css" and fonts:
            merged = font_face_css(fonts, "fonts/") + "\n" + source.read_text(encoding="utf-8")
            payload = merged.encode("utf-8")
        (assets / name).write_bytes(payload)
        # O fingerprint segue o conteúdo SERVIDO, não o do fonte: com a fonte
        # embutida os dois deixam de ser o mesmo arquivo.
        fingerprints[name] = hashlib.sha256(payload).hexdigest()[:8]

    brand = SITE_SRC_DIR / "brand"
    for name in BRAND_ASSETS:
        source = brand / name
        if source.is_file():
            (assets / name).write_bytes(source.read_bytes())
    return fingerprints


def version_assets(html_text: str, fingerprints: dict[str, str]) -> str:
    """Rewrite `assets/<name>` references to carry the content fingerprint."""
    for name, digest in fingerprints.items():
        html_text = html_text.replace(f"assets/{name}\"", f"assets/{name}?v={digest}\"")
    return html_text


WORDS_PER_MINUTE = 220

# A formula is read, not scanned word by word; counting `rac{a}{b}` as five
# words turned a 30-minute essay into a 100-minute one.
#
# A ordem das alternativas é a correção do bug: matemática de DISPLAY
# (`$$...$$` e `\[...\]`) precisa casar ANTES da inline. Com o padrão antigo
# `\$[^$]{1,400}\$`, um bloco `$$...$$` nunca casava inteiro — a classe `[^$]`
# barra o segundo cifrão —, então o motor casava `$<fórmula>$` e sobrava um
# cifrão ÓRFÃO, que em seguida pareava com o cifrão de ABERTURA do bloco
# seguinte. Toda a prosa entre duas fórmulas era engolida como se fosse
# fórmula: um essay de 3195 palavras contava 665 e virava "3 min".
#
# A inline também não pode atravessar quebra de linha: fórmula inline vive numa
# linha só, enquanto dois cifrões distantes quase sempre têm prosa — e parágrafo
# — no meio. `[^$\n]` transforma esse caso em não-casamento, que apenas deixa um
# cifrão solto na contagem, em vez de silenciar páginas inteiras.
MATH_SPAN = re.compile(
    r"\$\$[\s\S]{1,2000}?\$\$"       # display do corpus: $$ ... $$
    r"|\\\[[\s\S]{1,2000}?\\\]"      # display alternativo: \[ ... \]
    # Inline: `$x$`, numa linha só e sem espaço colado aos delimitadores. A
    # borda sem espaço é o que separa fórmula de dinheiro: em "R$ 50.000 e R$
    # 500.000" os dois cifrões são moeda, e sem essa guarda a prosa entre eles
    # sumiria da contagem exatamente como sumia entre dois blocos de display.
    r"|\$(?!\$)[^\s$](?:[^$\n]{0,397}[^\s$])?\$"
)
CODE_SPAN = re.compile(r"`[^`]{1,200}`")


def reading_minutes(text: str) -> int:
    """Rounded reading time over prose alone, never below one minute."""
    prose = CODE_SPAN.sub(" ", MATH_SPAN.sub(" ", text))
    return max(1, round(len(prose.split()) / WORDS_PER_MINUTE))


def write_data(root: Path, catalogue) -> dict[str, int]:
    """Write the machine files.

    The catalogue lists every essay, because the index does. Only an authorized
    essay contributes its body: `text` powers full-text search and exists solely
    for pages a reader can actually open.
    """
    # O índice é um CATÁLOGO, não um corpus. A busca da capa filtra os cartões
    # que já estão no DOM (`card.dataset.search`), então ninguém jamais baixou
    # este arquivo — e ele carregava o texto integral de todos os essays, 2,2 MB
    # servidos para nenhum leitor. Se um dia a busca virar full-text, o corpo
    # volta aqui de propósito e com o gate de privacidade acompanhando.
    allowed = {e.slug for e in catalogue if e.published}
    body_text = {
        e.slug: plain_text(public_body_for_index(e, allowed))
        for e in catalogue if e.published
    }

    search = []
    for essay in catalogue:
        entry = {
            "slug": essay.slug,
            "title": essay.title,
            "summary": essay.summary,
            "tags": list(essay.tags),
            "updated": essay.updated,
            "created": essay.created,
            "status": essay.status,
            "published": essay.published,
        }
        if essay.published:
            entry["minutes"] = reading_minutes(body_text[essay.slug])
            entry["url"] = f"essays/{essay.slug}.html"
        search.append(entry)

    def dump(name: str, data) -> None:
        (root / name).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    dump("search-index.json", search)
    dump("site-manifest.json", {
        "generated": date.today().isoformat(),
        "published": sorted(allowed),
        "count": len(allowed),
        "catalogue": len(catalogue),
    })
    return {slug: reading_minutes(text) for slug, text in body_text.items()}


def render_index(root: Path, catalogue, minutes: dict[str, int] | None = None,
                 fingerprints: dict[str, str] | None = None) -> None:
    """Render the catalogue: every essay, with only the authorized ones linked."""
    minutes = minutes or {}
    template = (SITE_SRC_DIR / "index.html").read_text(encoding="utf-8")
    tags = sorted({t for e in catalogue for t in e.tags}, key=str.casefold)
    tag_counts = {t: sum(1 for e in catalogue if t in e.tags) for t in tags}
    latest = sorted(catalogue, key=lambda e: e.updated or e.created, reverse=True)
    published = [e for e in catalogue if e.published]

    cards = []
    for essay in latest:
        tag_html = "".join(
            f'<span class="tag">{html.escape(t)}</span>' for t in essay.tags
        )
        # The search haystack is pre-folded so the client only lowercases input.
        searchable = html.escape(
            " ".join([essay.title, essay.summary, *essay.tags]).casefold(), quote=True
        )

        meta = [f'<span>{html.escape(essay.updated)}</span>']
        reading = minutes.get(essay.slug, 0)
        if reading:
            meta.append('<span class="dot" aria-hidden="true">·</span>'
                        f'<span>{reading} min de leitura</span>')

        badges = []
        if not essay.published:
            badges.append('<span class="badge badge-private">Privado</span>')
        if essay.status == "draft":
            badges.append('<span class="badge badge-draft">Rascunho</span>')
        elif essay.status == "revisao":
            badges.append('<span class="badge badge-review">Em revisão</span>')
        badge_html = f'<div class="badges">{"".join(badges)}</div>' if badges else ""

        # The title carries the link and stretches over the whole card (see
        # site.css); the expander is a sibling, never nested inside a link.
        if essay.published:
            title_html = (f'<a href="essays/{html.escape(essay.slug)}.html">'
                          f'{html.escape(essay.title)}</a>')
            read_html = ('<span class="read-link">Ler essay '
                         '<span aria-hidden="true">&rarr;</span></span>')
        else:
            # No link: the text is not published, and the card must not pretend.
            title_html = html.escape(essay.title)
            read_html = '<span class="read-link is-muted">Não publicado</span>'

        body = (
            f'<div class="card-head">'
            f'<div class="card-meta">{"".join(meta)}</div>{badge_html}</div>'
            f'<h3 class="card-title">{title_html}</h3>'
            f'<p class="card-summary">{html.escape(essay.summary)}</p>'
            f'<button class="card-expand" type="button" aria-expanded="false">'
            f'<span class="card-expand-text">Resumo</span>'
            f'<i aria-hidden="true">⌄</i></button>'
            f'<div class="tags">{tag_html}</div>'
            f'{read_html}'
        )

        cards.append(
            f'<article class="essay-card{"" if essay.published else " is-private"}"'
            f' data-search="{searchable}"'
            f' data-tags="{html.escape("|".join(essay.tags), quote=True)}"'
            f' data-updated="{html.escape(essay.updated, quote=True)}"'
            f' data-minutes="{reading}"'
            f' data-published="{"1" if essay.published else "0"}"'
            f' data-status="{html.escape(essay.status or "", quote=True)}"'
            f' data-title="{html.escape(essay.title, quote=True)}">'
            f'{body}</article>'
        )

    # Busiest themes first; the rest stay behind "mais temas" so the page does
    # not open with a wall of tags.
    ordered = sorted(tags, key=lambda name: (-tag_counts[name], name.casefold()))
    chips = "".join(
        f'<button class="filter-chip" type="button"'
        f' data-tag="{html.escape(name, quote=True)}">'
        f'{html.escape(name)} <span class="count">{tag_counts[name]}</span></button>'
        for name in ordered
    )
    updated = max((e.updated for e in catalogue if e.updated), default="—")

    page = (template
            .replace("{{COUNT}}", str(len(catalogue)))
            .replace("{{PUBLISHED}}", str(len(published)))
            .replace("{{TAG_COUNT}}", str(len(tags)))
            .replace("{{UPDATED}}", html.escape(updated))
            .replace("{{CARDS}}", "\n".join(cards))
            .replace("{{TAG_FILTERS}}", chips))
    (root / "index.html").write_text(
        version_assets(page, fingerprints or {}), encoding="utf-8")


def render_essays(root: Path, essays, no_render: bool = False) -> None:
    out = root / "essays"
    out.mkdir(parents=True, exist_ok=True)
    if no_render:
        return
    renderer = CODE_ROOT / "scripts" / "render_public_essay.py"
    for essay in essays:
        proc = subprocess.run(
            [sys.executable, str(renderer), essay.slug,
             "--output", str(out / f"{essay.slug}.html")],
            cwd=CODE_ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        if proc.returncode:
            raise SystemExit(proc.stdout + "\n" + proc.stderr)


def build(root: Path, no_render: bool = False):
    catalogue = collect_all()
    essays = [e for e in catalogue if e.published]
    clean(root)
    fonts = ensure_site_fonts(root)
    fingerprints = copy_frontend(root, fonts)
    ensure_site_mathjax(root)
    minutes = write_data(root, catalogue)
    render_index(root, catalogue, minutes, fingerprints)

    # The map is produced by the wiki's own renderers, on sanitized nodes.
    nodes, edges, tag_gaps, isolated = build_public_map.build()
    build_public_map.write(root, nodes, edges, tag_gaps, isolated)

    # O retrato da capa sai do graph.html recém-escrito, e por isso vem
    # depois dele. Sem navegador headless o passo é pulado e o PNG anterior
    # permanece: publicar não pode depender do Playwright estar instalado.
    #
    # `--no-render` não assa capa nenhuma. Esse modo existe para checagem
    # estrutural e de privacidade — nos testes e na CI — e um build que serve
    # para isso não pode exigir Chromium. Era o que deixava o job `core`
    # vermelho numa máquina sem browser.
    # Importado aqui, e não no topo: `scripts/lib/` só entra no sys.path
    # quando `repo_paths` é carregado, e o topo deste arquivo roda antes disso.
    if no_render:
        print("  capa: pulada (--no-render é build lógico, sem navegador)")
    else:
        import build_cover

        assado = build_cover.render(root)
        if assado.ok:
            print(f"  capa: {assado.detail}")
            for nome, kb in assado.written:
                print(f"  assets/{nome} ({kb:.0f} KB)")
        else:
            print(f"  capa: SKIP ({assado.reason}) — {assado.detail}")

    source = SITE_SRC_DIR / "404.html"
    if source.exists():
        (root / "404.html").write_text(
            version_assets(source.read_text(encoding="utf-8"), fingerprints),
            encoding="utf-8")
    # `render_public_essay.py` lê `assets/fonts/fonts.css` direto do site já
    # montado — por isso `ensure_site_fonts` roda antes daqui.
    render_essays(root, essays, no_render)
    return essays


def check(root: Path) -> list[str]:
    """Verify a built site still matches the current allowlist exactly."""
    require_site_root(root)
    allowed = {e.slug for e in collect_public()}
    errors: list[str] = []

    manifest = root / "site-manifest.json"
    if not manifest.exists():
        errors.append("missing site-manifest.json")
    else:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        if set(payload.get("published", [])) != allowed:
            errors.append("manifest differs from current publish:true allowlist")

    # The catalogue lists every essay. Body text and a page link belong only to
    # the authorized ones.
    search = root / "search-index.json"
    if search.exists():
        for entry in json.loads(search.read_text(encoding="utf-8")):
            slug = entry.get("slug")
            if entry.get("published") and slug not in allowed:
                errors.append(f"entry marked published but not authorized: {slug}")
            if not entry.get("published"):
                if entry.get("text"):
                    errors.append(f"body text exposed for unpublished essay: {slug}")
                if entry.get("url"):
                    errors.append(f"unauthorized link in search index: {slug}")

    # The map deliberately contains every node. What it must never contain is
    # body text, a private path, or a way into anything outside the allowlist.
    graph = root / "graph.json"
    if graph.exists():
        payload = json.loads(graph.read_text(encoding="utf-8"))
        for node in payload.get("nodes", []):
            node_id = node.get("id")
            slug = str(node_id or "").partition(":")[2]
            readable = bool(node.get("public"))
            if readable and slug not in allowed:
                errors.append(f"node marked public but not authorized: {node_id}")
            link = str(node.get("htmlFile") or "")
            if link and (not readable or link != f"essays/{slug}.html"):
                errors.append(f"unauthorized read link in map: {node_id} -> {link}")
            url = str(node.get("url") or "")
            if url and not url.startswith(("http://", "https://")):
                errors.append(f"non-external url in map: {node_id} -> {url}")
            for field in GRAPH_PRIVATE_FIELDS:
                if node.get(field):
                    errors.append(f"private field '{field}' in map node {node_id}")

    essays_dir = root / "essays"
    if essays_dir.exists():
        present = {p.stem for p in essays_dir.glob("*.html")}
        extra = present - allowed
        if extra:
            errors.append(f"stale/private HTML: {sorted(extra)}")
        # A page missing is as wrong as a page too many: `--no-render` empties
        # this directory, and a site checked only for what it must NOT contain
        # would pass with every essay gone.
        missing = allowed - present
        if missing:
            errors.append(f"authorized essay without a page: {sorted(missing)}")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="validate an existing site")
    ap.add_argument("--manifest", action="store_true", help="list what would be published")
    ap.add_argument("--no-render", action="store_true", help="skip Pandoc rendering")
    args = ap.parse_args()

    if args.manifest:
        print(json.dumps(
            [{"slug": e.slug, "title": e.title} for e in collect_public()],
            ensure_ascii=False, indent=2,
        ))
        return 0

    if args.check:
        errors = check(SITE_ROOT)
        print("site: PASS" if not errors else "site: FAIL")
        for error in errors:
            print(f"  ERROR {error}")
        return 1 if errors else 0

    essays = build(SITE_ROOT, args.no_render)
    print(f"site generated: {SITE_ROOT}")
    print(f"published essays: {len(essays)}")
    for essay in essays:
        print(f"  {essay.slug} — {essay.title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
