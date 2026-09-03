from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_public_overlay_does_not_restyle_canonical_components():
    css = (ROOT / "scripts/site_src/essay-theme.css").read_text(encoding="utf-8")
    forbidden = (
        "\nstrong {",
        "\n.content h2",
        "\n.content h3",
        "\n.box {",
        "\n.box-verdict {",
        "\n.quote {",
        "\n.pull-quote {",
        "\n.card {",
        "\ntable {",
        "\npre {",
        "\ncode {",
        "\nli::marker",
    )
    for selector in forbidden:
        assert selector not in css, selector


def test_theme_contract_and_cover_summary():
    essay = (ROOT / "scripts/site_src/essay-theme.css").read_text(encoding="utf-8").lower()
    atlas = (ROOT / "scripts/site_src/atlas-theme.css").read_text(encoding="utf-8").lower()
    template = (ROOT / "scripts/essay_template.html").read_text(encoding="utf-8")
    for css in (essay, atlas):
        assert "#2f5fb0" in css
        assert "#c9a45c" in css
        assert "#ffffff" in css
        assert "#090909" in css
    assert 'class="cover-summary"' in template
    assert "$summary$" in template


def test_library_contract():
    index = (ROOT / "scripts/site_src/index.html").read_text(encoding="utf-8")
    script = (ROOT / "scripts/site_src/site.js").read_text(encoding="utf-8")
    assert "sort-wrap" not in index
    assert "Finalizados · públicos · recentes" in index
    assert "statusRank(b) - statusRank(a)" in script
    assert ".card-summary" in script
