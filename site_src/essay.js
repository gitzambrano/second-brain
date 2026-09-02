const body=document.getElementById('articleBody'),toc=document.getElementById('toc'),heads=[...body.querySelectorAll('h2,h3')],used=new Map();function slug(s){let v=s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9\s-]/g,'').trim().replace(/[\s-]+/g,'-')||'section',n=used.get(v)||0;used.set(v,n+1);return n?`${v}-${n+1}`:v}for(const h of heads){if(!h.id)h.id=slug(h.textContent);const a=document.createElement('a');a.href=`#${h.id}`;a.textContent=h.textContent;if(h.tagName==='H3')a.classList.add('h3');toc?.appendChild(a)}const links=[...(toc?.querySelectorAll('a')||[])],io=new IntersectionObserver(es=>{for(const e of es)if(e.isIntersecting)links.forEach(a=>a.classList.toggle('active',a.getAttribute('href')===`#${e.target.id}`))},{rootMargin:'-20% 0px -70% 0px'});heads.forEach(h=>io.observe(h));const words=(body?.innerText.trim().match(/\S+/g)||[]).length;document.getElementById('readingTime').textContent=Math.max(1,Math.round(words/220));const p=document.getElementById('readingProgress');addEventListener('scroll',()=>{const d=document.documentElement,m=d.scrollHeight-innerHeight;p.style.width=`${m>0?(scrollY/m)*100:0}%`},{passive:true});

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
