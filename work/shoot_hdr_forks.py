# -*- coding: utf-8 -*-
"""Скриншоты шапок V1 и V2: метка форка + версия (чтобы скачанный файл опознавался).
Запуск из /home/user:  python3 work/shoot_hdr_forks.py"""
import pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path('work/shots')
OUT.mkdir(parents=True, exist_ok=True)
TARGETS = (
    ('v1', pathlib.Path('konstruktor/Конструктор_рекомендаций.html').resolve().as_uri()),
    ('v2', pathlib.Path('konstruktor/fork_v2/Конструктор_ИВ_версия2.html').resolve().as_uri()),
)
with sync_playwright() as p:
    b = p.chromium.launch()
    for tag, url in TARGETS:
        for name, vp in (('desk', {'width': 1440, 'height': 900}),
                         ('mob', {'width': 390, 'height': 844})):
            pg = b.new_page(viewport=vp)
            pg.goto(url)
            pg.wait_for_timeout(600)
            print(tag, name, '| title:', pg.title(),
                  '| sub:', (pg.locator('header.top .sub').first.text_content() or '').strip()[:110])
            pg.locator('header.top').screenshot(path=str(OUT / f'hdrfork_{tag}_{name}.png'))
            pg.close()
    b.close()
print('ok ->', OUT)
