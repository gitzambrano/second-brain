-- pdf_boxes.lua - Converte fenced divs semanticos (emitidos por
-- html_preprocess.transform_markdown) em ambientes/caixas LaTeX definidos
-- no header do export_essay_pdf.py.
--
-- O pipeline PDF roda o MESMO preprocessador do HTML, entao ambos os
-- exports enxergam a mesma estrutura: .box (+ .box-badge/.box-title/
-- .box-verdict), .quote, .pull-quote (+ .pq-cite), .card (+ .card-name/
-- .card-meta), .label-solo e ornamentos (<div class="ornament">).
--
-- A travessia do Pandoc e bottom-up: os divs internos viram comandos LaTeX
-- ANTES do div externo montar o ambiente, entao o externo apenas desempacota
-- conteudo ja convertido entre \begin{...}/\end{...}.
--
-- Tambem reduz o tamanho dos paragrafos-legenda de figura ("Fig. N - ...").

local stringify = pandoc.utils.stringify

-- Escapa caracteres especiais do LaTeX em texto plano vindo de stringify.
local function lescape(s)
  s = s:gsub('\\', '\001BSL\001')
  s = s:gsub('([#$%%_{}])', '\\%1')
  s = s:gsub('&', '\\&')
  s = s:gsub('~', '\\textasciitilde{}')
  s = s:gsub('%^', '\\textasciicircum{}')
  s = s:gsub('\001BSL\001', '$\\backslash$')
  return s
end

local function has_class(el, class)
  for _, c in ipairs(el.classes) do
    if c == class then return true end
  end
  return false
end

-- ------------------------------------------------------------------
-- Divs internos (viram comandos/comentarios LaTeX antes do ambiente)
-- ------------------------------------------------------------------

local MARKER_COMMANDS = {
  ['box-badge'] = function(txt) return '\\wbbadge{' .. lescape(txt) .. '}' end,
  ['box-title'] = function(txt) return '\\wbtitle{' .. lescape(txt) .. '}' end,
  ['card-name'] = function(txt) return '\\cardname{' .. lescape(txt) .. '}' end,
  ['card-meta'] = function(txt) return '\\cardmeta{' .. lescape(txt) .. '}' end,
}

function Div(el)
  for class, fmt in pairs(MARKER_COMMANDS) do
    if has_class(el, class) then
      return { pandoc.RawBlock('latex', fmt(stringify(el)) .. '%') }
    end
  end

  -- Rodape de caixa: filete + texto pequeno, dentro do proprio wikibox.
  if has_class(el, 'box-verdict') then
    local out = { pandoc.RawBlock('latex',
      '\\vspace{4pt}\\par\\hrule height 0.4pt\\vspace{5pt}\\begingroup\\small%') }
    for _, b in ipairs(el.content) do table.insert(out, b) end
    table.insert(out, pandoc.RawBlock('latex', '\\endgroup%'))
    return out
  end

  -- Citação de pull-quote: parte de baixo do ambiente, sem itálico.
  if has_class(el, 'pq-cite') then
    return {
      pandoc.RawBlock('latex',
        '\\par\\vspace{4pt}\\noindent{\\upshape\\footnotesize\\color{subtlegray}%'),
      pandoc.Para({ pandoc.Str(lescape(stringify(el))) }),
      pandoc.RawBlock('latex', '}%'),
    }
  end

  -- Rotulo solto: mini-cabecalho antes de listas/prosa.
  if has_class(el, 'label-solo') then
    return { pandoc.RawBlock('latex',
      '\\parahead{' .. lescape(stringify(el)) .. '}') }
  end

  return nil
end

-- ------------------------------------------------------------------
-- Ambientes externos
-- ------------------------------------------------------------------

local ENVS = {
  ['box'] = 'wikibox',
  ['quote'] = 'wikiquote',
  ['pull-quote'] = 'wikipull',
  ['card'] = 'wikicard',
}

local function env_for(el)
  for class, env in pairs(ENVS) do
    if has_class(el, class) then return env end
  end
  return nil
end

local orig_Div = Div
function Div(el)
  local env = env_for(el)
  if not env then return orig_Div(el) end
  local out = { pandoc.RawBlock('latex', '\\begin{' .. env .. '}%') }
  for _, b in ipairs(el.content) do table.insert(out, b) end
  table.insert(out, pandoc.RawBlock('latex', '\\end{' .. env .. '}%'))
  return out
end

-- Ornamento: o preprocessador emite <div class="ornament">glifo</div> como
-- HTML cru, que o writer LaTeX descartaria. Recria centralizado.
function RawBlock(el)
  if el.format == 'html' then
    local glyph = el.text:match('^<div class="ornament">(.-)</div>%s*$')
    if glyph then
      return { pandoc.RawBlock('latex',
        '\\begin{center}\\color{subtlegray}\\ornamentglyph{' ..
        lescape(glyph) .. '}\\end{center}') }
    end
  end
  return nil
end

-- ------------------------------------------------------------------
-- Legendas de figura em prosa ("Fig. N - ..." / "Figura N ...")
-- ------------------------------------------------------------------

function Para(el)
  -- Figura solta: paragrafo contendo somente imagem vai para o centro.
  -- Imagem inline no meio de prosa nao e tocada. As legendas "Fig. N - ..."
  -- sao paragrafos proprios e continuam alinhadas a esquerda.
  if #el.content == 1 and el.content[1].t == 'Image' then
    return {
      pandoc.RawBlock('latex', '\\begin{center}%'),
      el,
      pandoc.RawBlock('latex', '\\end{center}%'),
    }
  end

  local text = stringify(el)
  if text:match('^Fig%.%s*%d') or text:match('^Figura%s+%d') then
    -- Sem '%': o wrapper e INLINE e pode cair no meio de uma linha fisica
    -- do .tex — '%' comentaria o resto da linha (incluindo o '\emph{' que
    -- vem junto), deixando '}' orfaos ("Extra }" no LuaLaTeX). Um espaco
    -- depois de \small termina o comando com seguranca.
    local out = { pandoc.RawInline('latex', '\\begingroup\\small ') }
    for _, inl in ipairs(el.content) do table.insert(out, inl) end
    table.insert(out, pandoc.RawInline('latex', '\\endgroup'))
    return pandoc.Para(out)
  end
  return nil
end
