-- pdf_boxes.lua - Premium PDF: semantic boxes, typographic Sumário,
-- reference items with hanging indent, styled figure captions.
--
-- Pipeline: html_preprocess.transform_markdown → fenced divs → this filter
-- → LaTeX environments defined in HEADER_TEX (export_essay_pdf.py).
-- Wikibox receives a color argument from badge-content heuristics.
-- Sumário is converted from BulletList to sbtoc environment.
-- References (## Referências) get sbrefitem wrapping + Link→↗.

local stringify = pandoc.utils.stringify

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
-- Box color detection from badge content
-- ------------------------------------------------------------------

-- Ordem importa: a primeira regra que casar vence. As mais especificas
-- ("experimento mental", "evidencia empirica") vem antes das genericas,
-- senao "evidência empírica" cairia em nenhuma e "experimento" perderia
-- para um substring solto.
--
-- O vocabulario real do corpus e: IDEIA NN, EXPERIMENTO MENTAL N,
-- EVIDENCIA EMPIRICA N, MAPA CONCEITUAL. Os dois do meio nao casavam com
-- regra nenhuma e saiam no cinza padrao — justamente os dois tipos mais
-- expressivos. Antes de tirar um termo daqui, confira o que o corpus usa:
--   grep -oh 'class="box-badge">' -A2 output/html/*.html
local BADGE_COLOR_RULES = {
  {'experimento mental', 'boxexp'}, {'experimento', 'boxexp'},
  {'evidência empírica', 'boxev'}, {'evidencia empirica', 'boxev'},
  {'evidência', 'boxev'}, {'evidencia', 'boxev'}, {'dado', 'boxev'},
  {'mapa conceitual', 'boxmap'}, {'mapa', 'boxmap'},
  {'título', 'boxmap'}, {'titulo', 'boxmap'}, {'resumo', 'boxmap'},
  {'definição', 'boxmap'}, {'definicao', 'boxmap'}, {'conceito', 'boxmap'},
  {'framework', 'boxmap'}, {'teoria', 'boxmap'},
  {'exemplo', 'boxexp'}, {'caso', 'boxexp'}, {'casuístico', 'boxexp'},
  {'aplicação', 'boxexp'}, {'aplicacao', 'boxexp'},
  {'aviso', 'boxav'}, {'atenção', 'boxav'}, {'atencao', 'boxav'},
  {'cuidado', 'boxav'}, {'problema', 'boxav'}, {'risco', 'boxav'},
  {'ataque', 'boxav'}, {'objeção', 'boxav'}, {'objecao', 'boxav'},
  {'evolução', 'boxev'}, {'evolucao', 'boxev'}, {'história', 'boxev'},
  {'linha do tempo', 'boxev'}, {'cronologia', 'boxev'},
  {'insight', 'boxid'}, {'ideia', 'boxid'}, {'idéia', 'boxid'},
  {'tese', 'boxid'}, {'argumento', 'boxid'},
  {'princípio', 'boxid'}, {'principio', 'boxid'},
}

local function get_box_color(el)
  for _, b in ipairs(el.content) do
    if b.t == 'Div' and has_class(b, 'box-badge') then
      -- `string.lower` do Lua so mapeia ASCII: "EVIDÊNCIA" viraria
      -- "evidÊncia" (o Ê fica com os bytes da maiuscula) e nunca casaria
      -- com a regra acentuada. `pandoc.text.lower` e ciente de UTF-8.
      local badge = pandoc.text.lower(stringify(b))
      for _, rule in ipairs(BADGE_COLOR_RULES) do
        if badge:find(rule[1], 1, true) then
          return rule[2]
        end
      end
      return 'boxline'
    end
  end
  return 'boxline'
end

-- ------------------------------------------------------------------
-- State: Sumário and References tracking
-- ------------------------------------------------------------------

local after_sumario = false
local in_references = false

local ROMAN = {'I','II','III','IV','V','VI','VII','VIII','IX','X',
               'XI','XII','XIII','XIV','XV','XVI','XVII','XVIII','XIX','XX'}

local function is_roman(s)
  return s:match('^[IVXLCDM]+$') ~= nil
end

local function romanize_toc(num)
  local n = tonumber(num)
  if n and n <= #ROMAN then return ROMAN[n] end
  return num
end

-- Devolve (numeral, tamanho-do-prefixo-em-bytes) do inicio do texto, ou nil.
--
-- ATENCAO: padroes do Lua NAO tem grupo nao-capturante. A versao anterior
-- usava `%d+(?:%.%d+)*`, sintaxe de PCRE, que em Lua nunca casa — o ramo
-- arabe morria silenciosamente e todo Sumario numerado com "1." saia com a
-- numeracao DUPLICADA (goteira romana do contador + "1." no proprio titulo).
--
-- O numeral tambem e preservado no sistema em que o autor escreveu: romano
-- continua romano, arabe continua arabe. Romanizar "3." virava "III" no
-- kicker enquanto as subsecoes seguiam "3.1" — dois sistemas para o mesmo
-- capitulo na mesma pagina.
local function extract_toc_number(text)
  -- 1) Romanos: "I.", "II -", "XIV:"
  local r, rest_r = text:match('^%s*([IVXLCDM]+)%s*[%.%-%–:]%s*(.*)$')
  if r and is_roman(r) then
    return r, #text - #rest_r
  end
  -- 2) Arabes, com ou sem subnivel: "1.", "2 -", "1.1", "4:"
  local a, rest_a = text:match('^%s*(%d+[%d%.]*)%s*[%.%-%–:]%s*(.*)$')
  if a then
    a = a:gsub('%.$', '')
    return a, #text - #rest_a
  end
  -- 3) "1 Titulo" / "III Titulo" (sem pontuacao separadora)
  local b, rest_b = text:match('^%s*(%d+)%s+(%a.*)$')
  if b then
    return b, #text - #rest_b
  end
  return nil, 0
end

-- Remove `n` bytes do inicio dos inlines, descendo em elementos aninhados
-- (o item do Sumario e quase sempre um Link envolvendo o texto). Preserva
-- Math/Emph/Code intactos: o `stringify` + `lescape` da versao anterior
-- achatava tudo em texto e cuspia `\dot{\beta}` e `C_{n_\beta}` crus na
-- pagina.
local function drop_prefix(inlines, n)
  if n <= 0 then return inlines end
  local left = n
  local function walk(list)
    local out = {}
    for _, el in ipairs(list) do
      if left <= 0 then
        table.insert(out, el)
      elseif el.t == 'Str' then
        if #el.text <= left then
          left = left - #el.text
        else
          table.insert(out, pandoc.Str(el.text:sub(left + 1)))
          left = 0
        end
      elseif el.t == 'Space' or el.t == 'SoftBreak' then
        left = left - 1
      elseif el.content then
        el.content = walk(el.content)
        table.insert(out, el)
      else
        table.insert(out, el)
      end
    end
    return out
  end
  return walk(inlines)
end

-- Inlines de um item de lista (primeiro bloco Para/Plain).
local function item_inlines(item)
  for _, b in ipairs(item) do
    if b.t == 'Para' or b.t == 'Plain' then return b.content end
  end
  return {}
end

-- ------------------------------------------------------------------
-- Header: state machine for Sumário and References
-- ------------------------------------------------------------------

-- Padroes do Lua trabalham em BYTES, nao em caracteres: `[áa]` vira a classe
-- dos bytes 0xC3/0xA1/'a', entao `sum[áa]rio` exige UM byte entre "sum" e
-- "rio" e nunca casa com "sumário" (dois bytes). Busca literal (plain=true)
-- em cada grafia e o jeito seguro — sem esta correcao o Sumario continuava
-- lista de bullets e as Referencias nunca recebiam recuo pendente.
local function matches_any(haystack, needles)
  for _, n in ipairs(needles) do
    if haystack:find(n, 1, true) then return true end
  end
  return false
end

local SUMARIO_TITLES = {'sumário', 'sumario', 'summary', 'índice', 'indice'}
local REFS_TITLES = {'referências', 'referencias', 'references', 'bibliography'}

function Header(el)
  if el.level == 2 then
    after_sumario = false
    in_references = false
    local title = pandoc.text.lower(stringify(el))
    if matches_any(title, SUMARIO_TITLES) then
      after_sumario = true
      -- O kicker \sbkicker{Sumário} ja nomeia a secao (mesmo comportamento do
      -- HTML, onde `h2#sumário` fica display:none). Manter o titulo aqui
      -- imprimiria "SUMÁRIO" e "Sumário" em duas linhas seguidas.
      return {}
    elseif matches_any(title, REFS_TITLES) then
      in_references = true
      -- O kicker \sbkicker{Referências} já nomeia a seção em dourado.
      -- Suprime o título duplicado.
      return {}
    end
  end
  return nil
end

-- ------------------------------------------------------------------
-- Link: underline inline hyperlinks in PDF body
-- ------------------------------------------------------------------

function Link(el)
  if el.target:match('^#') or in_references then
    return el
  end
  local new_content = { pandoc.RawInline('latex', '\\uline{') }
  for _, c in ipairs(el.content) do
    table.insert(new_content, c)
  end
  table.insert(new_content, pandoc.RawInline('latex', '}'))
  el.content = new_content
  return el
end

-- ------------------------------------------------------------------
-- BulletList: convert Sumário to sbtoc environment
-- ------------------------------------------------------------------

function BulletList(el)
  if after_sumario then
    after_sumario = false
    -- O essay numera os proprios capitulos? Se sim, a goteira usa o numeral
    -- do autor; se nao, um romano sequencial (mesma convencao do kicker).
    local any_numbered = false
    for _, item in ipairs(el.content) do
      if extract_toc_number(stringify(item)) then
        any_numbered = true
      end
    end

    local blocks = { pandoc.RawBlock('latex', '\\begin{sbtoc}') }
    for i, item in ipairs(el.content) do
      local inlines = item_inlines(item)
      local num, plen = extract_toc_number(stringify(item))
      local gutter
      if num then
        gutter = num
        inlines = drop_prefix(inlines, plen)
      elseif not any_numbered then
        -- Arabico, igual ao contador sequencial do kicker (ver
        -- inject_chapter_kickers): as subsecoes sao "3.1" e um "III" na
        -- goteira poria dois sistemas de numeracao no mesmo documento.
        gutter = tostring(i)
      else
        gutter = ''
      end
      local cmd = (i == #el.content) and '\\sbtocopenlast' or '\\sbtocopen'
      -- Abre o comando, despeja os inlines ORIGINAIS (math/enfase intactos)
      -- e fecha. Nada de stringify aqui.
      table.insert(blocks, pandoc.RawBlock('latex', cmd .. '{' .. lescape(gutter) .. '}{%'))
      table.insert(blocks, pandoc.Plain(inlines))
      table.insert(blocks, pandoc.RawBlock('latex', '}%'))
    end
    table.insert(blocks, pandoc.RawBlock('latex', '\\end{sbtoc}'))
    return blocks
  end
  return nil
end

-- ------------------------------------------------------------------
-- Div: internal markers + external environments
-- ------------------------------------------------------------------

function Div(el)
  if has_class(el, 'box-badge') then
    return { pandoc.RawBlock('latex',
      '\\wbbadge{' .. lescape(stringify(el)) .. '}%') }
  end
  if has_class(el, 'box-title') then
    return { pandoc.RawBlock('latex',
      '\\wbtitle{' .. lescape(stringify(el)) .. '}%') }
  end
  if has_class(el, 'card-name') then
    return { pandoc.RawBlock('latex',
      '\\cardname{' .. lescape(stringify(el)) .. '}%') }
  end
  if has_class(el, 'card-meta') then
    return { pandoc.RawBlock('latex',
      '\\cardmeta{' .. lescape(stringify(el)) .. '}%') }
  end

  if has_class(el, 'box-verdict') then
    local out = { pandoc.RawBlock('latex',
      '\\vspace{4pt}\\par\\hrule height 0.4pt\\vspace{5pt}\\begingroup\\small%') }
    for _, b in ipairs(el.content) do table.insert(out, b) end
    table.insert(out, pandoc.RawBlock('latex', '\\endgroup%'))
    return out
  end

  if has_class(el, 'pq-cite') then
    return {
      pandoc.RawBlock('latex',
        '\\par\\vspace{2pt}\\noindent{\\upshape\\footnotesize\\color{subtlegray}' .. lescape(stringify(el)) .. '}%')
    }
  end

  if has_class(el, 'label-solo') then
    return { pandoc.RawBlock('latex',
      '\\parahead{' .. lescape(stringify(el)) .. '}') }
  end

  if has_class(el, 'box') then
    local color = get_box_color(el)
    local out = { pandoc.RawBlock('latex',
      '\\begin{wikibox}{' .. color .. '}%') }
    for _, b in ipairs(el.content) do table.insert(out, b) end
    table.insert(out, pandoc.RawBlock('latex', '\\end{wikibox}%'))
    return out
  end
  if has_class(el, 'quote') then
    local out = { pandoc.RawBlock('latex', '\\begin{wikiquote}%') }
    for _, b in ipairs(el.content) do table.insert(out, b) end
    table.insert(out, pandoc.RawBlock('latex', '\\end{wikiquote}%'))
    return out
  end
  if has_class(el, 'pull-quote') then
    local out = { pandoc.RawBlock('latex', '\\begin{wikipull}%') }
    for _, b in ipairs(el.content) do table.insert(out, b) end
    table.insert(out, pandoc.RawBlock('latex', '\\end{wikipull}%'))
    return out
  end
  if has_class(el, 'card') then
    local out = { pandoc.RawBlock('latex', '\\begin{wikicard}%') }
    for _, b in ipairs(el.content) do table.insert(out, b) end
    table.insert(out, pandoc.RawBlock('latex', '\\end{wikicard}%'))
    return out
  end

  return nil
end

-- ------------------------------------------------------------------
-- Para: figure centering, references wrapping, styled captions
-- ------------------------------------------------------------------

function Para(el)
  -- 1) Paragraph contains an Image (standalone or with inline caption text)
  local has_image = false
  for _, inl in ipairs(el.content) do
    if inl.t == 'Image' then
      has_image = true
      break
    end
  end

  if has_image then
    local images = {}
    local rest = {}
    for _, inl in ipairs(el.content) do
      if inl.t == 'Image' then
        table.insert(images, inl)
      else
        table.insert(rest, inl)
      end
    end
    local blocks = {
      pandoc.RawBlock('latex', '\\begin{center}%'),
      pandoc.Para(images),
    }
    if #rest > 0 then
      local rest_text = stringify(pandoc.Para(rest)):gsub('^%s+', ''):gsub('%s+$', '')
      if rest_text ~= '' then
        table.insert(blocks, pandoc.RawBlock('latex', '\\vspace{-4pt}\\begingroup\\small%'))
        table.insert(blocks, pandoc.Para(rest))
        table.insert(blocks, pandoc.RawBlock('latex', '\\endgroup%'))
      end
    end
    table.insert(blocks, pandoc.RawBlock('latex', '\\end{center}%'))
    return blocks
  end

  -- 2) References handling
  if in_references then
    -- O "Link" no fim de cada referencia e um pandoc.Link (t == 'Link'),
    -- nao um Str. A palavra fica (decisao do autor) e ganha UMA seta
    -- discreta ao lado. Os demais links da citacao (o titulo da obra, um
    -- termo no comentario) nao recebem seta nenhuma — antes cada um
    -- ganhava a sua e a referencia terminava com duas ou tres.
    local new_content = {}
    for _, inl in ipairs(el.content) do
      if inl.t == 'Link' and stringify(inl) == 'Link' then
        inl.content = {
          pandoc.Str('Link'),
          pandoc.RawInline('latex', '\\,\\textup{\\scriptsize↗}'),
        }
      end
      table.insert(new_content, inl)
    end
    return {
      pandoc.RawBlock('latex', '\\begin{sbrefitem}%'),
      pandoc.Plain(new_content),
      pandoc.RawBlock('latex', '\\end{sbrefitem}%'),
    }
  end

  -- 3) Standalone figure caption paragraph (e.g. "*Figura 1 — ...*")
  local text = stringify(el)
  if text:match('^Fig%.%s*%d') or text:match('^Figura%s+%d') then
    local out = {}
    local found_fig = false
    for _, inl in ipairs(el.content) do
      if inl.t == 'Str' and not found_fig then
        local fig_num = inl.text:match('^(Fig%.?%s*%d+)')
        if fig_num then
          table.insert(out, pandoc.RawInline('latex',
            '{\\color{sbink}\\textbf{' .. fig_num .. '}}'))
          local rest_str = inl.text:sub(#fig_num + 1)
          if rest_str ~= '' then
            table.insert(out, pandoc.Str(rest_str))
          end
          found_fig = true
        else
          table.insert(out, inl)
        end
      else
        table.insert(out, inl)
      end
    end
    return {
      pandoc.RawBlock('latex', '\\begin{center}\\vspace{-6pt}\\small%'),
      pandoc.Para(out),
      pandoc.RawBlock('latex', '\\end{center}%'),
    }
  end

  return nil
end

-- ------------------------------------------------------------------
-- RawBlock: ornament glyphs from HTML
-- ------------------------------------------------------------------

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


