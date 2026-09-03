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
    if (s === 'revisao' || s === 'maduro') return 2;
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

  /* --- Cover map ----------------------------------------------------------
     A still, low-fidelity portrait of the real graph: a sample of nodes drawn
     once from graph.json. No simulation, no interaction — the map page owns
     those. It is decoration with the courtesy of being true. */

  var cover = document.getElementById('coverMap');
  if (!cover) return;

  fetch('graph.json', { cache: 'no-store' })
    .then(function (response) { return response.json(); })
    .then(function (data) { paintCover(cover, data); })
    .catch(function () {
      var wrap = cover.closest('.cover-map');
      if (wrap) wrap.remove();
    });

  /* O desenho é o do grafo, congelado: mesma paleta de fábrica, mesmo raio
     (`radiusBase + sqrt(grau) * radiusScale`), mesmo gradiente radial no nó e
     o mesmo halo — que, como no mapa, só existe no escuro, porque em fundo
     claro ele vira sombra colorida e suja tudo. */
  var GRAPH_COLORS = {
    essay: '#4fa8ff', concept: '#5fd3c4', entity: '#e8b657',
    insights: '#b48ce8', reference: '#8a8f96'
  };
  var RADIUS_BASE = 5;
  var RADIUS_SCALE = 3;

  function rgba(hex, alpha) {
    var n = parseInt(hex.slice(1), 16);
    return 'rgba(' + ((n >> 16) & 255) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + alpha + ')';
  }

  function mixWhite(hex, amount) {
    var n = parseInt(hex.slice(1), 16);
    var mix = function (c) { return Math.round(c + (255 - c) * amount); };
    return 'rgb(' + mix((n >> 16) & 255) + ',' + mix((n >> 8) & 255) + ',' + mix(n & 255) + ')';
  }

  function paintCover(canvas, data) {
    var ctx = canvas.getContext('2d');

    // Uma amostra: algumas centenas de marcas leem como constelação, 1352 como
    // borrão. Referências entram na disputa como qualquer outro tipo.
    var all = (data.nodes || []).filter(function (n) {
      return typeof n.x0 === 'number' && typeof n.y0 === 'number';
    });
    var nodes = all.slice().sort(function (a, b) {
      return (b.degree || 0) - (a.degree || 0);
    }).slice(0, 300);
    var keep = {};
    nodes.forEach(function (n) { keep[n.id] = n; });
    var edges = (data.edges || []).filter(function (e) {
      return keep[e.source] && keep[e.target];
    }).slice(0, 600);

    // Extensão TOTAL da amostra, não o miolo: com um recorte percentil os nós
    // de fora eram desenhados além do quadro e o canvas os cortava numa reta —
    // o contorno que não pode existir. Como a amostra já são os 300 de maior
    // grau, o extremo cru não tem outlier que achate o desenho.
    function span(values) {
      var lo = Math.min.apply(null, values);
      var hi = Math.max.apply(null, values);
      return [lo, hi === lo ? lo + 1 : hi];
    }
    var xs = span(nodes.map(function (n) { return n.x0; }));
    var ys = span(nodes.map(function (n) { return n.y0; }));

    function draw() {
      var ratio = window.devicePixelRatio || 1;
      var rect = canvas.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      canvas.width = Math.round(rect.width * ratio);
      canvas.height = Math.round(rect.height * ratio);
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      ctx.clearRect(0, 0, rect.width, rect.height);

      var spanX = (xs[1] - xs[0]) || 1;
      var spanY = (ys[1] - ys[0]) || 1;
      // A folga reserva o raio do maior nó (e o halo, 2.4x): o enquadramento
      // é dos CENTROS, e sem isso o círculo mais gordo vazaria pela borda.
      var maxDegree = nodes.reduce(function (m, n) { return Math.max(m, n.degree || 1); }, 1);
      var pad = 6 + (RADIUS_BASE + Math.sqrt(maxDegree) * RADIUS_SCALE)
                    * Math.min(rect.width / spanX, rect.height / spanY) * 2.4;
      // Cabe INTEIRO dentro do quadro, em vez de preenchê-lo. Sem moldura, um
      // desenho sangrado deixaria o corte reto do canvas à mostra — que é
      // exatamente o contorno que não deve existir. Assim a silhueta do
      // próprio grafo é a forma, e ele flutua sobre a página.
      var scale = Math.min((rect.width - pad * 2) / spanX,
                           (rect.height - pad * 2) / spanY);
      var offX = (rect.width - spanX * scale) / 2 - xs[0] * scale;
      var offY = (rect.height - spanY * scale) / 2 - ys[0] * scale;
      var at = function (n) { return [n.x0 * scale + offX, n.y0 * scale + offY]; };
      var radius = function (n) {
        return Math.max(0.9, (RADIUS_BASE + Math.sqrt(n.degree || 1) * RADIUS_SCALE) * scale);
      };
      var dark = document.documentElement.dataset.theme !== 'light';

      ctx.strokeStyle = dark ? '#9aa0a8' : '#8a99aa';
      ctx.globalAlpha = 0.45;
      ctx.lineWidth = 0.7;
      ctx.beginPath();
      edges.forEach(function (e) {
        var a = at(keep[e.source]);
        var b = at(keep[e.target]);
        ctx.moveTo(a[0], a[1]);
        ctx.lineTo(b[0], b[1]);
      });
      ctx.stroke();
      ctx.globalAlpha = 1;

      nodes.forEach(function (n) {
        var p = at(n);
        if (p[0] < -12 || p[1] < -12 || p[0] > rect.width + 12 || p[1] > rect.height + 12) {
          return;
        }
        var r = radius(n);
        var color = GRAPH_COLORS[n.type] || GRAPH_COLORS.essay;

        if (dark) {
          var halo = ctx.createRadialGradient(p[0], p[1], 0, p[0], p[1], r * 2.4);
          halo.addColorStop(0, rgba(color, 0.5));
          halo.addColorStop(1, rgba(color, 0));
          ctx.fillStyle = halo;
          ctx.beginPath();
          ctx.arc(p[0], p[1], r * 2.4, 0, Math.PI * 2);
          ctx.fill();
        }

        var fill = ctx.createRadialGradient(
          p[0] - r * 0.3, p[1] - r * 0.35, 0, p[0], p[1], r);
        fill.addColorStop(0, mixWhite(color, 0.55));
        fill.addColorStop(1, color);
        ctx.fillStyle = fill;
        ctx.beginPath();
        ctx.arc(p[0], p[1], r, 0, Math.PI * 2);
        ctx.fill();
      });
    }

    draw();
    window.addEventListener('resize', draw);
    // O halo existe só no escuro; redesenha quando o tema muda.
    new MutationObserver(draw).observe(document.documentElement, {
      attributes: true, attributeFilter: ['data-theme']
    });
  }
})();
