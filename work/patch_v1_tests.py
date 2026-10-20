# -*- coding: utf-8 -*-
"""Тесты на пакет «V1 1.2.0» (перенос наработок v2): _harness.js + test_app.js + test_browser.py."""
import io, os, sys

def patch(path, reps):
    with io.open(path, encoding='utf-8') as f:
        s = f.read()
    o = s
    for old, new, label in reps:
        n = s.count(old)
        if n != 1:
            print('!! %s: якорь «%s» найден %d раз' % (path, label, n)); sys.exit(1)
        s = s.replace(old, new, 1)
        print('   ok  %s → %s' % (os.path.basename(path), label))
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(s)
    return len(o), len(s)


# ------------------------------------------------------------------ 1. _harness.js
patch(os.path.join('konstruktor', 'tools', '_harness.js'), [(
"""  isAdded, removeFrom, targetName, addBtn,""",
"""  isAdded, removeFrom, targetName, addBtn,
  blockName, microName, v1PhraseCount, v2OnlyMicroNames, syncHdrChips,""",
'экспорт новых функций V1')])


# ------------------------------------------------------------------ 2. test_app.js
NEW_SECTION = """
console.log('\\n== 1b. Перенос из v2: человекочитаемые коды и область видимости V1 (запись 46) ==');
ok(g.blockName('AS') === 'Актуальное состояние', 'blockName(AS) = ' + g.blockName('AS'));
ok(g.blockName('REC') === 'Рекомендации', 'blockName(REC) = ' + g.blockName('REC'));
ok(g.microName('AS5play') === 'Игра', 'microName(AS5play) = ' + g.microName('AS5play'));
ok(g.microName('RC4play').length > 0 && g.microName('RC4play') !== 'RC4play',
   'microName(RC4play) = ' + g.microName('RC4play'));
ok(g.microName('НЕТ-ТАКОГО') === 'НЕТ-ТАКОГО', 'неизвестный код возвращается как есть');
const v2Only = g.BANK.phrases.filter(p => p.block === 'AS' && (g.BANK.microIndex[p.micro] || {}).v2only).length;
ok(g.v1PhraseCount() === g.BANK.phrases.length - v2Only,
   'в V1 доступно фраз: ' + g.v1PhraseCount() + ' из ' + g.BANK.phrases.length + ' (только v2: ' + v2Only + ')');
ok(v2Only > 0, 'формулировки только для v2 в банке есть: ' + v2Only);
ok(/AS7prax/.test(g.v2OnlyMicroNames()) && /AS8vis/.test(g.v2OnlyMicroNames()),
   'пометка про микротемы версии 2: ' + g.v2OnlyMicroNames());
noThrow('syncHdrChips() не падает без DOM', () => g.syncHdrChips());
const bankSimple = g.vBank();
ok(bankSimple.indexOf('bankNote') >= 0, 'на вкладке банка есть строка-пояснение #bankNote');
ok(/Найдено/.test(bankSimple), 'в простом режиме банка виден счётчик «Найдено»');

"""
patch(os.path.join('konstruktor', 'tools', 'test_app.js'), [
("""ok(g.BANK.phrases.filter(p => p.block === 'AS' && p.micro === 'AS7prax').length >= 6,
   'формулировки праксиса (AS7prax) в банке есть');
""",
 """ok(g.BANK.phrases.filter(p => p.block === 'AS' && p.micro === 'AS7prax').length >= 6,
   'формулировки праксиса (AS7prax) в банке есть');
""" + NEW_SECTION, 'секция 1b'),
("""g.ensureMicro();
const emptyDoc = noThrow('buildDoc() на пустом документе', () => g.buildDoc());""",
 """g.ensureMicro();
ok(!g.S.micro.AS7prax && !g.S.micro.AS8vis,
   'ensureMicro() не создаёт в черновике V1 микротемы версии 2 (AS7prax/AS8vis)');
ok(Object.keys(g.S.micro).length === 6,
   'микротем актуального состояния в черновике V1: ' + Object.keys(g.S.micro).length);
const emptyDoc = noThrow('buildDoc() на пустом документе', () => g.buildDoc());""",
 'ensureMicro в секции 10'),
])


# ------------------------------------------------------------------ 3. test_browser.py
CHIPS = """
        # --- шапка в два ряда: чипы ФИО / период / специалист (перенос из v2, запись 44)
        assert page.locator('header.top .hdrrow').count() == 1, 'первый ряд шапки не собран'
        assert page.locator('header.top .hdrchips').count() == 1, 'строка чипов шапки отсутствует'
        assert page.locator('.hdrchips #saveinfo').count() == 1, \\
            'индикатор автосохранения не перенесён в строку чипов'
        chip_fio = page.inner_text('#hdrFio').strip()
        chip_period = page.inner_text('#hdrPeriod').strip()
        chip_spec = page.inner_text('#hdrSpec').strip()
        print('чипы шапки:', chip_fio, '|', chip_period, '|', chip_spec)
        assert 'Иванов' in chip_fio, 'в чипе нет ФИО загруженного проекта: ' + chip_fio
        assert chip_period.startswith('период:') and '—' in chip_period, 'чип периода: ' + chip_period
        assert chip_spec.startswith('специалист:'), 'чип специалиста: ' + chip_spec
        ver = page.inner_text('#ver').strip()
        print('версия в шапке:', ver)
        assert ver.startswith('1.2.0') and 'банк данных' in ver, 'версия приложения не показана: ' + ver
        # чипы обновляются на каждый ввод
        page.fill('[data-h="fio"]', 'Чипова Анна Петровна')
        page.wait_for_timeout(250)
        assert 'Чипова' in page.inner_text('#hdrFio'), 'чип ФИО не обновляется при вводе'
        page.fill('[data-h="fio"]', fio)
        page.wait_for_timeout(250)
        assert 'Иванов' in page.inner_text('#hdrFio'), 'чип ФИО не вернулся к значению проекта'
        page.screenshot(path=os.path.join(SHOTS, '01b_header_chips.png'), full_page=False)
"""

BANK = """
        # --- V1 не показывает формулировки микротем версии 2 (AS7prax, AS8vis)
        note = page.inner_text('#bankNote').strip()
        print('пометка банка:', note[:120])
        assert 'версия2' in note or 'версии 2' in note, 'нет пометки о формулировках версии 2: ' + note
        own = json.load(open(os.path.join(ROOT, 'data', 'phrases.json'), encoding='utf-8'))
        v2micro = {m['id'] for m in own['microblocks'] if m.get('v2only')}
        expect_own = len([p for p in own['phrases']
                          if not (p['block'] == 'AS' and p.get('micro') in v2micro)])
        shown = page.input_value('#bankCountSimple')
        print('счётчик банка (простой режим):', shown, '| ожидается «%d из %d»' % (expect_own, expect_own))
        assert shown == '%d из %d' % (expect_own, expect_own), 'счётчик банка: ' + shown
        assert rows_all == expect_own, 'в таблице банка V1 строк %d, ожидается %d' % (rows_all, expect_own)
        assert 'AS7prax' not in page.inner_text('#bankTable'), 'в таблице банка V1 виден код AS7prax'

        # --- продвинутый режим: названия блоков/микроблоков вместе с кодами (перенос из v2, запись 45)
        page.click('#btnMode')
        page.wait_for_timeout(500)
        blk_opts = page.locator('#fBlock option').all_inner_texts()
        mic_opts = page.locator('#fMicro option').all_inner_texts()
        print('фильтр «Блок»:', ' | '.join(blk_opts[:3]), '…')
        assert any('Актуальное состояние · AS' == o.strip() for o in blk_opts), \\
            'в фильтре «Блок» нет связки «название · код»: ' + str(blk_opts[:3])
        assert any('AS5play' in o for o in mic_opts), 'в фильтре «Микроблок» нет кода AS5play'
        assert not any('AS7prax' in o or 'AS8vis' in o for o in mic_opts), \\
            'в фильтре «Микроблок» остались микротемы версии 2'
        assert page.inner_text('#bankCount').strip() == str(expect_own), \\
            'счётчик «всего фраз» в продвинутом режиме: ' + page.inner_text('#bankCount')
        page.screenshot(path=os.path.join(SHOTS, '07c_bank_full_mode.png'), full_page=False)
        page.click('#btnMode')   # обратно в простой режим
        page.wait_for_timeout(400)
"""

PICKER = """
        # --- модалка подбора фраз: счётчик «Найдено» и легенда кодов (перенос из v2, запись 45)
        page.click('nav.tabs button:has-text("3. Актуальное состояние")')
        page.wait_for_timeout(400)
        page.locator('[data-pick^="MICRO:"]').first.click()
        page.wait_for_timeout(400)
        pick = page.inner_text('#pickerBody')
        print('модалка подбора, первые строки:', pick.split('\\n')[0][:90])
        assert pick.strip().startswith('Найдено:'), 'в модалке нет счётчика «Найдено»'
        assert 'AS5play-S2-07' in pick, 'в модалке нет легенды кодов'
        page.screenshot(path=os.path.join(SHOTS, '03b_picker_legend.png'), full_page=False)
        page.keyboard.press('Escape')
        page.wait_for_timeout(250)
        assert page.locator('#pickerOv').count() == 0, 'модалка не закрылась по Escape'
"""

patch(os.path.join('konstruktor', 'tools', 'test_browser.py'), [
("""        assert 'Иванов' in fio, 'проект не загрузился'
""",
 """        assert 'Иванов' in fio, 'проект не загрузился'
""" + CHIPS, 'чипы шапки'),
("""        assert rows_all > 150 and 0 < rows_f < rows_all
        page.screenshot(path=os.path.join(SHOTS, '07b_bank_filter.png'), full_page=False)
""",
 """        assert rows_all > 150 and 0 < rows_f < rows_all
        page.screenshot(path=os.path.join(SHOTS, '07b_bank_filter.png'), full_page=False)
        page.fill('#fText', '')
        page.wait_for_timeout(300)
        rows_all = page.locator('#bankTable tr').count() - 1
""" + BANK, 'банк V1 без микротем v2'),
("""        # --- скачивание .docx""", PICKER + """
        # --- скачивание .docx""", 'модалка подбора фраз'),
])

print('\nГотово.')
