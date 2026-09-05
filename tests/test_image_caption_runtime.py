"""Regression for image-adjacent prose being mistaken for a caption."""
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ESSAY_JS = ROOT / "scripts" / "site_src" / "essay.js"

pytestmark = [pytest.mark.html, pytest.mark.browser]


def test_post_image_emphasis_stays_inline_and_real_captions_stay_captions():
    """Legacy CSS must not turn ordinary italic terms after an image into blocks."""
    html = r"""
    <!doctype html><meta charset="utf-8">
    <style>
      .content > p:has(> picture:only-child) + p:has(> em:first-child){
        text-align:center;font-size:.84em;color:#777;margin-bottom:1.7rem;
      }
      .content p:has(> img) + p > em,
      .content p:has(> picture) + p > em{
        display:block;text-align:center;font-size:.84em;color:#777;
        line-height:1.5;margin-bottom:2rem;
      }
    </style>
    <div class="content">
      <p><picture><img alt="Q-Q"
        src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="></picture></p>
      <p id="prose">O modelo subestima o <em id="sink">sink rate</em> principalmente na cauda.</p>

      <p><picture><img alt="Rotor"
        src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="></picture></p>
      <p id="fig">Fig. 1 - Variação do <em id="flapping">flapping</em> longitudinal.</p>

      <p><img alt="Plot" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="></p>
      <p id="pure"><em id="caption">Figura 2 — Legenda integral.</em></p>
    </div>
    """

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.set_content(html)
        page.add_script_tag(content=ESSAY_JS.read_text(encoding="utf-8"))

        assert page.locator("#prose").evaluate("el => el.classList.contains('sb-image-caption')") is False
        assert page.locator("#sink").evaluate("el => getComputedStyle(el).display") == "inline"
        assert page.locator("#prose").evaluate("el => getComputedStyle(el).textAlign") != "center"

        assert page.locator("#fig").evaluate("el => el.classList.contains('sb-image-caption')") is True
        assert page.locator("#flapping").evaluate("el => getComputedStyle(el).display") == "inline"
        assert page.locator("#fig").evaluate("el => getComputedStyle(el).textAlign") == "center"

        assert page.locator("#pure").evaluate("el => el.classList.contains('sb-image-caption')") is True
        assert page.locator("#caption").evaluate("el => getComputedStyle(el).display") == "inline"
        assert page.locator("#pure").evaluate("el => getComputedStyle(el).textAlign") == "center"
        browser.close()
