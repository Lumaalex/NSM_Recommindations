# -*- coding: utf-8 -*-
"""Сквозная проверка HTML-конструктора в реальном браузере (Playwright, headless Chromium).
Запуск: python tools/test_browser.py
Проверяет: открытие файла, отсутствие ошибок консоли, загрузку проекта, переключение вкладок,
сборку документа и скачивание .docx."""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHOTS = os.path.abspath(os.path.join(HERE, '..', '..', 'work', 'shots'))
os.makedirs(SHOTS, exist_ok=True)

from playwright.sync_api import sync_playwright

HTML = 'file://' + os.path.join(ROOT, 'Конструктор_рекомендаций.html')
PROJ = os.path.join(ROOT, 'Пример_проекта.json')

errors, logs = [], []

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={'width': 1400, 'height': 1000},
                                accept_downloads=True)
        page.on('console', lambda m: (logs.append(m.type + ': ' + m.text),
                                      errors.append(m.text) if m.type == 'error' else None))
        page.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))

        page.goto(HTML)
        page.wait_for_timeout(600)
        assert page.locator('#nojs').count() == 0, 'заглушка «без JavaScript» не удалена при работающем JS'
        print('заголовок:', page.title())
        assert page.locator('a[href*="версия2"]').count() == 0, 'в v1 остались ссылки на версию 2'
        print('вкладок:', page.locator('nav.tabs button').count())
        page.screenshot(path=os.path.join(SHOTS, '01_header.png'), full_page=False)

        # --- загрузка примера проекта через реальный input[type=file]
        page.set_input_files('#fileProject', PROJ)
        page.wait_for_timeout(700)
        fio = page.input_value('[data-h="fio"]') if page.locator('[data-h="fio"]').count() else ''
        print('загружен проект, ФИО =', fio)
        assert 'Иванов' in fio, 'проект не загрузился'

        # --- шапка в два ряда: чипы ФИО / период / специалист (перенос из v2, запись 44)
        assert page.locator('header.top .hdrrow').count() == 1, 'первый ряд шапки не собран'
        assert page.locator('header.top .hdrchips').count() == 1, 'строка чипов шапки отсутствует'
        assert page.locator('.hdrchips #saveinfo').count() == 1, \
            'индикатор автосохранения не перенесён в строку чипов'
        chip_fio = page.inner_text('#hdrFio').strip()
        chip_period = page.inner_text('#hdrPeriod').strip()
        chip_spec = page.inner_text('#hdrSpec').strip()
        print('чипы шапки:', chip_fio, '|', chip_period, '|', chip_spec)
        assert 'Иванов' in chip_fio, 'в чипе нет ФИО загруженного проекта: ' + chip_fio
        assert chip_period.startswith('период:') and '—' in chip_period, 'чип периода: ' + chip_period
        assert chip_spec.startswith('специалист:'), 'чип специалиста: ' + chip_spec
        ver = page.inner_text('#ver').strip()
        print('версия в шапке:', ver)
        assert ver.startswith('1.2.0') and 'банк данных' in ver, 'версия приложения не показана: ' + ver
        # чипы обновляются на каждый ввод
        page.fill('[data-h="fio"]', 'Чипова Анна Петровна')
        page.wait_for_timeout(250)
        assert 'Чипова' in page.inner_text('#hdrFio'), 'чип ФИО не обновляется при вводе'
        page.fill('[data-h="fio"]', fio)
        page.wait_for_timeout(250)
        assert 'Иванов' in page.inner_text('#hdrFio'), 'чип ФИО не вернулся к значению проекта'
        page.screenshot(path=os.path.join(SHOTS, '01b_header_chips.png'), full_page=False)

        # --- проходим по вкладкам
        tabs = ['2. Опросник', '3. Актуальное состояние', '4. Цели и приёмы',
                '5. Результаты', '6. Рекомендации', '7. Документ', 'Банк фраз', 'Инструкция']
        shots = {'2. Опросник': '02_survey', '3. Актуальное состояние': '03_as',
                 '4. Цели и приёмы': '04_goals', '6. Рекомендации': '05_recs',
                 '7. Документ': '06_doc', 'Банк фраз': '07_bank'}
        for t in tabs:
            page.click(f'nav.tabs button:has-text("{t}")')
            page.wait_for_timeout(350)
            n = page.locator('#main .card').count()
            h = page.evaluate("document.getElementById('main').scrollHeight")
            print('вкладка «%s»: карточек %d, высота контента %dpx' % (t, n, h))
            if t in shots:
                page.screenshot(path=os.path.join(SHOTS, shots[t] + '.png'), full_page=False)

        # --- чек-лист на вкладке «Документ»
        page.click('nav.tabs button:has-text("7. Документ")')
        page.wait_for_timeout(400)
        checks = page.locator('.check').count()
        failed = page.locator('.check.fail').count()
        print('чек-лист: пунктов %d, провальных %d' % (checks, failed))
        assert checks >= 12
        # предпросмотр документа
        doc_len = page.evaluate("document.getElementById('docprint').innerText.length")
        print('символов в предпросмотре документа:', doc_len)
        assert doc_len > 5000
        page.screenshot(path=os.path.join(SHOTS, '06_doc_full.png'), full_page=True)

        # --- подписи кнопок шапки на десктопе
        save_lbl = page.inner_text('#btnSaveProject').strip()
        load_lbl = page.inner_text('#btnLoadProject').strip()
        reset_lbl = page.inner_text('#btnReset').strip()
        print('подписи шапки:', save_lbl, '|', load_lbl, '|', reset_lbl)
        assert save_lbl == 'Сохранить проект', 'подпись кнопки сохранения: ' + save_lbl
        assert load_lbl == 'Загрузить проект', 'подпись кнопки загрузки: ' + load_lbl
        assert reset_lbl == 'Новый документ', 'подпись кнопки нового документа: ' + reset_lbl

        # --- опросник: переключение ответа и появление подсказок ключа
        page.click('nav.tabs button:has-text("2. Опросник")')
        page.wait_for_timeout(400)
        boxes = page.locator('.qitem').count()
        print('пунктов опросника в DOM:', boxes)
        assert boxes > 40
        page.locator('.qitem').first.locator('label', has_text='2 · иногда').click()
        page.wait_for_timeout(500)
        sugg = page.locator('.qitem').first.locator('.sugg').count()
        print('подсказок ключа у первого пункта после ответа «иногда»:', sugg)
        assert sugg >= 1
        page.screenshot(path=os.path.join(SHOTS, '02b_survey_key.png'), full_page=False)

        # --- тумблер «+ в документ» / «✓ убрать»
        page.locator('.qitem').nth(0).locator('.scale label', has_text='2 · иногда').click()
        page.wait_for_timeout(500)
        item0 = page.locator('.qitem').nth(0)
        tog = item0.locator('.sugg button', has_text='+ в документ').first
        tog.click(); page.wait_for_timeout(400)
        tog2 = item0.locator('.sugg button', has_text='убрать').first
        assert tog2.count() == 1, 'после добавления кнопка не превратилась в «убрать»'
        print('тумблер: после «+ в документ» кнопка показывает «убрать»')
        tog2.click(); page.wait_for_timeout(400)
        assert item0.locator('.sugg button', has_text='+ в документ').count() >= 1, \
            'после «убрать» кнопка не вернулась в состояние «+ в документ»'
        print('тумблер: после «убрать» фраза удалена, кнопка снова «+ в документ»')

        # --- банк фраз: фильтр и счётчик строк
        page.click('nav.tabs button:has-text("Банк фраз")')
        page.wait_for_timeout(400)
        rows_all = page.locator('#bankTable tr').count() - 1
        page.fill('#fText', 'сюжет')
        page.wait_for_timeout(300)
        rows_f = page.locator('#bankTable tr').count() - 1
        print('банк фраз: всего строк %d, по фильтру «сюжет» %d' % (rows_all, rows_f))
        assert rows_all > 150 and 0 < rows_f < rows_all
        page.screenshot(path=os.path.join(SHOTS, '07b_bank_filter.png'), full_page=False)
        page.fill('#fText', '')
        page.wait_for_timeout(300)
        rows_all = page.locator('#bankTable tr').count() - 1

        # --- V1 не показывает формулировки микротем версии 2 (AS7prax, AS8vis)
        note = page.inner_text('#bankNote').strip()
        print('пометка банка:', note[:120])
        assert 'версия2' in note or 'версии 2' in note, 'нет пометки о формулировках версии 2: ' + note
        own = json.load(open(os.path.join(ROOT, 'data', 'phrases.json'), encoding='utf-8'))
        v2micro = {m['id'] for m in own['microblocks'] if m.get('v2only')}
        expect_own = len([p for p in own['phrases']
                          if not (p['block'] == 'AS' and p.get('micro') in v2micro)])
        shown = page.input_value('#bankCountSimple')
        print('счётчик банка (простой режим):', shown, '| ожидается «%d из %d»' % (expect_own, expect_own))
        assert shown == '%d из %d' % (expect_own, expect_own), 'счётчик банка: ' + shown
        assert rows_all == expect_own, 'в таблице банка V1 строк %d, ожидается %d' % (rows_all, expect_own)
        assert 'AS7prax' not in page.inner_text('#bankTable'), 'в таблице банка V1 виден код AS7prax'

        # --- продвинутый режим: названия блоков/микроблоков вместе с кодами (перенос из v2, запись 45)
        page.click('#btnMode')
        page.wait_for_timeout(500)
        blk_opts = page.locator('#fBlock option').all_inner_texts()
        mic_opts = page.locator('#fMicro option').all_inner_texts()
        print('фильтр «Блок»:', ' | '.join(blk_opts[:3]), '…')
        assert any('Актуальное состояние · AS' == o.strip() for o in blk_opts), \
            'в фильтре «Блок» нет связки «название · код»: ' + str(blk_opts[:3])
        assert any('AS5play' in o for o in mic_opts), 'в фильтре «Микроблок» нет кода AS5play'
        assert not any('AS7prax' in o or 'AS8vis' in o for o in mic_opts), \
            'в фильтре «Микроблок» остались микротемы версии 2'
        assert page.inner_text('#bankCount').strip() == str(expect_own), \
            'счётчик «всего фраз» в продвинутом режиме: ' + page.inner_text('#bankCount')
        page.screenshot(path=os.path.join(SHOTS, '07c_bank_full_mode.png'), full_page=False)
        page.click('#btnMode')   # обратно в простой режим
        page.wait_for_timeout(400)


        # --- модалка подбора фраз: счётчик «Найдено» и легенда кодов (перенос из v2, запись 45)
        page.click('nav.tabs button:has-text("3. Актуальное состояние")')
        page.wait_for_timeout(400)
        page.locator('[data-pick^="MICRO:"]').first.click()
        page.wait_for_timeout(400)
        pick = page.inner_text('#pickerBody')
        print('модалка подбора, первые строки:', pick.split('\n')[0][:90])
        assert pick.strip().startswith('Найдено:'), 'в модалке нет счётчика «Найдено»'
        assert 'AS5play-S2-07' in pick, 'в модалке нет легенды кодов'
        page.screenshot(path=os.path.join(SHOTS, '03b_picker_legend.png'), full_page=False)
        page.keyboard.press('Escape')
        page.wait_for_timeout(250)
        assert page.locator('#pickerOv').count() == 0, 'модалка не закрылась по Escape'

        # --- скачивание .docx
        page.click('nav.tabs button:has-text("7. Документ")')
        page.wait_for_timeout(300)
        with page.expect_download() as dl:
            page.click('#btnDocx')
        d = dl.value
        target = os.path.join(SHOTS, d.suggested_filename)
        d.save_as(target)
        print('скачан файл:', d.suggested_filename, os.path.getsize(target), 'байт')
        assert os.path.getsize(target) > 10000

        # --- автосохранение черновика
        saved = page.evaluate("window.localStorage.getItem('iv_constructor_doc_v1') !== null")
        print('черновик в localStorage:', saved)
        assert saved

        # --- режим без JavaScript (как Quick Look на iPhone): должна быть видна инструкция
        ctx_nojs = browser.new_context(java_script_enabled=False)
        pg2 = ctx_nojs.new_page()
        pg2.goto(HTML)
        pg2.wait_for_timeout(400)
        assert pg2.locator('#nojs').count() == 1, 'без JS заглушка не показана'
        assert pg2.locator('#nojs').is_visible(), 'заглушка не видна'
        txt = pg2.inner_text('#nojs')
        assert 'Как открыть на телефоне' in txt, 'в заглушке нет инструкции для телефона'
        print('режим без JS: заглушка с инструкцией видна (%d символов)' % len(txt))
        pg2.screenshot(path=os.path.join(SHOTS, '08_nojs_banner.png'))
        ctx_nojs.close()

        browser.close()

    print('\nОшибок консоли:', len(errors))
    for e in errors[:10]:
        print('  !', e)
    if errors:
        print('❌ ЕСТЬ ОШИБКИ В КОНСОЛИ')
        return 1
    print('✅ БРАУЗЕРНАЯ ПРОВЕРКА ПРОЙДЕНА')
    print('Скриншоты:', SHOTS)
    return 0


if __name__ == '__main__':
    sys.exit(main())
