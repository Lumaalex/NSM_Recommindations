# -*- coding: utf-8 -*-
"""
ПЕРЕСБОРКА ТОЛЬКО V1-КЛИЕНТОВ (без пересборки данных)
=====================================================
Запуск:   python tools/build_v1_only.py

В отличие от tools/build.py НЕ трогает data/phrases.json, Банк_фраз.xlsx, docx-шаблоны
и fork_v2/Конструктор_ИВ_версия2.html — пересобирает из уже собранных данных
(data/phrases.json) только:
    Конструктор_рекомендаций.html
    google/Index.html

Зачем: правки интерфейса V1 (app/template.html, app/style.css, app/docx_lib.js,
app/google_adapter.js) можно проверять и выкатывать, пока заказчик тестирует форк v2 —
его файл и мастер-база остаются байт в байт прежними.
"""
import io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.chdir(ROOT)

import build          # noqa: E402  (используем его build_html — сборка V1 из шаблона)
import build_google   # noqa: E402

JSON = os.path.join(ROOT, 'data', 'phrases.json')
if not os.path.exists(JSON):
    raise SystemExit('Нет data/phrases.json — сначала выполните python tools/build.py')

with io.open(JSON, encoding='utf-8') as f:
    data = json.load(f)

print('Данные: version=%s от %s, фраз=%d (БЕЗ пересборки из source_data.py / Excel)'
      % (data['meta']['version'], data['meta']['updated'], len(data['phrases'])))
out = [build.build_html(data)]
build_google.main()
for p in out:
    print('  -> %s  (%.1f КБ)' % (os.path.relpath(p, ROOT), os.path.getsize(p) / 1024))
print('Папка раздачи release/ (копии с понятными именами):')
import make_release      # noqa: E402
make_release.main()
print('Готово. fork_v2/*, data/phrases.json, Банк_фраз.xlsx и docx-шаблоны не изменялись.')
