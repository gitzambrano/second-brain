/* Library interactions: search, multi-tag filter, and four reading modes
   (list/grid × compact/full). Everything reads the cards already rendered by
   build_site.py, so with JavaScript disabled the page degrades to a plain list
   of every essay in the catalogue.

   The order is fixed — mature first, then public, then most recently updated,
   then alphabetical — and therefore not advertised in the chrome: a control the
   reader cannot change is noise. */
(function () {
  'use strict';

  var grid = document.getElementById('essayGrid');
  if (!grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll('.essay-card'));
  var input = document.getElementById('searchInput');
  var empty = document.getElementById('emptyState');
  var counter = document.getElementById('visibleCount');
  var chips = Array.prototype.slice.call(document.querySelectorAll('.filter-chip'));

  var VIEW_KEY = 'sb-view-v2';
  var activeTags = [];
  var layout = 'list';
  var density = 'compact';

  try {
    var saved = JSON.parse(localStorage.getItem(VIEW_KEY) || 'null');
    if (saved && (saved.layout === 'list' || saved.layout === 'grid')) layout = saved.layout;
    if (saved && (saved.density === 'compact' || saved.density === 'full')) density = saved.density;
  } catch (e) { /* sem storage */ }

  function saveView() {
    try {
      localStorage.setItem(VIEW_KEY, JSON.stringify({ layout: layout, density: density }));
    } catch (e) { /* sem storage */ }
  }

  function normalize(value) {
    return (value || '')
      .toLocaleLowerCase('pt-BR')
      .normalize('NFD')
      .replace(/[̀-ͯ]/g, '');
  }

  function tagsOf(card) {
    var raw = card.dataset.tags || '';
    return raw ? raw.split('|') : [];
  }

  /* A card passes when it carries AT LEAST ONE of the selected themes: picking
     a second theme widens the shelf instead of emptying it. */
  function matches(card, query) {
    if (query && normalize(card.dataset.search).indexOf(query) === -1) return false;
    if (!activeTags.length) return true;
    var own = tagsOf(card);
    for (var i = 0; i < activeTags.length; i++) {
      if (own.indexOf(activeTags[i]) !== -1) return true;
    }
    return false;
  }

  function statusRank(card) {
    var s = (card.dataset.status || '').toLowerCase();
    if (s === 'finalizado') return 3;
    if (s === 'revisao') return 2;
    if (s === 'draft') return 1;
    return 0;
  }

  function compare(a, b) {
    var status = statusRank(b) - statusRank(a);
    if (status) return status;

    var publicA = a.dataset.published === '1' ? 1 : 0;
    var publicB = b.dataset.published === '1' ? 1 : 0;
    if (publicA !== publicB) return publicB - publicA;

    var date = (b.dataset.updated || '').localeCompare(a.dataset.updated || '');
    if (date) return date;

    return (a.dataset.title || '').localeCompare(b.dataset.title || '', 'pt-BR');
  }

  /* --- View modes --------------------------------------------------------- */

  function applyView() {
    grid.classList.toggle('layout-list', layout === 'list');
    grid.classList.toggle('layout-grid', layout === 'grid');
    grid.classList.toggle('density-compact', density === 'compact');
    grid.classList.toggle('density-full', density === 'full');

    // A summary that is always visible has nothing to expand; drop any
    // leftover open state so the two densities never disagree.
    if (density === 'full') {
      cards.forEach(function (card) {
        card.classList.remove('is-open');
        var button = card.querySelector('.card-expand');
        if (button) button.setAttribute('aria-expanded', 'false');
      });
    }

    document.querySelectorAll('[data-layout]').forEach(function (button) {
      button.setAttribute('aria-pressed', String(button.dataset.layout === layout));
    });
    document.querySelectorAll('[data-density]').forEach(function (button) {
      button.setAttribute('aria-pressed', String(button.dataset.density === density));
    });
  }

  document.querySelectorAll('[data-layout]').forEach(function (button) {
    button.addEventListener('click', function () {
      layout = button.dataset.layout;
      applyView();
      saveView();
    });
  });
  document.querySelectorAll('[data-density]').forEach(function (button) {
    button.addEventListener('click', function () {
      density = button.dataset.density;
      applyView();
      saveView();
    });
  });

  /* --- Filtering ---------------------------------------------------------- */

  function apply() {
    var query = normalize(input ? input.value.trim() : '');
    var visible = cards.filter(function (card) { return matches(card, query); });
    visible.sort(compare);
    visible.forEach(function (card) { grid.appendChild(card); });
    cards.forEach(function (card) { card.hidden = visible.indexOf(card) === -1; });

    if (counter) counter.textContent = visible.length;
    if (empty) empty.hidden = visible.length !== 0;
  }

  if (input) input.addEventListener('input', apply);

  var filters = document.getElementById('filters');
  var tagToggle = document.getElementById('tagToggle');
  var tagCurrent = document.getElementById('tagCurrent');
  var tagClear = document.getElementById('tagClear');

  function showActiveTags() {
    if (tagCurrent) {
      // Sem seleção o chip diria "todos", que é o estado já implícito no botão
      // — e no celular, onde o espaço é o recurso escasso, ele empurraria o
      // rótulo para fora. Só aparece quando há o que mostrar.
      tagCurrent.hidden = activeTags.length === 0;
      tagCurrent.textContent = activeTags.length === 1 ? activeTags[0]
        : activeTags.length + ' temas';
    }
    if (tagToggle) tagToggle.classList.toggle('has-selection', activeTags.length > 0);
    if (tagClear) tagClear.hidden = activeTags.length === 0;
  }

  function setChipState(chip) {
    var on = activeTags.indexOf(chip.dataset.tag) !== -1;
    chip.classList.toggle('active', on);
    chip.setAttribute('aria-pressed', String(on));
  }

  chips.forEach(function (chip) {
    chip.setAttribute('aria-pressed', 'false');
    chip.addEventListener('click', function () {
      var tag = chip.dataset.tag || '';
      var at = activeTags.indexOf(tag);
      if (at === -1) activeTags.push(tag);
      else activeTags.splice(at, 1);   // a second press deselects
      chips.forEach(setChipState);
      showActiveTags();
      apply();
    });
  });

  if (tagClear) {
    tagClear.addEventListener('click', function () {
      activeTags = [];
      chips.forEach(setChipState);
      showActiveTags();
      apply();
    });
  }

  if (filters && tagToggle) {
    tagToggle.addEventListener('click', function () {
      var open = filters.hidden;
      filters.hidden = !open;
      tagToggle.setAttribute('aria-expanded', String(open));
    });
  }

  /* --- Expanding one summary ---------------------------------------------- */

  /* The expander is a real button that lives outside the card link, so it can
     be pressed as many times as the reader likes. */
  grid.addEventListener('click', function (event) {
    var button = event.target.closest && event.target.closest('.card-expand');
    if (!button || !grid.contains(button)) return;
    event.preventDefault();
    var card = button.closest('.essay-card');
    if (!card) return;
    var open = !card.classList.contains('is-open');
    card.classList.toggle('is-open', open);
    button.setAttribute('aria-expanded', String(open));
    var label = button.querySelector('.card-expand-text');
    if (label) label.textContent = open ? 'Recolher' : 'Resumo';
  });

  /* --- Keyboard ----------------------------------------------------------- */

  document.addEventListener('keydown', function (event) {
    var active = document.activeElement;
    var tag = active && active.tagName;
    if (event.key === '/' && tag !== 'INPUT' && tag !== 'TEXTAREA' && tag !== 'SELECT'
        && tag !== 'BUTTON' && !(active && active.isContentEditable)) {
      event.preventDefault();
      if (input) input.focus();
    }
    if (event.key === 'Escape') {
      if (active === input && input) {
        input.value = '';
        apply();
        input.blur();
      } else if (filters && !filters.hidden) {
        filters.hidden = true;
        if (tagToggle) {
          tagToggle.setAttribute('aria-expanded', 'false');
          tagToggle.focus();
        }
      }
    }
  });

  applyView();
  showActiveTags();
  apply();

  /* A capa é um PNG assado no build (scripts/lib/build_cover.py) e posto por
     CSS. Antes esta função baixava graph.json — 851 KB — e refazia o desenho a
     partir de uma amostra de 300 nós, o que dava outro contorno e metade das
     arestas: mais peso que o mapa que ilustrava, e sem se parecer com ele. */
})();
