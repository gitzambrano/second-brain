
path = 'data/wiki/sources/manifest.md'
entries = []
cur = None
for line in open(path, encoding='utf-8').read().splitlines():
    s = line.strip()
    if s.startswith('## ['):
        cur = [s, None]
        entries.append(cur)
    elif s.startswith('Verificação:') and cur is not None:
        cur[1] = s

last_unchecked = [e for e in entries if e[1] and 'não verificado' in e[1]]
no_verif = [e for e in entries if not e[1] or not e[1].startswith('Verificação:')]
print('entradas_total', len(entries))
print('ultimo_Verificacao_não_verificado', len(last_unchecked))
print('sem_linha_Verificacao', len(no_verif))