/* Public knowledge graph.

   Reads graph.json — which build_site.py fills only with essays authorized by
   `publish: true` — and lays it out with a small force simulation on a canvas.
   Nodes are sized by how connected they are and coloured by their first theme.
   Pan with a drag, zoom with the wheel, drag a node to pin it, click to inspect. */
(function () {
  'use strict';

  var root = document.documentElement;
  var canvas = document.getElementById('graphCanvas');
  if (!canvas) return;

  var ctx = canvas.getContext('2d');
  var search = document.getElementById('graphSearch');
  var tagSelect = document.getElementById('graphTag');
  var inspector = document.getElementById('graphInspector');
  var intro = document.getElementById('graphIntro');
  var legend = document.getElementById('graphLegend');

  var PALETTE = [
    '#7aabff', '#7be0c3', '#f2a65a', '#c99bff',
    '#ff8fa3', '#8fd694', '#ffd166', '#6fd2e8'
  ];

  var view = { x: 0, y: 0, zoom: 1 };
  var width = 0;
  var height = 0;
  var nodes = [];
  var edges = [];
  var byId = {};
  var colorOf = {};
  var selected = null;
  var hovered = null;
  var dragging = null;
  var panning = false;
  var pointer = { x: 0, y: 0 };
  var last = null;
  var query = '';
  var tagFilter = '';
  var settled = 0;

  var reduceMotion = window.matchMedia
    && matchMedia('(prefers-reduced-motion: reduce)').matches;

  function normalize(value) {
    return (value || '')
      .toLocaleLowerCase('pt-BR')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  function resize() {
    var ratio = window.devicePixelRatio || 1;
    width = canvas.clientWidth;
    height = canvas.clientHeight;
    canvas.width = Math.max(1, Math.round(width * ratio));
    canvas.height = Math.max(1, Math.round(height * ratio));
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  }

  function toWorld(clientX, clientY) {
    var rect = canvas.getBoundingClientRect();
    return {
      x: (clientX - rect.left - width / 2 - view.x) / view.zoom,
      y: (clientY - rect.top - height / 2 - view.y) / view.zoom
    };
  }

  function nodeRadius(node) {
    return 5 + Math.min(9, Math.sqrt(node.degree) * 3.4);
  }

  function isDimmed(node) {
    if (tagFilter && node.tags.indexOf(tagFilter) === -1) return true;
    if (query && normalize(node.title + ' ' + node.tags.join(' ')).indexOf(query) === -1) {
      return true;
    }
    return false;
  }

  /* --- Simulation -------------------------------------------------------- */

  function step() {
    var i, j, a, b, dx, dy, dist, force;

    for (i = 0; i < nodes.length; i++) {
      a = nodes[i];
      for (j = i + 1; j < nodes.length; j++) {
        b = nodes[j];
        dx = b.x - a.x;
        dy = b.y - a.y;
        dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
        force = 2600 / (dist * dist);
        dx /= dist; dy /= dist;
        a.vx -= dx * force; a.vy -= dy * force;
        b.vx += dx * force; b.vy += dy * force;
      }
    }

    edges.forEach(function (edge) {
      a = edge.a; b = edge.b;
      dx = b.x - a.x;
      dy = b.y - a.y;
      dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
      force = (dist - 140) * 0.012;
      dx /= dist; dy /= dist;
      a.vx += dx * force; a.vy += dy * force;
      b.vx -= dx * force; b.vy -= dy * force;
    });

    nodes.forEach(function (node) {
      node.vx -= node.x * 0.0016;
      node.vy -= node.y * 0.0016;
      if (node === dragging) { node.vx = node.vy = 0; return; }
      node.vx *= 0.86;
      node.vy *= 0.86;
      node.x += node.vx;
      node.y += node.vy;
    });
  }

  /* --- Rendering --------------------------------------------------------- */

  function draw() {
    var styles = getComputedStyle(root);
    var lineColor = styles.getPropertyValue('--line-strong').trim() || 'rgba(255,255,255,.3)';
    var textColor = styles.getPropertyValue('--text').trim() || '#fff';
    var mutedColor = styles.getPropertyValue('--muted').trim() || '#889';

    ctx.clearRect(0, 0, width, height);
    ctx.save();
    ctx.translate(width / 2 + view.x, height / 2 + view.y);
    ctx.scale(view.zoom, view.zoom);

    var focus = hovered || selected;
    var neighbours = {};
    if (focus) {
      neighbours[focus.id] = true;
      edges.forEach(function (edge) {
        if (edge.a === focus) neighbours[edge.b.id] = true;
        if (edge.b === focus) neighbours[edge.a.id] = true;
      });
    }

    ctx.lineWidth = 1 / view.zoom;
    edges.forEach(function (edge) {
      var active = focus && (edge.a === focus || edge.b === focus);
      var faded = isDimmed(edge.a) || isDimmed(edge.b);
      ctx.globalAlpha = active ? 0.85 : faded ? 0.06 : 0.28;
      ctx.strokeStyle = active ? colorOf[edge.a.tags[0]] || lineColor : lineColor;
      ctx.beginPath();
      ctx.moveTo(edge.a.x, edge.a.y);
      ctx.lineTo(edge.b.x, edge.b.y);
      ctx.stroke();
    });

    nodes.forEach(function (node) {
      var radius = nodeRadius(node);
      var faded = isDimmed(node) || (focus && !neighbours[node.id]);
      var color = colorOf[node.tags[0]] || '#7aabff';

      ctx.globalAlpha = faded ? 0.16 : 1;

      if (!faded) {
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius * 2.6, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.globalAlpha = faded ? 0.05 : 0.12;
        ctx.fill();
        ctx.globalAlpha = 1;
      }

      ctx.beginPath();
      ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();

      if (node === selected) {
        ctx.lineWidth = 2 / view.zoom;
        ctx.strokeStyle = textColor;
        ctx.stroke();
        ctx.lineWidth = 1 / view.zoom;
      }

      if (!faded && (view.zoom > 0.55 || nodes.length < 40)) {
        ctx.font = '500 ' + (12 / view.zoom) + 'px Inter, system-ui, sans-serif';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = node === focus ? textColor : mutedColor;
        ctx.fillText(node.title, node.x + radius + 7 / view.zoom, node.y);
      }
      ctx.globalAlpha = 1;
    });

    ctx.restore();
  }

  function loop() {
    if (!reduceMotion || settled < 260) {
      step();
      settled += 1;
    }
    draw();
    requestAnimationFrame(loop);
  }

  /* --- Inspector --------------------------------------------------------- */

  function openInspector(node) {
    selected = node;
    if (!inspector) return;
    inspector.hidden = false;
    document.getElementById('inspectorTitle').textContent = node.title;
    document.getElementById('inspectorSummary').textContent = node.summary || '';
    var tagBox = document.getElementById('inspectorTags');
    tagBox.textContent = '';
    node.tags.forEach(function (tag) {
      var chip = document.createElement('span');
      chip.className = 'tag';
      chip.textContent = tag;
      tagBox.appendChild(chip);
    });
    document.getElementById('inspectorLink').href = node.url;
  }

  function closeInspector() {
    selected = null;
    if (inspector) inspector.hidden = true;
  }

  function nodeAt(clientX, clientY) {
    var point = toWorld(clientX, clientY);
    for (var i = nodes.length - 1; i >= 0; i--) {
      var node = nodes[i];
      var radius = nodeRadius(node) + 6;
      if ((node.x - point.x) * (node.x - point.x) +
          (node.y - point.y) * (node.y - point.y) < radius * radius) {
        return node;
      }
    }
    return null;
  }

  function fitToContent() {
    if (!nodes.length) return;
    var minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    nodes.forEach(function (node) {
      minX = Math.min(minX, node.x); maxX = Math.max(maxX, node.x);
      minY = Math.min(minY, node.y); maxY = Math.max(maxY, node.y);
    });
    var spanX = Math.max(200, maxX - minX + 220);
    var spanY = Math.max(200, maxY - minY + 220);
    view.zoom = Math.min(2.2, Math.max(0.3, Math.min(width / spanX, height / spanY)));
    view.x = -((minX + maxX) / 2) * view.zoom;
    view.y = -((minY + maxY) / 2) * view.zoom;
  }

  /* --- Interaction ------------------------------------------------------- */

  canvas.addEventListener('pointerdown', function (event) {
    canvas.setPointerCapture(event.pointerId);
    last = { x: event.clientX, y: event.clientY };
    var hit = nodeAt(event.clientX, event.clientY);
    if (hit) { dragging = hit; } else { panning = true; canvas.classList.add('dragging'); }
  });

  canvas.addEventListener('pointermove', function (event) {
    pointer.x = event.clientX;
    pointer.y = event.clientY;

    if (dragging) {
      var point = toWorld(event.clientX, event.clientY);
      dragging.x = point.x;
      dragging.y = point.y;
      return;
    }
    if (panning && last) {
      view.x += event.clientX - last.x;
      view.y += event.clientY - last.y;
      last = { x: event.clientX, y: event.clientY };
      return;
    }
    var hit = nodeAt(event.clientX, event.clientY);
    hovered = hit;
    canvas.style.cursor = hit ? 'pointer' : '';
  });

  function endPointer(event) {
    if (dragging && last &&
        Math.abs(event.clientX - last.x) < 4 && Math.abs(event.clientY - last.y) < 4) {
      openInspector(dragging);
    }
    dragging = null;
    panning = false;
    last = null;
    canvas.classList.remove('dragging');
  }

  canvas.addEventListener('pointerup', endPointer);
  canvas.addEventListener('pointercancel', endPointer);

  canvas.addEventListener('wheel', function (event) {
    event.preventDefault();
    var factor = Math.exp(-event.deltaY * 0.0016);
    var next = Math.min(4, Math.max(0.22, view.zoom * factor));
    var rect = canvas.getBoundingClientRect();
    var cx = event.clientX - rect.left - width / 2;
    var cy = event.clientY - rect.top - height / 2;
    view.x = cx - (cx - view.x) * (next / view.zoom);
    view.y = cy - (cy - view.y) * (next / view.zoom);
    view.zoom = next;
  }, { passive: false });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') closeInspector();
    if (event.key === '/' && document.activeElement !== search) {
      event.preventDefault();
      if (search) search.focus();
    }
  });

  window.addEventListener('resize', resize);

  /* --- Load -------------------------------------------------------------- */

  fetch('graph.json', { cache: 'no-store' })
    .then(function (response) { return response.json(); })
    .then(function (data) {
      nodes = (data.nodes || []).map(function (node, i) {
        var angle = i * 2.399;
        var radius = Math.sqrt(i + 1) * 42;
        return {
          id: node.id,
          title: node.title || node.id,
          summary: node.summary || '',
          tags: node.tags || [],
          url: node.url,
          degree: 0,
          x: Math.cos(angle) * radius,
          y: Math.sin(angle) * radius,
          vx: 0, vy: 0
        };
      });
      nodes.forEach(function (node) { byId[node.id] = node; });

      edges = (data.edges || []).map(function (edge) {
        var a = byId[edge.source];
        var b = byId[edge.target];
        if (!a || !b) return null;
        a.degree += 1;
        b.degree += 1;
        return { a: a, b: b };
      }).filter(Boolean);

      var tags = [];
      nodes.forEach(function (node) {
        node.tags.forEach(function (tag) {
          if (tags.indexOf(tag) === -1) tags.push(tag);
        });
      });
      tags.sort(function (a, b) { return a.localeCompare(b, 'pt-BR'); });
      tags.forEach(function (tag, i) { colorOf[tag] = PALETTE[i % PALETTE.length]; });

      if (tagSelect) {
        tags.forEach(function (tag) {
          var option = document.createElement('option');
          option.value = tag;
          option.textContent = tag;
          tagSelect.appendChild(option);
        });
      }

      var nodeCount = document.getElementById('nodeCount');
      var edgeCount = document.getElementById('edgeCount');
      if (nodeCount) nodeCount.textContent = nodes.length;
      if (edgeCount) edgeCount.textContent = edges.length;

      if (legend) {
        tags.slice(0, 8).forEach(function (tag) {
          var item = document.createElement('span');
          var swatch = document.createElement('i');
          swatch.className = 'legend-swatch';
          swatch.style.background = colorOf[tag];
          item.appendChild(swatch);
          item.appendChild(document.createTextNode(tag));
          legend.appendChild(item);
        });
      }

      resize();
      for (var i = 0; i < 220; i++) step();
      fitToContent();
      loop();
    })
    .catch(function () {
      if (intro) {
        intro.innerHTML = '<div class="eyebrow">GRAFO</div>'
          + '<h1>Não foi possível carregar.</h1>'
          + '<p>O arquivo graph.json não está disponível.</p>';
      }
    });

  if (search) {
    search.addEventListener('input', function () {
      query = normalize(search.value.trim());
      closeInspector();
    });
  }
  if (tagSelect) {
    tagSelect.addEventListener('change', function () {
      tagFilter = tagSelect.value;
      closeInspector();
    });
  }

  var closeInspectorButton = document.getElementById('closeInspector');
  if (closeInspectorButton) closeInspectorButton.addEventListener('click', closeInspector);

  var closeIntroButton = document.getElementById('closeIntro');
  if (closeIntroButton) {
    closeIntroButton.addEventListener('click', function () {
      if (intro) intro.remove();
    });
  }

  var recenter = document.getElementById('recenterGraph');
  if (recenter) recenter.addEventListener('click', fitToContent);
})();
