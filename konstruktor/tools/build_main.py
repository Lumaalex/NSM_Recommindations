# -*- coding: utf-8 -*-
"""
СБОРКА ОСНОВНОЙ ВЕРСИИ КОНСТРУКТОРА (мейн, v3.2.0)
===================================================
Запуск:   python tools/build_main.py

Исходники:
  app/template_main.html   — каркас страницы с плейсхолдерами /*__CSS__*/, /*__APP__*/, /*__DATA__*/
  app/style_main.css       — оформление
  app/app_main.js          — логика клиента (V2VER = 3.2.0)
  data/phrases_main.json   — банк данных версии 3.2.0

Создаёт:
  main/Конструктор_ИВ_основная_3.2.0.html — канонический файл мейна (главный рабочий инструмент)

Банк фраз основной версии живёт в data/phrases_main.json (мастер-копия). Его правят
напрямую либо выгружают из конструктора (шаг «Банк фраз» → «Экспорт JSON») и кладут сюда;
затем выполняется эта сборка. Сборка детерминирована: на вход те же исходники — на выход
байт-в-байт тот же HTML.

Не путать с tools/build.py — он собирает старый форк V2 2.6.0 (source_data.py ->
data/phrases.json -> release/). Мейном является версия 3.2.0, собираемая этим скриптом.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TPL   = os.path.join(ROOT, 'app', 'template_main.html')
CSS   = os.path.join(ROOT, 'app', 'style_main.css')
APP   = os.path.join(ROOT, 'app', 'app_main.js')
DATA  = os.path.join(ROOT, 'data', 'phrases_main.json')
OUT   = os.path.join(ROOT, 'main', 'Конструктор_ИВ_основная_3.2.0.html')


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def build():
    tpl = read(TPL)
    for ph in ('/*__CSS__*/', '/*__APP__*/', '/*__DATA__*/'):
        if ph not in tpl:
            raise SystemExit('! в шаблоне не найден плейсхолдер %s' % ph)
    data = json.loads(read(DATA))
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    html = (tpl
            .replace('<style>\n/*__CSS__*/\n</style>', '<style>\n' + read(CSS).strip() + '\n</style>')
            .replace('<script>\n/*__APP__*/\n</script>', '<script>\n' + read(APP).strip() + '\n</script>')
            .replace('/*__DATA__*/', payload))
    # целостность: данные в собранном файле читаются обратно без потерь
    import re
    m = re.search(r'<script id="bank-data" type="application/json">(.*?)</script>', html, re.S)
    if not m or json.loads(m.group(1)) != data:
        raise SystemExit('! встроенный банк не совпадает с data/phrases_main.json')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    ver = re.search(r"V2VER\s*=\s*'([0-9.]+)'", html)
    print('Собрано: %-46s %8.1f КБ  v%s' % (os.path.relpath(OUT, ROOT),
                                            len(html.encode('utf-8')) / 1024,
                                            ver.group(1) if ver else '?'))
    print('Фраз в банке: %d | сфер: %d | пунктов опросника: %d | наблюдательных вопросов ИВ2: %d'
          % (len(data['phrases']), len(data.get('spheres', [])),
             len(data.get('questionnaire', [])), len(data.get('iv2_questions', []))))
    return OUT


if __name__ == '__main__':
    build()
