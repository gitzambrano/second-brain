/* Library interactions: search, tag filter, sort, and three view modes
   (grid, compact list, grouped by theme). Plus a small live preview of the
   public graph in the hero panel. All data comes from the cards already
   rendered by build_site.py, so the page works with JavaScript disabled
   down to a plain list of essays. */
(function () {
  'use strict';

  var grid = document.getElementById('essayGrid');
  if (!grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll('.essay-card'));
  var grouped = document.getElementById('groupedView');
  var input = document.getElementById('searchInput');
  var sortSelect = document.getElementById('sortSelect');
  var empty = document.getElementById('emptyState');
  var counter = document.getElementById('visibleCount');
  var chips = Array.prototype.slice.call(document.querySelectorAll('.filter-chip'));
  var viewButtons = Array.prototype.slice.call(document.querySelectorAll('.segmented [data-view]'));

  var activeTag = '';
  var view = 'grid';

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
    var mode = sortSelect ? sortSelect.value : 'recent';
    if (mode === 'title') {
      return function (a, b) {
        return a.dataset.title.localeCompare(b.dataset.title, 'pt-BR');
      };
    }
    if (mode === 'oldest') {
      return function (a, b) {
        return (a.dataset.updated || '').localeCompare(b.dataset.updated || '');
      };
    }
    if (mode === 'reading') {
      return function (a, b) {
        return (+a.dataset.minutes || 0) - (+b.dataset.minutes || 0);
      };
    }
    return function (a, b) {
      return (b.dataset.updated || '').localeCompare(a.dataset.updated || '');
    };
  }

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
  if (sortSelect) sortSelect.addEventListener('change', apply);

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      chips.forEach(function (other) { other.classList.remove('active'); });
      chip.classList.add('active');
      activeTag = chip.dataset.tag || '';
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
    if (event.key === '/' && tag !== 'INPUT' && tag !== 'TEXTAREA') {
      event.preventDefault();
      if (input) input.focus();
    }
    if (event.key === 'Escape' && document.activeElement === input) {
      input.value = '';
      apply();
      input.blur();
    }
  });

  apply();

  /* --- Hero graph preview ------------------------------------------------ */

  var canvas = document.getElementById('heroGraph');
  if (!canvas || !window.requestAnimationFrame) return;

  fetch('graph.json', { cache: 'no-store' })
    .then(function (response) { return response.json(); })
    .then(function (data) { drawPreview(canvas, data); })
    .catch(function () { canvas.remove(); });

  function drawPreview(target, data) {
    var ctx = target.getContext('2d');
    var nodes = (data.nodes || []).map(function (node, i) {
      var angle = i * 2.399;
      var radius = Math.sqrt(i + 1) * 22;
      return { x: Math.cos(angle) * radius, y: Math.sin(angle) * radius, node: node };
    });
    var index = {};
    nodes.forEach(function (item) { index[item.node.id] = item; });
    var edges = (data.edges || []).map(function (edge) {
      return [index[edge.source], index[edge.target]];
    }).filter(function (pair) { return pair[0] && pair[1]; });

    var width = 0;
    var height = 0;
    var frame = 0;

    function resize() {
      var ratio = window.devicePixelRatio || 1;
      var rect = target.getBoundingClientRect();
      width = rect.width;
      height = rect.height;
      target.width = Math.max(1, Math.round(width * ratio));
      target.height = Math.max(1, Math.round(height * ratio));
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    }

    function draw() {
      if (!width || !height) resize();
      var styles = getComputedStyle(document.documentElement);
      var accent = styles.getPropertyValue('--accent').trim() || '#7aabff';
      var line = styles.getPropertyValue('--line-strong').trim() || 'rgba(255,255,255,.3)';

      ctx.clearRect(0, 0, width, height);
      ctx.save();
      ctx.translate(width / 2, height / 2);

      var drift = Math.sin(frame / 220) * 6;

      ctx.strokeStyle = line;
      ctx.lineWidth = 1;
      edges.forEach(function (pair) {
        ctx.beginPath();
        ctx.moveTo(pair[0].x + drift, pair[0].y);
        ctx.lineTo(pair[1].x - drift, pair[1].y);
        ctx.stroke();
      });

      nodes.forEach(function (item, i) {
        var pulse = 1 + Math.sin((frame + i * 40) / 90) * 0.18;
        ctx.beginPath();
        ctx.arc(item.x + drift * 0.4, item.y, 4 * pulse, 0, Math.PI * 2);
        ctx.fillStyle = accent;
        ctx.globalAlpha = 0.85;
        ctx.fill();
        ctx.globalAlpha = 0.16;
        ctx.beginPath();
        ctx.arc(item.x + drift * 0.4, item.y, 13 * pulse, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
      });

      ctx.restore();
      frame += 1;
      requestAnimationFrame(draw);
    }

    resize();
    window.addEventListener('resize', resize);
    draw();
  }
})();
