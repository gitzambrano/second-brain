// Controle de tema compartilhado. O valor inicial é aplicado por um trecho
// inline no <head> de cada página, para a primeira pintura já sair na paleta
// certa; este arquivo só liga o botão e guarda a escolha. A preferência do
// sistema não é consultada: sem escolha guardada, o site abre no claro.
(function () {
  var root = document.documentElement;

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

  apply(root.dataset.theme || 'light', false);

  document.getElementById('themeToggle')?.addEventListener('click', function () {
    apply(root.dataset.theme === 'dark' ? 'light' : 'dark', true);
  });

})();
