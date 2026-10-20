# -*- coding: utf-8 -*-
"""Скриншоты V1 1.3.0: подвкладки опросника, 9 сфер, цвета, FEDL2i, связи, банк 201.
Запуск из /home/user:  python3 work/shoot_v130.py"""
import pathlib
from playwright.sync_api import sync_playwright

URL = pathlib.Path('konstruktor/Конструктор_рекомендаций.html').resolve().as_uri()
OUT = pathlib.Path('work/shots'); OUT.mkdir(parents=True, exist_ok=True)

FILL = """()=>{
  const set=(k,v)=>{const e=document.querySelector('[data-h="'+k+'"]');
    if(e){e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));}};
  set('fio','Иванов Пётр Сергеевич'); set('birth','01.01.2018');
  set('period_start','19.07.2026'); set('period_end','31.07.2026');
  set('specialist','Иванова А.Б.'); set('sessions','10'); set('fill_date','29.09.2026');
}"""

with sync_playwright() as p:
    b = p.chromium.launch()

    # ---------------------------------------------------- десктоп
    pg = b.new_page(viewport={'width': 1440, 'height': 960})
    pg.goto(URL); pg.wait_for_timeout(600)
    pg.evaluate(FILL); pg.wait_for_timeout(300)

    # 1. Опросник: подвкладка «Оценка: 9 сфер», оценка сферы 2 -> цветные подсказки
    pg.click('nav.tabs button:has-text("2. Опросник")'); pg.wait_for_timeout(500)
    pg.screenshot(path=str(OUT / 'v130_survey_spheres_top_desk.png'), full_page=False)
    pg.locator('.mb.sph').nth(1).locator('.scale label', has_text='2 · справляется, но не всегда').click()
    pg.wait_for_timeout(600)
    pg.locator('.mb.sph').nth(1).screenshot(path=str(OUT / 'v130_sphere_reg_colors_desk.png'))
    pg.locator('.mb.sph').nth(0).locator('.scale label', has_text='2 · есть особенности').click()
    pg.wait_for_timeout(600)
    pg.locator('.mb.sph').nth(0).scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    pg.screenshot(path=str(OUT / 'v130_sphere_sens_mini_desk.png'), full_page=False)

    # модалка подбора с пулом сферы
    pg.locator('.mb.sph').nth(3).locator('button[data-pool]').click()
    pg.wait_for_timeout(500)
    pg.locator('#pickerOv').screenshot(path=str(OUT / 'v130_picker_pool_desk.png'))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

    # 2. Сенсорный профиль FEDL2i
    pg.click('button.svtab:has-text("Сенсорный профиль")'); pg.wait_for_timeout(600)
    pg.screenshot(path=str(OUT / 'v130_sens_tab_desk.png'), full_page=False)
    pg.select_option('[data-sens="A1"]', '(+1)'); pg.wait_for_timeout(400)
    pg.select_option('[data-sens="A3"]', '(-1)'); pg.wait_for_timeout(400)
    pg.fill('[data-sens="A8"]', 'смешанный профиль: поиск сильных ощущений при тактильной защите')
    pg.wait_for_timeout(500)
    pg.locator('#main .card', has=pg.get_by_text('Текст для документа · 1.')).first.screenshot(
        path=str(OUT / 'v130_sens_autocard_desk.png'))
    pg.locator('#main .card button[data-sensapply="SPH-SENS"]').first.click(); pg.wait_for_timeout(600)

    # 3. Подробно: DIR
    pg.click('button.svtab:has-text("Подробно: DIR")'); pg.wait_for_timeout(500)
    pg.screenshot(path=str(OUT / 'v130_survey_dir_desk.png'), full_page=False)

    # 4. Вопросы ИВ (в простом режиме)
    pg.click('button.svtab:has-text("Вопросы ИВ")'); pg.wait_for_timeout(500)
    pg.locator('#main details').first.locator('summary').click(); pg.wait_for_timeout(300)
    pg.screenshot(path=str(OUT / 'v130_survey_iv2_desk.png'), full_page=False)

    # 5. Актуальное состояние: 8 микротем, автотекст FEDL2i, связи фразы
    pg.click('nav.tabs button:has-text("3. Актуальное состояние")'); pg.wait_for_timeout(500)
    pg.screenshot(path=str(OUT / 'v130_as_top_desk.png'), full_page=False)
    pg.locator('.mb[data-micro="AS3soc"]').scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    pg.locator('.mb[data-micro="AS3soc"]').screenshot(path=str(OUT / 'v130_as_sens_auto_desk.png'))
    # добавим фразу с известными связями и покажем «Связи этой фразы»
    pg.locator('.mb[data-micro="AS2emo"] button[data-pick="MICRO:AS2emo"]').click()
    pg.wait_for_timeout(400)
    pg.locator('#pickerBody .prow', has_text='Склонен к избегающему поведению').first.locator('button').click(force=True)
    pg.wait_for_timeout(500)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
    assert pg.locator('#pickerOv').count() == 0, 'модалка не закрылась'
    lnk = pg.locator('.mb[data-micro="AS2emo"] details:has-text("Связи этой фразы")').last
    lnk.locator('summary').scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    lnk.locator('summary').click(force=True)
    pg.wait_for_timeout(300)
    pg.locator('.mb[data-micro="AS2emo"]').scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    pg.locator('.mb[data-micro="AS2emo"]').screenshot(path=str(OUT / 'v130_as_links_desk.png'))

    # 6. Цели: сводная карточка связей
    pg.click('nav.tabs button:has-text("4. Цели и приёмы")'); pg.wait_for_timeout(500)
    pg.locator('.card:has-text("Подсказка: цели, приёмы и рекомендации")').first.screenshot(
        path=str(OUT / 'v130_goals_linked_desk.png'))

    # 7. Банк фраз: 201 из 201
    pg.click('nav.tabs button:has-text("Банк фраз")'); pg.wait_for_timeout(500)
    pg.fill('#fText', 'праксис'); pg.wait_for_timeout(400)
    pg.screenshot(path=str(OUT / 'v130_bank_all_desk.png'), full_page=False)
    pg.fill('#fText', ''); pg.wait_for_timeout(300)

    # 8. Тёмная тема: подсказки сфер
    # NB: шаг 4 переключил UI.stab на «Вопросы ИВ» (сохраняется в localStorage) —
    # явно возвращаем подвкладку «Оценка: 9 сфер».
    pg.click('#btnTheme'); pg.wait_for_timeout(400)
    pg.click('nav.tabs button:has-text("2. Опросник")'); pg.wait_for_timeout(500)
    pg.click('button.svtab[data-stab="spheres"]'); pg.wait_for_timeout(500)
    assert pg.locator('.mb.sph').count() >= 9, 'сферы не отрисовались (desktop dark)'
    pg.locator('.mb.sph').nth(1).scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    pg.locator('.mb.sph').nth(1).screenshot(path=str(OUT / 'v130_sphere_reg_dark_desk.png'))
    pg.click('#btnTheme'); pg.wait_for_timeout(300)
    pg.close()

    # ---------------------------------------------------- мобайл
    pg = b.new_page(viewport={'width': 390, 'height': 844})
    pg.goto(URL); pg.wait_for_timeout(600)
    pg.evaluate(FILL); pg.wait_for_timeout(300)
    pg.click('nav.tabs button:has-text("2. Опросник")'); pg.wait_for_timeout(500)
    # localStorage общий с десктопной страницей (тот же контекст браузера):
    # последняя подвкладка могла остаться «Вопросы ИВ» — возвращаем «Оценка: 9 сфер».
    pg.click('button.svtab[data-stab="spheres"]'); pg.wait_for_timeout(500)
    print('mobile .mb.sph count:', pg.locator('.mb.sph').count())
    assert pg.locator('.mb.sph').count() >= 9, 'сферы не отрисовались (mobile)'
    pg.locator('.mb.sph').nth(1).locator('.scale label', has_text='2 · справляется, но не всегда').click()
    pg.wait_for_timeout(600)
    pg.locator('.mb.sph').nth(1).screenshot(path=str(OUT / 'v130_sphere_reg_mob.png'))
    pg.click('button.svtab:has-text("Сенсорный профиль")'); pg.wait_for_timeout(500)
    pg.screenshot(path=str(OUT / 'v130_sens_tab_mob.png'), full_page=False)
    pg.click('nav.tabs button:has-text("3. Актуальное состояние")'); pg.wait_for_timeout(500)
    pg.screenshot(path=str(OUT / 'v130_as_mob.png'), full_page=False)
    pg.close()

    b.close()
print('скриншоты v130_* сохранены в', OUT)
