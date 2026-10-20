# -*- coding: utf-8 -*-
"""
ПРОВЕРКА В SAFARI (движок WebKit) ПО HTTP, В ЭМУЛЯЦИИ iPHONE
============================================================
Зачем: на iPhone предпросмотр HTML-файла (Quick Look) не выполняет JavaScript,
поэтому рабочий сценарий на телефоне — открыть конструктор в Safari по http://.
Этот тест поднимает локальный сервер и прогоняет мобильный сценарий на WebKit:
вкладки, загрузка проекта, тумблер «+ в документ / ✓ убрать», тема, кегль,
скачивание .docx, сохранение черновика после перезагрузки, отсутствие оверфлоу.

Запуск: python tools/test_safari.py
Если WebKit не установлен — тест вежливо пропускается.
"""
import os
import socket
import sys
import threading
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHOTS = os.path.abspath(os.path.join(HERE, '..', '..', 'work', 'shots'))
os.makedirs(SHOTS, exist_ok=True)
PORT = 8129

fails = []


def check(cond, msg):
    print(('  OK   ' if cond else '  FAIL ') + msg)
    if not cond:
        fails.append(msg)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, *a):
        pass


def free_port():
    for p in range(PORT, PORT + 40):
        with socket.socket() as s:
            try:
                s.bind(('127.0.0.1', p))
                return p
            except OSError:
                continue
    raise SystemExit('нет свободного порта')


def main():
    port = free_port()
    httpd = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url = 'http://127.0.0.1:%d/%s' % (port, urllib.parse.quote('Конструктор_рекомендаций.html'))

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('Playwright не установлен — тест пропущен')
        return 0

    iphone = {'viewport': {'width': 390, 'height': 844}, 'is_mobile': True, 'has_touch': True,
              'device_scale_factor': 3,
              'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) '
                            'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'}
    errs = []
    try:
        with sync_playwright() as pw:
            try:
                browser = pw.webkit.launch()
            except Exception as e:
                print('WebKit недоступен (%s) — тест пропущен' % str(e)[:120])
                return 0
            print('\n=== WebKit (Safari) + эмуляция iPhone 12, источник http://127.0.0.1:%d ===' % port)
            ctx = browser.new_context(**iphone, accept_downloads=True)
            page = ctx.new_page()
            page.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
            page.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)

            page.goto(url)
            page.wait_for_timeout(800)
            check(page.locator('#nojs').count() == 0, 'заглушка «без JS» скрыта при работающем JavaScript')
            check(page.locator('nav.tabs button').count() == 9, 'вкладки отрисованы: 9')

            page.set_input_files('#fileProject', os.path.join(ROOT, 'Пример_проекта.json'))
            page.wait_for_timeout(700)
            check('Иванов' in page.input_value('[data-h="fio"]'), 'проект загружен через input file')

            for t in ['2. Опросник', '3. Актуальное состояние', '4. Цели и приёмы',
                      '5. Результаты', '6. Рекомендации', '7. Документ', 'Банк фраз', 'Инструкция']:
                page.tap('nav.tabs button:has-text("%s")' % t)
                page.wait_for_timeout(300)
                ov = page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
                check(ov <= 1, '%s: оверфлоу %dpx' % (t, ov))

            # тумблер: считаем кнопки до и после, чтобы не зависеть от уже добавленных фраз
            page.tap('nav.tabs button:has-text("2. Опросник")')
            page.wait_for_timeout(400)
            # в простом режиме подсказки появляются после ответа: ставим «2» сфере «Эмоциональный фон»
            page.locator('.qitem').nth(1).locator('.scale label', has_text='2 · справляется, но не всегда').tap()
            page.wait_for_timeout(500)
            if page.locator('.qitem').nth(1).locator('.scale label.on').count() == 0:
                page.locator('.qitem').nth(1).locator('input[type=radio][value="2"]').tap(force=True)
                page.wait_for_timeout(500)
            check(page.locator('.qitem').nth(1).locator('.scale label.on').count() == 1,
                  'оценка сферы включилась касанием')
            item, free_before, added_before = None, 0, 0
            for i in range(9):   # ищем сферу, где есть ещё не добавленные фразы
                cand = page.locator('.mb').nth(i)
                fb = cand.locator('.sugg button', has_text='+ в документ').count()
                if fb:
                    item, free_before = cand, fb
                    added_before = cand.locator('.sugg button', has_text='убрать').count()
                    break
            if free_before:
                item.locator('.sugg button', has_text='+ в документ').first.tap()
                page.wait_for_timeout(400)
                free_mid = item.locator('.sugg button', has_text='+ в документ').count()
                added_mid = item.locator('.sugg button', has_text='убрать').count()
                check(free_mid == free_before - 1 and added_mid == added_before + 1,
                      'после «+ в документ» кнопка стала «✓ убрать» (%d→%d свободных, %d→%d убрать)'
                      % (free_before, free_mid, added_before, added_mid))
                item.locator('.sugg button', has_text='убрать').first.tap()
                page.wait_for_timeout(400)
                free_after = item.locator('.sugg button', has_text='+ в документ').count()
                check(free_after == free_before, 'после «✓ убрать» кнопка вернулась в «+ в документ»')
            else:
                check(False, 'ни в одной сфере опросника нет свободных кнопок добавления')

            # тема и кегль
            page.tap('#btnTheme')
            page.wait_for_timeout(300)
            check(page.evaluate("document.documentElement.getAttribute('data-theme')") == 'dark',
                  'тёмная тема в Safari включилась')
            before = page.evaluate("getComputedStyle(document.body).fontSize")
            page.tap('#btnFontPlus')
            page.wait_for_timeout(200)
            after = page.evaluate("getComputedStyle(document.body).fontSize")
            check(float(after[:-2]) > float(before[:-2]), 'кегль растёт: %s → %s' % (before, after))

            # документ и скачивание
            page.tap('nav.tabs button:has-text("7. Документ")')
            page.wait_for_timeout(500)
            check(page.locator('#docprint').count() == 1, 'предпросмотр документа есть')
            with page.expect_download() as dl:
                page.tap('#btnDocx')
            d = dl.value
            target = os.path.join('/tmp', 'safari_' + d.suggested_filename)
            d.save_as(target)
            check(os.path.getsize(target) > 10000, '.docx скачан: %d байт' % os.path.getsize(target))
            page.screenshot(path=os.path.join(SHOTS, 'safari_iphone_doc.png'))

            # перезагрузка: черновик, тема, кегль
            page.reload()
            page.wait_for_timeout(800)
            check('Иванов' in page.input_value('[data-h="fio"]'), 'черновик пережил перезагрузку')
            check(page.evaluate("document.documentElement.getAttribute('data-theme')") == 'dark',
                  'тема пережила перезагрузку')
            check(page.text_content('#fsLabel').strip() == '115%', 'кегль пережил перезагрузку')

            browser.close()
    finally:
        httpd.shutdown()

    check(len(errs) == 0, 'ошибок консоли: %d' % len(errs))
    for e in errs[:6]:
        print('   !', e)
    print('\n' + ('✅ SAFARI-ПРОВЕРКА ПРОЙДЕНА' if not fails else '❌ ПРОБЛЕМ: %d' % len(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
