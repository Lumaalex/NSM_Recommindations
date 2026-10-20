# -*- coding: utf-8 -*-
"""Пакет 2.6.0: правки tools/test_v2_browser.py (шаг 9 «Банк фраз» + чип специалиста).
Запуск: python3 work/patch_v260_tests.py"""
import io
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'konstruktor'))
P = os.path.join(ROOT, 'tools', 'test_v2_browser.py')

REPL = []


def rep(old, new, label):
    REPL.append((old, new, label))


rep("""import os
import sys

from playwright.sync_api import sync_playwright""",
    """import json
import os
import sys

from playwright.sync_api import sync_playwright""",
    'импорт json')

rep("""    page.on('dialog', lambda d: d.accept())""",
    """    # 2.6.0: в prompt отвечаем заготовленным текстом (нужно для «+ Новая фраза» на шаге 9)
    dlg_text = ['']
    dlg_log = []

    def on_dialog(d):
        dlg_log.append((d.type, d.message))
        try:
            d.accept(dlg_text[0] if d.type == 'prompt' else '')
        except Exception:
            pass

    page.on('dialog', on_dialog)

    def clk(loc):
        loc.tap() if touch else loc.click()""",
    'обработчик диалогов + помощник clk()')

rep("""    check(page.locator('.steps button').count() == 8, 'шагов в степпере: 8')""",
    """    check(page.locator('.steps button').count() == 9, 'шагов в степпере: 9 (9-й — «Банк фраз»)')""",
    'шагов в степпере: 9')

rep("""    page.fill('[data-h="specialist"]', 'Петрова А.И.')
    page.fill('[data-h="sessions"]', '10')""",
    """    page.fill('[data-h="specialist"]', 'Петрова А.И.')
    page.fill('[data-h="sessions"]', '10')
    page.wait_for_timeout(250)
    chip_spec = (page.text_content('#hdrSpec') or '').strip()
    check(chip_spec == 'специалист: Петрова А.И. · занятий: 10',
          '2.6.0: чип специалиста в шапке обновляется на ввод: ' + chip_spec)""",
    'чип специалиста в шапке')

rep("""    check(page.locator('[data-bank="AS|"]').count() >= 1, 'крупная кнопка банка дублирована на шаге 1')""",
    """    # 2.6.0: карточка-дубль «Банк фраз: смотреть и добавлять» с шага 1 убрана
    # (кнопка «Банк фраз» в шапке теперь ведёт на шаг 9), кнопки в карточках сфер остались
    check(page.locator('button[data-bank="AS|"]').count() == 0,
          'на шаге 1 нет карточки-дубля банка')
    check(page.locator('button:has-text("Банк фраз: смотреть и добавлять")').count() == 0,
          'текста карточки-дубля на шаге 1 нет')
    check(page.locator('[data-bank^="AS|SPH-"]').count() == 9,
          'кнопки «+ из банка фраз» остались в карточках всех 9 сфер')""",
    'шаг 1: карточка-дубль убрана')

STEP9 = '''    # --- 2.6.0: шаг 9 «Банк фраз» — полный банк с правками внутри конструктора ---
    clk(page.locator('#btnBank'))
    page.wait_for_timeout(450)
    on_step = (page.locator('.steps button.on').text_content() or '').strip()
    check(on_step.startswith('9.'), 'кнопка «Банк фраз» в шапке открывает шаг 9: ' + on_step)
    rows9 = page.locator('#bank9Table tr').count() - 1
    check(rows9 == 201, 'в таблице банка строк: %d (весь общий банк)' % rows9)
    check(page.locator('#bank9Add').is_visible() and page.locator('#bank9Reset').is_visible()
          and page.locator('#bank9ExportCsv').is_visible() and page.locator('#bank9Import').is_visible(),
          'на шаге 9 есть кнопки: новая фраза, экспорт, импорт, возврат встроенного банка')
    check((page.text_content('#hdrSpec') or '').strip() == 'специалист: Петрова А.И. · занятий: 10',
          'чип специалиста виден и на шаге 9')
    check('Справочники банка' in (page.text_content('#main') or ''), 'на шаге 9 есть справочники банка')
    check(overflow(page) <= 1, 'оверфлоу страницы на шаге 9: %d' % overflow(page))
    if prefix == 'v2desk':
        page.screenshot(path=os.path.join(SHOTS, 'v260_bank9.png'))
    else:
        page.screenshot(path=os.path.join(SHOTS, 'v260_mob_bank9.png'))

    # фильтры: блок, микроблок, статус, поиск
    page.select_option('#f9Block', 'AS')
    page.wait_for_timeout(300)
    n_as = page.locator('#bank9Table tr').count() - 1
    blocks9 = page.eval_on_selector_all('#bank9Table select[data-b9f="block"]', 'es => es.map(e => e.value)')
    check(0 < n_as < 201 and set(blocks9) == {'AS'}, 'фильтр по блоку: %d строк, все блока AS' % n_as)
    page.select_option('#f9Block', '')
    page.wait_for_timeout(250)
    page.select_option('#f9Micro', 'AS5play')
    page.wait_for_timeout(300)
    micros9 = page.eval_on_selector_all('#bank9Table select[data-b9f="micro"]', 'es => es.map(e => e.value)')
    check(len(micros9) > 0 and set(micros9) == {'AS5play'}, 'фильтр по микроблоку: %d строк' % len(micros9))
    page.select_option('#f9Micro', '')
    page.wait_for_timeout(250)
    page.select_option('#f9Status', 'S3')
    page.wait_for_timeout(300)
    stats9 = page.eval_on_selector_all('#bank9Table select[data-b9f="status"]', 'es => es.map(e => e.value)')
    check(len(stats9) > 0 and all('S3' in v for v in stats9), 'фильтр по статусу: %d строк' % len(stats9))
    page.select_option('#f9Status', '')
    page.wait_for_timeout(250)
    page.fill('#f9Text', 'сюжет')
    page.wait_for_timeout(350)
    n_q = page.locator('#bank9Table tr').count() - 1
    check(0 < n_q < 60, 'поиск по тексту сужает список: %d строк' % n_q)
    if prefix == 'v2desk':
        page.screenshot(path=os.path.join(SHOTS, 'v260_bank9_filters.png'))
    page.fill('#f9Text', '')
    page.wait_for_timeout(300)
    check(page.locator('#bank9Table tr').count() - 1 == 201, 'пустой поиск возвращает все строки')
    clk(page.locator('#bank9ClearFilters'))
    page.wait_for_timeout(350)
    check(page.input_value('#f9Block') == '' and page.input_value('#f9Text') == '',
          '«Сбросить фильтры» очищает фильтры шага 9')

    # своя фраза: «+ Новая фраза» → правка в строке
    dlg_text[0] = 'AS5play-S2-BROWSER'
    clk(page.locator('#bank9Add'))
    page.wait_for_timeout(450)
    dlg_text[0] = ''
    check(page.locator('textarea[data-b9id="AS5play-S2-BROWSER"]').count() == 1,
          '«+ Новая фраза» добавила строку в таблицу')
    check(page.evaluate("window.V2API.BANK.phraseIndex['AS5play-S2-BROWSER'].micro") == 'AS5play'
          and page.evaluate("window.V2API.BANK.phraseIndex['AS5play-S2-BROWSER'].block") == 'AS',
          'блок и микротема новой фразы определены по коду (AS5play-S2-BROWSER)')
    page.fill('textarea[data-b9id="AS5play-S2-BROWSER"]', 'Своя формулировка из браузерного теста')
    page.wait_for_timeout(300)
    check(page.evaluate("window.V2API.BANK.phraseIndex['AS5play-S2-BROWSER'].text")
          == 'Своя формулировка из браузерного теста', 'текст фразы правится прямо в строке')
    page.fill('input[data-b9f="tags"][data-b9id="AS5play-S2-BROWSER"]', 'тест; своя тема')
    page.wait_for_timeout(250)
    check(page.evaluate("window.V2API.BANK.phraseIndex['AS5play-S2-BROWSER'].tags") == 'тест; своя тема',
          'теги правятся в строке')
    page.select_option('select[data-b9f="status"][data-b9id="AS5play-S2-BROWSER"]', 'S1')
    page.wait_for_timeout(350)
    check(page.evaluate("window.V2API.BANK.phraseIndex['AS5play-S1-BROWSER'] || "
                        "window.V2API.BANK.phraseIndex['AS5play-S2-BROWSER']") is not None
          and page.evaluate("(window.V2API.BANK.phraseIndex['AS5play-S2-BROWSER']||{}).status") == 'S1',
          'статус меняется селектом в строке')
    page.eval_on_selector('input[data-b9f="id"][data-b9id="AS5play-S2-BROWSER"]',
                          "e => { e.value = 'AS5play-S1-BROWSER'; e.dispatchEvent(new Event('change')); }")
    page.wait_for_timeout(400)
    check(page.locator('textarea[data-b9id="AS5play-S1-BROWSER"]').count() == 1,
          'ID фразы переименован прямо в строке')
    check(page.evaluate("(window.V2API.BANK.phraseIndex['AS5play-S1-BROWSER']||{}).text")
          == 'Своя формулировка из браузерного теста', 'после переименования текст фразы сохранён')

    # правки банка переживают перезагрузку страницы
    page.reload()
    page.wait_for_timeout(800)
    check(page.evaluate("!!(window.V2API.BANK.phraseIndex['AS5play-S1-BROWSER']||{}).text"),
          'правки банка переживают перезагрузку страницы')
    check(page.evaluate("localStorage.getItem('iv_constructor_bank_v2') !== null"),
          'правки банка лежат в localStorage[iv_constructor_bank_v2] (свой ключ, не общий с V1)')
    check(page.evaluate("localStorage.getItem('iv_constructor_bank_v1') === null"),
          'ключ банка V1 при этом не создаётся — форки не пересекаются')
    check(page.locator('#bank9Table tr').count() - 1 == 202,
          'после перезагрузки в банке строк: %d' % (page.locator('#bank9Table tr').count() - 1))

    # «В документ» — кладёт фразу в её блок, не уходя с шага
    row_own = page.locator('tr:has(input[data-b9id="AS5play-S1-BROWSER"])')
    clk(row_own.locator('[data-tg]').first)
    page.wait_for_timeout(400)
    check(page.evaluate("window.V2API.S.as.some(x => x.src === 'AS5play-S1-BROWSER')"),
          '«В документ»: фраза блока AS добавлена в актуальное состояние')
    check((page.locator('.steps button.on').text_content() or '').strip().startswith('9.'),
          'после добавления фразы остаёмся на шаге 9')
    check('убрать' in (page.locator('tr:has(input[data-b9id="AS5play-S1-BROWSER"]) [data-tg]').first
                       .text_content() or ''), 'кнопка «В документ» стала «✓ убрать»')
    # своя фраза сразу доступна в подборе фраз на шагах
    clk(page.locator('.steps button:has-text("1. Актуальное состояние")'))
    page.wait_for_timeout(400)
    idx_play = page.evaluate("() => window.V2API.BANK.spheres.findIndex("
                             "s => window.V2API.sphereAsPool(s.id).some(p => p.micro === 'AS5play'))")
    check(idx_play >= 0, 'найдена сфера, в пуле которой есть микротема «Игра» (индекс %d)' % idx_play)
    clk(page.locator('.sph').nth(idx_play).locator('[data-bank^="AS|"]').first)
    page.wait_for_timeout(400)
    page.fill('#pkQ', 'Своя формулировка из браузерного теста')
    page.wait_for_timeout(350)
    check(page.locator('#pkBody .prow').count() == 1,
          'своя фраза из шага 9 находится в окне подбора на шаге 1')
    page.keyboard.press('Escape')
    page.wait_for_timeout(300)

    # экспорт CSV и JSON
    clk(page.locator('.steps button:has-text("9. Банк фраз")'))
    page.wait_for_timeout(400)
    with page.expect_download() as dl_csv:
        clk(page.locator('#bank9ExportCsv'))
    dcsv = dl_csv.value
    p_csv = os.path.join('/tmp', prefix + '_' + dcsv.suggested_filename)
    dcsv.save_as(p_csv)
    csv_txt = io.open(p_csv, encoding='utf-8-sig').read()
    check(dcsv.suggested_filename.endswith('.csv'), 'экспорт CSV: ' + dcsv.suggested_filename)
    check(csv_txt.splitlines()[0].startswith('ID;Направление;Блок;Микроблок'), 'заголовок CSV на месте')
    check('AS5play-S1-BROWSER' in csv_txt and 'Своя формулировка из браузерного теста' in csv_txt,
          'своя фраза попала в выгрузку CSV')
    check(len(csv_txt.splitlines()) == 203, 'строк в CSV (с заголовком): %d' % len(csv_txt.splitlines()))
    with page.expect_download() as dl_js:
        clk(page.locator('#bank9ExportJson'))
    djs = dl_js.value
    p_js = os.path.join('/tmp', prefix + '_' + djs.suggested_filename)
    djs.save_as(p_js)
    bj = json.load(io.open(p_js, encoding='utf-8'))
    check(len(bj['phrases']) == 202 and 'phraseIndex' not in bj,
          'экспорт JSON: %d фраз, служебные индексы не выгружаются' % len(bj['phrases']))
    check(bj['meta']['version'] == '1.2.0', 'в выгрузке банка сохранена версия данных')

    # импорт CSV: новая строка + перенос старой нумерации кодов
    imp_csv = os.path.join('/tmp', prefix + '_import.csv')
    with io.open(imp_csv, 'w', encoding='utf-8') as f:
        f.write('ID;Направление;Блок;Микроблок;Способность;Статус;Текст;Источник;Требует примера;'
                'Подсказка примера;Цели(ID);Приёмы(ID);Рекомендации(ID);Теги;Активна\\n')
        f.write('AS5play-S1-IMP;IV;AS;AS5play;;S1;Импортированная формулировка из CSV;тест;Да;;;;импорт;Да\\n')
        f.write('AS1-S3-02;IV;AS;AS1;;S3;Старая нумерация кода из файла;тест;Да;;;;импорт;Да\\n')
    page.set_input_files('#fileBank', imp_csv)
    page.wait_for_timeout(700)
    check(page.evaluate("!!window.V2API.BANK.phraseIndex['AS5play-S1-IMP']"),
          'импорт CSV: новая строка добавлена в банк')
    check(page.evaluate("(window.V2API.BANK.phraseIndex['AS1sens-S3-02']||{}).text")
          == 'Старая нумерация кода из файла',
          'импорт CSV: старый код AS1-S3-02 перенесён картой code_migration на AS1sens-S3-02')
    check(page.locator('#bank9Table tr').count() - 1 == 203,
          'после импорта CSV в таблице строк: %d' % (page.locator('#bank9Table tr').count() - 1))

    # импорт JSON: банк заменяется целиком
    imp_json = os.path.join('/tmp', prefix + '_import.json')
    with io.open(imp_json, 'w', encoding='utf-8') as f:
        json.dump({'meta': {'version': '1.2.0'}, 'phrases': [
            {'id': 'AS5play-S1-J1', 'dir': 'IV', 'block': 'AS', 'micro': 'AS5play', 'status': 'S1',
             'text': 'Фраза из импортированного JSON', 'source': 'тест', 'needs_example': True,
             'example_hint': '', 'links_goal': [], 'links_meth': [], 'links_rec': [], 'tags': '',
             'active': True}]}, f, ensure_ascii=False)
    page.set_input_files('#fileBank', imp_json)
    page.wait_for_timeout(700)
    check(page.evaluate("window.V2API.BANK.phrases.length") == 1
          and page.evaluate("!!window.V2API.BANK.phraseIndex['AS5play-S1-J1']"),
          'импорт JSON: банк заменён файлом (1 фраза)')
    check(page.evaluate("(window.V2API.BANK.ped_scale||[]).length") > 0,
          'разделы, которых нет в файле, взяты из встроенного банка (шкала на месте)')
    if prefix == 'v2desk':
        page.screenshot(path=os.path.join(SHOTS, 'v260_bank9_import.png'))

    # возврат встроенного банка
    clk(page.locator('#bank9Reset'))
    page.wait_for_timeout(600)
    check(page.evaluate("window.V2API.BANK.phrases.length") == 201,
          '«Вернуть встроенный банк»: снова 201 фраза')
    check(page.evaluate("!window.V2API.BANK.phraseIndex['AS5play-S1-BROWSER']")
          and page.evaluate("!window.V2API.BANK.phraseIndex['AS5play-S1-IMP']"),
          'свои и импортированные фразы удалены')
    check(page.evaluate("localStorage.getItem('iv_constructor_bank_v2') === null"),
          'хранилище правок банка очищено')
    check(page.locator('#bank9Table tr').count() - 1 == 201,
          'таблица перестроена после сброса: %d строк' % (page.locator('#bank9Table tr').count() - 1))
    check(any(t == 'confirm' for t, m in dlg_log), 'сброс банка спрашивает подтверждение')

'''

rep("""    # цвета кодов оценок различаются по баллам""",
    STEP9 + """    # цвета кодов оценок различаются по баллам""",
    'сценарии шага 9 в браузере')

rep("""    check(page.input_value('[data-h="fio"]') == '', 'кнопка «Новый документ» очищает черновик')""",
    """    check(page.input_value('[data-h="fio"]') == '', 'кнопка «Новый документ» очищает черновик')
    check((page.text_content('#hdrSpec') or '').strip() == 'специалист не указан',
          '2.6.0: после «Нового документа» чип специалиста пустой: '
          + (page.text_content('#hdrSpec') or '').strip())""",
    'чип специалиста после «Нового документа»')

# io нужен для чтения выгрузок
rep("""import json
import os
import sys""",
    """import io
import json
import os
import sys""",
    'импорт io')


def main():
    with io.open(P, encoding='utf-8') as f:
        src = f.read()
    out = src
    for old, new, label in REPL:
        n = out.count(old)
        if n != 1:
            raise SystemExit('! %s: найдено вхождений %d (ожидалось 1)' % (label, n))
        out = out.replace(old, new)
        print('  + %s' % label)
    with io.open(P, 'w', encoding='utf-8') as f:
        f.write(out)
    print('Записано: %s (%d → %d байт)' % (os.path.relpath(P, ROOT), len(src), len(out)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
