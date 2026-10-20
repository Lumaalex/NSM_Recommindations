# -*- coding: utf-8 -*-
"""Чинит проблемный rep(...) в patch_v130_template.py (строка оканчивалась на '+\"\"\" —
литерал ломался). Пересобираем вызов из одинарных литералов с \\n-эскейпами."""
import io, ast
D3 = '"' * 3
p = 'patch_v130_template.py'
lines = io.open(p, encoding='utf-8').read().split('\n')
start = None
for i, ln in enumerate(lines):
    if ln.startswith('rep(' + D3 + '  /* счётчик и легенда кодов'):
        start = i
        break
assert start is not None, 'rep-блок не найден'
end = start + 1
while not lines[end].startswith('rep('):
    end += 1
block = lines[start:end]
print('блок строк %d..%d:' % (start + 1, end))
for ln in block:
    print('   |', ln[:110])
assert block[0] == 'rep(' + D3 + '  /* счётчик и легенда кодов — перенос из v2 (запись 45) */'
assert block[3] == D3 + '  /* счётчик и легенда кодов — перенос из v2 (запись 45) */'
assert block[5].endswith('+""")'.replace('"""', D3) + ')') or block[5].endswith(D3 + ')')

HEAD1 = "  /* счётчик и легенда кодов — перенос из v2 (запись 45) */\n"
HEAD2 = "  let html='<div class=\"small muted\" style=\"margin-bottom:6px\">Найдено: '+list.length+\n"
OLD = HEAD1 + HEAD2 + "    '. Кнопка «+ добавить» кладёт фразу в «'+esc(targetName(to))+'».<br>'+" + '"'
NEW = HEAD1 + HEAD2 + "    (PICKER.pool? ' (пул фраз сферы)':'')+'. Кнопка «+ добавить» кладёт фразу в «'+esc(targetName(to))+'».<br>'+" + '"'

def lit(t):
    return "'" + t.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n') + "'"

lines[start:end] = ['rep(' + lit(OLD) + ',\n    ' + lit(NEW) + ')']
io.open(p, 'w', encoding='utf-8').write('\n'.join(lines))
ast.parse(io.open(p, encoding='utf-8').read())
print('пересобрано, синтаксис ОК')
