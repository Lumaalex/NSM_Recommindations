# -*- coding: utf-8 -*-
"""Проверка мобильной адаптации и тем оформления в реальном браузере.
Запуск: python tools/test_mobile.py
Эмулирует телефон (iPhone 12, 390x844, touch) и маленький Android (360x740):
  * горизонтальный оверфлоу страницы по всем вкладкам должен отсутствовать;
  * вкладки, шкала опросника, банк фраз и скачивание .docx должны работать касаниями;
  * тёмная тема и масштаб шрифта переключаются и запоминаются после перезагрузки.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHOTS = os.path.abspath(os.path.join(HERE, '..', '..', 'work', 'shots'))
os.makedirs(SHOTS, exist_ok=True)

from playwright.sync_api import sync_playwright

HTML = 'file://' + os.path.join(ROOT, 'Конструктор_рекомендаций.html')
PROJ = os.path.join(ROOT, 'Пример_проекта.json')

TABS = ['1. Шапка', '2. Опросник', '3. Актуальное состояние', '4. Цели и приёмы',
        '5. Результаты', '6. Рекомендации', '7. Документ', 'Банк фраз', 'Инструкция']

fails = []


def check(cond, msg):
    print(('  OK   ' if cond else '  FAIL ') + msg)
    if not cond:
        fails.append(msg)


def overflow(page):
    return page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")


def run_device(pw, name, viewport, mobile, touch, shots_prefix):
    print('\n=== Устройство: %s (%dx%d) ===' % (name, viewport['width'], viewport['height']))
    browser = pw.chromium.launch()
    ctx = browser.new_context(viewport=viewport, is_mobile=mobile, has_touch=touch,
                              device_scale_factor=2, accept_downloads=True)
    page = ctx.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.goto(HTML)
    page.wait_for_timeout(500)

    save_lbl = page.inner_text('#btnSaveProject').strip()
    check(save_lbl == 'Сохранить', 'короткая подпись на телефоне: «%s»' % save_lbl)

    # загрузка примера проекта
    page.set_input_files('#fileProject', PROJ)
    page.wait_for_timeout(600)

    for t in TABS:
        page.tap('nav.tabs button:has-text("%s")' % t) if touch else \
            page.click('nav.tabs button:has-text("%s")' % t)
        page.wait_for_timeout(350)
        ov = overflow(page)
        check(ov <= 1, '%s: горизонтальный оверфлоу %dpx' % (t, ov))

    # вкладки листаются свайпом (scrollWidth навбара больше клиентской ширины — это норма)
    page.tap('nav.tabs button:has-text("2. Опросник")') if touch else \
        page.click('nav.tabs button:has-text("2. Опросник")')
    page.wait_for_timeout(300)
    nav_scroll = page.evaluate("() => { const n = document.querySelector('nav.tabs'); return n.scrollWidth > n.clientWidth; }")
    print('  инфо: навбар прокручивается по горизонтали: %s' % nav_scroll)

    # касание по шкале опросника
    first = page.locator('.qitem').first
    first.locator('label', has_text='3 · стабильно').tap() if touch else \
        first.locator('label', has_text='3 · стабильно').click()
    page.wait_for_timeout(400)
    check(first.locator('.sugg').count() >= 1, 'касание по шкале даёт подсказки ключа')

    # кнопка «+ в документ» пальцем
    btn = first.locator('.sugg button', has_text='+ в документ').first
    if btn.count():
        btn.tap() if touch else btn.click()
        page.wait_for_timeout(400)
        check(True, 'кнопка «+ в документ» нажимается')

    # тема: переключение и сохранение
    page.tap('#btnTheme') if touch else page.click('#btnTheme')
    page.wait_for_timeout(300)
    theme = page.evaluate("document.documentElement.getAttribute('data-theme')")
    check(theme == 'dark', 'тёмная тема включилась: %s' % theme)
    body_bg = page.evaluate("getComputedStyle(document.body).backgroundColor")
    print('  фон body в тёмной теме: %s' % body_bg)
    page.screenshot(path=os.path.join(SHOTS, shots_prefix + '_dark_survey.png'))

    # масштаб шрифта
    before = page.evaluate("getComputedStyle(document.body).fontSize")
    page.tap('#btnFontPlus') if touch else page.click('#btnFontPlus')
    page.wait_for_timeout(200)
    after = page.evaluate("getComputedStyle(document.body).fontSize")
    check(float(after.rstrip('px')) > float(before.rstrip('px')),
          'шрифт увеличился: %s → %s' % (before, after))
    lbl = page.text_content('#fsLabel')
    check(lbl.strip() == '115%', 'индикатор масштаба: %s' % lbl)

    # перезагрузка: настройки и черновик должны сохраниться
    page.reload()
    page.wait_for_timeout(600)
    theme2 = page.evaluate("document.documentElement.getAttribute('data-theme')")
    lbl2 = page.text_content('#fsLabel')
    fio2 = page.input_value('[data-h="fio"]')
    check(theme2 == 'dark', 'после перезагрузки тема осталась тёмной: %s' % theme2)
    check(lbl2.strip() == '115%', 'после перезагрузки масштаб сохранился: %s' % lbl2)
    check('Иванов' in (fio2 or ''), 'черновик проекта пережил перезагрузку')

    # документ и скачивание .docx с телефона
    page.tap('nav.tabs button:has-text("7. Документ")') if touch else \
        page.click('nav.tabs button:has-text("7. Документ")')
    page.wait_for_timeout(500)
    check(overflow(page) <= 1, 'вкладка «Документ»: оверфлоу %dpx' % overflow(page))
    page.screenshot(path=os.path.join(SHOTS, shots_prefix + '_dark_doc.png'), full_page=False)
    with page.expect_download() as dl:
        page.tap('#btnDocx') if touch else page.click('#btnDocx')
    d = dl.value
    target = os.path.join(SHOTS, shots_prefix + '_' + d.suggested_filename)
    d.save_as(target)
    check(os.path.getsize(target) > 10000, 'скачивание .docx с мобильного: %d байт' % os.path.getsize(target))

    # светлая тема + скриншоты интерфейса
    page.tap('#btnTheme') if touch else page.click('#btnTheme')
    page.wait_for_timeout(300)
    page.screenshot(path=os.path.join(SHOTS, shots_prefix + '_light_header.png'))
    page.tap('nav.tabs button:has-text("Банк фраз")') if touch else \
        page.click('nav.tabs button:has-text("Банк фраз")')
    page.wait_for_timeout(400)
    check(overflow(page) <= 1, 'банк фраз: оверфлоу %dpx (таблица скроллится внутри)' % overflow(page))
    page.screenshot(path=os.path.join(SHOTS, shots_prefix + '_light_bank.png'))

    check(len(errors) == 0, 'ошибок консоли: %d' % len(errors))
    for e in errors[:5]:
        print('     !', e)
    browser.close()


def main():
    with sync_playwright() as pw:
        run_device(pw, 'iPhone 12 / 390x844, touch', {'width': 390, 'height': 844}, True, True, 'mob390')
        run_device(pw, 'маленький Android / 360x740, touch', {'width': 360, 'height': 740}, True, True, 'mob360')
    print('\n' + ('✅ МОБИЛЬНАЯ ПРОВЕРКА ПРОЙДЕНА' if not fails else '❌ ПРОБЛЕМ: %d' % len(fails)))
    for f in fails:
        print('  -', f)
    print('Скриншоты:', SHOTS)
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
