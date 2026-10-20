# -*- coding: utf-8 -*-
"""Скриншоты пакета 2.6.0 форка v2: чип специалиста в шапке + шаг 9 «Банк фраз».
Запуск из /home/user:  python3 work/shoot_v260.py"""
import pathlib
from playwright.sync_api import sync_playwright

URL = pathlib.Path('konstruktor/fork_v2/Конструктор_ИВ_версия2.html').resolve().as_uri()
OUT = pathlib.Path('work/shots')
OUT.mkdir(parents=True, exist_ok=True)

FILL = """()=>{
  const set=(k,v)=>{const e=document.querySelector('[data-h="'+k+'"]');
    if(e){e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));}};
  set('fio','Иванов Пётр Сергеевич'); set('birth','01.01.2018');
  set('fill_date','12.10.2026');
  set('period_start','19.07.2026'); set('period_end','31.07.2026');
  set('specialist','Иванова А.Б.'); set('sessions','10');
}"""


def shoot(pg, mob):
    sfx = 'mob' if mob else 'desk'
    dlg = ['']                                   # что отвечать в prompt (ID новой фразы)

    def on_dialog(d):
        try:
            d.accept(dlg[0])
        except Exception:
            pass

    pg.on('dialog', on_dialog)
    pg.evaluate(FILL)
    pg.wait_for_timeout(300)

    # 1. шапка: три чипа (ФИО · дата заполнения · специалист и занятий)
    pg.locator('header.top').screenshot(path=str(OUT / f'v260_01_hdr_chips_{sfx}.png'))

    # 2. шаг 1 без карточки-дубля банка
    pg.locator('.card h2', has_text='Актуальное состояние').first.scroll_into_view_if_needed()
    pg.wait_for_timeout(250)
    pg.screenshot(path=str(OUT / f'v260_02_step1_no_dup_{sfx}.png'), full_page=False)

    # 3. шаг 9 «Банк фраз»: таблица всего банка
    pg.click('#btnBank')
    pg.wait_for_timeout(500)
    pg.screenshot(path=str(OUT / f'v260_03_step9_table_{sfx}.png'), full_page=False)

    # 4. фильтры: блок AS + поиск «сюжет»
    pg.select_option('#f9Block', 'AS')
    pg.wait_for_timeout(300)
    pg.fill('#f9Text', 'сюжет')
    pg.wait_for_timeout(400)
    pg.screenshot(path=str(OUT / f'v260_04_step9_filters_{sfx}.png'), full_page=False)
    shown = pg.text_content('#bank9Rows')
    print('   строк после фильтра: %s' % shown)

    # 5. своя фраза: «+ Новая фраза» и правка в строке
    pg.fill('#f9Text', '')
    pg.select_option('#f9Block', '')
    pg.wait_for_timeout(300)
    dlg[0] = 'AS5play-S2-DEMO'
    pg.click('#bank9Add')
    pg.wait_for_timeout(500)
    pg.fill('textarea[data-b9id="AS5play-S2-DEMO"]',
            'Своя формулировка: разворачивает сюжет игры после показа взрослым.')
    pg.fill('input[data-b9f="tags"][data-b9id="AS5play-S2-DEMO"]', 'сюжет; демонстрация')
    pg.wait_for_timeout(300)
    pg.fill('#f9Text', 'Своя формулировка')
    pg.wait_for_timeout(400)
    pg.screenshot(path=str(OUT / f'v260_05_step9_own_phrase_{sfx}.png'), full_page=False)

    # 6. «В документ» — фраза уходит в свой блок, шаг не меняется
    pg.locator('tr:has(input[data-b9id="AS5play-S2-DEMO"]) [data-tg]').first.click()
    pg.wait_for_timeout(500)
    pg.locator('tr:has(input[data-b9id="AS5play-S2-DEMO"])').first.scroll_into_view_if_needed()
    pg.wait_for_timeout(250)
    pg.screenshot(path=str(OUT / f'v260_06_step9_to_doc_{sfx}.png'), full_page=False)

    # 7. справочники банка (внизу шага 9)
    pg.fill('#f9Text', '')
    pg.wait_for_timeout(300)
    pg.locator('.card h2', has_text='Справочники банка').scroll_into_view_if_needed()
    pg.wait_for_timeout(300)
    pg.screenshot(path=str(OUT / f'v260_07_step9_refs_{sfx}.png'), full_page=False)

    # 8. своя фраза видна в подборе на шаге 1
    pg.click('.steps button:has-text("1. Актуальное состояние")')
    pg.wait_for_timeout(400)
    idx = pg.evaluate("() => window.V2API.BANK.spheres.findIndex("
                      "s => window.V2API.sphereAsPool(s.id).some(p => p.micro === 'AS5play'))")
    pg.locator('.sph').nth(idx).locator('[data-bank^="AS|"]').first.click()
    pg.wait_for_timeout(400)
    pg.fill('#pkQ', 'Своя формулировка')
    pg.wait_for_timeout(400)
    pg.screenshot(path=str(OUT / f'v260_08_picker_own_{sfx}.png'), full_page=False)
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(300)

    # 9. возврат встроенного банка
    pg.click('#btnBank')
    pg.wait_for_timeout(400)
    dlg[0] = ''
    pg.click('#bank9Reset')
    pg.wait_for_timeout(600)
    n = pg.evaluate("() => window.V2API.BANK.phrases.length")
    print('   после возврата встроенного банка фраз: %d' % n)
    pg.screenshot(path=str(OUT / f'v260_09_step9_reset_{sfx}.png'), full_page=False)


def main():
    with sync_playwright() as pw:
        for label, vp, mob in [('десктоп 1280', {'width': 1280, 'height': 950}, False),
                               ('iPhone 390x844', {'width': 390, 'height': 844}, True)]:
            print('=== %s ===' % label)
            b = pw.chromium.launch()
            ctx = b.new_context(viewport=vp, is_mobile=mob, has_touch=mob, device_scale_factor=2)
            pg = ctx.new_page()
            pg.goto(URL)
            pg.wait_for_timeout(700)
            shoot(pg, mob)
            b.close()
    print('Скриншоты: %s/v260_*' % OUT)


if __name__ == '__main__':
    main()
