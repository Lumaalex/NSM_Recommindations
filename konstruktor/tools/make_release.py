# -*- coding: utf-8 -*-
"""
ПАПКА РАЗДАЧИ release/ — копии готовых клиентов с понятными именами
===================================================================
Запуск:   python tools/make_release.py          (или автоматически в конце tools/build.py)

Зачем. Рабочее имя файла ничего не говорит о том, какой это форк и какой версии:
    fork_v2/Конструктор_ИВ_версия2.html    -> V2 «от общего к частному» (последняя версия)
Из-за этого заказчик скачивал не тот файл (в просмотрщике скачивается тот файл,
который сейчас открыт, а имена в списке загрузок выглядят похоже).

Клиенты других версий (V1 «большая версия», Google-версия) из репозитория удалены —
в раздаче только последняя версия конструктора.

Что делает скрипт: берёт УЖЕ СОБРАННЫЕ html-файлы, определяет версию прямо из их
содержимого (V2VER) и кладёт в release/ байт-в-байт копии с именами вида
    Конструктор_ИВ_V2_от_общего_к_частному_<версия>.html
плюс release/КАКОЙ_ФАЙЛ_СКАЧАТЬ.md с таблицей «что это, кому давать».

Важно: release/ — только раздача. Канонический файл — fork_v2/Конструктор_ИВ_версия2.html;
правка release/*.html вручную бессмысленна (перезатрётся при следующей сборке).
Старые копии с прежними номерами версий удаляются, чтобы в папке не лежало два
похожих файла разной свежести.
"""
import hashlib
import io
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REL = os.path.join(ROOT, 'release')

# исходник -> (префикс имени копии, регулярка версии, описание)
SOURCES = [
    (os.path.join(ROOT, 'fork_v2', 'Конструктор_ИВ_версия2.html'),
     'Конструктор_ИВ_V2_от_общего_к_частному', r"V2VER\s*=\s*'([0-9.]+)'",
     'V2 «от общего к частному» (последняя версия): актуальное состояние -> фразы -> цели -> приёмы -> '
     'результаты -> цели на след. период -> рекомендации -> документ; шкала 5…1 и S0; '
     'шаг 9 — банк фраз с правками'),
]

MANAGED_PREFIXES = tuple(s[1] for s in SOURCES)
README_NAME = 'КАКОЙ_ФАЙЛ_СКАЧАТЬ.md'


def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def version_of(path, pattern):
    with io.open(path, encoding='utf-8') as f:
        head = f.read(400000)
    m = re.search(pattern, head)
    return m.group(1) if m else '0.0.0'


def clean_stale(keep):
    """Удаляем ранее созданные скриптом копии, которых нет в текущем наборе."""
    if not os.path.isdir(REL):
        return []
    removed = []
    for name in sorted(os.listdir(REL)):
        if not name.endswith('.html'):
            continue
        if name in keep:
            continue
        if name.startswith(MANAGED_PREFIXES):
            os.remove(os.path.join(REL, name))
            removed.append(name)
    return removed


FORK_LABELS = {
    'Конструктор_ИВ_V2_от_общего_к_частному': 'V2 «от общего к частному»',
}


def fork_label(dst, ver):
    """Метка форка по имени копии: отрезаем «_<версия>.html» и смотрим в FORK_LABELS."""
    base = os.path.basename(dst)
    suffix = '_%s.html' % ver
    pre = base[: -len(suffix)] if base.endswith(suffix) else base
    return FORK_LABELS.get(pre, pre)


def make_readme(items):
    # версии в тексте не зашиваем — берём из имён собранных копий, чтобы readme не устаревал
    vers = ' либо '.join('«%s · версия %s»' % (fork_label(dst, ver), ver)
                         for dst, src, ver, desc in items)
    lines = [
        '# Какой файл скачать',
        '',
        'Это папка **раздачи**: здесь лежит точная копия готового конструктора с понятным',
        'именем (в имени — форк и версия). Канонический файл, который собирает',
        '`python tools/build.py`, лежит в `fork_v2/`.',
        '',
        '| Файл в этой папке | Что это | Версия | Откуда скопирован |',
        '|---|---|---|---|',
    ]
    for dst, src, ver, desc in items:
        lines.append('| `%s` | %s | %s | `%s` |'
                     % (os.path.basename(dst), desc, ver, os.path.relpath(src, ROOT)))
    lines += [
        '',
        '## Как не перепутать',
        '',
        '1. В просмотрщике/браузере скачивается **тот файл, который сейчас открыт**.',
        '   Сначала откройте нужный, потом нажимайте «Скачать».',
        '2. Открыли файл — посмотрите на шапку: там написаны форк и версия',
        '   (%s),' % vers,
        '   а также в заголовок вкладки браузера.',
        '3. Файлы проектов (.json) между разными версиями конструктора не переносятся.',
        '',
        'Папка перезаписывается скриптом `python tools/make_release.py` (вызывается и в конце',
        '`python tools/build.py`). Копии проверяются по md5 — содержимое совпадает с исходниками.',
        '',
    ]
    return '\n'.join(lines)


def main():
    os.makedirs(REL, exist_ok=True)
    items, keep = [], set()
    for src, prefix, pattern, desc in SOURCES:
        if not os.path.exists(src):
            print('! пропуск: нет %s (сначала python tools/build.py)' % os.path.relpath(src, ROOT))
            continue
        ver = version_of(src, pattern)
        dst = os.path.join(REL, '%s_%s.html' % (prefix, ver))
        shutil.copyfile(src, dst)
        same = md5(src) == md5(dst)
        if not same:
            raise SystemExit('! копия не совпала с исходником: %s' % dst)
        items.append((dst, src, ver, desc))
        keep.add(os.path.basename(dst))
        print('  -> %-58s %7.1f КБ  v%-6s md5=%s'
              % (os.path.relpath(dst, ROOT), os.path.getsize(dst) / 1024, ver, md5(dst)[:8]))
    for name in clean_stale(keep):
        print('  -  удалена устаревшая копия %s' % name)
    with io.open(os.path.join(REL, README_NAME), 'w', encoding='utf-8') as f:
        f.write(make_readme(items))
    print('Папка раздачи: %s (файлов: %d + %s)'
          % (os.path.relpath(REL, ROOT), len(items), README_NAME))
    return [d for d, _, _, _ in items]


if __name__ == '__main__':
    main()
