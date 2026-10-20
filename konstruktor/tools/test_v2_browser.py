# -*- coding: utf-8 -*-
"""Сквозной тест форка v2 в браузере (десктоп + мобильный).
Запуск: python tools/test_v2_browser.py"""
import io
import json
import os
import sys

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHOTS = os.path.abspath(os.path.join(HERE, '..', '..', 'work', 'shots'))
os.makedirs(SHOTS, exist_ok=True)
HTML = 'file://' + os.path.join(ROOT, 'fork_v2', 'Конструктор_ИВ_версия2.html')

fails = []


def check(cond, msg):
    print(('  OK   ' if cond else '  FAIL ') + msg)
    if not cond:
        fails.append(msg)


def overflow(page):
    return page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")


def run(pw, label, vp, mobile, touch, prefix):
    print('\n=== v2, %s ===' % label)
    browser = pw.chromium.launch()
    ctx = browser.new_context(viewport=vp, is_mobile=mobile, has_touch=touch,
                              device_scale_factor=2, accept_downloads=True)
    page = ctx.new_page()
    errs = []
    page.on('pageerror', lambda e: errs.append(str(e)))
    page.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    # 2.6.0: в prompt отвечаем заготовленным текстом (нужно для «+ Новая фраза» на шаге 9)
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
        loc.tap() if touch else loc.click()
    page.goto(HTML)
    page.wait_for_timeout(500)
    check(page.locator('#nojs').count() == 0, 'заглушка скрыта при работающем JS')
    check(page.locator('.steps button').count() == 9, 'шагов в степпере: 9 (9-й — «Банк фраз»)')
    check(page.locator('#btnBank').is_visible(), 'кнопка «Банк фраз» видна в шапке')

    # форки независимы: перекрёстных ссылок быть не должно
    check(page.locator('a[href*="Конструктор_рекоменданий"]').count() == 0,
          'в v2 нет ссылок на классическую версию')

    # шаг 1: шапка + оценка сфер
    page.fill('[data-h="fio"]', 'Тестов Тест Тестович')
    page.fill('[data-h="period_start"]', '01.09.2026')
    page.fill('[data-h="period_end"]', '30.09.2026')
    page.fill('[data-h="specialist"]', 'Петрова А.И.')
    page.fill('[data-h="sessions"]', '10')
    page.wait_for_timeout(250)
    chip_spec = (page.text_content('#hdrSpec') or '').strip()
    check(chip_spec == 'специалист: Петрова А.И. · занятий: 10',
          '2.6.0: чип специалиста в шапке обновляется на ввод: ' + chip_spec)
    sph = page.locator('.sph')
    n = sph.count()
    check(n == 9, 'сфер на шаге оценки: %d' % n)
    names = [(sph.nth(i).locator('.hd .t').text_content() or '') for i in range(n)]
    check(any('Двигательное планирование и праксис' in t for t in names),
          'сфера 8 «Двигательное планирование и праксис» на шаге оценки')
    check(any('Зрительно-пространственная обработка' in t for t in names),
          'сфера 9 «Зрительно-пространственная обработка информации» на шаге оценки')
    check(any('Инициатива, цепочки общения' in t for t in names),
          'сфера 5 «Инициатива, цепочки общения, целенаправленность» на шаге оценки')
    picks = ['4', '3', '4', '2', '3', '3', '2', '4', '2']
    for i in range(n):
        lab = sph.nth(i).locator('.peds label', has_text=picks[i]).first
        lab.tap() if touch else lab.click()
        page.wait_for_timeout(120)
    check(sph.nth(1).locator('.suggrow').count() >= 1, 'после оценки выпадают формулировки сферы')
    # 2.6.0: карточка-дубль «Банк фраз: смотреть и добавлять» с шага 1 убрана
    # (кнопка «Банк фраз» в шапке теперь ведёт на шаг 9), кнопки в карточках сфер остались
    check(page.locator('button[data-bank="AS|"]').count() == 0,
          'на шаге 1 нет карточки-дубля банка')
    check(page.locator('button:has-text("Банк фраз: смотреть и добавлять")').count() == 0,
          'текста карточки-дубля на шаге 1 нет')
    check(page.locator('[data-bank^="AS|SPH-"]').count() == 9,
          'кнопки «+ из банка фраз» остались в карточках всех 9 сфер')

    # --- шкала 2.5.0: критерий через поддержку и соответствие V1 ---
    hint1 = sph.nth(1).locator('.peds + .small')
    check(hint1.count() == 1, 'под выбранной оценкой видна строка критерия')
    htxt = (hint1.text_content() or '')
    check('Без поддержки не получается' in htxt, 'критерий уровня 3: «только со стабильной поддержкой»')
    check('1 · с поддержкой' in htxt, 'в строке критерия показано соответствие V1')
    t5 = sph.nth(0).locator('.peds label[data-ped$="|5"]').first.get_attribute('title') or ''
    check('ресурс' in t5 and '3 · стабильно' in t5, 'тултип кнопки 5: критерий + соответствие V1')
    page.locator('details.help summary', has_text='Расшифровка баллов').first.click()
    help_tbl = page.locator('details.help table.bank').first
    hh = help_tbl.text_content() or ''
    check('Критерий через поддержку' in hh, 'в расшифровке есть колонка критерия через поддержку')
    check('2 · иногда' in hh and 'N · не проверялось' in hh,
          'в расшифровке видно соответствие V1 для баллов и S0')
    page.locator('details.help summary', has_text='Расшифровка баллов').first.click()

    # --- шапка: ФИО и дата заполнения видны в приложении ---
    fio_chip = (page.text_content('#hdrFio') or '').strip()
    date_chip = (page.text_content('#hdrDate') or '').strip()
    check('Тестов' in fio_chip, 'в шапке приложения видно ФИО ребёнка: ' + fio_chip)
    check(page.locator('[data-h="fill_date"]').count() == 1, 'есть поле «Дата заполнения»')
    fd = page.input_value('[data-h="fill_date"]')
    check(len(fd.split('.')) == 3, 'дата заполнения проставлена сегодняшним днём: ' + fd)
    check(fd in date_chip, 'дата заполнения видна в шапке: ' + date_chip)
    page.fill('[data-h="fill_date"]', '12.10.2026')
    page.wait_for_timeout(200)
    check('12.10.2026' in (page.text_content('#hdrDate') or ''), 'шапка обновляется при вводе даты')

    # --- блок A (сенсорные системы) прямо в карточке сферы «Сенсорная переработка» ---
    mini = sph.nth(0).locator('.sens-mini')
    check(mini.count() == 1, 'в сфере «Сенсорная переработка» есть блок A таблицы FEDL2i')
    check(mini.locator('select[data-sens]').count() == 7,
          'сенсорных систем в блоке A: %d' % mini.locator('select[data-sens]').count())
    check(sph.nth(1).locator('.sens-mini').count() == 0,
          'у сферы «Эмоции и регуляция» мини-таблицы FEDL2i нет')
    check(page.locator('.sens-mini select[data-sens="A1"]').count() == 1,
          'блок A показан только в сфере «Сенсорная переработка»')
    # остальные сферы дополняются своими блоками таблицы FEDL2i (свёрнуты, чтобы не удлинять шаг)
    check(sph.nth(5).locator('.sens-mini').count() == 1
          and sph.nth(5).locator('select[data-sens="C1"]').count() == 1
          and sph.nth(5).locator('select[data-sens="D8"]').count() == 1,
          'сферу «Коммуникация» дополняют блоки C и D')
    check(sph.nth(7).locator('select[data-sens="B1"]').count() == 1
          and sph.nth(7).locator('select[data-sens="F5"]').count() == 1,
          'сферу «Праксис» дополняют блоки B и F')
    check(sph.nth(8).locator('select[data-sens="E1"]').count() == 1,
          'сферу «Зрительно-пространственная» дополняет блок E')
    check(sph.nth(7).locator('details.sens-mini[open]').count() == 0,
          'мини-таблица сферы 8 свёрнута — шаг оценки не перегружен')
    mini.locator('select[data-sens="A1"]').select_option('(+1)')
    page.wait_for_timeout(250)
    mini.locator('select[data-sens="A4"]').select_option('(-1)')
    page.wait_for_timeout(250)
    mini.locator('textarea[data-sens="A8"]').fill('ищет сильные vestibular нагрузки, шум переносит плохо')
    page.wait_for_timeout(250)
    check('Готов к сборке' in (mini.text_content() or '') or 'Сенсорная переработка' in (mini.text_content() or ''),
          'мини-блок показывает собираемый текст профиля')
    if prefix == 'v2desk':
        page.screenshot(path=os.path.join(SHOTS, 'v220_sens_mini.png'))

    # --- шаг 2: сенсорный опросник FEDL2i ---
    page.tap('.steps button:has-text("2. Сенсорный опросник")') if touch else \
        page.click('.steps button:has-text("2. Сенсорный опросник")')
    page.wait_for_timeout(350)
    blocks = page.locator('.sens-blk').count()
    check(blocks == 6, 'блоков опросника A–F: %d' % blocks)
    nsens = page.locator('[data-sens]').count()
    check(nsens == 46, 'пунктов опросника: %d' % nsens)
    check(page.locator('.sens-blk', has_text='B. Двигательное планирование').count() == 1,
          'блок B «Двигательное планирование» на месте')
    check(page.locator('select[data-sens="A1"]').input_value() == '(+1)',
          'оценки блока A общие со сферой: A1 = (+1)')
    page.locator('select[data-sens="B1"]').select_option('Да')
    page.locator('select[data-sens="C6"]').select_option('1-3')
    page.wait_for_timeout(250)
    check('Заполнено пунктов: 5' in (page.text_content('#main') or '').replace('\n', ' '),
          'счётчик заполнения опросника считается')
    check(page.locator('.steps button:has-text("2. Сенсорный опросник").done').count() == 1,
          'шаг «Сенсорный опросник» отмечен галочкой после заполнения')
    page.tap('[data-sensapply]') if touch else page.click('[data-sensapply]')
    page.wait_for_timeout(300)
    auto = page.locator('#sensAutoCard .auto-note')
    check(auto.count() == 1, 'появился собранный текст сенсорного профиля')
    atext = (auto.text_content() or '')
    check('слуховая — повышенная чувствительность' in atext, 'оценки систем переведены в слова: ' + atext[:70] + '…')
    check('вестибулярная — сниженная чувствительность' in atext, 'знак (−1) прочитан как «сниженная»')
    check('Доминирующий функциональный профиль' in atext, 'доминирующий профиль добавлен в текст')
    if prefix == 'v2desk':
        page.screenshot(path=os.path.join(SHOTS, 'v220_sens_tab.png'), full_page=False)

    # --- авто-профиль доезжает до документа ---
    page.tap('.steps button:has-text("8. Документ")') if touch else page.click('.steps button:has-text("8. Документ")')
    page.wait_for_timeout(400)
    doct = page.text_content('#docwrap') or ''
    check('Сенсорная переработка: слуховая' in doct, 'сенсорный профиль попал в «Актуальное состояние»')
    check(doct.count('Сенсорная переработка: слуховая') == 1, 'сенсорный профиль в документе один раз')
    check('Дата заполнения: 12.10.2026' in doct.replace('\n', ' ') or 'Дата заполнения:' in doct,
          'дата заполнения есть в шапке документа')
    fname = (page.text_content('.filename') or '').strip()
    check('Тестов' in fname and '12-10-2026' in fname, 'имя файла содержит ФИО и дату: ' + fname)
    # убрать профиль из документа
    page.tap('.steps button:has-text("2. Сенсорный опросник")') if touch else \
        page.click('.steps button:has-text("2. Сенсорный опросник")')
    page.wait_for_timeout(300)
    page.tap('[data-sensdrop]') if touch else page.click('[data-sensdrop]')
    page.wait_for_timeout(300)
    page.tap('.steps button:has-text("8. Документ")') if touch else page.click('.steps button:has-text("8. Документ")')
    page.wait_for_timeout(400)
    check('Сенсорная переработка: слуховая' not in (page.text_content('#docwrap') or ''),
          'кнопка «убрать из документа» работает')
    # вернуть обратно для дальнейших проверок
    page.tap('.steps button:has-text("2. Сенсорный опросник")') if touch else \
        page.click('.steps button:has-text("2. Сенсорный опросник")')
    page.wait_for_timeout(250)
    page.tap('[data-sensapply]') if touch else page.click('[data-sensapply]')
    page.wait_for_timeout(250)
    # возвращаемся на шаг 1 — дальше идут проверки оценки сфер
    page.tap('.steps button:has-text("1. Актуальное состояние")') if touch else \
        page.click('.steps button:has-text("1. Актуальное состояние")')
    page.wait_for_timeout(350)
    check(page.locator('.sph').count() == 9, 'после сенсорного опросника снова видны сферы')
    check('Сенсорная переработка' in (page.locator('#sensAutoCard').count() and '' or
          (page.locator('.sens-mini .auto-note').text_content() or '')),
          'собранный профиль виден и в карточке сферы')
    check(sph.nth(0).locator('.suggrow').count() >= 4,
          'под оценку выпадают все варианты банка сферы: %d' % sph.nth(0).locator('.suggrow').count())
    # банк фраз в v2: модалка из карточки сферы
    sph.nth(0).locator('[data-bank^="AS|"]').first.click()
    page.wait_for_timeout(400)
    rows = page.locator('#pkBody .prow').count()
    check(rows >= 4, 'модалка банка открыта, строк: %d' % rows)
    page.locator('#pkBody .prow button', has_text='+ добавить').first.click()
    page.wait_for_timeout(300)
    check(page.locator('#pkBody .prow button', has_text='✓ убрать').count() >= 1,
          'добавление из банка работает и кнопка становится «убрать»')
    page.keyboard.press('Escape')
    page.wait_for_timeout(300)
    check(page.locator('#pickerOv').count() == 0, 'Escape закрывает банк фраз')
    added = 0
    for i in range(n):
        btn = sph.nth(i).locator('.suggrow button', has_text='+ добавить').first
        if btn.count():
            btn.tap() if touch else btn.click()
            added += 1
            page.wait_for_timeout(120)
    check(added >= 5, 'добавлено формулировок актуального состояния: %d' % added)
    # тумблер убрать
    brem = page.locator('.sph').nth(1).locator('.suggrow button', has_text='✓ убрать').first
    if brem.count():
        brem.tap() if touch else brem.click()
        page.wait_for_timeout(200)
        check(page.locator('.sph').nth(1).locator('.suggrow button', has_text='+ добавить').count() >= 1,
              'тумблер «убрать → добавить» работает')
    if prefix == 'v2desk':
        page.screenshot(path=os.path.join(SHOTS, 'v2_stage1.png'))

    # шаг 2: цели
    page.tap('.steps button:has-text("3. Цели")') if touch else page.click('.steps button:has-text("3. Цели")')
    page.wait_for_timeout(300)
    sugg = page.locator('.suggrow button', has_text='+ цель')
    check(sugg.count() >= 3, 'целей предложено: %d' % sugg.count())
    for i in range(min(4, sugg.count())):
        page.locator('.suggrow button', has_text='+ цель').first.tap() if touch else \
            page.locator('.suggrow button', has_text='+ цель').first.click()
        page.wait_for_timeout(120)
    check(page.locator('[data-itemdel^="goals:"]').count() == 4, 'выбрано целей: 4')

    # шаг 3: приёмы
    page.tap('.steps button:has-text("4. Приёмы")') if touch else page.click('.steps button:has-text("4. Приёмы")')
    page.wait_for_timeout(300)
    for i in range(3):
        b = page.locator('.suggrow button', has_text='+ приём').first
        if b.count():
            b.tap() if touch else b.click()
            page.wait_for_timeout(120)
    exs = page.locator('[data-itemex^="methods:"]')
    for i in range(exs.count()):
        exs.nth(i).evaluate("el => { el.closest('details').open = true; }")
        exs.nth(i).fill('На 4 занятии педагог сделал паузу, ребёнок продолжил действие сам.')
    check(page.locator('[data-itemdel^="methods:"]').count() == 3, 'выбрано приёмов: 3')

    # шаг 4: архив и результаты
    page.tap('.steps button:has-text("5. Результаты")') if touch else \
        page.click('.steps button:has-text("5. Результаты")')
    page.wait_for_timeout(300)
    page.tap('#archSave') if touch else page.click('#archSave')
    page.wait_for_timeout(300)
    with page.expect_download() as dl_snap:
        page.tap('#archFile') if touch else page.click('#archFile')
    snap = dl_snap.value
    snap_path = os.path.join('/tmp', prefix + '_snapshot.json')
    snap.save_as(snap_path)
    import json as _json
    snap_data = _json.load(open(snap_path, encoding='utf-8'))
    check(snap_data.get('project') == 'iv-constructor-v2-snapshot' and snap_data.get('scores'),
          'снимок сохранён в отдельный файл (оценок: %d)' % len(snap_data.get('scores', {})))
    # меняем одну оценку вверх, чтобы появилась динамика
    page.tap('.steps button:has-text("1. Актуальное состояние")') if touch else \
        page.click('.steps button:has-text("1. Актуальное состояние")')
    page.wait_for_timeout(300)
    lab = page.locator('.sph').nth(2).locator('.peds label', has_text='4').first
    lab.tap() if touch else lab.click()
    page.wait_for_timeout(200)
    page.tap('.steps button:has-text("5. Результаты")') if touch else \
        page.click('.steps button:has-text("5. Результаты")')
    page.wait_for_timeout(300)
    check(page.locator('.dyn').count() >= 1, 'таблица динамики по сферам есть: %d' % page.locator('.dyn').count())
    db = page.locator('[data-dynrow]').first
    if db.count():
        db.tap() if touch else db.click()
        page.wait_for_timeout(250)
        check(page.locator('[data-itemdel^="results:"]').count() >= 1, 'строка «было → стало» добавлена')
    if prefix == 'v2desk':
        page.screenshot(path=os.path.join(SHOTS, 'v2_stage4.png'))

    # шаг 6: рекомендации и литература
    page.tap('.steps button:has-text("7. Рекомендации")') if touch else \
        page.click('.steps button:has-text("7. Рекомендации")')
    page.wait_for_timeout(300)
    rb = page.locator('.suggrow button', has_text='+ рекомендация')
    check(rb.count() >= 4, 'рекомендаций предложено: %d' % rb.count())
    for i in range(min(5, rb.count())):
        page.locator('.suggrow button', has_text='+ рекомендация').first.tap() if touch else \
            page.locator('.suggrow button', has_text='+ рекомендация').first.click()
        page.wait_for_timeout(120)
    litb = page.locator('[data-lit]').first
    if litb.count():
        litb.tap() if touch else litb.click()
        page.wait_for_timeout(200)
        check(page.locator('[data-lit]', has_text='✓ в подборке').count() >= 1, 'приоритетная книга отмечена')

    # коды S5..S0, причина S0, неактуальные цели
    page.tap('.steps button:has-text("1. Актуальное состояние")') if touch else page.click('.steps button:has-text("1. Актуальное состояние")')
    page.wait_for_timeout(300)
    check(page.locator('.sph').nth(0).locator('.peds label.on .pcode', has_text='S4').count() == 1,
          'код S4 показан на оценённой сфере')
    lab1 = page.locator('.sph').nth(5).locator('.peds label', has_text='способность не сформирована').first
    lab1.tap() if touch else lab1.click()
    page.wait_for_timeout(250)
    check(page.locator('.sph').nth(5).locator('.notice', has_text='не актуальны').count() == 1,
          'S1: уведомление «цели в этой сфере сейчас не актуальны»')
    page.locator('.sph').nth(6).locator('.peds label.sig').first.tap() if touch else \
        page.locator('.sph').nth(6).locator('.peds label.sig').first.click()
    page.wait_for_timeout(250)
    sel = page.locator('.sph').nth(6).locator('select[data-reason]')
    check(sel.count() == 1, 'S0: появился выбор причины')
    sel.select_option(label='отказ ребёнка от занятия')
    page.wait_for_timeout(250)
    check(page.locator('.sph').nth(6).locator('.notice', has_text='оценка невозможна').count() == 1,
          'S0: уведомление о невозможности оценки')
    page.tap('.steps button:has-text("3. Цели")') if touch else page.click('.steps button:has-text("3. Цели")')
    page.wait_for_timeout(300)
    check(page.locator('.notice', has_text='цели в этой сфере сейчас не актуальны').count() >= 1,
          'шаг 3 (цели): сфера S1 исключена с пояснением')
    check(page.locator('.notice', has_text='цели появятся после повторной оценки').count() >= 1,
          'шаг 3 (цели): сфера S0 исключена с пояснением')

    # шаг 5: цели на следующий период — отдельная вкладка, генерация и отмена
    page.tap('.steps button:has-text("6. Цели на след. период")') if touch else \
        page.click('.steps button:has-text("6. Цели на след. период")')
    page.wait_for_timeout(300)
    check(page.locator('[data-nextgen]').count() == 1, 'редактор целей на следующий период — отдельный шаг 6')
    check(page.locator('#ownbox_next').count() == 1, 'окно «своя цель» принадлежит шагу 6')
    page.tap('[data-nextgen]') if touch else page.click('[data-nextgen]')
    page.wait_for_timeout(300)
    gen_n = page.locator('[data-itemdel^="next:"]').count()
    check(gen_n >= 3, 'генерация дала целей следующего периода: %d' % gen_n)
    check(page.locator('[data-nextundo]').count() == 1, 'появилась кнопка отмены генерации')
    page.tap('[data-nextundo]') if touch else page.click('[data-nextundo]')
    page.wait_for_timeout(300)
    check(page.locator('[data-itemdel^="next:"]').count() == 0, 'отмена вернула пустой список')
    page.tap('[data-nextgen]') if touch else page.click('[data-nextgen]')
    page.wait_for_timeout(300)

    # шаг 6: документ
    # окна «своя формулировка» не пересекаются между блоками
    page.tap('.steps button:has-text("7. Рекомендации")') if touch else page.click('.steps button:has-text("7. Рекомендации")')
    page.wait_for_timeout(300)
    chips = page.locator('[data-itemdel^="recs:"]').locator('xpath=ancestor::li').locator('.meta .pill').count()
    check(chips >= 1, 'у выбранных рекомендаций видны метки сфер: %d' % chips)
    page.tap('[data-own="recs"]') if touch else page.click('[data-own="recs"]')
    page.wait_for_timeout(250)
    check(page.locator('#ownbox_recs').is_visible(), '«+ своя рекомендация» открывает своё окно')
    check('скрыть' in (page.text_content('[data-own="recs"]') or ''), 'кнопка показывает, что окно можно свернуть')
    check(not page.locator('#ownbox_next').is_visible(), 'окно целей следующего периода при этом закрыто')
    page.tap('[data-own="recs"]') if touch else page.click('[data-own="recs"]')
    page.wait_for_timeout(250)

    page.tap('.steps button:has-text("8. Документ")') if touch else page.click('.steps button:has-text("8. Документ")')
    page.wait_for_timeout(400)
    check(page.locator('.doc').count() == 1, 'предпросмотр документа есть')
    check(overflow(page) <= 1, 'оверфлоу страницы: %d' % overflow(page))
    with page.expect_download() as dl:
        page.tap('#btnDocx') if touch else page.click('#btnDocx')
    d = dl.value
    target = os.path.join('/tmp', prefix + '_' + d.suggested_filename)
    d.save_as(target)
    check(os.path.getsize(target) > 10000, '.docx скачан: %d байт' % os.path.getsize(target))
    if prefix == 'v2desk':
        page.screenshot(path=os.path.join(SHOTS, 'v2_stage6.png'))

    else:
        page.screenshot(path=os.path.join(SHOTS, 'v2_mob_stage6.png'))
    check(page.locator('.check').count() == 8, 'самопроверка: 8 пунктов с иконками')
    check(page.locator('.check .ic').first.text_content() in ('✓', '✕', '!'),
          'иконки самопроверки отрисованы: ' + page.locator('.check .ic').first.text_content())
    check(page.locator('.check.pass').count() >= 3, 'заполненный документ даёт зелёные галочки: %d'
          % page.locator('.check.pass').count())
    check(page.locator('.check.fail').count() >= 1, 'незаполненные пункты помечены красным ✕: %d'
          % page.locator('.check.fail').count())


    # --- 2.6.0: шаг 9 «Банк фраз» — полный банк с правками внутри конструктора ---
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
                'Подсказка примера;Цели(ID);Приёмы(ID);Рекомендации(ID);Теги;Активна\n')
        f.write('AS5play-S1-IMP;IV;AS;AS5play;;S1;Импортированная формулировка из CSV;тест;Да;;;;импорт;Да\n')
        f.write('AS1-S3-02;IV;AS;AS1;;S3;Старая нумерация кода из файла;тест;Да;;;;импорт;Да\n')
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

    # цвета кодов оценок различаются по баллам
    page.tap('.steps button:has-text("1. Актуальное состояние")') if touch else page.click('.steps button:has-text("1. Актуальное состояние")')
    page.wait_for_timeout(300)
    cols = page.evaluate("() => Array.from(document.querySelectorAll('.sph>.hd .pill.cd'))"
                         ".map(e => getComputedStyle(e).backgroundColor)")
    check(len(cols) >= 3 and len(set(cols)) >= 3,
          'цвета кодов оценок различаются: %d плашек, %d цвета' % (len(cols), len(set(cols))))

    # сброс оценок и новый документ
    before = page.locator('.sph>.hd .pill.cd').count()
    page.tap('[data-clearscores]') if touch else page.click('[data-clearscores]')
    page.wait_for_timeout(300)
    after = page.locator('.sph>.hd .pill.cd').count()
    check(before > 0 and after == 0, 'кнопка «Сбросить оценки» очищает оценки (%d → %d)' % (before, after))
    page.tap('#btnNew') if touch else page.click('#btnNew')
    page.wait_for_timeout(300)
    check(page.input_value('[data-h="fio"]') == '', 'кнопка «Новый документ» очищает черновик')
    check((page.text_content('#hdrSpec') or '').strip() == 'специалист не указан',
          '2.6.0: после «Нового документа» чип специалиста пустой: '
          + (page.text_content('#hdrSpec') or '').strip())
    check(page.locator('.steps button.done').count() == 0,
          'после нового документа зелёные галочки шагов исчезли')
    ver = (page.text_content('#appver') or '').strip()
    check(len(ver.split('.')) == 3 and ver.replace('.', '').isdigit(),
          'версия показана в шапке без литералов: ' + ver)
    # заголовок вкладки и метка форка: скачанный файл должен опознаваться без открытия
    check(page.title().endswith('v' + ver), 'заголовок вкладки содержит версию форка: ' + page.title())
    check('v2.2' not in page.title(), 'в заголовке нет устаревшего литерала v2.2')
    check('V2 «от общего к частному»' in (page.locator('header.top .sub').first.text_content() or ''),
          'в шапке есть метка форка V2')

    check(len(errs) == 0, 'ошибок консоли: %d' % len(errs))
    for e in errs[:5]:
        print('   !', e)
    browser.close()


def main():
    with sync_playwright() as pw:
        run(pw, 'десктоп 1280', {'width': 1280, 'height': 950}, False, False, 'v2desk')
        run(pw, 'iPhone 390x844', {'width': 390, 'height': 844}, True, True, 'v2mob')
    print('\n' + ('✅ V2 В БРАУЗЕРЕ: ВСЁ ЗЕЛЁНОЕ' if not fails else '❌ ПРОБЛЕМ: %d' % len(fails)))
    for f in fails:
        print('  -', f)
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
