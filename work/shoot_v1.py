# -*- coding: utf-8 -*-
"""Скриншоты V1 после переноса наработок v2 (пакет 1.2.0): шапка-чипы, банк, модалка подбора."""
import pathlib
from playwright.sync_api import sync_playwright

URL = pathlib.Path('konstruktor/Конструктор_рекомендаций.html').resolve().as_uri()
OUT = pathlib.Path('work/shots'); OUT.mkdir(parents=True, exist_ok=True)

FILL = """()=>{
  const set=(k,v)=>{const e=document.querySelector('[data-h="'+k+'"]');
    if(e){e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));}};
  set('fio','Иванов Пётр Сергеевич'); set('birth','01.01.2018');
  set('period_start','19.07.2026'); set('period_end','31.07.2026');
  set('specialist','Иванова А.Б.'); set('sessions','10');
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp in (('desk', {'width': 1440, 'height': 900}), ('mob', {'width': 390, 'height': 844})):
        pg = b.new_page(viewport=vp)
        pg.goto(URL); pg.wait_for_timeout(600)
        pg.evaluate(FILL); pg.wait_for_timeout(300)
        pg.locator('header.top').screenshot(path=str(OUT / f'v120_header_{name}.png'))

        # банк фраз (простой режим)
        pg.click('nav.tabs button:has-text("Банк фраз")'); pg.wait_for_timeout(500)
        pg.screenshot(path=str(OUT / f'v120_bank_simple_{name}.png'), full_page=False)

        # модалка подбора фраз с легендой кодов (простой режим)
        pg.click('nav.tabs button:has-text("3. Актуальное состояние")'); pg.wait_for_timeout(500)
        pg.locator('[data-pick^="MICRO:"]').first.click(); pg.wait_for_timeout(500)
        pg.locator('#pickerOv').screenshot(path=str(OUT / f'v120_picker_{name}.png'))
        pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

        # продвинутый режим: фильтры «название · код»
        pg.click('nav.tabs button:has-text("Банк фраз")'); pg.wait_for_timeout(400)
        pg.click('#btnMode'); pg.wait_for_timeout(700)
        pg.screenshot(path=str(OUT / f'v120_bank_full_{name}.png'), full_page=False)
        pg.close()
    b.close()
print('Скриншоты:', OUT)
