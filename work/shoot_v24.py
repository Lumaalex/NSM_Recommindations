# -*- coding: utf-8 -*-
"""Скриншоты v2.4.0: шаг «Актуальное состояние», банк фраз с новыми кодами и названиями блоков."""
import pathlib
from playwright.sync_api import sync_playwright

URL = pathlib.Path('konstruktor/fork_v2/Конструктор_ИВ_версия2.html').resolve().as_uri()
OUT = pathlib.Path('work/shots'); OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1440, 'height': 1000})
    pg.goto(URL); pg.wait_for_timeout(600)

    # 1) шаг 1 — теперь «Актуальное состояние»
    steps = pg.locator('.steps button')
    print('шаги:', [steps.nth(i).inner_text().strip() for i in range(steps.count())])
    pg.locator('.steps').screenshot(path=str(OUT / 'v240_steps.png'))
    pg.locator('#main').screenshot(path=str(OUT / 'v240_step1_aktualnoe.png'))

    # оценка сферы 3 «Интерес» → подсказки с новыми кодами
    card = pg.locator('.sph', has_text='Интерес к миру, игрушкам, людям, играм').first
    card.locator('[data-ped="SPH-WOR|4"]').click()
    pg.wait_for_timeout(400)
    hints = pg.eval_on_selector_all('.sph .suggrow .tx', 'els=>els.slice(0,4).map(e=>e.textContent.trim().slice(0,60))')
    print('подсказки сферы:', hints)
    card.screenshot(path=str(OUT / 'v240_sphere3_interest.png'))

    # 2) банк фраз: названия блоков в выпадающем списке + коды AS1sens… в строках
    pg.click('#btnBank'); pg.wait_for_timeout(400)
    opts = pg.eval_on_selector_all('#pkBlock option', 'els=>els.map(e=>e.textContent)')
    print('блок документа, опции:', opts)
    pg.locator('.pick').screenshot(path=str(OUT / 'v240_bank_AS.png'))

    # сфера «Интерес» в банке: видны коды AS1sens-*
    pg.select_option('#pkSphere', 'SPH-WOR'); pg.wait_for_timeout(300)
    rows = pg.eval_on_selector_all('#pkBody .prow .small.muted', 'els=>els.slice(0,6).map(e=>e.textContent)')
    print('подписи строк банка:', rows)
    pg.locator('.pick').screenshot(path=str(OUT / 'v240_bank_sphere_wor.png'))

    # блок «Цели на период реабилитации»
    pg.select_option('#pkBlock', 'GOAL'); pg.wait_for_timeout(300)
    pg.locator('.pick').screenshot(path=str(OUT / 'v240_bank_goals.png'))

    pg.close(); b.close()
print('ok')
