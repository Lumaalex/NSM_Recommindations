# -*- coding: utf-8 -*-
"""
СБОРКА GOOGLE-ВЕРСИИ
====================
Запуск:  python tools/build_google.py
Результат: google/Index.html — тот же интерфейс, но:
  * банк фраз подставляется сервером из Google Таблицы (скрипт <?!= bankJson ?>);
  * встроен адаптер app/google_adapter.js: черновики и .docx уходят на Диск,
    создаётся Google Doc, правки банка уходят на модерацию.
Вне Apps Script полученный файл работает как обычный офлайн-конструктор.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.join(ROOT, 'app', 'template.html')
ADAPTER = os.path.join(ROOT, 'app', 'google_adapter.js')
OUT = os.path.join(ROOT, 'google', 'Index.html')
MARKER = '/* ---------------------------------------------------------------- СТАРТ */'


def main():
    with open(TEMPLATE, encoding='utf-8') as f:
        tpl = f.read()
    with open(ADAPTER, encoding='utf-8') as f:
        adapter = f.read()
    with open(os.path.join(ROOT, 'app', 'style.css'), encoding='utf-8') as f:
        css = f.read()
    with open(os.path.join(ROOT, 'app', 'docx_lib.js'), encoding='utf-8') as f:
        docxlib = f.read()
    for marker in ('/*__DATA__*/', '/*__CSS__*/', '/*__DOCX_LIB__*/'):
        if marker not in tpl:
            raise SystemExit('В шаблоне нет маркера ' + marker)
    tpl = tpl.replace('/*__CSS__*/', css.strip()).replace('/*__DOCX_LIB__*/', docxlib.strip())
    if MARKER not in tpl:
        raise SystemExit('В шаблоне нет маркера СТАРТ для вставки адаптера')

    tpl = tpl.replace('/*__DATA__*/', '<?!= bankJson ?>')
    tpl = tpl.replace(MARKER, adapter + '\n' + MARKER, 1)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(tpl)
    print('Собрано: %s (%.1f КБ)' % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024))
    print('Дальше: google/УСТАНОВКА.md — вставить Code.gs и Index.html в Apps Script вашей таблицы.')


if __name__ == '__main__':
    main()
