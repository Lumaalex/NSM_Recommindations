# -*- coding: utf-8 -*-
"""Проверка папки раздачи release/ (копии клиентов с понятными именами).
Запуск: python tools/test_release.py
Проверяет: копии байт-в-байт равны исходникам, версия в имени файла = версии внутри файла,
устаревших копий нет, readme перечисляет все файлы, в V1-копии нет ссылок на форк v2."""
import hashlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import make_release as MR  # noqa: E402

fails = []


def check(cond, msg):
    print(('  OK   ' if cond else '  FAIL ') + msg)
    if not cond:
        fails.append(msg)


def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    check(os.path.isdir(MR.REL), 'папка release/ существует')
    if not os.path.isdir(MR.REL):
        return 1
    have = sorted(n for n in os.listdir(MR.REL) if n.endswith('.html'))
    expect = []
    for src, prefix, pattern, _ in MR.SOURCES:
        if not os.path.exists(src):
            check(False, 'нет исходника %s — выполните python tools/build.py'
                  % os.path.relpath(src, ROOT))
            continue
        ver = MR.version_of(src, pattern)
        name = '%s_%s.html' % (prefix, ver)
        expect.append((name, src, ver, prefix, pattern))
    check(len(have) == len(expect), 'в release/ %d html-копий (ожидалось %d)' % (len(have), len(expect)))

    for name, src, ver, prefix, pattern in expect:
        dst = os.path.join(MR.REL, name)
        if not os.path.exists(dst):
            check(False, 'нет копии %s' % name)
            continue
        check(md5(dst) == md5(src), 'копия %s байт-в-байт равна исходнику' % name)
        check(MR.version_of(dst, pattern) == ver,
              'версия внутри копии %s = %s' % (name, ver))
        check(name.endswith(ver + '.html'), 'версия %s указана в имени файла' % ver)

    stale = [n for n in have if n.startswith(MR.MANAGED_PREFIXES)
             and n not in [e[0] for e in expect]]
    check(not stale, 'устаревших копий нет' + (': %s' % stale if stale else ''))

    rd = os.path.join(MR.REL, MR.README_NAME)
    check(os.path.exists(rd), 'есть %s' % MR.README_NAME)
    if os.path.exists(rd):
        txt = io.open(rd, encoding='utf-8').read()
        for name, src, ver, _, _ in expect:
            check(name in txt, 'readme упоминает %s' % name)
            check(os.path.relpath(src, ROOT) in txt, 'readme указывает исходник %s'
                  % os.path.relpath(src, ROOT))

    v1 = [n for n, s, v, p, pt in expect if p.startswith('Конструктор_ИВ_V1')]
    if v1:
        body = io.open(os.path.join(MR.REL, v1[0]), encoding='utf-8').read()
        check('версия2.html' not in body and 'fork_v2' not in body,
              'в копии V1 нет ссылок на форк v2 (форки независимы)')
        check('V2VER' not in body, 'в копии V1 нет кода форка v2')

    print()
    if fails:
        print('❌ ПРОВЕРЕНО С ЗАМЕЧАНИЯМИ: %d' % len(fails))
        for f in fails:
            print('   -', f)
        return 1
    print('✅ ПАПКА РАЗДАЧИ В ПОРЯДКЕ')
    return 0


if __name__ == '__main__':
    sys.exit(main())
