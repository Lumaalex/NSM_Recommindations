# -*- coding: utf-8 -*-
"""
Пакет 2.6.0 (форк V2 «от общего к частному») — правки app/template_v2.html
==========================================================================
1) чип специалиста в шапке (#hdrSpec, specChipText());
2) шаг 9 «Банк фраз» — полный банк с правками внутри конструктора 2
   (vStage9/renderBank9/bindBank9Table/BK9, bankNewPhrase/bankRenamePhrase/
   bankSetField/bankDeletePhrase/mergeBankRows/replaceBank/importBankFile,
   экспорт-импорт JSON/CSV, localStorage['iv_constructor_bank_v2']);
3) шаг 1 почищен: карточка-дубль «Банк фраз: смотреть и добавлять» убрана;
4) кнопка «Банк фраз» в шапке ведёт на шаг 9;
5) V2VER = 2.6.0.

Запуск:  python3 work/patch_v260_template.py
Каждая замена обязана найтись ровно один раз — иначе скрипт падает (ничего не записав).
"""
import io
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'konstruktor')
ROOT = os.path.abspath(ROOT)
TPL = os.path.join(ROOT, 'app', 'template_v2.html')

REPL = []


def rep(old, new, label):
    REPL.append((old, new, label))


# ------------------------------------------------------------------ 1. шапка: чип специалиста
rep("""    <span class="pill" id="hdrDate" title="Дата заполнения">дата не указана</span>
  </div>""",
    """    <span class="pill" id="hdrDate" title="Дата заполнения">дата не указана</span>
    <span class="pill" id="hdrSpec" title="Специалист и количество занятий — подтягиваются из шапки документа">специалист не указан</span>
  </div>""",
    'шапка: чип специалиста #hdrSpec')

rep('<button class="b ghost small" id="btnBank" title="Открыть банк фраз: просмотр и добавление в документ">Банк фраз</button>',
    '<button class="b ghost small" id="btnBank" title="Шаг 9 «Банк фраз»: просмотр, правка, импорт и экспорт банка">Банк фраз</button>',
    'шапка: подсказка кнопки «Банк фраз»')

rep("""<input type="file" id="fileArch" accept=".json" style="display:none">""",
    """<input type="file" id="fileArch" accept=".json" style="display:none">
<input type="file" id="fileBank" accept=".json,.csv" style="display:none">""",
    'скрытый input для импорта банка')

# ------------------------------------------------------------------ 2. CSS шага 9
rep("""@media(max-width:640px){
  .hdrchips .pill{max-width:72vw}""",
    """/* ---- 2.6.0: шаг 9 «Банк фраз» (таблица с правкой в строке) ---- */
.b9bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:10px}
table.bank9 td input[type="text"],table.bank9 td textarea,table.bank9 td select{width:100%;
  box-sizing:border-box;font:inherit;font-size:calc(12.5px * var(--fs));background:var(--panel);
  color:var(--ink);border:1px solid var(--line);border-radius:5px;padding:3px 5px}
table.bank9 td.idcol input{width:120px}
table.bank9 td textarea{min-height:46px;resize:vertical}
table.bank9 tr.own td{background:var(--acc2)}
table.bank9 td label.small{display:flex;gap:5px;align-items:center;white-space:nowrap}
@media(max-width:640px){
  .hdrchips .pill{max-width:72vw}""",
    'CSS шага 9')

# ------------------------------------------------------------------ 3. версия + банк в localStorage
rep("""const V2VER = '2.5.0';   // версия форка v2 (см. CHANGELOG.md, записи 25–28, 35–45, 62)
const BANK = (function(){ const b = JSON.parse(document.getElementById('bank-data').textContent);
  b.phraseIndex={}; b.phrases.forEach(p=>b.phraseIndex[p.id]=p);
  b.svcIndex={}; (b.service_phrases||[]).forEach(s=>b.svcIndex[s.id]=s);
  b.sphereIndex={}; (b.spheres||[]).forEach(s=>b.sphereIndex[s.id]=s);
  return b; })();
const byId = id => BANK.phraseIndex[id];""",
    """const V2VER = '2.6.0';   // версия форка v2 (см. CHANGELOG.md, записи 25–28, 35–45, 62, 63)
/* Встроенный банк сборки — эталон для кнопки «Вернуть встроенный банк» (2.6.0). */
const BANK_DEFAULT = JSON.parse(document.getElementById('bank-data').textContent);
/* --- перенос старых кодов банка на семантические (2.4.0: AS1→AS1sens, AS4→AS4ini, RC1→RC1home…).
   Объявления стоят ДО loadBank() — иначе TDZ-ошибка на первой загрузке. --- */
const CODE_MIG = BANK_DEFAULT.code_migration||{};
const migCode = id => (id && CODE_MIG[id]) || id;
/* --- 2.6.0: правки банка живут в этом браузере; ключ СВОЙ, не общий с V1 --- */
const LS_BANK='iv_constructor_bank_v2';
function indexBank(b){
  b.phraseIndex={};  (b.phrases||[]).forEach(p=> b.phraseIndex[p.id]=p);
  b.svcIndex={};     (b.service_phrases||[]).forEach(s=> b.svcIndex[s.id]=s);
  b.microIndex={};   (b.microblocks||[]).forEach(m=> b.microIndex[m.id]=m);
  b.blockIndex={};   (b.blocks||[]).forEach(x=> b.blockIndex[x.id]=x);
  b.statusIndex={};  (b.statuses||[]).forEach(x=> b.statusIndex[x.code]=x);
  b.sphereIndex={};  (b.spheres||[]).forEach(s=> b.sphereIndex[s.id]=s);
  return b;
}
/* индексы в хранилище не пишем — они пересобираются при загрузке */
function stripBank(b){ const c=JSON.parse(JSON.stringify(b));
  ['phraseIndex','svcIndex','microIndex','blockIndex','statusIndex','sphereIndex'].forEach(k=>delete c[k]);
  return c; }
/* старый сохранённый банк (до 2.4.0) переводится на семантические коды — ничего не теряется */
function migrateBankLegacy(b){
  const M=CODE_MIG; if(!b||!Object.keys(M).length) return b;
  (b.microblocks||[]).forEach(m=>{ if(M[m.id]) m.id=M[m.id]; });
  (b.phrases||[]).forEach(p=>{
    if(M[p.id]) p.id=M[p.id];
    if(p.micro&&M[p.micro]) p.micro=M[p.micro];
    ['links_goal','links_meth','links_rec'].forEach(k=>{ if(Array.isArray(p[k])) p[k]=p[k].map(x=>M[x]||x); });
  });
  (b.service_phrases||[]).forEach(s=>{ if(s.microblock&&M[s.microblock]) s.microblock=M[s.microblock]; });
  (b.abilities||[]).forEach(a=>{ if(a.micro&&M[a.micro]) a.micro=M[a.micro]; });
  (b.spheres||[]).forEach(sp=>{ if(sp.micro&&M[sp.micro]) sp.micro=M[sp.micro];
    if(Array.isArray(sp.bank_as)) sp.bank_as=sp.bank_as.map(x=>M[x]||x); });
  return b;
}
function loadBank(){
  try{ const raw=localStorage.getItem(LS_BANK);
    if(raw){ const b=JSON.parse(raw);
      if(b&&Array.isArray(b.phrases)&&b.phrases.length) return indexBank(migrateBankLegacy(b)); }
  }catch(e){ console.warn('банк из localStorage не прочитан', e); }
  return indexBank(JSON.parse(JSON.stringify(BANK_DEFAULT)));
}
function persistBank(){ try{ localStorage.setItem(LS_BANK, JSON.stringify(stripBank(BANK))); }
  catch(e){ flash('Банк не сохранён: хранилище браузера недоступно'); return; }
  flash('Банк фраз сохранён в этом браузере'); }
let BANK = loadBank();
const byId = id => BANK.phraseIndex[id];""",
    'банк: BANK_DEFAULT/CODE_MIG/LS_BANK/indexBank/loadBank/persistBank')

rep("""/* --- перенос старых кодов банка на семантические (2.4.0: AS1→AS1sens, AS4→AS4ini, RC1→RC1home…) --- */
const CODE_MIG = BANK.code_migration||{};
const migCode = id => (id && CODE_MIG[id]) || id;
function migrateScores(scores){""",
    """/* CODE_MIG и migCode объявлены выше — до loadBank() (2.6.0) */
function migrateScores(scores){""",
    'убран дубль CODE_MIG/migCode')

rep("""   Банк фраз общий с классической версией (data/phrases.json / Банк_фраз.xlsx).""",
    """   Банк фраз общий с классической версией (data/phrases.json / Банк_фраз.xlsx);
   с 2.6.0 его можно смотреть и править внутри конструктора — шаг 9 «Банк фраз».""",
    'комментарий о банке в шапке файла')

# ------------------------------------------------------------------ 4. шаги: 9 штук
rep("""  {n:8, name:'8. Документ'},
];""",
    """  {n:8, name:'8. Документ'},
  {n:9, name:'9. Банк фраз'},
];""",
    'STAGES: шаг 9')

rep("""  return false;   // шаг «Документ» галочкой не помечается""",
    """  return false;   // шаги «Документ» и «Банк фраз» галочкой не помечаются""",
    'stageDone: комментарий')

rep("""  const fns={1:vStage1,2:vSensStage,3:vStage2,4:vStage3,5:vStage4,6:vStage5,7:vStage6,8:vStage7};
  $('#main').innerHTML=(fns[S.stage]||vStage1)();
  const hf=$('#hdrFio'); if(hf) hf.textContent=(S.header.fio||'').trim()||'ФИО не указано';
  const hd=$('#hdrDate'); if(hd) hd.textContent='заполнено: '+((S.header.fill_date||'').trim()||'—');
  bind();""",
    """  const fns={1:vStage1,2:vSensStage,3:vStage2,4:vStage3,5:vStage4,6:vStage5,7:vStage6,8:vStage7,9:vStage9};
  $('#main').innerHTML=(fns[S.stage]||vStage1)();
  const hf=$('#hdrFio'); if(hf) hf.textContent=(S.header.fio||'').trim()||'ФИО не указано';
  const hd=$('#hdrDate'); if(hd) hd.textContent='заполнено: '+((S.header.fill_date||'').trim()||'—');
  const hs=$('#hdrSpec'); if(hs) hs.textContent=specChipText();   // 2.6.0: специалист виден на любом шаге
  bind();""",
    'render(): шаг 9 + чип специалиста')

# ------------------------------------------------------------------ 5. шаг 1 без карточки-дубля
rep("""  html+=`<div class="card"><div class="statusbar">
    <button class="b" data-bank="AS|">Банк фраз: смотреть и добавлять</button>
    <span class="small muted">открывается поверх шага; фильтр по блоку, сфере и коду оценки</span>
  </div></div>
  <div class="card"><h2>Актуальное состояние</h2>""",
    """  /* 2.6.0: карточка «Банк фраз: смотреть и добавлять» убрана — она дублировала кнопку в шапке,
     которая теперь ведёт на шаг 9. Кнопки «+ из банка фраз» в карточках сфер остались. */
  html+=`<div class="card"><h2>Актуальное состояние</h2>""",
    'шаг 1: убрана карточка-дубль банка')

# ------------------------------------------------------------------ 6. чип специалиста: функция + ввод
rep("""function render(){
  const nav=$('#steps'); nav.innerHTML='';""",
    """/* 2.6.0: чип специалиста в шапке — ФИО · дата заполнения · специалист и занятий видно всегда */
function specChipText(){
  const h=S.header||{};
  const sp=String(h.specialist||'').trim(), sn=String(h.sessions||'').trim();
  if(!sp&&!sn) return 'специалист не указан';
  if(!sp) return 'занятий: '+sn;
  return 'специалист: '+sp+(sn? ' · занятий: '+sn : '');
}
function render(){
  const nav=$('#steps'); nav.innerHTML='';""",
    'specChipText()')

rep("""    if(el.dataset.h==='fill_date'){ const hd=$('#hdrDate');
      if(hd) hd.textContent='заполнено: '+((el.value||'').trim()||'—'); } });""",
    """    if(el.dataset.h==='fill_date'){ const hd=$('#hdrDate');
      if(hd) hd.textContent='заполнено: '+((el.value||'').trim()||'—'); }
    if(el.dataset.h==='specialist'||el.dataset.h==='sessions'){ const hs=$('#hdrSpec');
      if(hs) hs.textContent=specChipText(); } });""",
    'bind(): чип специалиста обновляется на ввод')

# ------------------------------------------------------------------ 7. ШАГ 9
STEP9 = r"""
/* ============================================================ ШАГ 9: БАНК ФРАЗ
   2.6.0: полный банк внутри форка v2 — как вкладка «Банк фраз» в V1 1.3.0.
   Таблица всех формулировок с фильтрами (блок/микроблок/статус/поиск), правкой прямо
   в строке (ID, блок, микроблок, статус, текст, теги, «требует примера»), добавлением
   и удалением фраз, экспортом и импортом JSON/CSV. Правки хранятся в этом браузере
   (localStorage['iv_constructor_bank_v2'] — свой ключ, не общий с V1), переживают
   перезагрузку страницы и сразу влияют на подбор фраз во всех шагах.
   Колонка «В документ» кладёт фразу в её блок, не уходя с шага.                     */
let BK9={block:'',micro:'',status:'',q:''};       // состояние фильтров шага 9
const BK9_ARR={AS:'as',GOAL:'goals',METH:'methods',RES:'results',NEXT:'next',REC:'recs'};
const ID2BLOCK={AS:'AS',GL:'GOAL',MT:'METH',RS:'RES',NX:'NEXT',RC:'REC'};
function bankPhraseCount(){ return (BANK.phrases||[]).filter(p=>p.active!==false).length; }
function blockName(id){ const b=(BANK.blockIndex||{})[id]; return (b&&b.name)||id||'—'; }
function microName(id){ const m=(BANK.microIndex||{})[id]; return (m&&m.name)||id||'—'; }
function statusName(code){ const s=(BANK.statusIndex||{})[code]; return (s&&s.name)||code||'—'; }
function bank9Rows(){
  const q=String(BK9.q||'').toLowerCase().trim();
  return (BANK.phrases||[]).filter(p=>p.active!==false
    &&(!BK9.block||p.block===BK9.block)
    &&(!BK9.micro||p.micro===BK9.micro)
    &&(!BK9.status||String(p.status||'').split(',').map(x=>x.trim()).indexOf(BK9.status)>=0)
    &&(!q||((p.text||'')+' '+(p.id||'')+' '+(p.tags||'')).toLowerCase().indexOf(q)>=0));
}
function vStage9(){
  const blocks=(BANK.blocks||[]).map(b=>'<option value="'+esc(b.id)+'"'+(BK9.block===b.id?' selected':'')+'>'
    +esc(b.name)+' · '+esc(b.id)+'</option>').join('');
  const micros=(BANK.microblocks||[]).map(m=>'<option value="'+esc(m.id)+'"'+(BK9.micro===m.id?' selected':'')+'>'
    +esc(m.name)+' · '+esc(m.id)+'</option>').join('');
  const stats=(BANK.statuses||[]).map(s=>'<option value="'+esc(s.code)+'"'+(BK9.status===s.code?' selected':'')+'>'
    +esc(s.code)+' — '+esc(s.name)+'</option>').join('');
  return `<div class="card">
    <h2>Банк фраз</h2>
    <p class="hint">Мастер-база — файл <span class="kbd">Банк_фраз.xlsx</span> (банк общий с классической версией).
    Фразы можно править и добавлять прямо здесь: изменения хранятся в этом браузере и сразу
    попадают в подбор фраз на всех шагах. Чтобы перенести правки на другой компьютер —
    «Экспорт JSON» (или «Экспорт CSV» для Excel) и «Импорт» там. Код фразы: блок · микротема ·
    статус · номер, например <b>AS5play-S2-07</b> = «Актуальное состояние», микротема «Игра», статус S2, фраза 07.</p>
    <div class="b9bar">
      <button class="b small" id="bank9Add">+ Новая фраза</button>
      <button class="b gray small" id="bank9ClearFilters">Сбросить фильтры</button>
      <button class="b ghost small" id="bank9ExportJson">Экспорт JSON</button>
      <button class="b ghost small" id="bank9ExportCsv">Экспорт CSV (для Excel)</button>
      <button class="b ghost small" id="bank9Import">Импорт JSON / CSV</button>
      <button class="b danger small" id="bank9Reset">Вернуть встроенный банк</button>
      <span class="small muted">Всего фраз: <b id="bank9Count">${bankPhraseCount()}</b> ·
        показано: <b id="bank9Rows">${bank9Rows().length}</b></span>
    </div>
    <div class="filters">
      <div><label class="f">Блок</label><select id="f9Block"><option value="">все</option>${blocks}</select></div>
      <div><label class="f">Микроблок</label><select id="f9Micro"><option value="">все</option>${micros}</select></div>
      <div><label class="f">Статус</label><select id="f9Status"><option value="">все</option>${stats}</select></div>
      <div><label class="f">Поиск по тексту</label><input type="text" id="f9Text" value="${esc(BK9.q)}"
        placeholder="сюжет, сенсор, инициатив…"></div>
    </div>
    <div class="small muted" id="bank9Note" style="margin:6px 0"></div>
    <div class="scroll"><table class="bank bank9" id="bank9Table"></table></div>
  </div>
  <div class="card"><h2>Справочники банка</h2>
    <h3>Статусы способности (коды фраз)</h3>
    <div class="scrollx"><table class="bank"><tr><th>Код</th><th>Название</th><th>Когда ставим</th><th>Куда попадает</th></tr>
      ${(BANK.statuses||[]).map(s=>`<tr><td><span class="pill ${esc(s.code)}">${esc(s.code)}</span></td>
        <td><b>${esc(s.name)}</b></td><td>${esc(s.definition||'')}</td><td>${esc(s.goes_to||'')}</td></tr>`).join('')}
    </table></div>
    <h3>Служебные фразы (когда данных нет)</h3>
    <div class="scrollx"><table class="bank"><tr><th>ID</th><th>Ситуация</th><th>Формулировка</th></tr>
      ${(BANK.service_phrases||[]).map(s=>`<tr><td>${esc(s.id)}</td><td>${esc(s.situation||'')}</td>
        <td>${esc(s.text||'')}</td></tr>`).join('')}
    </table></div>
    <div class="notice info" style="margin-top:8px">Правки банка на этом шаге не меняют мастер-базу
    <span class="kbd">Банк_фраз.xlsx</span>: они живут в этом браузере и в выгруженном JSON/CSV.
    Чтобы правка стала общей для всех — перенесите её в таблицу и пересоберите конструктор.</div>
  </div>`;
}
function renderBank9(){
  const t=$('#bank9Table'); if(!t) return;
  const rows=bank9Rows(), all=(BANK.phrases||[]).length, act=bankPhraseCount();
  const note=$('#bank9Note');
  if(note) note.textContent = act<all
    ? 'Показаны активные формулировки общего банка: '+act+' из '+all+' (отключённые скрыты).'
    : 'В банке '+all+' формулировок. Правки видны сразу во всех шагах — подсказки и окно подбора берут фразы отсюда.';
  const bl=(BANK.blocks||[]), mi=(BANK.microblocks||[]), st=(BANK.statuses||[]);
  const bOpts=cur=>'<option value="">—</option>'+bl.map(b=>'<option value="'+esc(b.id)+'"'
    +(b.id===cur?' selected':'')+'>'+esc(b.id)+' · '+esc(b.name)+'</option>').join('')
    +(cur&&!bl.some(b=>b.id===cur)? '<option value="'+esc(cur)+'" selected>'+esc(cur)+'</option>' : '');
  const mOpts=cur=>'<option value="">—</option>'+mi.map(m=>'<option value="'+esc(m.id)+'"'
    +(m.id===cur?' selected':'')+'>'+esc(m.id)+' · '+esc(m.name)+'</option>').join('')
    +(cur&&!mi.some(m=>m.id===cur)? '<option value="'+esc(cur)+'" selected>'+esc(cur)+'</option>' : '');
  const sOpts=cur=>{ const c=String(cur||'');
    return st.map(s=>'<option value="'+esc(s.code)+'"'+(s.code===c?' selected':'')+'>'
      +esc(s.code)+' — '+esc(s.name)+'</option>').join('')
      +(c&&!st.some(s=>s.code===c)? '<option value="'+esc(c)+'" selected>'+esc(c)+'</option>' : ''); };
  t.innerHTML='<tr><th>ID</th><th>Блок</th><th>Микроблок</th><th>Статус</th><th>Формулировка</th>'
    +'<th>Пример</th><th>В документ</th><th></th></tr>'
    + rows.map(p=>{
      const sph=p.block==='AS'? (sphereOfId('as',p.id)||'') : '';
      return '<tr'+(p.source==='пользователь'?' class="own"':'')+'>'
        +'<td class="idcol"><input type="text" data-b9f="id" data-b9id="'+esc(p.id)+'" value="'+esc(p.id)+'"'
          +' title="ID фразы: блок · микротема · статус · номер"></td>'
        +'<td><select data-b9f="block" data-b9id="'+esc(p.id)+'" title="'+esc(blockName(p.block))+'">'+bOpts(p.block)+'</select></td>'
        +'<td><select data-b9f="micro" data-b9id="'+esc(p.id)+'" title="'+esc(microName(p.micro))+'">'+mOpts(p.micro||'')+'</select></td>'
        +'<td><select data-b9f="status" data-b9id="'+esc(p.id)+'" title="'+esc(statusName(String(p.status||'').split(',')[0]))+'">'+sOpts(p.status)+'</select></td>'
        +'<td><textarea data-b9f="text" data-b9id="'+esc(p.id)+'" rows="2">'+esc(p.text)+'</textarea>'
          +'<input type="text" data-b9f="tags" data-b9id="'+esc(p.id)+'" value="'+esc(p.tags||'')+'"'
          +' placeholder="теги: тема/домен" style="margin-top:4px"></td>'
        +'<td><label class="small"><input type="checkbox" data-b9f="needs_example" data-b9id="'+esc(p.id)+'"'
          +(p.needs_example?' checked':'')+'> требует примера</label>'
          +'<div class="small muted">'+esc(p.example_hint||'')+'</div></td>'
        +'<td>'+addBtnV2(BK9_ARR[p.block]||'as', p.id, '+ в документ', sph||undefined)
          +(sph? '<div class="small muted">'+esc(sphereName(sph))+'</div>' : '')+'</td>'
        +'<td><button class="b danger small" data-b9del="'+esc(p.id)+'">удалить</button></td></tr>';
    }).join('');
  const br=$('#bank9Rows'); if(br) br.textContent=rows.length;
  const bc=$('#bank9Count'); if(bc) bc.textContent=act;
  bindBank9Table();
}
function bindBank9Table(){
  $$('#bank9Table [data-b9f]').forEach(el=>{
    const id=el.dataset.b9id, f=el.dataset.b9f; if(!byId(id)) return;
    if(f==='id') el.onchange=()=>bankRenamePhrase(id, el.value);
    else if(f==='needs_example') el.onchange=()=>bankSetField(id,f,el.checked);
    else if(el.tagName==='SELECT') el.onchange=()=>{ bankSetField(id,f,el.value); renderBank9(); };
    else el.oninput=()=>bankSetField(id,f,el.value);
  });
  $$('#bank9Table [data-b9del]').forEach(b=>b.onclick=()=>bankDeletePhrase(b.dataset.b9del));
  $$('#bank9Table [data-tg]').forEach(b=>b.onclick=()=>{ const parts=b.dataset.tg.split('|');
    toggleIn(parts[0], parts[1], parts[2]? {sphere:parts[2]} : undefined); });
  const keys={f9Block:'block',f9Micro:'micro',f9Status:'status',f9Text:'q'};
  Object.keys(keys).forEach(id=>{ const el=$('#'+id); if(!el) return;
    el.onchange=el.oninput=()=>{ BK9[keys[id]]=el.value; renderBank9(); }; });
}
function bindBank9(){
  renderBank9();
  const ba=$('#bank9Add'); if(ba) ba.onclick=()=>{ const p=bankNewPhrase(); if(p){ BK9.q=''; render(); } };
  const bc=$('#bank9ClearFilters'); if(bc) bc.onclick=()=>{ BK9={block:'',micro:'',status:'',q:''}; render(); };
  const bej=$('#bank9ExportJson'); if(bej) bej.onclick=exportBankJson;
  const bec=$('#bank9ExportCsv'); if(bec) bec.onclick=exportBankCsv;
  const bi=$('#bank9Import'); if(bi) bi.onclick=()=>{ const f=$('#fileBank'); if(f) f.click(); };
  const br=$('#bank9Reset'); if(br) br.onclick=()=>{
    if(confirm('Вернуть встроенный банк? Все правки банка в этом браузере будут потеряны.')) resetBank(); };
}

/* ------------------------------------------------------- правки банка (ядро, без DOM) */
function bankSetField(id,f,v){
  const p=byId(id); if(!p||f==='id') return false;
  if(f==='needs_example') p.needs_example=!!v; else p[f]=v;
  persistBank(); return true;
}
function bankRenamePhrase(oldId,newId){
  newId=String(newId||'').trim(); const p=byId(oldId); if(!p) return false;
  if(!newId||newId===oldId) return false;
  if(byId(newId)){ alert('Такой ID уже есть: '+newId); return false; }
  delete BANK.phraseIndex[oldId]; p.id=newId; BANK.phraseIndex[newId]=p;
  persistBank(); renderBank9(); flash('ID изменён: '+oldId+' → '+newId); return true;
}
function bankNewPhrase(id){
  id=String(id||'').trim();
  if(!id) id=String(prompt('ID новой фразы (например AS5play-S2-07):')||'').trim();
  if(!id) return null;
  if(byId(id)){ alert('Такой ID уже есть: '+id); return null; }
  const pre=id.split('-')[0];
  const micro=((BANK.microblocks||[]).map(m=>m.id).filter(m=>id.indexOf(m)===0)[0])||'';
  const block=ID2BLOCK[pre]||((BANK.microIndex||{})[micro]||{}).block||'AS';
  const st=(BANK.statuses||[]).map(s=>s.code).filter(c=>id.indexOf('-'+c+'-')>=0)[0]||'S2';
  const p={id:id, dir:'IV', block:block, micro:micro, ability:'', status:st, text:'',
    source:'пользователь', needs_example:true, example_hint:'', links_goal:[], links_meth:[],
    links_rec:[], tags:'', active:true};
  BANK.phrases.push(p); BANK=indexBank(BANK); persistBank(); renderBank9();
  flash('Новая фраза '+id+' добавлена — заполните формулировку');
  return p;
}
function bankDeletePhrase(id){
  if(!byId(id)) return false;
  if(!confirm('Удалить фразу '+id+'?')) return false;
  BANK.phrases=(BANK.phrases||[]).filter(p=>p.id!==id);
  BANK=indexBank(BANK); persistBank(); renderBank9();
  flash('Фраза удалена: '+id); return true;
}
/* строки из CSV/импорта сливаются с банком по ID; старые коды переводятся картой code_migration */
function mergeBankRows(rows){
  const idx={}; (BANK.phrases||[]).forEach(p=>idx[p.id]=p);
  let added=0, updated=0;
  (rows||[]).forEach(r=>{
    if(!r||!r.id) return;
    const row=Object.assign({},r); row.id=migCode(String(row.id).trim());
    if(row.micro) row.micro=migCode(row.micro);
    ['links_goal','links_meth','links_rec'].forEach(k=>{ if(Array.isArray(row[k])) row[k]=row[k].map(migCode); });
    if(!row.text) row.text='';
    if(idx[row.id]){ Object.assign(idx[row.id],row); updated++; }
    else { BANK.phrases.push(row); idx[row.id]=row; added++; }
  });
  BANK=indexBank(BANK); persistBank();
  return {added:added, updated:updated};
}
/* полная замена банка (импорт JSON): недостающие разделы берутся из встроенного банка */
function replaceBank(b){
  if(!b||!Array.isArray(b.phrases)||!b.phrases.length) throw new Error('в файле нет массива phrases');
  const merged=JSON.parse(JSON.stringify(Object.assign({},BANK_DEFAULT,b)));
  BANK=indexBank(migrateBankLegacy(merged)); persistBank();
  return BANK.phrases.length;
}
function resetBank(){
  try{ localStorage.removeItem(LS_BANK); }catch(e){}
  BANK=indexBank(JSON.parse(JSON.stringify(BANK_DEFAULT)));
  render(); flash('Встроенный банк возвращён: '+bankPhraseCount()+' фраз');
}
function importBankFile(file){
  const r=new FileReader();
  r.onload=()=>{ const txt=r.result;
    try{
      if(/\.csv$/i.test(file.name||'')){
        const rows=parseCsv(txt);
        if(!rows.length) throw new Error('в CSV не найдено строк');
        const res=mergeBankRows(rows); render();
        flash('Импортировано строк: '+(res.added+res.updated)+' (новых: '+res.added+', обновлено: '+res.updated+')');
      } else {
        const b=JSON.parse(txt);
        if(b&&b.project&&b.doc) throw new Error('это файл проекта — его загружают кнопкой «Загрузить» в шапке');
        const n=replaceBank(b); render(); flash('Банк загружен: '+n+' фраз');
      }
    }catch(e){ alert('Импорт не удался: '+e.message); }
  };
  r.readAsText(file,'utf-8');
}
function bankFileName(ext){
  return 'банк_фраз_v2_'+((BANK.meta||{}).version||'x')+'_'+V2VER+'.'+ext;
}
function exportBankJson(){
  downloadBlob(new Blob([JSON.stringify(stripBank(BANK),null,2)],{type:'application/json'}), bankFileName('json'));
  flash('Банк выгружен в JSON');
}
function exportBankCsv(){
  downloadBlob(new Blob(['\ufeff'+toCsv(BANK.phrases||[])],{type:'text/csv;charset=utf-8'}), bankFileName('csv'));
  flash('Банк выгружен в CSV (разделитель «;», для Excel)');
}

/* ------------------------------------------------------- CSV (порт из V1 1.3.0) */
const CSV_COLS=[['id','ID'],['dir','Направление'],['block','Блок'],['micro','Микроблок'],['ability','Способность'],
  ['status','Статус'],['text','Текст'],['source','Источник'],['needs_example','Требует примера'],
  ['example_hint','Подсказка примера'],['links_goal','Цели(ID)'],['links_meth','Приёмы(ID)'],
  ['links_rec','Рекомендации(ID)'],['tags','Теги'],['active','Активна']];
function csvCell(v){ if(v===true) return 'Да'; if(v===false) return 'Нет'; if(Array.isArray(v)) return '"'+v.join(';')+'"';
  v=String(v==null?'':v); return /[",;\n]/.test(v)? '"'+v.replace(/"/g,'""')+'"' : v; }
function toCsv(rows){ return CSV_COLS.map(c=>c[1]).join(';')+'\n'
  + (rows||[]).map(r=>CSV_COLS.map(c=>csvCell(r[c[0]])).join(';')).join('\n'); }
function splitCsvLine(line){
  const res=[]; let cur='',q=false;
  for(let i=0;i<line.length;i++){ const c=line[i];
    if(q){ if(c==='"'){ if(line[i+1]==='"'){cur+='"';i++;} else q=false; } else cur+=c; }
    else { if(c==='"') q=true; else if(c===';'||c===','){res.push(cur);cur='';} else cur+=c; } }
  res.push(cur); return res.map(s=>s.trim());
}
function parseCsv(text){
  text=String(text||'').replace(/^\ufeff/,''); const lines=text.split(/\r?\n/).filter(l=>l.trim());
  if(!lines.length) return [];
  const head=splitCsvLine(lines[0]), mapIdx={};
  CSV_COLS.forEach(pair=>{ const k=pair[0], label=pair[1];
    const i=head.indexOf(label); if(i>=0) mapIdx[k]=i;
    const j=head.indexOf(k); if(j>=0&&mapIdx[k]===undefined) mapIdx[k]=j; });
  const out=[];
  for(let i=1;i<lines.length;i++){
    const cells=splitCsvLine(lines[i]), o={};
    Object.keys(mapIdx).forEach(k=>{ o[k]=cells[mapIdx[k]]||''; });
    ['links_goal','links_meth','links_rec'].forEach(k=>{
      o[k]=String(o[k]||'').split(/[;,]/).map(s=>s.trim()).filter(Boolean); });
    o.needs_example=['да','1','true','yes'].indexOf(String(o.needs_example).toLowerCase())>=0;
    o.active=!(['нет','0','false','no'].indexOf(String(o.active).toLowerCase())>=0);
    if(!o.id||!o.text) continue;
    o.status=o.status||''; o.dir=o.dir||'IV'; o.block=o.block||'AS'; o.micro=o.micro||'';
    o.ability=o.ability||''; o.source=o.source||''; o.example_hint=o.example_hint||''; o.tags=o.tags||'';
    out.push(o);
  }
  return out;
}

"""
rep("""/* ------------------------------------------------------- ШАГ 1: шапка + актуальное состояние (оценка сфер) */""",
    STEP9 + """/* ------------------------------------------------------- ШАГ 1: шапка + актуальное состояние (оценка сфер) */""",
    'шаг 9 «Банк фраз»: функции и CSV')

# ------------------------------------------------------------------ 8. кнопка шапки + input файла
rep("""$('#btnBank').onclick=()=>openBank('AS','');""",
    """/* 2.6.0: кнопка «Банк фраз» в шапке ведёт на шаг 9 (полный банк с правками).
   Окно подбора с фильтром по блоку/сфере/коду осталось на кнопках «+ из банка фраз» внутри шагов. */
$('#btnBank').onclick=()=>{ S.stage=9; save(); render(); window.scrollTo(0,0); };
$('#fileBank').onchange=e=>{ const f=e.target.files[0]; if(f) importBankFile(f); e.target.value=''; };""",
    'кнопка «Банк фраз» → шаг 9; импорт файла')

rep("""  const bp=$('#btnPrint'); if(bp) bp.onclick=()=>window.print();
}""",
    """  const bp=$('#btnPrint'); if(bp) bp.onclick=()=>window.print();
  if(S.stage===9) bindBank9();          // 2.6.0: шаг «Банк фраз» — таблица и её кнопки
}""",
    'bind(): привязка шага 9')

# ------------------------------------------------------------------ 9. экспорт для тестов
rep("""  get S(){return S}, set S(v){S=v}, get BANK(){return BANK}, render, buildDoc, docText, fileName,""",
    """  get S(){return S}, set S(v){S=v}, get BANK(){return BANK}, set BANK(v){BANK=v},
  render, buildDoc, docText, fileName,""",
    'V2API: BANK стал перезаписываемым')

rep("""  pedInfo, pedHint, mkfOf,""",
    """  pedInfo, pedHint, mkfOf,
  vStage9, renderBank9, bindBank9Table, bindBank9, bank9Rows, bankPhraseCount, blockName, microName,
  statusName, bankNewPhrase, bankRenamePhrase, bankSetField, bankDeletePhrase, mergeBankRows,
  replaceBank, resetBank, importBankFile, exportBankJson, exportBankCsv, bankFileName,
  toCsv, parseCsv, splitCsvLine, persistBank, stripBank, loadBank, indexBank, migrateBankLegacy,
  specChipText, openBank, closeBank,
  get BK9(){return BK9}, set BK9(v){BK9=v}, get LS_BANK(){return LS_BANK},
  get BANK_DEFAULT(){return BANK_DEFAULT}, get CODE_MIG(){return CODE_MIG}, get CSV_COLS(){return CSV_COLS},""",
    'V2API: экспорт функций шага 9')


def main():
    with io.open(TPL, encoding='utf-8') as f:
        src = f.read()
    out = src
    for old, new, label in REPL:
        n = out.count(old)
        if n != 1:
            raise SystemExit('! %s: найдено вхождений %d (ожидалось 1)' % (label, n))
        out = out.replace(old, new)
        print('  + %s' % label)
    with io.open(TPL, 'w', encoding='utf-8') as f:
        f.write(out)
    print('Записано: %s (%d → %d байт)' % (os.path.relpath(TPL, ROOT), len(src), len(out)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
