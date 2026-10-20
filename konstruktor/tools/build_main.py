# -*- coding: utf-8 -*-
"""
СБОРКА ОСНОВНОЙ ВЕРСИИ КОНСТРУКТОРА (мейн)
==========================================
Запуск:   python tools/build_main.py

Номер версии в имени выходного файла НЕ зашит — он берётся из константы
V2VER в app/app_main.js. При повышении версии достаточно поменять V2VER и
пересобрать: файл создастся с актуальным именем, старая сборка удалится.

Исходники:
  app/template_main.html   — каркас страницы с плейсхолдерами /*__CSS__*/, /*__APP__*/, /*__DATA__*/
  app/style_main.css       — оформление
  app/app_main.js          — логика клиента (V2VER = версия приложения)
  data/phrases_main.json   — банк данных основной версии

Создаёт:
  main/Конструктор_ИВ_основная_<версия>.html — канонический файл мейна (главный рабочий инструмент)

Банк фраз основной версии живёт в data/phrases_main.json (мастер-копия). Его правят
напрямую либо выгружают из конструктора (шаг «Банк фраз» → «Экспорт JSON») и кладут сюда;
затем выполняется эта сборка. Сборка детерминирована: на вход те же исходники — на выход
байт-в-байт тот же HTML.

Не путать с tools/build.py — он собирает старый форк V2 2.6.0 (source_data.py ->
data/phrases.json -> release/). Мейном является основная версия, собираемая этим скриптом.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TPL   = os.path.join(ROOT, 'app', 'template_main.html')
CSS   = os.path.join(ROOT, 'app', 'style_main.css')
APP   = os.path.join(ROOT, 'app', 'app_main.js')
DATA  = os.path.join(ROOT, 'data', 'phrases_main.json')


def app_version():
    """Версия приложения берётся из V2VER в app/app_main.js — не дублируется в имени файла."""
    with open(APP, encoding='utf-8') as f:
        m = re.search(r"V2VER\s*=\s*'([0-9.]+)'", f.read())
    if not m:
        raise SystemExit('! в app/app_main.js не найдена константа V2VER')
    return m.group(1)


VERSION = app_version()
OUT = os.path.join(ROOT, 'main', 'Конструктор_ИВ_основная_%s.html' % VERSION)


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
    # сборка другой версии больше не нужна в main/ — убираем, чтобы не было двух «канонических» файлов
    main_dir = os.path.dirname(OUT)
    for name in sorted(os.listdir(main_dir)):
        if (name.startswith('Конструктор_ИВ_основная_') and name.endswith('.html')
                and os.path.join(main_dir, name) != OUT):
            os.remove(os.path.join(main_dir, name))
            print('  -  убрана устаревшая сборка %s' % name)
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
