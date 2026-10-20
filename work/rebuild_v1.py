# -*- coding: utf-8 -*-
"""Пересборка ТОЛЬКО V1-клиентов из существующих данных (data/phrases.json не меняется):
   Конструктор_рекомендаций.html  и  google/Index.html.
   Запуск:  python3 work/rebuild_v1.py   (из /home/user)
"""
import io, json, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'konstruktor')
ROOT = os.path.abspath(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
os.chdir(ROOT)

import build            # noqa: E402  (используем его build_html — шаблон V1)
import build_google     # noqa: E402

with io.open(os.path.join('data', 'phrases.json'), encoding='utf-8') as f:
    data = json.load(f)

print('Данные: version=%s, фраз=%d (БЕЗ пересборки из source_data.py)' % (data['meta']['version'], len(data['phrases'])))
print('  ->', os.path.basename(build.build_html(data)))
build_google.main()
