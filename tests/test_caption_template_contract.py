"""Standalone template must not infer captions from incidental emphasis."""
from pathlib import Path


def test_template_uses_semantic_caption_classification():
    template = (Path(__file__).resolve().parents[1] / "scripts" / "essay_template.html").read_text(encoding="utf-8")
    assert ".content p:has(> img) + p > em{display:block" not in template
    assert ".content > p:has(> picture:only-child) + p:has(> em:first-child)" not in template
    assert ".content p.sb-image-caption" in template
    assert "function isImageCaption(paragraph)" in template
    assert "paragraph.classList.add('sb-image-caption')" in template
