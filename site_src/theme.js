// Shared theme control. The initial value is applied by a tiny inline snippet in
// each page <head> so the first paint already has the right palette; this file
// only wires the toggle and keeps it in sync with the system preference.
(function () {
  var root = document.documentElement;
  var media = window.matchMedia ? matchMedia('(prefers-color-scheme: light)') : null;

  function apply(theme, persist) {
    root.dataset.theme = theme;
    var button = document.getElementById('themeToggle');
    if (button) {
      button.setAttribute('aria-pressed', String(theme === 'light'));
      button.setAttribute(
        'aria-label', theme === 'light' ? 'Mudar para tema escuro' : 'Mudar para tema claro'
      );
    }
    if (persist) {
      try { localStorage.setItem('sb-theme', theme); } catch (e) { /* private mode */ }
    }
  }

  apply(root.dataset.theme || 'dark', false);

  document.getElementById('themeToggle')?.addEventListener('click', function () {
    apply(root.dataset.theme === 'dark' ? 'light' : 'dark', true);
  });

  // Follow the system only while the visitor has not made an explicit choice.
  media?.addEventListener?.('change', function (event) {
    var stored = null;
    try { stored = localStorage.getItem('sb-theme'); } catch (e) { /* private mode */ }
    if (!stored) apply(event.matches ? 'light' : 'dark', false);
  });
})();
