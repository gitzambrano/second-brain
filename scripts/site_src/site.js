/* Library interactions: search, tag filter, sort, and three view modes
   (grid, compact list, grouped by theme). Everything reads the cards already
   rendered by build_site.py, so with JavaScript disabled the page degrades to
   a plain list of every published essay. */
(function () {
  'use strict';

  var grid = document.getElementById('essayGrid');
  if (!grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll('.essay-card'));
  var grouped = document.getElementById('groupedView');
  var input = document.getElementById('searchInput');
  var empty = document.getElementById('emptyState');
  var counter = document.getElementById('visibleCount');
  var chips = Array.prototype.slice.call(document.querySelectorAll('.filter-chip'));
  var viewButtons = Array.prototype.slice.call(document.querySelectorAll('.segmented [data-view]'));

  var activeTag = '';
  var view = 'list';

  function normalize(value) {
    return (value || '')
      .toLocaleLowerCase('pt-BR')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  function tagsOf(card) {
    var raw = card.dataset.tags || '';
    return raw ? raw.split('|') : [];
  }

  function matches(card, query) {
    var hitQuery = !query || normalize(card.dataset.search).indexOf(query) !== -1;
    var hitTag = !activeTag || tagsOf(card).indexOf(activeTag) !== -1;
    return hitQuery && hitTag;
  }

  function comparator() {
    return makeComparator();
  }

  /* --- Ordenação por prioridade de dimensões -----------------------------
     A lista ordena por um conjunto de critérios (status, privacidade, data,
     título, leitura) em que a ORDEM lista a importância de cada um — quem
     está primeiro vale mais, e só desempata quem vem depois. O padrão é o
     que o Usuário pediu: maduro e público primeiro, depois os mais novos,
     depois alfabético. A preferência fica no localStorage. */
  var SORT_KEY = 'sb-sort-v1';

  function statusRank(card) {
    var s = (card.dataset.status || '').toLowerCase();
    if (s === 'finalizado') return 3;
    if (s === 'revisao' || s === 'maduro') return 2;
    if (s === 'draft') return 1;
    return 0;
  }

  var SORT_DIMS = {
    status: {
      label: 'Status',
      dir: -1,
      compare: function (a, b) { return statusRank(a) - statusRank(b); }
    },
    privacy: {
      label: 'Privacidade',
      dir: -1,
      compare: function (a, b) {
        return ((a.dataset.published === '1') ? 1 : 0) - ((b.dataset.published === '1') ? 1 : 0);
      }
    },
    date: {
      label: 'Data',
      dir: -1,
      compare: function (a, b) {
        return (a.dataset.updated || '').localeCompare(b.dataset.updated || '');
      }
    },
    title: {
      label: 'Título',
      dir: 1,
      compare: function (a, b) {
        return (a.dataset.title || '').localeCompare(b.dataset.title || '', 'pt-BR');
      }
    },
    reading: {
      label: 'Leitura',
      dir: 1,
      compare: function (a, b) {
        return (+a.dataset.minutes || 0) - (+b.dataset.minutes || 0);
      }
    }
  };

  var DEFAULT_ORDER = ['status', 'privacy', 'date', 'title', 'reading'];

  function defaultState() {
    var dir = {};
    Object.keys(SORT_DIMS).forEach(function (k) { dir[k] = SORT_DIMS[k].dir; });
    return { order: DEFAULT_ORDER.slice(), dir: dir };
  }

  var sortState;
  try {
    sortState = JSON.parse(localStorage.getItem(SORT_KEY) || 'null');
  } catch (e) { sortState = null; }
  if (!sortState || !Array.isArray(sortState.order) ||
      sortState.order.some(function (k) { return !SORT_DIMS[k]; }) ||
      !sortState.order.length) {
    sortState = defaultState();
  }

  function saveSort() {
    try { localStorage.setItem(SORT_KEY, JSON.stringify(sortState)); } catch (e) { /* sem storage */ }
  }

  function makeComparator() {
    return function (a, b) {
      var status = statusRank(b) - statusRank(a);
      if (status) return status;

      var publicA = a.dataset.published === '1' ? 1 : 0;
      var publicB = b.dataset.published === '1' ? 1 : 0;
      if (publicA !== publicB) return publicB - publicA;

      var date = (b.dataset.updated || '').localeCompare(a.dataset.updated || '');
      if (date) return date;

      return (a.dataset.title || '').localeCompare(b.dataset.title || '', 'pt-BR');
    };
  }

  function directionLabel(key) {
    var d = SORT_DIMS[key], dir = sortState.dir[key];
    var value = dir < 0 ? '↑ ' : '↓ ';
    if (key === 'status') return value + (dir < 0 ? 'maduro primeiro' : 'rascunho primeiro');
    if (key === 'privacy') return value + (dir < 0 ? 'público primeiro' : 'privado primeiro');
    if (key === 'date') return value + (dir < 0 ? 'mais novo primeiro' : 'mais antigo primeiro');
    if (key === 'title') return value + (dir < 0 ? 'Z–A' : 'A–Z');
    return value + (dir < 0 ? 'mais longa primeiro' : 'mais curta primeiro');
  }

  function renderSortList() {
    var list = document.getElementById('sortList');
    if (!list) return;
    list.textContent = '';
    sortState.order.forEach(function (key, idx) {
      var item = document.createElement('div');
      item.className = 'sort-item';
      item.dataset.key = key;
      item.setAttribute('role', 'listitem');

      var up = document.createElement('button');
      up.type = 'button';
      up.className = 'sort-move';
      up.setAttribute('aria-label', 'Subir prioridade de ' + SORT_DIMS[key].label);
      up.textContent = '↑';
      up.disabled = idx === 0;
      up.addEventListener('click', function () { moveSort(key, -1); });

      var down = document.createElement('button');
      down.type = 'button';
      down.className = 'sort-move';
      down.setAttribute('aria-label', 'Descer prioridade de ' + SORT_DIMS[key].label);
      down.textContent = '↓';
      down.disabled = idx === sortState.order.length - 1;
      down.addEventListener('click', function () { moveSort(key, 1); });

      var dim = document.createElement('button');
      dim.type = 'button';
      dim.className = 'sort-dim';
      dim.setAttribute('aria-pressed', String(sortState.dir[key] > 0));
      var name = document.createElement('span');
      name.className = 'sort-dim-name';
      name.textContent = SORT_DIMS[key].label;
      var label = document.createElement('span');
      label.className = 'sort-dim-dir';
      label.textContent = directionLabel(key);
      dim.appendChild(name);
      dim.appendChild(label);
      dim.addEventListener('click', function () { flipSort(key); });

      item.appendChild(up);
      item.appendChild(down);
      item.appendChild(dim);
      list.appendChild(item);
    });
  }

  function refreshSort() {
    renderSortList();
    updateSortSummary();
    saveSort();
    apply();
  }

  function updateSortSummary() {
    var summary = document.getElementById('sortSummary');
    if (summary) {
      summary.textContent = sortState.order.slice(0, 3)
        .map(function (k) { return SORT_DIMS[k].label; })
        .join(' → ') + (sortState.order.length > 3 ? ' → …' : '');
    }
  }

  function moveSort(key, delta) {
    var i = sortState.order.indexOf(key);
    var j = i + delta;
    if (i < 0 || j < 0 || j >= sortState.order.length) return;
    sortState.order.splice(i, 1);
    sortState.order.splice(j, 0, key);
    refreshSort();
  }

  function flipSort(key) {
    sortState.dir[key] = sortState.dir[key] < 0 ? 1 : -1;
    refreshSort();
  }

  var sortToggle = document.getElementById('sortToggle');
  var sortPanel = document.getElementById('sortPanel');
  if (sortToggle && sortPanel) {
    sortToggle.addEventListener('click', function (event) {
      event.stopPropagation();
      var open = sortPanel.hidden;
      sortPanel.hidden = !open;
      sortToggle.setAttribute('aria-expanded', String(open));
      if (open) renderSortList();
    });
    document.addEventListener('click', function (event) {
      if (!sortPanel.hidden && !sortPanel.contains(event.target)) {
        sortPanel.hidden = true;
        sortToggle.setAttribute('aria-expanded', 'false');
      }
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && !sortPanel.hidden) {
        sortPanel.hidden = true;
        sortToggle.setAttribute('aria-expanded', 'false');
        sortToggle.focus();
      }
    });
  }
  renderSortList();
  updateSortSummary();

  function renderFlat(visible) {
    grouped.hidden = true;
    grid.hidden = false;
    grid.classList.toggle('as-list', view === 'list');
    visible.forEach(function (card) { grid.appendChild(card); });
    cards.forEach(function (card) { card.hidden = visible.indexOf(card) === -1; });
  }

  function renderGrouped(visible) {
    grid.hidden = true;
    grouped.hidden = false;
    grouped.textContent = '';
    cards.forEach(function (card) { card.hidden = false; });

    var buckets = Object.create(null);
    var untagged = [];
    visible.forEach(function (card) {
      var tags = tagsOf(card);
      if (!tags.length) { untagged.push(card); return; }
      tags.forEach(function (tag) {
        (buckets[tag] = buckets[tag] || []).push(card);
      });
    });

    // Biggest themes first, alphabetical within the same size.
    var names = Object.keys(buckets).sort(function (a, b) {
      return buckets[b].length - buckets[a].length || a.localeCompare(b, 'pt-BR');
    });
    if (untagged.length) { names.push(null); buckets[''] = untagged; }

    names.forEach(function (name) {
      var key = name === null ? '' : name;
      var section = document.createElement('section');
      section.className = 'group';

      var heading = document.createElement('div');
      heading.className = 'group-heading';
      var title = document.createElement('h3');
      title.textContent = name === null ? 'Sem tema' : name;
      var count = document.createElement('span');
      count.className = 'count';
      count.textContent = buckets[key].length;
      heading.appendChild(title);
      heading.appendChild(count);

      var box = document.createElement('div');
      box.className = 'essay-grid';
      // A card can belong to several themes, so each group shows a clone.
      buckets[key].forEach(function (card) {
        box.appendChild(card.cloneNode(true));
      });

      section.appendChild(heading);
      section.appendChild(box);
      grouped.appendChild(section);
    });
  }

  function apply() {
    var query = normalize(input ? input.value.trim() : '');
    var visible = cards.filter(function (card) { return matches(card, query); });
    visible.sort(comparator());

    if (view === 'group') renderGrouped(visible);
    else renderFlat(visible);

    if (counter) counter.textContent = visible.length;
    if (empty) empty.hidden = visible.length !== 0;
  }

  if (input) input.addEventListener('input', apply);

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      chips.forEach(function (other) {
        other.classList.remove('active');
        other.setAttribute('aria-pressed', 'false');
      });
      chip.classList.add('active');
      chip.setAttribute('aria-pressed', 'true');
      activeTag = chip.dataset.tag || '';
      showActiveTag();
      apply();
    });
  });

  viewButtons.forEach(function (button) {
    button.addEventListener('click', function () {
      view = button.dataset.view;
      viewButtons.forEach(function (other) {
        other.setAttribute('aria-pressed', String(other === button));
      });
      apply();
    });
  });

  document.addEventListener('keydown', function (event) {
    var tag = document.activeElement && document.activeElement.tagName;
    if (event.key === '/' && tag !== 'INPUT' && tag !== 'TEXTAREA' && tag !== 'SELECT' && tag !== 'BUTTON' && !document.activeElement.isContentEditable) {
      event.preventDefault();
      if (input) input.focus();
    }
    if (event.key === 'Escape' && document.activeElement === input) {
      input.value = '';
      apply();
      input.blur();
    }
  });

  /* Expand a single summary without navigating the card. */
  function toggleCardSummary(summary, event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    var card = summary.closest('.essay-card');
    if (!card) return;
    var expanded = card.classList.toggle('summary-expanded');
    summary.setAttribute('aria-expanded', String(expanded));
    summary.title = expanded ? 'Recolher resumo' : 'Expandir resumo';
  }

  document.addEventListener('click', function (event) {
    var summary = event.target.closest && event.target.closest('.card-summary');
    if (summary) toggleCardSummary(summary, event);
  });

  document.addEventListener('keydown', function (event) {
    var summary = event.target.closest && event.target.closest('.card-summary');
    if (summary && (event.key === 'Enter' || event.key === ' ')) {
      toggleCardSummary(summary, event);
    }
  });

  /* --- Summaries, tag drawer ---------------------------------------------- */

  var library = document.getElementById('library');
  var summaryToggle = document.getElementById('toggleSummaries');
  if (summaryToggle && library) {
    summaryToggle.addEventListener('click', function () {
      var on = summaryToggle.getAttribute('aria-pressed') !== 'true';
      summaryToggle.setAttribute('aria-pressed', String(on));
      library.classList.toggle('no-summaries', !on);
    });
  }

  // Themes live behind a toggle: 35 chips are a wall, not a filter.
  var filters = document.getElementById('filters');
  var tagToggle = document.getElementById('tagToggle');
  var tagCurrent = document.getElementById('tagCurrent');
  if (filters && tagToggle) {
    tagToggle.addEventListener('click', function () {
      var open = filters.hidden;
      filters.hidden = !open;
      tagToggle.setAttribute('aria-expanded', String(open));
    });
  }
  function showActiveTag() {
    if (tagCurrent) tagCurrent.textContent = activeTag || 'todos';
  }

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

  function paintCover(canvas, data) {
    var ctx = canvas.getContext('2d');
    var TYPE_COLOR = {
      essay: '#7aabff', concept: '#7be0c3', entity: '#f2a65a',
      insights: '#c99bff', reference: '#8494ad'
    };

    // Cap the sample: a few hundred marks read as a constellation, 1352 as mud.
    var all = (data.nodes || []).filter(function (n) {
      return typeof n.x0 === 'number' && typeof n.y0 === 'number';
    });
    var byDegree = all.slice().sort(function (a, b) {
      return (b.degree || 0) - (a.degree || 0);
    });
    var nodes = byDegree.slice(0, 320);
    var keep = {};
    nodes.forEach(function (n) { keep[n.id] = n; });
    var edges = (data.edges || []).filter(function (e) {
      return keep[e.source] && keep[e.target];
    }).slice(0, 700);

    // A force layout throws a few nodes far out; framing on the raw extent
    // would shrink the whole constellation to a dot. Frame the middle 90%.
    function span(values) {
      var sorted = values.slice().sort(function (a, b) { return a - b; });
      var lo = sorted[Math.floor(sorted.length * 0.05)];
      var hi = sorted[Math.floor(sorted.length * 0.95)];
      return [lo, hi === lo ? lo + 1 : hi];
    }
    var xs = span(nodes.map(function (n) { return n.x0; }));
    var ys = span(nodes.map(function (n) { return n.y0; }));
    var bounds = { minX: xs[0], maxX: xs[1], minY: ys[0], maxY: ys[1] };

    function draw() {
      var ratio = window.devicePixelRatio || 1;
      var rect = canvas.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      canvas.width = Math.round(rect.width * ratio);
      canvas.height = Math.round(rect.height * ratio);
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      ctx.clearRect(0, 0, rect.width, rect.height);

      var spanX = (bounds.maxX - bounds.minX) || 1;
      var spanY = (bounds.maxY - bounds.minY) || 1;
      var pad = 26;
      var scale = Math.min((rect.width - pad * 2) / spanX,
                           (rect.height - pad * 2) / spanY);
      var offX = (rect.width - spanX * scale) / 2 - bounds.minX * scale;
      var offY = (rect.height - spanY * scale) / 2 - bounds.minY * scale;
      var at = function (n) {
        return [n.x0 * scale + offX, n.y0 * scale + offY];
      };

      var styles = getComputedStyle(document.documentElement);
      ctx.strokeStyle = styles.getPropertyValue('--line-strong').trim() || '#556';
      ctx.globalAlpha = 0.22;
      ctx.lineWidth = 0.6;
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
        if (p[0] < -10 || p[1] < -10 || p[0] > rect.width + 10 || p[1] > rect.height + 10) {
          return;
        }
        var r = 1.4 + Math.min(4.2, Math.sqrt(n.degree || 1) * 0.75);
        ctx.beginPath();
        ctx.arc(p[0], p[1], r, 0, Math.PI * 2);
        ctx.fillStyle = TYPE_COLOR[n.type] || '#7aabff';
        ctx.globalAlpha = n.public ? 1 : 0.62;
        ctx.fill();
        if (n.public) {
          ctx.globalAlpha = 1;
          ctx.lineWidth = 1.4;
          ctx.strokeStyle = styles.getPropertyValue('--text-strong').trim() || '#fff';
          ctx.stroke();
        }
      });
      ctx.globalAlpha = 1;
    }

    draw();
    window.addEventListener('resize', draw);
    // The palette changes with the theme; redraw when it does.
    new MutationObserver(draw).observe(document.documentElement, {
      attributes: true, attributeFilter: ['data-theme']
    });
  }
})();
