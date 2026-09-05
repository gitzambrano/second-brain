from check_dedupe import reference_core
from check_references import check_essay


def test_reference_core_ignores_context_note():
    a = "Author, A., *Book Title*, Publisher, 2020. — Nota A. [Link](https://example.com/book)"
    b = "Author, A., *Book Title*, Publisher, 2020. — Nota B. [Link](https://example.com/book)"
    assert reference_core(a) == reference_core(b)


def test_reference_core_detects_bibliographic_difference():
    a = "Author, A., *Book Title*, Publisher, 2020. [Link](https://example.com/book)"
    b = "Author, A., *Book Title*, Other Publisher, 2020. [Link](https://example.com/book)"
    assert reference_core(a) != reference_core(b)


def test_unused_reference_is_not_a_lint_issue(tmp_path):
    essay = tmp_path / "essay.md"
    essay.write_text("""# Teste\n\nPor Autor\n\nTexto com citação [1].\n\n## Referências\n\n[1] Autor, A., *Usada*, Editora, 2020. [Link](https://example.com/a)\n\n[2] Autor, B., *Leitura complementar*, Editora, 2021. [Link](https://example.com/b)\n""", encoding="utf-8")
    result = check_essay(essay)
    assert all(issue["code"] != "REFERENCIA_NAO_USADA" for issue in result["issues"])
