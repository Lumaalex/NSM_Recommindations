# -*- coding: utf-8 -*-
"""
Перенос наработок v2 в V1 (Конструктор_рекомендаций.html), пакет «V1 1.2.0».
Правится ТОЛЬКО app/template.html — данные (source_data.py / phrases.json / Банк_фраз.xlsx) не трогаются.

Пункты переноса:
  A1  шапка в два ряда + чипы ФИО / период / специалист·занятия   (v2, запись 44)
  A2  индикатор автосохранения убран из середины шапки в строку чипов
  A3  версия ПРИЛОЖЕНИЯ видна в шапке (V1VER), отдельно от версии данных
  A4  фильтр банка: «название · код» у блоков и микроблоков        (v2, запись 45)
  A5  таблица банка в простом режиме: человекочитаемые названия вместо кодов
  A6  модалка подбора фраз: счётчик «Найдено: N» + легенда кодов + микротема у фразы
"""
import io, os, sys

TPL = os.path.join('konstruktor', 'app', 'template.html')

with io.open(TPL, encoding='utf-8') as f:
    src = f.read()
orig = src

R = []   # (old, new, label)

# ---------------------------------------------------------------- A1/A2: CSS
R.append((
"""<style>
/*__CSS__*/
</style>""",
"""<style>
/*__CSS__*/
/* ==================================================== СТИЛИ V1 (перенос из v2, запись 44)
   Шапка в два ряда: 1-й ряд — заголовок и кнопки, 2-й ряд — чипы «кто/какой период/кто заполнял»
   и индикатор автосохранения. Правила не переопределяют gap/padding header.top,
   чтобы мобильная адаптация из app/style.css продолжала работать. */
header.top{flex-direction:column;align-items:stretch}
.hdrrow{display:flex;gap:10px;align-items:center;flex-wrap:wrap;width:100%}
.hdrchips{display:flex;gap:6px;align-items:center;min-width:0;flex-wrap:wrap;width:100%;
  padding-top:calc(5px * var(--fs));border-top:1px solid rgba(255,255,255,.16)}
.hdrchips .pill{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:46vw;
  background:var(--soft);border:1px solid var(--line);color:var(--ink);font-size:calc(12px * var(--fs))}
.hdrchips .savechip{margin-left:auto}
@media(max-width:760px){
  .hdrrow{gap:7px}
  .hdrchips{padding-top:5px}
  .hdrchips .pill{max-width:72vw}
}
</style>""", 'A1 CSS шапки'))

# ---------------------------------------------------------------- A1: разметка шапки
R.append((
"""<header class="top">
  <div>
    <h1>Конструктор рекомендаций</h1>""",
"""<header class="top">
  <div class="hdrrow">
  <div>
    <h1>Конструктор рекомендаций</h1>""", 'A1 открытие hdrrow'))

R.append((
"""  <div class="spacer"></div>
  <div class="sub" id="saveinfo">—</div>
  <button class="b ghost small" id="btnSaveProject\"""",
"""  <div class="spacer"></div>
  <button class="b ghost small" id="btnSaveProject\"""", 'A2 saveinfo убран из 1-го ряда'))

R.append((
"""  <button class="b ghost small" id="btnReset" title="Очистить черновик и начать новый документ"><span class="short">Новый</span><span class="lbl">Новый документ</span></button>
</header>""",
"""  <button class="b ghost small" id="btnReset" title="Очистить черновик и начать новый документ"><span class="short">Новый</span><span class="lbl">Новый документ</span></button>
  </div>
  <div class="hdrchips">
    <span class="pill" id="hdrFio" title="ФИО подопечного — используется в заголовке документа и в имени файла">ФИО не указано</span>
    <span class="pill" id="hdrPeriod" title="Период реабилитации из шапки документа">период не указан</span>
    <span class="pill" id="hdrSpec" title="Специалист и количество занятий">специалист не указан</span>
    <span class="sub savechip" id="saveinfo">—</span>
  </div>
</header>""", 'A1 строка чипов'))

# ---------------------------------------------------------------- A3: версия приложения
R.append((
"""const BANK_DEFAULT = JSON.parse(document.getElementById('bank-data').textContent);""",
"""const V1VER = '1.2.0';   // версия приложения V1 (см. CHANGELOG.md, записи 9–13, 46); данные — BANK.meta.version
const BANK_DEFAULT = JSON.parse(document.getElementById('bank-data').textContent);""", 'A3 V1VER'))

R.append((
"""$('#ver').textContent = BANK.meta.version+' от '+BANK.meta.updated;""",
"""$('#ver').textContent = V1VER+' · банк данных '+BANK.meta.version+' от '+BANK.meta.updated;""", 'A3 #ver'))

# ---------------------------------------------------------------- A1: чипы в JS
R.append((
"""function render(){ renderTabs(); const m=$('#main'); ensureMicro();""",
"""/* --- чипы шапки: ФИО, период, специалист и количество занятий (перенос из v2, запись 44).
   Обновляются при каждом рендере и на каждый ввод в полях вкладки «1. Шапка». --- */
function syncHdrChips(){
  const h=(S&&S.header)||{};
  const f=$('#hdrFio'); if(f) f.textContent=(h.fio||'').trim()||'ФИО не указано';
  const a=(h.period_start||'').trim(), b=(h.period_end||'').trim(), p=$('#hdrPeriod');
  if(p) p.textContent=(a||b)? 'период: '+(a||'…')+' — '+(b||'…') : 'период не указан';
  const sp=(h.specialist||'').trim(), se=(h.sessions||'').trim(), s=$('#hdrSpec'), parts=[];
  if(sp) parts.push('специалист: '+sp);
  if(se) parts.push('занятий: '+se);
  if(s) s.textContent=parts.length? parts.join(' · ') : 'специалист не указан';
}
function render(){ renderTabs(); const m=$('#main'); ensureMicro(); syncHdrChips();""", 'A1 syncHdrChips'))

R.append((
"""  document.querySelectorAll('[data-h]').forEach(el=>el.oninput=()=>{S.header[el.dataset.h]=el.value; save();});""",
"""  document.querySelectorAll('[data-h]').forEach(el=>el.oninput=()=>{S.header[el.dataset.h]=el.value; save(); syncHdrChips();});""",
 'A1 live-update чипов'))

# ---------------------------------------------------------------- A4: фильтры банка «название · код»
R.append((
"""  const blocks=(BANK.blocks||[]).map(b=>`<option value="${b.id}">${esc(b.name)}</option>`).join('');
  const micros=(BANK.microblocks||[]).map(m=>`<option value="${m.id}">${esc(m.name)}</option>`).join('');""",
"""  /* названия блоков и микроблоков — вместе с кодом, чтобы код не приходилось угадывать (перенос из v2, запись 45) */
  const blocks=(BANK.blocks||[]).map(b=>`<option value="${b.id}">${esc(b.name)} · ${esc(b.id)}</option>`).join('');
  const micros=(BANK.microblocks||[]).map(m=>`<option value="${m.id}">${esc(m.name)} · ${esc(m.id)}</option>`).join('');""",
 'A4 фильтры банка'))

# ---------------------------------------------------------------- A5: таблица банка — названия вместо кодов
R.append((
"""        <td class="small muted">${esc(p.block)}${p.micro? ' · '+esc(p.micro):''}</td><td>${esc(p.text)}</td></tr>`).join('');""",
"""        <td class="small muted">${esc(blockName(p.block))}${p.micro? ' · '+esc(microName(p.micro)):''}</td><td>${esc(p.text)}</td></tr>`).join('');""",
 'A5 простой режим: названия'))

R.append((
"""      <td>${esc(p.block)}</td><td>${esc(p.micro||'—')}</td>""",
"""      <td title="${esc(blockName(p.block))}">${esc(p.block)}</td><td title="${esc(p.micro? microName(p.micro):'')}">${esc(p.micro||'—')}</td>""",
 'A5 продвинутый режим: подсказки'))

# ---------------------------------------------------------------- A6: модалка подбора фраз
R.append((
"""  const list=pickerCandidates();
  let html='';
  if(!list.length) html='<div class="muted small" style="padding:10px">Ничего не найдено. Измените фильтр или добавьте свою фразу на странице блока.</div>';
  list.forEach(p=>{
    html+=`<div class="prow"><div class="ptxt">${p.status&&p.status.length===2? '<span class="pill '+esc(p.status)+'">'+esc(p.status)+'</span> ':''}${esc(p.text)}
      ${!isSimple()? '<div class="small muted">ID: '+esc(p.id)+(p.example_hint? ' · пример: '+esc(p.example_hint):'')+'</div>':''}</div>
      ${addBtn(p.id, to, '+ добавить')}</div>`;
  });""",
"""  const list=pickerCandidates();
  /* счётчик и легенда кодов — перенос из v2 (запись 45) */
  let html='<div class="small muted" style="margin-bottom:6px">Найдено: '+list.length+
    '. Кнопка «+ добавить» кладёт фразу в «'+esc(targetName(to))+'».<br>'+
    'Код фразы: блок · микротема · статус · номер — например <b>AS5play-S2-07</b> = «Актуальное состояние», '+
    'микротема «Игра» (AS5play), статус S2 (иногда), фраза 07.</div>';
  if(!list.length) html+='<div class="muted small" style="padding:10px">Ничего не найдено. Измените фильтр или добавьте свою фразу на странице блока.</div>';
  list.forEach(p=>{
    const meta = !isSimple()
      ? 'ID: '+esc(p.id)+(p.micro? ' · '+esc(microName(p.micro)):'')+(p.example_hint? ' · пример: '+esc(p.example_hint):'')
      : (p.micro? 'микротема: '+esc(microName(p.micro)) : '');
    html+=`<div class="prow"><div class="ptxt">${p.status&&p.status.length===2? '<span class="pill '+esc(p.status)+'">'+esc(p.status)+'</span> ':''}${esc(p.text)}
      ${meta? '<div class="small muted">'+meta+'</div>':''}</div>
      ${addBtn(p.id, to, '+ добавить')}</div>`;
  });""", 'A6 модалка подбора'))

# ---------------------------------------------------------------- хелперы имён (для A5/A6)
R.append((
"""function targetName(to){""",
"""/* человекочитаемые названия блока и микроблока по коду (перенос из v2, запись 45) */
function blockName(id){ const b=(BANK.blockIndex||{})[id]; return (b&&b.name)||id||'—'; }
function microName(id){ const m=(BANK.microIndex||{})[id]; return (m&&m.name)||id||'—'; }
function targetName(to){""", 'хелперы blockName/microName'))

# ---------------------------------------------------------------- применение
for old, new, label in R:
    n = src.count(old)
    if n != 1:
        print('!! ЯКОРЬ НЕ НАЙДЕН ИЛИ НЕ ОДИН (%d) — %s' % (n, label))
        sys.exit(1)
    src = src.replace(old, new, 1)
    print('   ok  %s' % label)

if src == orig:
    print('!! ничего не изменилось'); sys.exit(1)

with io.open(TPL, 'w', encoding='utf-8') as f:
    f.write(src)
print('Записано: %s (%d → %d байт)' % (TPL, len(orig), len(src)))
