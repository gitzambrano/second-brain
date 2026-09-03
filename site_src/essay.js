/* Site chrome for an exported essay: floating summary, reading progress and
   the theme toggle. The essay body itself is rendered by the export pipeline
   and is not touched here. */
(function () {
  'use strict';

  var root = document.documentElement;

  /* --- Theme --------------------------------------------------------------- */
  var themeButton = document.getElementById('sbTheme');
  function applyTheme(theme, persist) {
    root.dataset.theme = theme;
    if (themeButton) themeButton.setAttribute('aria-pressed', String(theme === 'light'));
    if (persist) {
      try { localStorage.setItem('sb-theme', theme); } catch (e) { /* private mode */ }
    }
  }
  applyTheme(root.dataset.theme || 'dark', false);
  if (themeButton) {
    themeButton.addEventListener('click', function () {
      applyTheme(root.dataset.theme === 'dark' ? 'light' : 'dark', true);
    });
  }

  /* --- Summary ------------------------------------------------------------- */
  var list = document.getElementById('sbTocList');
  var panel = document.getElementById('sbToc');
  var fab = document.getElementById('sbTocFab');
  if (!list || !panel || !fab) return;

  var used = {};
  function slugify(text) {
    var base = text.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .toLowerCase().replace(/[^a-z0-9\s-]/g, '').trim().replace(/[\s-]+/g, '-') || 'secao';
    var seen = used[base] || 0;
    used[base] = seen + 1;
    return seen ? base + '-' + (seen + 1) : base;
  }

  function cleanHeadingText(heading) {
    var clone = heading.cloneNode(true);
    var kicker = clone.querySelector('.sb-kicker');
    var kickerText = kicker ? kicker.textContent.trim() : '';
    if (kicker) kicker.remove();
    var selfnum = clone.querySelector('.sb-selfnum');
    var selfnumText = selfnum ? selfnum.textContent.trim() : '';
    if (selfnum) selfnum.remove();
    var hlink = clone.querySelector('.hlink');
    if (hlink) hlink.remove();

    var baseText = clone.textContent.replace(/\s+/g, ' ').trim();

    if (kickerText) {
      if (!baseText.toLowerCase().startsWith(kickerText.toLowerCase())) {
        return kickerText + ' — ' + baseText;
      }
    } else if (selfnumText) {
      if (!baseText.startsWith(selfnumText)) {
        return selfnumText + ' ' + baseText;
      }
    }
    return baseText;
  }

  var headings = [].slice.call(document.querySelectorAll('.content h2:not(#sumário):not(#sumario), .content h3'));
  if (!headings.length) {
    headings = [].slice.call(document.querySelectorAll('h2:not(#sumário):not(#sumario), h3'));
  }
  headings.forEach(function (heading) {
    if (!heading.id) heading.id = slugify(heading.textContent);
    var link = document.createElement('a');
    link.href = '#' + heading.id;
    link.textContent = cleanHeadingText(heading);
    if (heading.tagName === 'H3') link.className = 'h3';
    list.appendChild(link);
  });

  var links = [].slice.call(list.querySelectorAll('a'));
  if (headings.length && 'IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (a) {
          a.classList.toggle('active', a.getAttribute('href') === '#' + entry.target.id);
        });
      });
    }, { rootMargin: '-15% 0px -75% 0px' });
    headings.forEach(function (h) { observer.observe(h); });
  }

  function setOpen(open) {
    panel.hidden = !open;
    fab.setAttribute('aria-expanded', String(open));
    try { localStorage.setItem('sb-toc-open', open ? '1' : '0'); } catch (e) { /* private */ }
  }

  // Always starts closed: an open panel lands on top of the title, and the
  // first thing a reader wants is the essay, not its index.
  setOpen(false);

  fab.addEventListener('click', function () { setOpen(panel.hidden); });
  var close = document.getElementById('sbTocClose');
  if (close) close.addEventListener('click', function () { setOpen(false); });

  // Following a link means the reader is done choosing; keep it open on desktop.
  panel.addEventListener('click', function (event) {
    if (event.target.closest('a') && window.innerWidth < 1280) setOpen(false);
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && !panel.hidden) setOpen(false);
  });

  /* --- Reading progress ---------------------------------------------------- */
  var fill = document.getElementById('sbProgressFill');
  if (fill) {
    addEventListener('scroll', function () {
      var max = document.documentElement.scrollHeight - innerHeight;
      fill.style.width = (max > 0 ? (scrollY / max) * 100 : 0) + '%';
    }, { passive: true });
  }
})();
