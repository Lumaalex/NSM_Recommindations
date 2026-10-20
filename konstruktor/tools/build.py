# -*- coding: utf-8 -*-
"""
СБОРКА КОМПЛЕКТА «КОНСТРУКТОР РЕКОМЕНДАЦИЙ» (V2 «от общего к частному»)
=======================================================================
Запуск:   python tools/build.py
Источник: tools/source_data.py

Создаёт:
  data/phrases.json                              — банк данных, вшитый в конструктор
  fork_v2/Конструктор_ИВ_версия2.html            — канонический файл V2 (из app/template_v2.html)
  release/                                       — папка раздачи (копии с понятными именами)

Файлы других версий (V1 «большая версия», Google-версия, Excel-мастер-база, docx-шаблоны)
из сборки исключены: репозиторий хранит только последнюю версию конструктора — V2.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import source_data as SD

OUT_JSON   = os.path.join(ROOT, 'data', 'phrases.json')
OUT_V2     = os.path.join(ROOT, 'fork_v2', 'Конструктор_ИВ_версия2.html')


# --------------------------------------------------------------------------- 1. JSON
def build_json(data):
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return OUT_JSON


# --------------------------------------------------------------------------- 2. HTML (V2)
def build_html_v2(data):
    tpl_path = os.path.join(ROOT, 'app', 'template_v2.html')
    with open(tpl_path, encoding='utf-8') as f:
        tpl = f.read()
    with open(os.path.join(ROOT, 'app', 'style.css'), encoding='utf-8') as f:
        css = f.read()
    with open(os.path.join(ROOT, 'app', 'docx_lib.js'), encoding='utf-8') as f:
        docxlib = f.read()
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    tpl = tpl.replace('/*__CSS__*/', css.strip()).replace('/*__DOCX_LIB__*/', docxlib.strip())
    tpl = tpl.replace('/*__DATA__*/', payload)
    with open(OUT_V2, 'w', encoding='utf-8') as f:
        f.write(tpl)
    return OUT_V2


# --------------------------------------------------------------------------- MAIN
def main():
    data = SD.build()
    errs = SD.validate(data)
    if errs:
        print('! Замечания целостности данных (%d):' % len(errs))
        for e in errs:
            print('   -', e)
        raise SystemExit(1)
    out = [build_json(data), build_html_v2(data)]
    print('Собрано:')
    for p in out:
        print('  %-42s %8.1f КБ' % (os.path.relpath(p, ROOT), os.path.getsize(p) / 1024))
    print('Фраз в банке: %d | пунктов опросника: %d | наблюдательных вопросов ИВ2: %d'
          % (len(data['phrases']), len(data['questionnaire']), len(data['iv2_questions'])))
    print('Папка раздачи release/ (копии с понятными именами):')
    import make_release  # noqa
    make_release.main()


if __name__ == '__main__':
    main()
