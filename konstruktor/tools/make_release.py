# -*- coding: utf-8 -*-
"""
ПАПКА РАЗДАЧИ release/ — копии готовых клиентов с понятными именами
===================================================================
Запуск:   python tools/make_release.py          (или автоматически в конце tools/build.py)

Зачем. Рабочие имена файлов ничего не говорят о том, какой это форк и какой версии:
    Конструктор_рекомендаций.html          -> V1 «большая версия»
    fork_v2/Конструктор_ИВ_версия2.html    -> V2 «от общего к частному»
    google/Index.html                      -> Google-версия (V1 + адаптер)
Из-за этого заказчик скачивал не тот файл (в просмотрщике скачивается тот файл,
который сейчас открыт, а имена в списке загрузок выглядят похоже).

Что делает скрипт: берёт УЖЕ СОБРАННЫЕ html-файлы, определяет версию прямо из их
содержимого (V1VER / V2VER) и кладёт в release/ байт-в-байт копии с именами вида
    Конструктор_ИВ_V1_большая_версия_<версия>.html
    Конструктор_ИВ_V2_от_общего_к_частному_<версия>.html
    Конструктор_ИВ_Google_версия_<версия>.html
плюс release/КАКОЙ_ФАЙЛ_СКАЧАТЬ.md с таблицей «что это, кому давать».

Важно: release/ — только раздача. Канонические файлы — в корне репозитория;
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
    (os.path.join(ROOT, 'Конструктор_рекомендаций.html'),
     'Конструктор_ИВ_V1_большая_версия', r"V1VER\s*=\s*'([0-9.]+)'",
     'V1 «большая версия»: опросник (9 сфер + сенсорный блок FEDL2i), банк фраз, '
     'оценка 3/2/1/0/N, печать и выгрузка .docx'),
    (os.path.join(ROOT, 'fork_v2', 'Конструктор_ИВ_версия2.html'),
     'Конструктор_ИВ_V2_от_общего_к_частному', r"V2VER\s*=\s*'([0-9.]+)'",
     'V2 «от общего к частному»: актуальное состояние -> фразы -> цели -> приёмы -> '
     'результаты -> цели на след. период -> рекомендации -> документ; шкала 5…1 и S0; '
     'шаг 9 — банк фраз с правками'),
    (os.path.join(ROOT, 'google', 'Index.html'),
     'Конструктор_ИВ_Google_версия', r"V1VER\s*=\s*'([0-9.]+)'",
     'Google-версия: тот же V1 для вставки на Google Sites (нужен app/google_adapter.js '
     'и серверная часть Code.gs)'),
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
    'Конструктор_ИВ_V1_большая_версия': 'V1 «большая версия»',
    'Конструктор_ИВ_V2_от_общего_к_частному': 'V2 «от общего к частному»',
    'Конструктор_ИВ_Google_версия': 'Google-версия (V1 + адаптер)',
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
        'Это папка **раздачи**: здесь лежат точные копии готовых конструкторов с понятными',
        'именами (в имени — форк и версия). Канонические файлы, которые собирает',
        '`python tools/build.py`, лежат в корне репозитория и в `fork_v2/`, `google/`.',
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
        '3. Оба форка самостоятельны: у каждого свой черновик в браузере, файлы проектов',
        '   (.json) между ними не переносятся.',
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
