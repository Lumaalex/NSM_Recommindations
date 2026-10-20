# -*- coding: utf-8 -*-
import pathlib, sys
from playwright.sync_api import sync_playwright
URL = pathlib.Path('konstruktor/fork_v2/Конструктор_ИВ_версия2.html').resolve().as_uri()
OUT = pathlib.Path('work/shots'); OUT.mkdir(parents=True, exist_ok=True)
TAG = sys.argv[1] if len(sys.argv) > 1 else 'before'
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp in (('desk', {'width':1440,'height':900}), ('mob', {'width':390,'height':844})):
        pg = b.new_page(viewport=vp)
        pg.goto(URL); pg.wait_for_timeout(500)
        pg.evaluate("()=>{const f=document.querySelector('[data-h=\"fio\"]');if(f){f.value='Иванов Пётр';f.dispatchEvent(new Event('input',{bubbles:true}));}const d=document.querySelector('[data-h=\"fill_date\"]');if(d){d.value='29.09.2026';d.dispatchEvent(new Event('input',{bubbles:true}));}}")
        pg.wait_for_timeout(300)
        pg.locator('header.top').screenshot(path=str(OUT/f'hdr_{TAG}_{name}.png'))
        pg.close()
    b.close()
print('ok')
