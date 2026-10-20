# -*- coding: utf-8 -*-
"""
ПЕРЕСБОРКА ТОЛЬКО ФОРКА V2 (без пересборки данных)
==================================================
Запуск:   python tools/build_v2_only.py

В отличие от tools/build.py НЕ трогает data/phrases.json, Банк_фраз.xlsx, docx-шаблоны,
Конструктор_рекомендаций.html и google/Index.html — пересобирает из уже собранных данных
(data/phrases.json) только:
    fork_v2/Конструктор_ИВ_версия2.html
и обновляет папку раздачи release/.

Зачем: правки интерфейса форка v2 (app/template_v2.html) можно проверять и выкатывать,
пока мастер-база и V1-клиенты должны оставаться байт в байт прежними
(зеркало tools/build_v1_only.py).
"""
import io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.chdir(ROOT)

import build          # noqa: E402  (используем его build_html_v2 — сборка форка v2 из шаблона)

JSON = os.path.join(ROOT, 'data', 'phrases.json')
if not os.path.exists(JSON):
    raise SystemExit('Нет data/phrases.json — сначала выполните python tools/build.py')

with io.open(JSON, encoding='utf-8') as f:
    data = json.load(f)

print('Данные: version=%s от %s, фраз=%d (БЕЗ пересборки из source_data.py / Excel)'
      % (data['meta']['version'], data['meta']['updated'], len(data['phrases'])))
out = build.build_html_v2(data)
print('  -> %s  (%.1f КБ)' % (os.path.relpath(out, ROOT), os.path.getsize(out) / 1024))
print('Папка раздачи release/ (копии с понятными именами):')
import make_release      # noqa: E402
make_release.main()
print('Готово. data/phrases.json, Банк_фраз.xlsx, docx-шаблоны, V1 и google/ не изменялись.')
