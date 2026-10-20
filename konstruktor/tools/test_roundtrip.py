# -*- coding: utf-8 -*-
"""Честный круговой тест: правка в Банк_фраз.xlsx действительно доезжает до JSON и HTML.
Запуск: python tools/test_roundtrip.py"""
import json, os, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import excel_to_json  # noqa

fails = 0


def ok(cond, msg):
    global fails
    print(('  OK   ' if cond else '  FAIL ') + msg)
    if not cond:
        fails += 1


def main():
    src = os.path.join(ROOT, 'Банк_фраз.xlsx')
    tmp = tempfile.mkdtemp()
    copy = os.path.join(tmp, 'bank.xlsx')
    shutil.copy(src, copy)

    import openpyxl
    wb = openpyxl.load_workbook(copy)
    ws = wb['Фразы']
    # 1) меняем текст существующей фразы
    ws['G2'] = 'ПРОВЕРКА_ПРАВКИ: демонстрирует интерес к игрушкам.'
    # 2) добавляем новую строку в СТАРОМ формате кодов — должна автоматически
    #    перенестись на семантические коды (AS5-S2-99 -> AS5play-S2-99, AS5 -> AS5play)
    row = ['AS5-S2-99', 'IV', 'AS', 'AS5', 'AB-PLAY', 'S2',
           'ПРОВЕРКА_НОВАЯ: тестовая формулировка кругового цикла.', 'тест', 'Да', '',
           'GL-09', 'MT-13', 'RC-16', 'тест', 'Да']
    ws.append(row)
    # 3) правим ключ опросника — тоже старыми кодами
    wq = wb['Опросник_ключ']
    wq['H2'] = 'as: AS1-S3-03 | res: RS-20'
    wb.save(copy)

    data = excel_to_json.load(copy)
    p = data['phraseIndex'] if 'phraseIndex' in data else {x['id']: x for x in data['phrases']}
    ok(p['AS1sens-S3-01']['text'].startswith('ПРОВЕРКА_ПРАВКИ'),
       'правка текста доехала: ' + p['AS1sens-S3-01']['text'][:40])
    ok('AS5play-S2-99' in p and p['AS5play-S2-99']['links_goal'] == ['GL-09']
       and p['AS5play-S2-99']['micro'] == 'AS5play',
       'новая строка импортирована со связями и старым кодом, переведённым на семантический')
    ok(data['questionnaire'][0]['key']['3']['as'] == ['AS1sens-S3-03'],
       'правка ключа опросника доехала (старый код AS1-S3-03 переведён)')
    import source_data as SD
    base = len(SD.build()['phrases'])
    ok(len(data['phrases']) == base + 1,
       'всего фраз после правки: %d (ожидалось %d + 1 новая)' % (len(data['phrases']), base))
    # --- новые колонки листа «Сферы» и «Микроблоки» должны переживать круг Excel -> JSON
    sph = {x['id']: x for x in data['spheres']}
    ok(len(data['spheres']) == 9, 'сфер прочитано из Excel: %d' % len(data['spheres']))
    ok(sph['SPH-SENS'].get('sens_blocks') == ['A'],
       'привязка блока FEDL2i к сфере доехала: %s' % sph['SPH-SENS'].get('sens_blocks'))
    ok(sph['SPH-MOT'].get('sens_blocks') == ['B', 'F'] and sph['SPH-VIS'].get('sens_blocks') == ['E'],
       'сферы 8–9 привязаны к блокам B/F и E')
    ok(sph['SPH-COM'].get('sens_blocks') == ['C', 'D'], 'сфера «Коммуникация» привязана к блокам C и D')
    ok('AS4ini-S3-04' in (sph['SPH-INI'].get('bank_as') or [])
       and 'AS4ini-S3-04' not in (sph['SPH-KON'].get('bank_as') or []),
       'пул фраз сферы (bank_as) доехал из Excel')
    mb = {x['id']: x for x in data['microblocks']}
    ok(mb['AS7prax'].get('v2only') is True and mb['AS1sens'].get('v2only') is not True,
       'флаг «Только v2» у микротем AS7prax/AS8vis доехал из Excel')
    ok(len(data['literature']) == 24, 'литература прочитана: %d поз.' % len(data['literature']))
    ok(len(data['service_phrases']) >= 10, 'служебные фразы прочитаны: %d' % len(data['service_phrases']))
    ok(len(data['checklist']) >= 10, 'чек-лист прочитан: %d' % len(data['checklist']))
    ok(len(data['link_map']) >= 10, 'карта связей прочитана: %d' % len(data['link_map']))
    ok(len(data['support_types']) == 4, 'типы поддержки прочитаны: %d' % len(data['support_types']))

    shutil.rmtree(tmp, ignore_errors=True)
    print('\n' + ('✅ КРУГОВОЙ ТЕСТ ПРОЙДЕН' if fails == 0 else '❌ ПРОВАЛОВ: %d' % fails))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
