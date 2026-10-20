# -*- coding: utf-8 -*-
"""Скриншоты v2 2.5.0: критерий через поддержку у оценок 5…1/S0, расшифровка с колонками V1.
Запуск из /home/user:  python3 work/shoot_v250.py"""
import pathlib
from playwright.sync_api import sync_playwright

URL = pathlib.Path('konstruktor/fork_v2/Конструктор_ИВ_версия2.html').resolve().as_uri()
OUT = pathlib.Path('work/shots'); OUT.mkdir(parents=True, exist_ok=True)

FILL = """()=>{
  const set=(k,v)=>{const e=document.querySelector('[data-h="'+k+'"]');
    if(e){e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));}};
  set('fio','Иванов Пётр Сергеевич'); set('birth','01.01.2018');
  set('period_start','19.07.2026'); set('period_end','31.07.2026');
  set('specialist','Иванова А.Б.'); set('sessions','10');
}"""


def shoot(pg, tag, mob):
    sfx = 'mob' if mob else 'desk'
    sph = pg.locator('.sph')
    # 1. верх шага 1 — новая подсказка про критерий поддержки
    pg.locator('.card h2', has_text='Актуальное состояние').first.scroll_into_view_if_needed()
    pg.wait_for_timeout(200)
    pg.screenshot(path=str(OUT / f'v250_stage1_hint_{sfx}.png'), full_page=False)
    # 2. сфера 2 с оценкой 3 — строка критерия под кнопками
    sph.nth(1).scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    sph.nth(1).locator('.peds label', has_text='3').first.click()
    pg.wait_for_timeout(400)
    sph.nth(1).screenshot(path=str(OUT / f'v250_sphere3_criteria_{sfx}.png'))
    # 3. сфера 1 с оценкой 5 (ресурс)
    sph.nth(0).locator('.peds label', has_text='5').first.click()
    pg.wait_for_timeout(400)
    sph.nth(0).scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    sph.nth(0).screenshot(path=str(OUT / f'v250_sphere5_resource_{sfx}.png'))
    # 4. S0 у сферы 3 — критерий сигнала
    sph.nth(2).locator('label.sig').first.click(force=True)
    pg.wait_for_timeout(400)
    sph.nth(2).scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    sph.nth(2).screenshot(path=str(OUT / f'v250_sphere_s0_{sfx}.png'))
    # 5. расшифровка с колонками «Критерий через поддержку» и «Соответствие в V1»
    d = pg.locator('details.help', has=pg.locator('summary', has_text='Расшифровка баллов')).first
    d.locator('summary').click(force=True)
    pg.wait_for_timeout(300)
    d.scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    d.screenshot(path=str(OUT / f'v250_help_table_{sfx}.png'))


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1440, 'height': 960})
    pg.goto(URL); pg.wait_for_timeout(700)
    pg.evaluate(FILL); pg.wait_for_timeout(300)
    shoot(pg, 'desk', False)
    pg.close()

    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                        is_mobile=True, has_touch=True)
    pm = ctx.new_page()
    pm.goto(URL); pm.wait_for_timeout(700)
    pm.evaluate(FILL); pm.wait_for_timeout(300)
    shoot(pm, 'mob', True)
    b.close()

print('готово:', sorted(x.name for x in OUT.glob('v250_*')))
