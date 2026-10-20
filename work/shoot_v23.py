# -*- coding: utf-8 -*-
"""Скриншоты v2.3.0: 9 сфер, мини-таблицы FEDL2i в сферах, шаг «Сенсорный опросник»."""
import os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
HTML = 'file://' + os.path.join(ROOT, 'konstruktor', 'fork_v2', 'Конструктор_ИВ_версия2.html')
SHOTS = os.path.join(ROOT, 'work', 'shots')
os.makedirs(SHOTS, exist_ok=True)

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={'width': 1280, 'height': 1000})
    pg.goto(HTML)
    pg.wait_for_timeout(500)
    pg.fill('[data-h="fio"]', 'Иванова Мария')
    pg.wait_for_timeout(200)
    sph = pg.locator('.sph')
    picks = ['4', '3', '4', '2', '3', '3', '2', '4', '2']
    for i in range(sph.count()):
        sph.nth(i).locator('.peds label', has_text=picks[i]).first.click()
        pg.wait_for_timeout(90)
    pg.screenshot(path=os.path.join(SHOTS, 'v230_step1_9spheres.png'), full_page=True)
    # сфера 8: раскрываем мини-таблицу FEDL2i (блоки B и F)
    sph.nth(7).locator('details.sens-det' if pg.locator('details.sens-det').count() else 'details.sens-mini').first.evaluate("d=>d.open=true")
    pg.wait_for_timeout(250)
    sph.nth(7).scroll_into_view_if_needed()
    pg.wait_for_timeout(250)
    pg.screenshot(path=os.path.join(SHOTS, 'v230_sphere8_praxis.png'))
    # сфера 6: коммуникация + блоки C/D
    sph.nth(5).locator('details.sens-mini').first.evaluate("d=>d.open=true")
    pg.wait_for_timeout(200)
    sph.nth(5).scroll_into_view_if_needed()
    pg.wait_for_timeout(200)
    pg.screenshot(path=os.path.join(SHOTS, 'v230_sphere6_communication.png'))
    # шаг 2: опросник с привязкой блоков к сферам
    pg.click('.steps button:has-text("2. Сенсорный опросник")')
    pg.wait_for_timeout(400)
    pg.screenshot(path=os.path.join(SHOTS, 'v230_step2_fedl_mapping.png'))
    b.close()
print('скриншоты:', ', '.join(sorted(f for f in os.listdir(SHOTS) if f.startswith('v230'))))
