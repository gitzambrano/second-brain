/* The public map of the whole base.

   graph.json carries every essay, concept, entity, insight and reference, plus
   every connection between them, with the layout already solved at build time.
   Only essays authorized with `publish: true` are readable — those open. Every
   other node is identity only and is labelled "privado".

   Because the layout arrives precomputed, there is no force simulation here:
   the canvas is redrawn on demand instead of every frame, so a graph of a few
   thousand nodes stays responsive. */
(function () {
  'use strict';

  var root = document.documentElement;
  var canvas = document.getElementById('graphCanvas');
  if (!canvas) return;

  var ctx = canvas.getContext('2d');
  var search = document.getElementById('graphSearch');
  var typeSelect = document.getElementById('graphType');
  var tagSelect = document.getElementById('graphTag');
  var inspector = document.getElementById('graphInspector');
  var intro = document.getElementById('graphIntro');
  var legend = document.getElementById('graphLegend');
  var indexPanel = document.getElementById('graphIndex');
  var indexBody = document.getElementById('indexBody');

  var TYPES = {
    essay: { label: 'Essays', color: '#7aabff' },
    concept: { label: 'Conceitos', color: '#7be0c3' },
    entity: { label: 'Entidades', color: '#f2a65a' },
    insights: { label: 'Insights', color: '#c99bff' },
    reference: { label: 'Referências', color: '#8494ad' }
  };

  var view = { x: 0, y: 0, zoom: 1 };
  var width = 0;
  var height = 0;
  var nodes = [];
  var edges = [];
  var byId = {};
  var adjacency = {};
  var selected = null;
  var hovered = null;
  var dragging = null;
  var panning = false;
  var last = null;
  var moved = 0;
  var query = '';
  var typeFilter = '';
  var tagFilter = '';
  var needsDraw = true;

  function normalize(value) {
    return (value || '')
      .toLocaleLowerCase('pt-BR')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  function invalidate() { needsDraw = true; }

  function colorFor(node) {
    return (TYPES[node.type] || {}).color || '#7aabff';
  }

  function nodeRadius(node) {
    return 3.2 + Math.min(11, Math.sqrt(node.degree) * 2.1);
  }

  function isMatch(node) {
    if (typeFilter && node.type !== typeFilter) return false;
    if (tagFilter && node.tags.indexOf(tagFilter) === -1) return false;
    if (query && node.haystack.indexOf(query) === -1) return false;
    return true;
  }

  /* --- Geometry ---------------------------------------------------------- */

  function resize() {
    var ratio = window.devicePixelRatio || 1;
    width = canvas.clientWidth;
    height = canvas.clientHeight;
    canvas.width = Math.max(1, Math.round(width * ratio));
    canvas.height = Math.max(1, Math.round(height * ratio));
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    invalidate();
  }

  function toWorld(clientX, clientY) {
    var rect = canvas.getBoundingClientRect();
    return {
      x: (clientX - rect.left - width / 2 - view.x) / view.zoom,
      y: (clientY - rect.top - height / 2 - view.y) / view.zoom
    };
  }

  function fitToContent(subset) {
    var list = (subset && subset.length) ? subset : nodes;
    if (!list.length) return;
    var minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    list.forEach(function (node) {
      minX = Math.min(minX, node.x); maxX = Math.max(maxX, node.x);
      minY = Math.min(minY, node.y); maxY = Math.max(maxY, node.y);
    });
    var spanX = Math.max(160, maxX - minX + 160);
    var spanY = Math.max(160, maxY - minY + 160);
    view.zoom = Math.min(3, Math.max(0.08, Math.min(width / spanX, height / spanY)));
    view.x = -((minX + maxX) / 2) * view.zoom;
    view.y = -((minY + maxY) / 2) * view.zoom;
    invalidate();
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
    var near = focus ? adjacency[focus.id] : null;

    ctx.lineWidth = Math.max(0.4, 1 / view.zoom);
    ctx.strokeStyle = lineColor;
    ctx.globalAlpha = focus ? 0.08 : 0.16;
    ctx.beginPath();
    edges.forEach(function (edge) {
      if (focus && (edge.a === focus || edge.b === focus)) return;
      if (!edge.a.visible || !edge.b.visible) return;
      ctx.moveTo(edge.a.x, edge.a.y);
      ctx.lineTo(edge.b.x, edge.b.y);
    });
    ctx.stroke();

    if (focus) {
      ctx.globalAlpha = 0.9;
      ctx.strokeStyle = colorFor(focus);
      ctx.lineWidth = Math.max(0.8, 1.6 / view.zoom);
      ctx.beginPath();
      edges.forEach(function (edge) {
        if (edge.a !== focus && edge.b !== focus) return;
        ctx.moveTo(edge.a.x, edge.a.y);
        ctx.lineTo(edge.b.x, edge.b.y);
      });
      ctx.stroke();
    }

    nodes.forEach(function (node) {
      var radius = nodeRadius(node);
      var dim = !node.visible || (focus && node !== focus && !(near && near[node.id]));

      ctx.globalAlpha = dim ? 0.12 : 1;
      ctx.beginPath();
      ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
      ctx.fillStyle = colorFor(node);
      ctx.fill();

      // A readable essay gets a ring: on this map, openable is the exception.
      if (node.published && !dim) {
        ctx.lineWidth = Math.max(0.8, 1.8 / view.zoom);
        ctx.strokeStyle = textColor;
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    });

    ctx.restore();

    // Labels are drawn in screen space so overlap can be measured in pixels:
    // the densest areas would otherwise turn into unreadable stacked text.
    var candidates = nodes.filter(function (node) {
      if (!node.visible) return false;
      if (focus) return node === focus || (near && near[node.id]);
      return true;
    });
    candidates.sort(function (a, b) { return b.degree - a.degree; });

    ctx.font = '500 11px Inter, system-ui, sans-serif';
    ctx.textBaseline = 'middle';

    var claimed = [];
    var budget = focus ? 40 : 90;
    for (var i = 0; i < candidates.length && budget > 0; i++) {
      var node = candidates[i];
      var sx = node.x * view.zoom + width / 2 + view.x;
      var sy = node.y * view.zoom + height / 2 + view.y;
      if (sx < -40 || sy < -20 || sx > width + 40 || sy > height + 20) continue;

      var label = node.title.length > 46 ? node.title.slice(0, 45) + '…' : node.title;
      var box = {
        left: sx + nodeRadius(node) * view.zoom + 6,
        top: sy - 8,
        right: sx + nodeRadius(node) * view.zoom + 6 + ctx.measureText(label).width,
        bottom: sy + 8
      };
      var blocked = false;
      for (var j = 0; j < claimed.length; j++) {
        var other = claimed[j];
        if (box.left < other.right && box.right > other.left
            && box.top < other.bottom && box.bottom > other.top) {
          blocked = true;
          break;
        }
      }
      if (blocked) continue;

      claimed.push(box);
      budget -= 1;
      ctx.fillStyle = node === focus ? textColor : node.published ? textColor : mutedColor;
      ctx.fillText(label, box.left, sy);
    }
  }

  function loop() {
    if (needsDraw) {
      needsDraw = false;
      draw();
    }
    requestAnimationFrame(loop);
  }

  function applyFilters() {
    var visible = 0;
    nodes.forEach(function (node) {
      node.visible = isMatch(node);
      if (node.visible) visible += 1;
    });
    var counter = document.getElementById('nodeCount');
    if (counter) counter.textContent = visible;
    renderIndex();
    invalidate();
  }

  /* --- Inspector --------------------------------------------------------- */

  function badge(text, kind) {
    var el = document.createElement('span');
    el.className = 'badge' + (kind ? ' badge-' + kind : '');
    el.textContent = text;
    return el;
  }

  function openInspector(node) {
    selected = node;
    if (!inspector) return;
    inspector.hidden = false;

    var badges = document.getElementById('inspectorBadges');
    badges.textContent = '';
    badges.appendChild(badge((TYPES[node.type] || {}).label || node.type, 'type'));
    if (node.published) {
      badges.appendChild(badge('Público', 'public'));
    } else {
      badges.appendChild(badge('Privado', 'private'));
    }
    if (node.status === 'draft') badges.appendChild(badge('Rascunho', 'draft'));

    document.getElementById('inspectorTitle').textContent = node.title;

    var summary = document.getElementById('inspectorSummary');
    summary.textContent = node.summary || '';
    summary.hidden = !node.summary;

    var tagBox = document.getElementById('inspectorTags');
    tagBox.textContent = '';
    node.tags.forEach(function (tag) {
      var chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'tag';
      chip.textContent = tag;
      chip.addEventListener('click', function () {
        if (tagSelect) { tagSelect.value = tag; }
        tagFilter = tag;
        applyFilters();
      });
      tagBox.appendChild(chip);
    });

    var neighbours = document.getElementById('inspectorNeighbours');
    neighbours.textContent = '';
    var ids = Object.keys(adjacency[node.id] || {});
    if (ids.length) {
      var label = document.createElement('div');
      label.className = 'rail-label';
      label.textContent = ids.length + ' conexões';
      neighbours.appendChild(label);
      var list = document.createElement('div');
      list.className = 'neighbour-list';
      ids.slice(0, 12).forEach(function (id) {
        var other = byId[id];
        if (!other) return;
        var item = document.createElement('button');
        item.type = 'button';
        item.className = 'neighbour';
        item.innerHTML = '<i style="background:' + colorFor(other) + '"></i>';
        item.appendChild(document.createTextNode(other.title));
        item.addEventListener('click', function () { focusNode(other); });
        list.appendChild(item);
      });
      neighbours.appendChild(list);
    }

    var link = document.getElementById('inspectorLink');
    var note = document.getElementById('inspectorNote');
    if (node.published && node.url) {
      link.href = node.url;
      link.firstChild.textContent = 'Abrir essay ';
      link.hidden = false;
      note.hidden = true;
    } else if (node.type === 'reference' && node.url) {
      link.href = node.url;
      link.firstChild.textContent = 'Abrir referência ';
      link.hidden = false;
      note.hidden = true;
    } else {
      link.hidden = true;
      note.hidden = false;
    }
    invalidate();
  }

  function closeInspector() {
    selected = null;
    if (inspector) inspector.hidden = true;
    invalidate();
  }

  function focusNode(node) {
    view.zoom = Math.max(view.zoom, 1.1);
    view.x = -node.x * view.zoom;
    view.y = -node.y * view.zoom;
    openInspector(node);
  }

  function nodeAt(clientX, clientY) {
    var point = toWorld(clientX, clientY);
    var best = null;
    var bestDistance = Infinity;
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i];
      if (!node.visible) continue;
      var reach = nodeRadius(node) + 6 / view.zoom;
      var dx = node.x - point.x;
      var dy = node.y - point.y;
      var distance = dx * dx + dy * dy;
      if (distance < reach * reach && distance < bestDistance) {
        best = node;
        bestDistance = distance;
      }
    }
    return best;
  }

  /* --- Complete index ---------------------------------------------------- */

  function renderIndex() {
    if (!indexBody || indexPanel.hidden) return;
    indexBody.textContent = '';
    var visible = nodes.filter(function (node) { return node.visible; });
    document.getElementById('indexCount').textContent = visible.length + ' nós';

    Object.keys(TYPES).forEach(function (type) {
      var group = visible.filter(function (node) { return node.type === type; });
      if (!group.length) return;
      group.sort(function (a, b) { return a.title.localeCompare(b.title, 'pt-BR'); });

      var heading = document.createElement('div');
      heading.className = 'index-group';
      heading.innerHTML = '<span>' + TYPES[type].label + '</span><span class="count">'
        + group.length + '</span>';
      indexBody.appendChild(heading);

      var list = document.createElement('div');
      list.className = 'index-list';
      group.forEach(function (node) {
        var item = document.createElement('button');
        item.type = 'button';
        item.className = 'index-item' + (node.published ? ' is-public' : '');
        var dot = document.createElement('i');
        dot.style.background = colorFor(node);
        item.appendChild(dot);
        var title = document.createElement('span');
        title.textContent = node.title;
        item.appendChild(title);
        if (node.published) {
          var mark = document.createElement('em');
          mark.textContent = 'público';
          item.appendChild(mark);
        }
        item.addEventListener('click', function () { focusNode(node); });
        list.appendChild(item);
      });
      indexBody.appendChild(list);
    });
  }

  function toggleIndex() {
    var button = document.getElementById('toggleIndex');
    indexPanel.hidden = !indexPanel.hidden;
    button.setAttribute('aria-expanded', String(!indexPanel.hidden));
    renderIndex();
  }

  /* --- Interaction ------------------------------------------------------- */

  canvas.addEventListener('pointerdown', function (event) {
    canvas.setPointerCapture(event.pointerId);
    last = { x: event.clientX, y: event.clientY };
    moved = 0;
    var hit = nodeAt(event.clientX, event.clientY);
    if (hit) {
      dragging = hit;
    } else {
      panning = true;
      canvas.classList.add('dragging');
    }
  });

  canvas.addEventListener('pointermove', function (event) {
    if (dragging) {
      var point = toWorld(event.clientX, event.clientY);
      dragging.x = point.x;
      dragging.y = point.y;
      moved += 1;
      invalidate();
      return;
    }
    if (panning && last) {
      view.x += event.clientX - last.x;
      view.y += event.clientY - last.y;
      last = { x: event.clientX, y: event.clientY };
      invalidate();
      return;
    }
    var hit = nodeAt(event.clientX, event.clientY);
    if (hit !== hovered) {
      hovered = hit;
      canvas.style.cursor = hit ? 'pointer' : '';
      invalidate();
    }
  });

  function endPointer() {
    if (dragging && moved < 3) openInspector(dragging);
    dragging = null;
    panning = false;
    last = null;
    canvas.classList.remove('dragging');
  }

  canvas.addEventListener('pointerup', endPointer);
  canvas.addEventListener('pointercancel', endPointer);

  canvas.addEventListener('wheel', function (event) {
    event.preventDefault();
    var next = Math.min(6, Math.max(0.06, view.zoom * Math.exp(-event.deltaY * 0.0016)));
    var rect = canvas.getBoundingClientRect();
    var cx = event.clientX - rect.left - width / 2;
    var cy = event.clientY - rect.top - height / 2;
    view.x = cx - (cx - view.x) * (next / view.zoom);
    view.y = cy - (cy - view.y) * (next / view.zoom);
    view.zoom = next;
    invalidate();
  }, { passive: false });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      closeInspector();
      if (indexPanel && !indexPanel.hidden) toggleIndex();
    }
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
      nodes = (data.nodes || []).map(function (node) {
        return {
          id: node.id,
          title: node.title || node.id,
          summary: node.summary || '',
          tags: node.tags || [],
          type: node.type,
          status: node.status || '',
          url: node.url || '',
          published: !!node.published,
          degree: node.degree || 0,
          x: node.x || 0,
          y: node.y || 0,
          visible: true,
          haystack: normalize((node.title || '') + ' ' + (node.tags || []).join(' '))
        };
      });
      nodes.forEach(function (node) {
        byId[node.id] = node;
        adjacency[node.id] = {};
      });

      edges = (data.edges || []).map(function (edge) {
        var a = byId[edge.source];
        var b = byId[edge.target];
        if (!a || !b) return null;
        adjacency[a.id][b.id] = true;
        adjacency[b.id][a.id] = true;
        return { a: a, b: b };
      }).filter(Boolean);

      var counts = data.counts || {};
      if (typeSelect) {
        Object.keys(TYPES).forEach(function (type) {
          if (!counts[type]) return;
          var option = document.createElement('option');
          option.value = type;
          option.textContent = TYPES[type].label + ' (' + counts[type] + ')';
          typeSelect.appendChild(option);
        });
      }

      var tags = [];
      nodes.forEach(function (node) {
        node.tags.forEach(function (tag) {
          if (tags.indexOf(tag) === -1) tags.push(tag);
        });
      });
      tags.sort(function (a, b) { return a.localeCompare(b, 'pt-BR'); });
      if (tagSelect) {
        tags.forEach(function (tag) {
          var option = document.createElement('option');
          option.value = tag;
          option.textContent = tag;
          tagSelect.appendChild(option);
        });
      }

      document.getElementById('nodeCount').textContent = nodes.length;
      document.getElementById('edgeCount').textContent = edges.length;

      if (legend) {
        Object.keys(TYPES).forEach(function (type) {
          if (!counts[type]) return;
          var item = document.createElement('span');
          var swatch = document.createElement('i');
          swatch.className = 'legend-swatch';
          swatch.style.background = TYPES[type].color;
          item.appendChild(swatch);
          item.appendChild(document.createTextNode(TYPES[type].label));
          legend.appendChild(item);
        });
      }

      resize();
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
      applyFilters();
    });
  }
  if (typeSelect) {
    typeSelect.addEventListener('change', function () {
      typeFilter = typeSelect.value;
      closeInspector();
      applyFilters();
    });
  }
  if (tagSelect) {
    tagSelect.addEventListener('change', function () {
      tagFilter = tagSelect.value;
      closeInspector();
      applyFilters();
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

  var indexButton = document.getElementById('toggleIndex');
  if (indexButton) indexButton.addEventListener('click', toggleIndex);
  var closeIndexButton = document.getElementById('closeIndex');
  if (closeIndexButton) closeIndexButton.addEventListener('click', toggleIndex);

  var recenter = document.getElementById('recenterGraph');
  if (recenter) {
    recenter.addEventListener('click', function () {
      fitToContent(nodes.filter(function (node) { return node.visible; }));
    });
  }
})();
