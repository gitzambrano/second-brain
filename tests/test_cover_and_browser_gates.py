"""Regressões do navegador headless: capa, gates visuais e `--no-render`.

O job `core` da CI ficava vermelho por um encadeamento de três descuidos:
`build_site.py --no-render` chamava o gerador de capa, o gerador de capa só
sabia reconhecer "pacote Playwright ausente" (`except ImportError`) e não
"pacote presente, Chromium não baixado", e a CI não instala Chromium nesse job.
O resultado era uma exceção de navegador num build que existe justamente para
checagem estrutural e de privacidade.

Estes testes prendem as três coisas no lugar.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from conftest import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

import sanity_common  # noqa: E402


def _build_cover():
    import build_cover

    return build_cover


def test_resolve_chromium_names_every_outcome(monkeypatch):
    """Os quatro desfechos são distinguíveis, não um `None` mudo."""
    states = {
        sanity_common.PLAYWRIGHT_ABSENT,
        sanity_common.CHROMIUM_MANAGED,
        sanity_common.CHROMIUM_SYSTEM,
        sanity_common.CHROMIUM_ABSENT,
    }
    assert len(states) == 4

    state, executable, detail = sanity_common.resolve_chromium()
    assert state in states
    assert detail
    if state in (sanity_common.CHROMIUM_MANAGED, sanity_common.CHROMIUM_SYSTEM):
        assert executable and Path(executable).exists()
    else:
        assert executable is None


def test_missing_playwright_package_is_a_clean_skip(monkeypatch, tmp_path):
    build_cover = _build_cover()
    monkeypatch.setattr(
        build_cover,
        "resolve_chromium",
        lambda: (sanity_common.PLAYWRIGHT_ABSENT, None, "pacote playwright não instalado"),
    )
    result = build_cover.render(tmp_path)
    assert not result.ok
    assert result.reason == sanity_common.PLAYWRIGHT_ABSENT
    assert result.written == []


def test_installed_playwright_without_chromium_is_a_clean_skip(monkeypatch, tmp_path):
    """O caso que quebrava a CI: pacote presente, browser não baixado.

    O código antigo só capturava `ImportError`, então aqui ele chegava a
    `p.chromium.launch()` e explodia.
    """
    build_cover = _build_cover()
    monkeypatch.setattr(
        build_cover,
        "resolve_chromium",
        lambda: (sanity_common.CHROMIUM_ABSENT, None, "sem browser; rode playwright install"),
    )
    (tmp_path / "graph.html").write_text("<html></html>", encoding="utf-8")

    result = build_cover.render(tmp_path)
    assert not result.ok
    assert result.reason == sanity_common.CHROMIUM_ABSENT
    assert "playwright install" in result.detail
    assert not (tmp_path / "assets").exists(), "skip não deve criar diretório de saída"


def test_a_system_chromium_is_accepted_as_a_fallback(monkeypatch, tmp_path):
    """Chrome do sistema serve quando o browser gerenciado não foi baixado."""
    build_cover = _build_cover()
    fake = tmp_path / "chrome"
    fake.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        build_cover,
        "resolve_chromium",
        lambda: (sanity_common.CHROMIUM_SYSTEM, str(fake), f"chromium do sistema em {fake}"),
    )
    # Sem graph.html o render para antes de abrir o navegador; o que importa
    # aqui é que o estado SYSTEM não é tratado como ausência.
    result = build_cover.render(tmp_path)
    assert result.reason == "graph-absent"


def test_cover_result_still_iterates_like_a_list(tmp_path):
    build_cover = _build_cover()
    result = build_cover.CoverResult("ok", "x", "y", [("cover-dark.png", 42.0)])
    assert result.ok
    assert list(result) == [("cover-dark.png", 42.0)]
    assert len(result) == 1


def test_no_render_build_never_touches_the_browser():
    """`--no-render` é build lógico: não pode importar nem chamar build_cover."""
    source = (ROOT / "scripts" / "build_site.py").read_text(encoding="utf-8")
    marker = "if no_render:"
    assert marker in source
    tail = source[source.index(marker):]
    head, _, rest = tail.partition("else:")
    assert "build_cover" not in head, "a capa foi assada no ramo --no-render"
    assert "import build_cover" in rest, "a capa deve viver só no ramo com render"


@pytest.mark.parametrize(
    "script", ["check_html_browser.py", "check_site_pages.py"]
)
def test_visual_gates_resolve_the_browser_through_the_shared_helper(script):
    """Uma única definição de 'existe Chromium aqui', não três cópias."""
    source = (ROOT / "scripts" / script).read_text(encoding="utf-8")
    assert "resolve_chromium()" in source
    assert "chromium-browser" not in source, "busca de executável duplicada"
