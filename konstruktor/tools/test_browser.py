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
        # метка форка и версия в заголовке вкладки: скачанный файл должен опознаваться без открытия
        _ver = (page.text_content('#ver') or '').split(' · ')[0].strip()
        assert page.title().endswith('v' + _ver), \
            'в заголовке вкладки нет версии V1 (%r, версия %r)' % (page.title(), _ver)
        _sub = page.locator('header.top .sub').first.text_content() or ''
        assert 'V1 «большая версия»' in _sub, 'в шапке нет метки форка V1'
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
        assert ver.startswith('1.3.0') and 'банк данных' in ver, 'версия приложения не показана: ' + ver
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

        # --- опросник 1.3.0: подвкладки «Оценка: 9 сфер / Подробно: DIR / Сенсорный профиль / Вопросы ИВ»
        page.click('nav.tabs button:has-text("2. Опросник")')
        page.wait_for_timeout(400)
        sv_tabs = page.locator('button.svtab').all_inner_texts()
        print('подвкладки опросника:', ' | '.join(t.strip() for t in sv_tabs))
        assert len(sv_tabs) == 4, 'подвкладок опросника: %d' % len(sv_tabs)
        assert any('9 сфер' in t for t in sv_tabs), 'нет подвкладки «Оценка: 9 сфер»'
        assert any('FEDL2i' in t for t in sv_tabs), 'нет подвкладки сенсорного профиля'
        assert any('Вопросы ИВ' in t for t in sv_tabs), 'нет подвкладки вопросов ИВ'
        boxes = page.locator('.qitem').count()
        print('сфер в оценке:', boxes)
        assert boxes == 9, 'вопросов в подвкладке «Оценка: 9 сфер»: %d' % boxes

        # --- варианты ответов согласованы с формулировкой сферы (обратная связь 1.2.0)
        sens_labels = page.locator('.qitem').nth(0).locator('.scale label').all_inner_texts()
        print('варианты ответа сферы 1 (сенсорная):', ' / '.join(x.strip() for x in sens_labels))
        assert any('возрастная норма' in x for x in sens_labels), 'у сенсорной сферы нет варианта «возрастная норма»'
        assert not any(x.strip().endswith('не проявляется') for x in sens_labels), \
            'у сферы «Сенсорная переработка» остался несогласованный вариант «не проявляется»'
        assert 'Сенсорная переработка' in page.locator('.mb.sph .hd .t').first.inner_text(), \
            'сфера 1 — не «Сенсорная переработка информации»'

        # --- оценка сферы: цвет выбранной кнопки + цветные блоки подсказок
        page.locator('.mb.sph').nth(1).locator('.scale label', has_text='2 · справляется, но не всегда').click()
        page.wait_for_timeout(500)
        sph2 = page.locator('.mb.sph').nth(1)
        on_lbl = sph2.locator('.scale label.on')
        assert on_lbl.count() == 1, 'выбранный вариант ответа не подсветился'
        assert 'st-S2' in (on_lbl.get_attribute('class') or ''), \
            'выбранная оценка не окрашена в цвет статуса: ' + str(on_lbl.get_attribute('class'))
        sugg = sph2.locator('.sugg')
        print('подсказок у сферы 2 после оценки «2»:', sugg.count())
        assert sugg.count() >= 4, 'мало блоков подсказок (AS/цели/приёмы/рекомендации): %d' % sugg.count()
        assert sugg.filter(has=page.get_by_text('Актуальное состояние')).count() >= 1, 'нет блока «Актуальное состояние»'
        for kind in ['goal', 'meth', 'rec']:
            assert sph2.locator('.sugg[data-sugg="%s"]' % kind).count() >= 1, 'нет цветного блока ' + kind
        bcolors = page.evaluate('''() => {
          const pick = s => { const e = document.querySelector(s);
            return e ? getComputedStyle(e).backgroundColor : null; };
          return {goal: pick('.mb.sph .sugg[data-sugg="goal"]'),
                  meth: pick('.mb.sph .sugg[data-sugg="meth"]'),
                  rec:  pick('.mb.sph .sugg[data-sugg="rec"]')};
        }''')
        print('цвета блоков подсказок (goal/meth/rec):', bcolors)
        assert len({bcolors['goal'], bcolors['meth'], bcolors['rec']}) == 3, \
            'блоки целей/приёмов/рекомендаций не различаются цветом: ' + str(bcolors)
        page.screenshot(path=os.path.join(SHOTS, '02b_survey_key.png'), full_page=False)

        # --- кнопка «+ в документ» цветом выбранной оценки; тумблер «+ в документ» / «✓ убрать»
        tog = sph2.locator('.sugg button', has_text='+ в документ').first
        assert 'st-' in (tog.get_attribute('class') or ''), \
            'кнопка «+ в документ» не окрашена в цвет оценки: ' + str(tog.get_attribute('class'))
        print('класс кнопки «+ в документ»:', tog.get_attribute('class'))
        tog.click(); page.wait_for_timeout(400)
        tog2 = sph2.locator('.sugg button', has_text='убрать').first
        assert tog2.count() == 1, 'после добавления кнопка не превратилась в «убрать»'
        print('тумблер: после «+ в документ» кнопка показывает «убрать»')
        tog2.click(); page.wait_for_timeout(400)
        assert sph2.locator('.sugg button', has_text='+ в документ').count() >= 1, \
            'после «убрать» кнопка не вернулась в состояние «+ в документ»'
        print('тумблер: после «убрать» фраза удалена, кнопка снова «+ в документ»')

        # --- подробная оценка DIR (53 пункта) — на отдельной подвкладке
        page.click('button.svtab:has-text("Подробно: DIR")')
        page.wait_for_timeout(500)
        boxes = page.locator('.qitem').count()
        print('пунктов подробного опросника DIR:', boxes)
        assert boxes > 40, 'в подвкладке DIR мало пунктов: %d' % boxes
        page.locator('.qitem').first.locator('label', has_text='2 · иногда').click()
        page.wait_for_timeout(500)
        assert page.locator('.qitem').first.locator('.sugg').count() >= 1, 'ключ DIR не предложил формулировки'
        page.screenshot(path=os.path.join(SHOTS, '02c_survey_dir.png'), full_page=False)

        # --- сенсорный опросник FEDL2i: 46 пунктов, сборка текста в «Актуальное состояние»
        page.click('button.svtab:has-text("Сенсорный профиль")')
        page.wait_for_timeout(500)
        n_sens = page.locator('[data-sens]').count()
        print('пунктов FEDL2i на вкладке:', n_sens)
        assert n_sens == 46, 'пунктов FEDL2i: %d (ожидалось 46)' % n_sens
        assert page.locator('#main input[data-h="fill_date"]').count() >= 1, 'нет даты заполнения опросника'
        page.select_option('[data-sens="A1"]', '(+1)')
        page.wait_for_timeout(500)
        assert page.locator('button[data-sensapply="SPH-SENS"]').count() >= 1, \
            'после отметки A1 нет кнопки сборки текста сферы 1'
        page.locator('#main .card button[data-sensapply="SPH-SENS"]').first.click()
        page.wait_for_timeout(500)
        page.click('nav.tabs button:has-text("3. Актуальное состояние")')
        page.wait_for_timeout(400)
        # текст добавленной фразы лежит в textarea карточки микротемы 3 (сенсорика)
        ta_vals = page.eval_on_selector_all('.mb textarea[data-itext^="AS3soc"]',
                                            'els => els.map(e => e.value)')
        assert any('Сенсорная переработка: слуховая — повышенная чувствительность' in v for v in ta_vals), \
            'автотекст FEDL2i не попал в «Актуальное состояние»: ' + str(ta_vals)[:120]
        print('автотекст сенсорного профиля добавлен в микротему «Сенсорная переработка информации»')
        page.screenshot(path=os.path.join(SHOTS, '02d_sens.png'), full_page=False)

        # --- вопросы ИВ доступны и в простом режиме (отдельная подвкладка, группы свёрнуты)
        page.click('nav.tabs button:has-text("2. Опросник")')
        page.wait_for_timeout(300)
        page.click('button.svtab:has-text("Вопросы ИВ")')
        page.wait_for_timeout(400)
        n_iv2 = page.locator('[data-iv2]').count()
        print('вопросов ИВ2:', n_iv2)
        assert n_iv2 > 40, 'вопросов ИВ2: %d' % n_iv2

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

        # --- 1.3.0: V1 показывает ВСЕ формулировки общего банка (включая сферы 8–9)
        own = json.load(open(os.path.join(ROOT, 'data', 'phrases.json'), encoding='utf-8'))
        expect_all = len([p for p in own['phrases'] if p.get('active') is not False])
        shown = page.input_value('#bankCountSimple')
        print('счётчик банка (простой режим):', shown, '| ожидается «%d из %d»' % (expect_all, expect_all))
        assert shown == '%d из %d' % (expect_all, expect_all), 'счётчик банка: ' + shown
        assert rows_all == expect_all, 'в таблице банка V1 строк %d, ожидается %d' % (rows_all, expect_all)
        # в простом режиме таблица показывает названия микротем, коды — в продвинутом
        bank_txt = page.inner_text('#bankTable')
        assert 'Двигательное планирование и праксис' in bank_txt, 'в таблице банка нет микротемы праксиса'
        assert 'Зрительно-пространственная обработка' in bank_txt, 'в таблице банка нет микротемы AS8vis'

        # --- продвинутый режим: названия блоков/микроблоков вместе с кодами (перенос из v2, запись 45)
        page.click('#btnMode')
        page.wait_for_timeout(500)
        blk_opts = page.locator('#fBlock option').all_inner_texts()
        mic_opts = page.locator('#fMicro option').all_inner_texts()
        print('фильтр «Блок»:', ' | '.join(blk_opts[:3]), '…')
        assert any('Актуальное состояние · AS' == o.strip() for o in blk_opts), \
            'в фильтре «Блок» нет связки «название · код»: ' + str(blk_opts[:3])
        assert any('AS5play' in o for o in mic_opts), 'в фильтре «Микроблок» нет кода AS5play'
        assert any('AS7prax' in o for o in mic_opts), \
            'в фильтре «Микроблок» нет микротемы праксиса (с 1.3.0 видна в V1)'
        assert any('AS8vis' in o for o in mic_opts), 'в фильтре «Микроблок» нет микротемы AS8vis'
        assert page.inner_text('#bankCount').strip() == str(expect_all), \
            'счётчик «всего фраз» в продвинутом режиме: ' + page.inner_text('#bankCount')
        assert 'AS7prax' in page.inner_text('#bankTable'), 'в таблице банка (продвинутый режим) нет кода AS7prax'
        page.screenshot(path=os.path.join(SHOTS, '07c_bank_full_mode.png'), full_page=False)
        page.click('#btnMode')   # обратно в простой режим
        page.wait_for_timeout(400)


        # --- модалка подбора фраз: счётчик «Найдено», легенда кодов, цвет строки по блоку
        page.click('nav.tabs button:has-text("3. Актуальное состояние")')
        page.wait_for_timeout(400)
        page.locator('[data-pick^="MICRO:"]').first.click()
        page.wait_for_timeout(400)
        pick = page.inner_text('#pickerBody')
        print('модалка подбора, первые строки:', pick.split('\n')[0][:90])
        assert pick.strip().startswith('Найдено:'), 'в модалке нет счётчика «Найдено»'
        assert 'AS5play-S2-07' in pick, 'в модалке нет легенды кодов'
        assert page.locator('#pickerBody .prow.to-as').count() > 0, 'строки модалки не помечены цветом блока'
        page.screenshot(path=os.path.join(SHOTS, '03b_picker_legend.png'), full_page=False)
        page.keyboard.press('Escape')
        page.wait_for_timeout(250)
        assert page.locator('#pickerOv').count() == 0, 'модалка не закрылась по Escape'

        # --- развёрнутые связи: у фразы АС из банка видны её цели, приёмы и рекомендации.
        # В примере проекта фраза AS2emo-FR-S2-01 уже добавлена — проверяем её блок связей.
        item_links = page.locator('.mb[data-micro="AS2emo"] details:has-text("Связи этой фразы")')
        assert item_links.count() >= 1, 'у добавленной фразы АС нет блока «Связи этой фразы»'
        links_txt = item_links.first.inner_text()
        print('связи выбранной фразы (фрагмент):', links_txt.replace('\n', ' ')[:110])
        assert 'цели' in links_txt and 'приёмы' in links_txt and 'рекомендации' in links_txt, \
            'в связях фразы нет целей/приёмов/рекомендаций: ' + links_txt[:80]
        page.locator('.mb[data-micro="AS2emo"] details:has-text("Связи этой фразы")').first.locator('summary').click()
        page.wait_for_timeout(300)
        page.screenshot(path=os.path.join(SHOTS, '03c_item_links.png'), full_page=False)

        # --- сводная карточка связей на вкладке «4. Цели и приёмы»
        page.click('nav.tabs button:has-text("4. Цели и приёмы")')
        page.wait_for_timeout(400)
        linked = page.locator('.card:has-text("Подсказка: цели, приёмы и рекомендации")')
        assert linked.count() >= 1, 'на вкладке целей нет сводной карточки связей'
        ltxt = linked.first.inner_text()
        assert 'Развитие способности к саморегуляции в ситуации фрустрации' in ltxt, \
            'в карточке связей нет цели GL-04 из выбранной фразы: ' + ltxt[:120]
        print('карточка связей на вкладке целей: символов', len(ltxt))
        linked.first.locator('.sugg[data-sugg="goal"] button', has_text='+ в документ').first.click()
        page.wait_for_timeout(400)
        assert page.locator('.card:has-text("Подсказка: цели, приёмы и рекомендации") .sugg[data-sugg="goal"] button:has-text("убрать")').count() >= 1, \
            'цель из карточки связей не добавилась в документ'
        page.screenshot(path=os.path.join(SHOTS, '04b_linked_cards.png'), full_page=False)
        # рекомендации: та же карточка на вкладке 6
        page.click('nav.tabs button:has-text("6. Рекомендации")')
        page.wait_for_timeout(400)
        assert page.locator('.card:has-text("Подсказка: цели, приёмы и рекомендации") .sugg[data-sugg="rec"]').count() >= 1, \
            'на вкладке рекомендаций нет блока связанных рекомендаций'

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
