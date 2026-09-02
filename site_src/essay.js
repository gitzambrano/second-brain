const body=document.getElementById('articleBody'),toc=document.getElementById('toc'),heads=[...body.querySelectorAll('h2,h3')],used=new Map();function slug(s){let v=s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9\s-]/g,'').trim().replace(/[\s-]+/g,'-')||'section',n=used.get(v)||0;used.set(v,n+1);return n?`${v}-${n+1}`:v}for(const h of heads){if(!h.id)h.id=slug(h.textContent);const a=document.createElement('a');a.href=`#${h.id}`;a.textContent=h.textContent;if(h.tagName==='H3')a.classList.add('h3');toc?.appendChild(a)}const links=[...(toc?.querySelectorAll('a')||[])],io=new IntersectionObserver(es=>{for(const e of es)if(e.isIntersecting)links.forEach(a=>a.classList.toggle('active',a.getAttribute('href')===`#${e.target.id}`))},{rootMargin:'-20% 0px -70% 0px'});heads.forEach(h=>io.observe(h));const words=(body?.innerText.trim().match(/\S+/g)||[]).length;document.getElementById('readingTime').textContent=Math.max(1,Math.round(words/220));const p=document.getElementById('readingProgress');addEventListener('scroll',()=>{const d=document.documentElement,m=d.scrollHeight-innerHeight;p.style.width=`${m>0?(scrollY/m)*100:0}%`},{passive:true});

/* Gold chapter breaks: the prose arrives from Pandoc without the label, so the
   kicker is inserted here. Self-numbered titles ("## 3. ...") hide their number
   and show CAPÍTULO N; semantic sections keep their word; otherwise a local
   counter numbers them. References gets a fixed REFERÊNCIAS label. */
(function () {
  var content = document.getElementById('articleBody');
  if (!content) return;
  var h2s = [...content.querySelectorAll('h2:not(#sum\u00e1rio):not(#refer\u00eancias):not(#referencias)')];
  if (!h2s.length) return;
  var selfNum = h2s.some(function (h) {
    return /^\s*(?:(?:se[çc][aã]o|cap[íi]tulo|parte)\s+)?(?:\d+|[IVXLC]+)[.\s—–:-]/i.test(h.textContent);
  });
  var SECTION_RE = /^\s*(?:(?:se[çc][aã]o|cap[íi]tulo|parte)\s*)?(?:\d+|[IVXLC]+)?\s*[.:\-—–]?\s*(introdu[çc][aã]o|conclus[aã]o|resumo(?:\s+executivo)?|pref[áa]cio|pr[óo]logo|ep[íi]logo|posf[áa]cio|p[óo]s-?escrito|agradecimentos|ap[êe]ndice|anexos?)\b/i;
  function stripSelfNumber(h) {
    var n = h.firstChild;
    while (n && n.nodeType !== 3) n = n.nextSibling;
    if (!n) return null;
    var m = /^\s*((?:(?:se[çc][aã]o|cap[íi]tulo|parte)\s+)?((?:\d+|[IVXLC]+))(?:[.\s—–:-]+))(?!\d)([\s\S]*)/i.exec(n.data);
    if (!m) return null;
    var span = document.createElement('span');
    span.className = 'sb-selfnum';
    span.setAttribute('aria-hidden', 'true');
    span.textContent = m[1];
    n.data = m[3];
    h.insertBefore(span, n);
    return m[2].toUpperCase();
  }
  function makeKicker(text) {
    var k = document.createElement('span');
    k.className = 'sb-kicker';
    k.textContent = text;
    return k;
  }
  var chapterNo = 0;
  h2s.forEach(function (h) {
    var sem = SECTION_RE.exec(h.textContent);
    var num = selfNum ? stripSelfNumber(h) : null;
    var label = null;
    if (sem) label = sem[1].toUpperCase();
    else if (num) label = 'CAPÍTULO ' + (/^[0-9]/.test(num) && num.length < 2 ? '0' + num : num);
    else if (!selfNum) { chapterNo += 1; label = 'CAPÍTULO ' + (chapterNo < 10 ? '0' + chapterNo : chapterNo); }
    if (label) h.insertBefore(makeKicker(label), h.firstChild);
  });
  var refs = content.querySelector('h2#refer\u00eancias, h2#referencias');
  if (refs) {
    var k = makeKicker('REFERÊNCIAS');
    refs.textContent = '';
    refs.appendChild(k);
  }
})();

/* Summary controls: collapsible in the desktop rail, a sheet on a phone.
   The choice is remembered so it does not have to be made on every essay. */
(function () {
  var pane = document.getElementById('tocPane');
  var toggle = document.getElementById('tocToggle');
  var fab = document.getElementById('tocFab');
  if (!pane) return;

  function setCollapsed(collapsed) {
    pane.classList.toggle('collapsed', collapsed);
    if (toggle) {
      toggle.setAttribute('aria-expanded', String(!collapsed));
      toggle.setAttribute('aria-label', collapsed ? 'Expandir o sumário' : 'Recolher o sumário');
      toggle.firstChild.textContent = collapsed ? '+' : '−';
    }
    try { localStorage.setItem('sb-toc', collapsed ? 'collapsed' : 'open'); } catch (e) { /* private mode */ }
  }

  var stored = null;
  try { stored = localStorage.getItem('sb-toc'); } catch (e) { /* private mode */ }
  if (stored === 'collapsed') setCollapsed(true);

  if (toggle) {
    toggle.addEventListener('click', function () {
      setCollapsed(!pane.classList.contains('collapsed'));
    });
  }

  if (fab) {
    fab.addEventListener('click', function () {
      var open = !pane.classList.contains('open');
      pane.classList.toggle('open', open);
      fab.setAttribute('aria-expanded', String(open));
      fab.textContent = open ? 'Fechar' : 'Sumário';
    });
    // Following a link means the reader is done with the summary.
    pane.addEventListener('click', function (event) {
      if (event.target.closest('a')) {
        pane.classList.remove('open');
        fab.setAttribute('aria-expanded', 'false');
        fab.textContent = 'Sumário';
      }
    });
  }
})();
