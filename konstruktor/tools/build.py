# -*- coding: utf-8 -*-
"""
СБОРКА КОМПЛЕКТА «КОНСТРУКТОР РЕКОМЕНДАЦИЙ»
===========================================
Запуск:   python tools/build.py
Источник: tools/source_data.py  (или Банк_фраз.xlsx — см. tools/excel_to_json.py)

Создаёт:
  data/phrases.json
  Конструктор_рекомендаций.html
  Банк_фраз.xlsx
  Шаблон_заключения_ИВ.docx
  Памятка_специалиста.docx
"""
import json, os, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import source_data as SD

OUT_HTML   = os.path.join(ROOT, 'Конструктор_рекомендаций.html')
OUT_XLSX   = os.path.join(ROOT, 'Банк_фраз.xlsx')
OUT_JSON   = os.path.join(ROOT, 'data', 'phrases.json')
OUT_V2     = os.path.join(ROOT, 'fork_v2', 'Конструктор_ИВ_версия2.html')
OUT_TPL    = os.path.join(ROOT, 'Шаблон_заключения_ИВ.docx')
OUT_MEMO   = os.path.join(ROOT, 'Памятка_специалиста.docx')
TEMPLATE   = os.path.join(ROOT, 'app', 'template.html')


# --------------------------------------------------------------------------- 1. JSON
def build_json(data):
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return OUT_JSON


# --------------------------------------------------------------------------- 2. HTML
def build_html(data):
    with open(TEMPLATE, encoding='utf-8') as f:
        tpl = f.read()
    with open(os.path.join(ROOT, 'app', 'style.css'), encoding='utf-8') as f:
        css = f.read()
    with open(os.path.join(ROOT, 'app', 'docx_lib.js'), encoding='utf-8') as f:
        docxlib = f.read()
    if '/*__DOCX_LIB__*/' not in tpl:
        raise SystemExit('В шаблоне нет маркера /*__DOCX_LIB__*/')
    tpl = tpl.replace('/*__DOCX_LIB__*/', docxlib.strip())
    if '/*__CSS__*/' not in tpl:
        raise SystemExit('В app/template.html не найден маркер /*__CSS__*/')
    tpl = tpl.replace('/*__CSS__*/', css.strip())
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    if '/*__DATA__*/' not in tpl:
        raise SystemExit('В app/template.html не найден маркер /*__DATA__*/')
    html = tpl.replace('/*__DATA__*/', payload)
    with open(OUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    return OUT_HTML


# --------------------------------------------------------------------------- 3. EXCEL
def build_html_v2(data):
    tpl_path = os.path.join(ROOT, 'app', 'template_v2.html')
    with open(tpl_path, encoding='utf-8') as f:
        tpl = f.read()
    with open(os.path.join(ROOT, 'app', 'style.css'), encoding='utf-8') as f:
        css = f.read()
    with open(os.path.join(ROOT, 'app', 'docx_lib.js'), encoding='utf-8') as f:
        docxlib = f.read()
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    tpl = tpl.replace('/*__CSS__*/', css.strip()).replace('/*__DOCX_LIB__*/', docxlib.strip())
    tpl = tpl.replace('/*__DATA__*/', payload)
    with open(OUT_V2, 'w', encoding='utf-8') as f:
        f.write(tpl)
    return OUT_V2


def build_excel(data):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = openpyxl.Workbook()
    HDR_FILL = PatternFill('solid', fgColor='1F3B54')
    HDR_FONT = Font(name='Times New Roman', size=10, bold=True, color='FFFFFF')
    BODY_FONT = Font(name='Times New Roman', size=10)
    WRAP = Alignment(wrap_text=True, vertical='top')
    THIN = Border(*[Side(style='thin', color='BFBFBF')] * 4)

    def sheet(name, headers, rows, widths, freeze='A2', title=None):
        ws = wb.create_sheet(name)
        r0 = 1
        if title:
            ws.cell(1, 1, title).font = Font(name='Times New Roman', size=12, bold=True)
            r0 = 3
        for j, h in enumerate(headers, 1):
            c = ws.cell(r0, j, h)
            c.fill, c.font, c.alignment, c.border = HDR_FILL, HDR_FONT, WRAP, THIN
        for i, row in enumerate(rows, r0 + 1):
            for j, v in enumerate(row, 1):
                c = ws.cell(i, j, v)
                c.font, c.alignment, c.border = BODY_FONT, WRAP, THIN
        for j, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(j)].width = w
        ws.freeze_panes = ws.cell(r0 + 1, 1).coordinate
        if rows:
            ws.auto_filter.ref = f'A{r0}:{get_column_letter(len(headers))}{r0 + len(rows)}'
        return ws

    wb.remove(wb.active)

    # --- Инструкция
    ws = wb.create_sheet('Инструкция')
    ws.column_dimensions['A'].width = 118
    lines = [
        ('БАНК ФРАЗ КОНСТРУКТОРА РЕКОМЕНДАЦИЙ', True),
        ('Версия %s от %s' % (data['meta']['version'], data['meta']['updated']), False),
        ('', False),
        ('СТАНДАРТ ДОКУМЕНТА', True),
        (data['meta']['standard'], False),
        ('Верхнеуровневые блоки пропускать нельзя. Пропускать можно только отдельные формулировки внутри блока — '
         'вместо них ставится служебная отметка (лист «Служебные_фразы»).', False),
        ('', False),
        ('КАК ДОБАВИТЬ СВОЮ ФРАЗУ', True),
        ('1. Откройте лист «Фразы», допишите строку внизу.', False),
        ('2. ID — уникальный и понятный: AS5play-S2-07 = блок AS (актуальное состояние), '
         'микроблок AS5play (игра), статус S2 (иногда), порядковый номер 07.', False),
        ('3. Блок: AS / GOAL / METH / RES / NEXT / REC / LIT (см. лист «Блоки»).', False),
        ('4. Микроблок — код с буквенным хвостом, по которому видно тему: '
         'AS1sens интерес · AS2emo эмоции и регуляция · AS3soc сенсорика · AS4ini контакт/инициатива · '
         'AS5play игра · AS6com коммуникация · AS7prax праксис · AS8vis зрительно-пространственная; '
         'рекомендации: RC1home · RC2int · RC3sens · RC4play · RC5frustr · RC6peers (см. лист «Микроблоки»). '
         'Старые цифровые коды (AS1, RC1…) в прежних файлах при сборке переводятся в новые автоматически.', False),
        ('5. Статус: S3 стабильно / S2 иногда / S1 с поддержкой / S0 не проявляется / SN не проверялось.', False),
        ('6. «Требует примера» — Да, если формулировка является оценкой способности (для рекомендаций — Нет).', False),
        ('7. Колонки «Цели(ID)», «Приёмы(ID)», «Рекомендации(ID)» — связи через точку с запятой. '
         'Именно они дают цепочку «наблюдение → цель → приём → рекомендация» в конструкторе.', False),
        ('8. Сохраните файл и запустите  python tools/build.py  — HTML-конструктор и JSON пересоберутся.', False),
        ('   Альтернатива: выгрузите из конструктора CSV и замените им лист «Фразы» '
         '(или импортируйте CSV прямо в конструктор, вкладка «Банк фраз»).', False),
        ('', False),
        ('ПРАВИЛА НАПОЛНЕНИЯ', True),
        ('• Одна фраза = одна мысль.', False),
        ('• Формулировка наблюдаема: не «развивается», а «поддерживает цепочки контакта в несколько шагов».', False),
        ('• Для блока «Рекомендации» — язык родителя, без терминов (со-регуляция, коммуникативные циклы, праксис).', False),
        ('• Не дублируйте смысл разными словами: лучше одна точная фраза, чем три приблизительных.', False),
        ('', False),
        ('ЛИСТЫ ФАЙЛА', True),
        ('Фразы — мастер-банк формулировок по всем блокам документа.', False),
        ('Опросник_ключ — пункты DIR 1–6 и сенсорика со шкалой 0/1/2/3/N и ключом к фразам.', False),
        ('ИВ2_наблюдения — наблюдательные вопросы (свободный ответ) из опросника ИВ2.', False),
        ('Статусы — определения статусов способности и правило их постановки.', False),
        ('Поддержка — что считается поддержкой взрослого (слово / действие / аффект / условие).', False),
        ('Блоки, Микроблоки, Способности — структура документа.', False),
        ('Служебные_фразы — чем заменять отсутствующие данные.', False),
        ('Карта_связей — наблюдение → цель → приём → рекомендация.', False),
        ('Чек-лист — контроль перед выдачей документа.', False),
        ('Литература — утверждённый список центра (вставляется в документ целиком).', False),
        ('Направления — ИВ и заготовка под другие направления (ФЛТ и пр.).', False),
    ]
    for i, (txt, bold) in enumerate(lines, 1):
        c = ws.cell(i, 1, txt)
        c.font = Font(name='Times New Roman', size=12 if bold else 10, bold=bold)
        c.alignment = Alignment(wrap_text=True, vertical='top')

    # --- Фразы
    rows = []
    for p in data['phrases']:
        rows.append([p['id'], p.get('dir', 'IV'), p['block'], p.get('micro', ''), p.get('ability', ''),
                     p.get('status', ''), p['text'], p.get('source', ''),
                     'Да' if p.get('needs_example') else 'Нет', p.get('example_hint', ''),
                     ';'.join(p.get('links_goal', [])), ';'.join(p.get('links_meth', [])),
                     ';'.join(p.get('links_rec', [])), p.get('tags', ''),
                     'Да' if p.get('active', True) else 'Нет'])
    ws = sheet('Фразы',
               ['ID', 'Направление', 'Блок', 'Микроблок', 'Способность', 'Статус', 'Текст формулировки',
                'Источник', 'Требует примера', 'Подсказка: какой пример нужен',
                'Цели(ID)', 'Приёмы(ID)', 'Рекомендации(ID)', 'Теги/домен', 'Активна'],
               rows, [13, 11, 8, 10, 13, 10, 78, 10, 9, 42, 14, 14, 16, 22, 8])
    dv = DataValidation(type='list', formula1='"AS,GOAL,METH,RES,NEXT,REC,LIT"', allow_blank=True)
    ws.add_data_validation(dv); dv.add(f'C4:C{3 + len(rows) + 200}')
    dv2 = DataValidation(type='list', formula1='"S3,S2,S1,S0,SN"', allow_blank=True)
    ws.add_data_validation(dv2); dv2.add(f'F4:F{3 + len(rows) + 200}')

    # --- Опросник с ключом
    rows = []
    for q in data['questionnaire']:
        k = q.get('key') or {}
        def fmt(x):
            v = k.get(x) or {}
            parts = []
            for kk in ('as', 'goal', 'meth', 'rec', 'res', 'nxt', 'svc'):
                if v.get(kk):
                    parts.append(kk + ': ' + ';'.join(v[kk]))
            return ' | '.join(parts)
        rows.append([q['id'], q.get('source', ''), q.get('stage', ''), q.get('domain', ''), q.get('micro', ''),
                     q['text'], '0/1/2/3/N', fmt(3), fmt(2), fmt(1), fmt(0), fmt('N')])
    sheet('Опросник_ключ',
          ['ID', 'Источник', 'Стадия DIR', 'Домен', 'Микроблок', 'Пункт опросника', 'Шкала',
           'Ключ: 3 (стабильно)', 'Ключ: 2 (иногда)', 'Ключ: 1 (с поддержкой)', 'Ключ: 0 (не проявляется)',
           'Ключ: N (не проверялось)'],
          rows, [10, 12, 10, 22, 10, 70, 11, 40, 40, 40, 40, 30])

    # --- Ядро опросника (экспресс-режим)
    rows = []
    for q in data.get('survey_core', []):
        k = q.get('key') or {}
        def fmtc(x):
            v = k.get(x) or {}
            parts = []
            for kk in ('as', 'goal', 'meth', 'rec', 'res', 'nxt', 'svc'):
                if v.get(kk):
                    parts.append(kk + ': ' + ';'.join(v[kk]))
            return ' | '.join(parts)
        rows.append([q['id'], q.get('micro', ''), q.get('domain', ''), q['text'],
                     fmtc(3), fmtc(2), fmtc(1), fmtc(0), fmtc('N')])
    sheet('Опросник_ядро',
          ['ID', 'Микроблок', 'Область', 'Оценка (вопрос эксперта)',
           'Ключ: 3 (стабильно)', 'Ключ: 2 (иногда)', 'Ключ: 1 (с поддержкой)',
           'Ключ: 0 (не проявляется)', 'Ключ: N (не проверялось)'],
          rows, [8, 10, 22, 62, 40, 40, 40, 40, 30])

    # --- ИВ2
    rows = [[q['id'], q['group'], q['text'], ''] for q in data['iv2_questions']]
    sheet('ИВ2_наблюдения', ['ID', 'Раздел', 'Вопрос', 'Наблюдение (заполняет специалист)'],
          rows, [10, 34, 86, 60])

    # --- Статусы
    rows = [[s['code'], s['name'], s['definition'], s['rule'], s['goes_to']] for s in data['statuses']]
    sheet('Статусы', ['Код', 'Название', 'Когда ставим', 'Правило', 'Куда попадает'],
          rows, [8, 20, 80, 70, 60])

    # --- Поддержка
    rows = [[s['name'], s['examples']] for s in data['support_types']]
    ws = sheet('Поддержка', ['Тип поддержки', 'Примеры'], rows, [18, 110])
    ws.cell(len(rows) + 3, 1, 'Если без одного из этих компонентов ребёнок способность не проявил — это S1, а не S3.')\
        .font = Font(name='Times New Roman', size=10, bold=True, color='B23B3B')

    # --- Блоки / микроблоки / способности
    rows = [[b['id'], b['order'], b['name'], 'Да' if b['mandatory'] else 'Нет', b['hint']] for b in data['blocks']]
    sheet('Блоки', ['ID', '№', 'Название блока', 'Обязателен', 'Что пишем'], rows, [8, 5, 40, 11, 110])
    rows = [[m['id'], m['block'], m['order'], m['name'], 'Да' if m['mandatory'] else 'Нет',
             m.get('service') or '', 'Да' if m.get('v2only') else 'Нет'] for m in data['microblocks']]
    sheet('Микроблоки', ['ID', 'Блок', '№', 'Название микротемы', 'Обязателен', 'Служебная фраза (ID)',
                         'Только v2'],
          rows, [8, 8, 5, 62, 11, 16, 9])
    rows = [[a['id'], a['name'], a['micro'], a['stage']] for a in data['abilities']]
    sheet('Способности', ['ID', 'Способность', 'Микроблок', 'Стадия DIR'], rows, [14, 52, 10, 10])

    # --- Служебные фразы
    rows = [[s['id'], s.get('microblock') or '—', s['situation'], s['text']] for s in data['service_phrases']]
    sheet('Служебные_фразы', ['ID', 'Микроблок', 'Ситуация', 'Формулировка'], rows, [12, 10, 34, 110])

    # --- Карта связей
    rows = [[r['marker'], r['stable'], r['sometimes'], r['goal'], r['method'], r['rec']] for r in data['link_map']]
    sheet('Карта_связей', ['Маркер / способность', 'Если стабильно', 'Если иногда', 'Цель', 'Приём', 'Рекомендация'],
          rows, [40, 30, 30, 42, 42, 52])

    # --- Чек-лист
    rows = [[c['id'], c['text'], {'block': 'обязательно', 'warn': 'желательно'}.get(c['severity'], c['severity'])]
            for c in data['checklist']]
    sheet('Чек-лист', ['№', 'Проверка перед выдачей документа', 'Важность'], rows, [6, 116, 12])

    # --- Литература
    rows = [[i + 1, t] for i, t in enumerate(data['literature'])]
    sheet('Литература', ['№', 'Издание'], rows, [5, 120])

    # --- Форк v2: сферы, шкала МКФ, ключ сфер, правила литературы
    rows = [[x['id'], x['order'], x['name'], x['short'], x['micro'],
             ';'.join(x.get('sens_blocks') or []), ';'.join(x.get('bank_as') or [])]
            for x in data.get('spheres', [])]
    sheet('Сферы', ['ID', '№', 'Название сферы', 'Коротко', 'Микроблок документа',
                    'Блоки FEDL2i', 'Пул фраз банка (ID)'], rows, [12, 5, 52, 26, 12, 14, 60])
    rows = [[x['ped'], x['mkf'], x.get('code', ''), x['name'], x['text'],
             x.get('support', ''), x.get('v1', '')] for x in data.get('ped_scale', [])]
    sheet('Шкала_МКФ', ['Оценка педагога', 'Балл МКФ', 'Код', 'Название',
                        'Что означает (педагогическим языком)',
                        'Критерий через поддержку (язык V1)', 'Соответствие в V1'],
          rows, [14, 10, 8, 30, 90, 90, 40])
    rows = [[i + 1, r] for i, r in enumerate(data.get('ped_reasons', []))]
    sheet('Причины_S0', ['№', 'Причина невозможности оценки'], rows, [5, 60])
    rows = [[k, sc['name'], ' | '.join(sc['options']), sc['legend']]
            for k, sc in sorted(data.get('sens_scales', {}).items())]
    sheet('Сенсорный_шкалы', ['Код шкалы', 'Название', 'Варианты (через | )', 'Легенда'], rows, [12, 22, 46, 80])
    rows = [[b['title'], it['id'], it['name'], it['scale'], b.get('note', '')]
            for b in data.get('sens_fedl', []) for it in b['items']]
    sheet('Сенсорный_опросник', ['Блок', 'ID пункта', 'Пункт', 'Шкала', 'Примечание к блоку'],
          rows, [40, 10, 74, 10, 60])
    rows = [[x['id'], x['name'], x['text'], x.get('svc', ''), x.get('v1', '')]
            for x in data.get('ped_signals', [])]
    sheet('Сигнальные_отметки', ['ID', 'Название', 'Значение', 'Служебная фраза (ID)',
                                 'Соответствие в V1'], rows, [14, 26, 90, 16, 26])
    rows = []
    for sid, keys in (data.get('sphere_keys') or {}).items():
        for ped in [5, 4, 3, 2, 1, 'SIG-STRESS', 'SIG-NOINFO']:
            k = keys.get(ped) or keys.get(str(ped))
            if not k:
                continue
            rows.append([sid, ped, ';'.join(k.get('as', [])), ';'.join(k.get('goal', [])),
                         ';'.join(k.get('meth', [])), ';'.join(k.get('rec', [])), ';'.join(k.get('svc', []))])
    sheet('Ключ_сфер', ['Сфера(ID)', 'Оценка', 'Актуальное(ID)', 'Цели(ID)', 'Приёмы(ID)',
                        'Рекомендации(ID)', 'Служебные(ID)'], rows, [12, 12, 26, 22, 22, 24, 16])
    rows = [[sid, ';'.join(subs)] for sid, subs in (data.get('lit_rules') or {}).items()]
    sheet('Литература_правила', ['Сфера(ID)', 'Подстроки названий из списка «Литература»'], rows, [12, 90])

    # --- Направления
    rows = [[d['id'], d['name'], d['short'], d['subject_default'], 'Да' if d['active'] else 'Нет', d['note']]
            for d in data['directions']]
    sheet('Направления', ['ID', 'Название', 'Коротко', 'Термин по умолчанию', 'Наполнено', 'Примечание'],
          rows, [8, 36, 8, 18, 11, 90])

    wb.save(OUT_XLSX)
    return OUT_XLSX


# --------------------------------------------------------------------------- 4. WORD
def _setup_doc(document):
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    st = document.styles['Normal']
    st.font.name = 'Times New Roman'
    st.font.size = Pt(12)
    try:
        st.element.rPr.rFonts.set(
            __import__('docx').oxml.ns.qn('w:eastAsia'), 'Times New Roman')
    except Exception:
        pass
    pf = st.paragraph_format
    pf.space_after = Pt(8)
    pf.line_spacing = 1.08
    sec = document.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
    sec.left_margin, sec.right_margin = Cm(3.0), Cm(1.5)
    sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(2.0)
    return document


def _para(document, text, bold=False, italic=False, size=12, align=None, color=None, after=8):
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    p = document.add_paragraph()
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(size)
    r.bold, r.italic = bold, italic
    if color:
        r.font.color.rgb = RGBColor(*color)
    p.paragraph_format.space_after = Pt(after)
    if align == 'center':
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == 'just':
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return p


def build_template_docx(data):
    import docx
    from docx.shared import Pt, Cm
    d = docx.Document()
    _setup_doc(d)
    _para(d, 'Индивидуальные рекомендации по направлению «Игровое взаимодействие»', bold=True, align='center', after=12)

    tbl = d.add_table(rows=0, cols=2)
    tbl.style = 'Table Grid'
    for label in ['ФИО:', 'Дата рождения:', 'Дата начала периода реабилитации:',
                  'Дата окончания периода реабилитации:', 'Специалист:', 'Количество занятий:']:
        row = tbl.add_row().cells
        row[0].text, row[1].text = label, ''
        for c in row:
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.name = 'Times New Roman'; r.font.size = Pt(12)
    tbl.columns[0].width = Cm(7.5)
    _para(d, '', after=6)

    hints = {
        'AS': 'Только наблюдаемые факты. Без целей и без «необходимо». Каждая значимая формулировка имеет статус '
              '(S3/S2/S1/S0/SN) и пример с занятия. Все 6 микротем обязательны.',
        'GOAL': 'Цели из статусов S2 / S1 / S0 / SN. Для S3 — цель расширения или переноса в новые ситуации.',
        'METH': 'Каждый приём соответствует цели и подкреплён примером с занятия.',
        'RES': 'Только стабильное (S3). Формат: было → стало → доказательство.',
        'NEXT': 'Незакрытые цели + новые зоны роста.',
        'REC': 'Домашний перенос приёмов работы. Что делать — как делать — зачем. Без терминов.',
        'LIT': 'Утверждённый список центра, вставляется целиком.',
    }
    titles = {'AS': 'Актуальное состояние', 'GOAL': 'Цели на период реабилитации:',
              'METH': 'Приёмы работы:', 'RES': 'Результаты:', 'NEXT': 'Цели на следующий период:',
              'REC': 'Рекомендации:', 'LIT': 'Рекомендуемая литература:'}

    for b in data['blocks']:
        _para(d, titles.get(b['id'], b['name']), bold=True, after=4)
        _para(d, '[' + hints.get(b['id'], '') + ']', italic=True, size=10, color=(0x80, 0x80, 0x80), after=6)
        if b['id'] == 'AS':
            for m in [x for x in data['microblocks'] if x['block'] == 'AS']:
                _para(d, '%d) %s — статус: S3 / S2 / S1 / S0 / SN' % (m['order'], m['name']), size=11, after=2)
                _para(d, '[формулировка]', color=(0xA0, 0xA0, 0xA0), after=2)
                _para(d, 'Пример с занятия: [на занятии №__ в ситуации __ ребёнок __; специалист __; ребёнок __]',
                      italic=True, size=10, color=(0x80, 0x80, 0x80), after=8)
        elif b['id'] == 'REC':
            for m in [x for x in data['microblocks'] if x['block'] == 'REC']:
                _para(d, '• %s%s' % (m['name'], '' if m['mandatory'] else ' (по релевантности)'), size=11, after=2)
                _para(d, '[рекомендация для родителей]', color=(0xA0, 0xA0, 0xA0), after=6)
        elif b['id'] == 'LIT':
            for i, t in enumerate(data['literature'], 1):
                p = _para(d, '%d. %s' % (i, t), size=11, after=2)
        else:
            for k in (1, 2, 3):
                _para(d, '[формулировка %d]' % k, color=(0xA0, 0xA0, 0xA0), after=2)
                if b['id'] in ('METH', 'RES'):
                    _para(d, 'Пример с занятия: [конкретный факт]', italic=True, size=10,
                          color=(0x80, 0x80, 0x80), after=6)
                else:
                    _para(d, '', after=4)
        _para(d, '', after=2)

    _para(d, 'Служебные отметки (когда данных нет, блок не удаляется):', bold=True, size=11, after=4)
    for s in data['service_phrases']:
        _para(d, '• %s — %s' % (s['situation'], s['text']), size=10, after=2)

    d.save(OUT_TPL)
    return OUT_TPL


def build_memo_docx(data):
    import docx
    from docx.shared import Pt, Cm
    d = docx.Document()
    _setup_doc(d)
    _para(d, 'ПАМЯТКА СПЕЦИАЛИСТА', bold=True, size=14, align='center', after=2)
    _para(d, 'Конструктор рекомендаций · направление «Игровое взаимодействие»', size=11, align='center',
          color=(0x60, 0x60, 0x60), after=12)

    _para(d, 'Пайплайн', bold=True, after=4)
    for i, t in enumerate([
        'Наблюдение. Фиксируйте факт, а не вывод. Плохо: «ребёнок не идёт на контакт». Хорошо: «на 2 занятии '
        'ребёнок 3 минуты играл с песком самостоятельно; когда педагог молча сел рядом — не отвернулся; когда '
        'педагог взял такую же лопатку — посмотрел на него и продолжил копать».',
        'Кодирование статуса. Ребёнок сделал сам? Взрослый подсказывал словом? Показывал действием? Использовал '
        'эмоцию, интонацию, паузу? Создал условие (игрушка, среда, ритуал, снижение нагрузки)? Наблюдение было '
        'невключённым? Проявление однократное или повторяющееся?',
        'Перенос в документ. Стабильное → ресурс и результаты. Иногда → цель закрепить. С поддержкой → цель снять '
        'опору. Нет базы → цель на более базовой стадии. Стресс → служебная отметка, приоритет регуляции (стадия 1).',
        'Проверка по чек-листу и выдача документа.']):
        _para(d, '%d. %s' % (i + 1, t), after=6, align='just')

    _para(d, 'Статусы способности', bold=True, after=4)
    t = d.add_table(rows=1, cols=3); t.style = 'Table Grid'
    hdr = t.rows[0].cells
    for i, h in enumerate(['Код', 'Когда ставим', 'Куда попадает']):
        hdr[i].text = h
        for p in hdr[i].paragraphs:
            for r in p.runs: r.bold = True; r.font.size = Pt(10); r.font.name = 'Times New Roman'
    for s in data['statuses']:
        row = t.add_row().cells
        row[0].text = '%s — %s' % (s['code'], s['name'])
        row[1].text = s['definition']
        row[2].text = s['goes_to']
        for c in row:
            for p in c.paragraphs:
                for r in p.runs: r.font.size = Pt(9); r.font.name = 'Times New Roman'
    _para(d, '', after=6)
    _para(d, 'Правило центра: если ребёнок виделся один раз, но проявление яркое и самостоятельное — допустимо '
             'написать «стабильно». Всё остальное — «иногда». Если условие создал взрослый (показал знакомую '
             'сюжетную игрушку, начал сюжет, дал предмет) — это «с поддержкой».', after=8, align='just')

    _para(d, 'Что считается поддержкой взрослого', bold=True, after=4)
    for s in data['support_types']:
        _para(d, '• %s: %s' % (s['name'], s['examples']), size=11, after=2, align='just')
    _para(d, '', after=6)

    _para(d, 'Минимальный формат примера с занятия', bold=True, after=4)
    _para(d, 'На занятии [номер/дата] в ситуации [условие] ребёнок [действие]. Специалист [без вмешательства / '
             'сказал / показал / создал условие]. Ребёнок [последствие].', italic=True, after=8, align='just')
    _para(d, 'Ни одна оценка способности не вносится в документ, если специалист не может привести хотя бы один '
             'конкретный пример наблюдения.', bold=True, after=8, align='just')

    _para(d, 'Три правила против копипаста', bold=True, after=4)
    for i, t_ in enumerate([
        'Нет цели без наблюдения: нельзя написать «развивать сюжетную игру», если в актуальном состоянии про '
        'сюжетную игру ничего нет.',
        'Нет приёма без цели: нельзя написать «использовать би-ба-бо», если это не связано с целью.',
        'Нет рекомендации без домашнего переноса: специалисту — «со-регуляция аффекта», родителю — «когда ребёнок '
        'расстроился, сначала не объясняйте и не требуйте; сядьте рядом, говорите тихо, используйте знакомое '
        'движение или сенсорную игру; когда напряжение ушло — мягко возвращайтесь к игре».']):
        _para(d, '%d. %s' % (i + 1, t_), after=6, align='just')

    _para(d, 'Чек-лист перед выдачей документа', bold=True, after=4)
    for i, c in enumerate(data['checklist'], 1):
        _para(d, '%d. %s' % (i, c['text']), size=11, after=2, align='just')

    _para(d, '', after=6)
    _para(d, 'Обязательные блоки документа: ' + ' · '.join(
        b['name'].rstrip(':') for b in data['blocks']), bold=True, size=11, after=4, align='just')
    _para(d, data['meta']['standard'], size=11, after=4, align='just')
    d.save(OUT_MEMO)
    return OUT_MEMO


# --------------------------------------------------------------------------- MAIN
def main():
    from_excel = ('--from-excel' in sys.argv) or ('-x' in sys.argv)
    if from_excel:
        import excel_to_json  # noqa
        data = excel_to_json.load()
        print('Источник данных: Банк_фраз.xlsx')
    elif os.path.exists(OUT_XLSX):
        data = SD.build()
        print('Источник данных: tools/source_data.py  '
              '(чтобы собрать из Excel: python tools/build.py --from-excel)')
    else:
        data = SD.build()
    errs = SD.validate(data)
    if errs:
        print('! Замечания целостности данных (%d):' % len(errs))
        for e in errs:
            print('   -', e)
        if not from_excel:
            raise SystemExit(1)
        print('   (сборка из Excel продолжается — исправьте ID и пересоберите)')
    out = [build_json(data), build_html(data), build_html_v2(data)]
    if from_excel:
        print('Банк_фраз.xlsx не перезаписывается: он и есть мастер-база.')
    else:
        out.append(build_excel(data))
    out += [build_template_docx(data), build_memo_docx(data)]
    print('Собрано:')
    for p in out:
        print('  %-42s %8.1f КБ' % (os.path.relpath(p, ROOT), os.path.getsize(p) / 1024))
    print('Фраз в банке: %d | пунктов опросника: %d | наблюдательных вопросов ИВ2: %d'
          % (len(data['phrases']), len(data['questionnaire']), len(data['iv2_questions'])))
    print('Папка раздачи release/ (копии с понятными именами):')
    import make_release  # noqa
    make_release.main()


if __name__ == '__main__':
    main()
