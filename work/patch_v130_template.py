# -*- coding: utf-8 -*-
"""Пакет V1 1.3.0 — правки app/template.html по обратной связи заказчика.
Запуск: cd konstruktor && python3 ../work/patch_v130_template.py
Каждая правка проверяется: фрагмент должен встречаться ровно один раз."""
import io, sys

PATH = 'app/template.html'
src = io.open(PATH, encoding='utf-8').read()
n_applied = 0

def rep(old, new, cnt=1):
    """литеральная замена ровно cnt вхождений"""
    global src, n_applied
    c = src.count(old)
    assert c == cnt, 'вхождений %d (ожидалось %d): %r...' % (c, cnt, old[:90])
    src = src.replace(old, new)
    n_applied += 1

def splice(start_marker, end_marker, new):
    """замена всего текста от start_marker до end_marker (не включая) на new"""
    global src, n_applied
    i = src.index(start_marker)
    assert src.count(start_marker) == 1, start_marker
    j = src.index(end_marker, i)
    src = src[:i] + new + src[j:]
    n_applied += 1

def drop(start_marker, end_marker):
    splice(start_marker, end_marker, '')

def insert_before(marker, text):
    global src, n_applied
    assert src.count(marker) == 1, marker
    src = src.replace(marker, text + marker)
    n_applied += 1

# ------------------------------------------------------------------ R1: CSS
CSS_NEW = '''
/* ==================================================== СТИЛИ V1 · пакет 1.3.0
   Обратная связь от 2026-09-29: вкладки опросника, цветовая модель блоков фраз
   и кнопок по оценке, мини-таблицы FEDL2i. Общие app/style.css и v2 не трогаем. */
.svtabbar{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 12px;padding:0}
button.svtab{background:var(--panel);border:1px solid var(--line);border-radius:16px;
  padding:calc(6px * var(--fs)) calc(13px * var(--fs));cursor:pointer;font:inherit;
  font-size:calc(12.5px * var(--fs));color:var(--ink)}
button.svtab:hover{background:var(--acc2)}
button.svtab.on{background:var(--acc);border-color:var(--acc);color:var(--acc-ink);font-weight:600}
button.svtab .n{opacity:.7;font-weight:400}
/* цветовая модель блоков подсказок: свой оттенок синего у каждого блока документа */
.sugg{margin-top:10px}
.sugg[data-sugg="as"]{background:#e7f0f8;border-left:5px solid #1d4f7c}
.sugg[data-sugg="goal"]{background:#eaf3fa;border-left:5px solid #2f6f9f}
.sugg[data-sugg="meth"]{background:#edf5fb;border-left:5px solid #4d88b4}
.sugg[data-sugg="rec"]{background:#f1f8fd;border-left:5px solid #79a8ca}
.sugg[data-sugg="res"]{background:#eef5ee;border-left:5px solid #4c7a52}
.sugg[data-sugg="nxt"]{background:#f2f4f9;border-left:5px solid #5d6a8a}
.sugg[data-sugg="svc"]{background:var(--soft);border-left:5px solid var(--sn)}
.sugg .st{font-weight:700}
[data-theme="dark"] .sugg[data-sugg="as"]{background:#1b2a38;border-left-color:#7cb4e0}
[data-theme="dark"] .sugg[data-sugg="goal"]{background:#1a2936;border-left-color:#5b95c2}
[data-theme="dark"] .sugg[data-sugg="meth"]{background:#1a2833;border-left-color:#4d80aa}
[data-theme="dark"] .sugg[data-sugg="rec"]{background:#192630;border-left-color:#41688c}
[data-theme="dark"] .sugg[data-sugg="res"]{background:#182419;border-left-color:#5c8f62}
[data-theme="dark"] .sugg[data-sugg="nxt"]{background:#1c2029;border-left-color:#7486ae}
[data-theme="dark"] .sugg[data-sugg="svc"]{background:#20262e;border-left-color:#8d98a5}
/* кнопки оценки и «+ в документ» красятся в цвет выбранной оценки */
button.b.st-S3:not(.gray){background:var(--s3);border-color:var(--s3);color:#fff}
button.b.st-S2:not(.gray){background:var(--s2);border-color:var(--s2);color:#fff}
button.b.st-S1:not(.gray){background:var(--s1);border-color:var(--s1);color:#fff}
button.b.st-S0:not(.gray){background:var(--s0);border-color:var(--s0);color:#fff}
button.b.st-SN:not(.gray){background:var(--sn);border-color:var(--sn);color:#fff}
button.b.st-S3.gray,button.b.st-S2.gray,button.b.st-S1.gray,
button.b.st-S0.gray,button.b.st-SN.gray{border-left:4px solid var(--stc,#bbb)}
button.b.st-S3.gray{--stc:var(--s3)}button.b.st-S2.gray{--stc:var(--s2)}
button.b.st-S1.gray{--stc:var(--s1)}button.b.st-S0.gray{--stc:var(--s0)}
button.b.st-SN.gray{--stc:var(--sn)}
.scale label.on.st-S3{background:var(--s3);border-color:var(--s3);color:#fff}
.scale label.on.st-S2{background:var(--s2);border-color:var(--s2);color:#fff}
.scale label.on.st-S1{background:var(--s1);border-color:var(--s1);color:#fff}
.scale label.on.st-S0{background:var(--s0);border-color:var(--s0);color:#fff}
.scale label.on.st-SN{background:var(--sn);border-color:var(--sn);color:#fff}
.scale label .pill{margin-right:2px}
/* строки модалки подбора: цвет полосы — по блоку документа, куда ляжет фраза */
.prow.to-as{border-left:4px solid #1d4f7c}
.prow.to-goal{border-left:4px solid #2f6f9f}
.prow.to-meth{border-left:4px solid #4d88b4}
.prow.to-rec{border-left:4px solid #79a8ca}
.prow.to-res{border-left:4px solid #4c7a52}
.prow.to-next{border-left:4px solid #5d6a8a}
.prow.to-svc{border-left:4px solid var(--sn)}
/* сенсорный опросник FEDL2i (перенос из v2) */
.sens-mini{border:1px solid var(--line);border-radius:8px;background:var(--panel2);
  padding:8px;margin-top:8px}
.sens-row{display:flex;gap:8px;align-items:flex-start;border-bottom:1px dashed var(--line);
  padding:4px 0}
.sens-row:last-child{border-bottom:none}
.sens-name{flex:1 1 auto;min-width:0;font-size:calc(13px * var(--fs))}
.sens-ctl{flex:0 0 auto;min-width:0}
.sens-ctl select{max-width:190px;font:inherit;font-size:calc(12.5px * var(--fs))}
.sens-ctl textarea{width:min(320px,60vw);font:inherit;font-size:calc(12.5px * var(--fs))}
.sens-blk{margin:0 0 12px}
.sens-scale{display:flex;gap:6px;flex-wrap:wrap;margin:2px 0 6px}
.sens-scale span{font-size:calc(11.5px * var(--fs));border:1px solid var(--line);border-radius:6px;
  padding:1px 7px;background:var(--panel);color:var(--muted)}
.auto-note{background:var(--info-bg);border:1px solid var(--info-line);border-radius:6px;
  padding:8px 10px;margin-top:6px;font-size:calc(13px * var(--fs))}
@media(max-width:760px){
  .sens-row{flex-wrap:wrap}
  .sens-ctl select,.sens-ctl textarea{width:100%;max-width:none}
  button.svtab{flex:1 1 auto}
}
@media print{ .svtabbar{display:none} }
</style>'''
rep('</style>\n</head>', CSS_NEW + '\n</head>')

# ------------------------------------------------------------------ R2: версия
rep("const V1VER = '1.2.0';   // версия приложения V1 (см. CHANGELOG.md, записи 9–13, 46); данные — BANK.meta.version",
    "const V1VER = '1.3.0';   // версия приложения V1 (см. CHANGELOG.md, записи 9–13, 46, 54–61); данные — BANK.meta.version")

# ------------------------------------------------------------------ R3: CORE2SPH
insert_before('const LS_BANK = ',
'''/* Соответствие старых 8 вопросов ядра опросника (C1…C8, лист «Опросник_ядро») и девяти сфер
   оценки (лист «Сферы») — для переноса ответов в старых черновиках и проектах V1.
   Если одну сферу покрывали два вопроса ядра (эмоции + фрустрация), берётся худший ответ. */
const CORE2SPH = {C1:'SPH-WOR', C2:'SPH-REG', C3:'SPH-REG', C4:'SPH-SENS', C5:'SPH-KON',
                  C6:'SPH-INI', C7:'SPH-SYM', C8:'SPH-COM'};
''')

# ------------------------------------------------------------------ R4: migrateDoc
rep("""  Object.keys(d.blocks||{}).forEach(bk=>(d.blocks[bk]||[]).forEach(i=>{ if(i && i.src) i.src=M[i.src]||i.src; }));
  return d;
}""",
"""  Object.keys(d.blocks||{}).forEach(bk=>(d.blocks[bk]||[]).forEach(i=>{ if(i && i.src) i.src=M[i.src]||i.src; }));
  /* 1.3.0: черновик дополняется полем сенсорного опросника FEDL2i */
  if(!d.sens || typeof d.sens!=='object') d.sens={};
  if(!d.sensOpen || typeof d.sensOpen!=='object') d.sensOpen={};
  /* 1.3.0: ответы 8 вопросов ядра (C1…C8) переводятся на 9 сфер оценки (SPH-*).
     При конфликте (C2+C3 → SPH-REG) сохраняется худший ответ; N считается хуже числа. */
  const av = d.answers||{}; const worst=(x,y)=> String(x)==='N'? y : (String(y)==='N'? x : Math.min(Number(x),Number(y)));
  Object.keys(CORE2SPH).forEach(cid=>{ const a=av[cid];
    if(a && a.value!=='' && a.value!=null){ const sid=CORE2SPH[cid];
      if(!av[sid] || av[sid].value==='' || av[sid].value==null) av[sid]={value:a.value, note:a.note||''};
      else av[sid]={value:worst(av[sid].value,a.value), note:av[sid].note||a.note||''}; }
    delete av[cid]; });
  return d;
}""")

# ------------------------------------------------------------------ R5: blankDoc
rep("""    answers: {},        // qid -> {value, note}
    iv2: {},            // iv2 id -> текст наблюдения""",
"""    answers: {},        // qid -> {value, note}; с 1.3.0 здесь и оценки 9 сфер (SPH-*)
    iv2: {},            // iv2 id -> текст наблюдения
    sens: {},           // пункт FEDL2i (A1…F5) -> значение шкалы (сенсорный опросник)
    sensOpen: {},       // сфера -> раскрыта ли её мини-таблица FEDL2i""")

# ------------------------------------------------------------------ R6: UI.stab
rep("""    if(o && typeof o==='object') return {theme:(o.theme==='dark'?'dark':'light'),
      fsIdx:Math.min(FS_STEPS.length-1, Math.max(0, o.fsIdx|0)),
      mode:(o.mode==='full'?'full':'simple')}; }catch(e){}
  return {theme:'light', fsIdx:1, mode:'simple'}; })();""",
"""    if(o && typeof o==='object') return {theme:(o.theme==='dark'?'dark':'light'),
      fsIdx:Math.min(FS_STEPS.length-1, Math.max(0, o.fsIdx|0)),
      mode:(o.mode==='full'?'full':'simple'),
      stab:(['spheres','dir','sens','iv2'].indexOf(o.stab)>=0? o.stab : 'spheres')}; }catch(e){}
  return {theme:'light', fsIdx:1, mode:'simple', stab:'spheres'}; })();""")

# ------------------------------------------------------------------ R7: предикаты области видимости
rep("""/* Микротемы с флагом v2only (сферы 8–9 форка «от общего к частному») в классической версии
   не показываются и в документ не попадают — они принадлежат только Конструктору_ИВ_версия2.html. */
function microV2Only(mid){ const m=(BANK.microIndex||{})[mid]; return !!(m&&m.v2only); }
function microV1(m){ return !!m && m.block==='AS' && !m.v2only; }
function phraseV1(p){ return !!p && p.active!==false && !(p.block==='AS' && microV2Only(p.micro)); }
/* сколько формулировок доступно именно в V1 и какие микротемы принадлежат только версии 2 */
function v1PhraseCount(){ return (BANK.phrases||[]).filter(phraseV1).length; }
function v2OnlyMicroNames(){ return (BANK.microblocks||[]).filter(m=>m.v2only)
  .map(m=>m.name+' ('+m.id+')').join(', '); }""",
"""/* С версии 1.3.0 V1 показывает ВЕСЬ общий банк (201 формулировка): микротемы сфер 8–9
   (AS7prax, AS8vis) пришли в «большую» версию вместе с сенсорным опросником FEDL2i.
   Флаг v2only в данных остаётся признаком «микротема добавлена форком v2» — для справок. */
function microV2Only(mid){ const m=(BANK.microIndex||{})[mid]; return !!(m&&m.v2only); }
function microV1(m){ return !!m && m.block==='AS'; }
function phraseV1(p){ return !!p && p.active!==false; }
/* сколько формулировок банк отдаёт в интерфейс (без отключённых active:false) */
function v1PhraseCount(){ return (BANK.phrases||[]).filter(phraseV1).length; }
function v2OnlyMicroNames(){ return (BANK.microblocks||[]).filter(m=>m.v2only)
  .map(m=>m.name+' ('+m.id+')').join(', '); }""")

# ------------------------------------------------------------------ R8: ensureMicro
rep("""    if(!microV1(m)) return;   // микротемы только для версии 2 (AS7prax, AS8vis) в V1 не создаём""",
"""    if(!microV1(m)) return;   // с 1.3.0 создаются все микротемы AS, включая AS7prax/AS8vis (сферы 8–9)""")

# ------------------------------------------------------------------ R9: вкладка «Шапка» — дата заполнения
rep("""      <div><label class="f">Количество занятий</label><input type="text" data-h="sessions" value="${esc(h.sessions)}" placeholder="10"></div>
    </div>""",
"""      <div><label class="f">Количество занятий</label><input type="text" data-h="sessions" value="${esc(h.sessions)}" placeholder="10"></div>
      <div><label class="f">Дата заполнения</label><input type="text" data-h="fill_date" value="${esc(h.fill_date||'')}" placeholder="29.09.2026"></div>
    </div>""")

# ------------------------------------------------------------------ R10: ВКЛАДКА 2 (опросник) — полная замена раздела
NEW_SURVEY = r'''/* ============================================================ ВКЛАДКА 2: ОПРОСНИК
   С версии 1.3.0 опросник — с внутренними вкладками (в обоих режимах):
   «Оценка: 9 сфер» (методология версии 2, лист «Сферы»), «Подробно: DIR» (53 пункта),
   «Сенсорный профиль FEDL2i» (таблица индивидуальных особенностей, блоки A–F)
   и «Вопросы ИВ» (наблюдательные, свободный ответ).                                */
const SURVEY_TABS=[
  {id:'spheres', name:'Оценка: 9 сфер'},
  {id:'dir',     name:'Подробно: DIR'},
  {id:'sens',    name:'Сенсорный профиль FEDL2i'},
  {id:'iv2',     name:'Вопросы ИВ'},
];
const STATUS_OF_ANS={'3':'S3','2':'S2','1':'S1','0':'S0','N':'SN'};
/* Ответ V1 (3/2/1/0/N) -> ключ сферы в банке (sphere_keys, педагогическая шкала 5…1).
   Система оценок V1 не менялась (по договорённости от 2026-09-29), поэтому для подсказок
   ответ переводится в ближайший уровень педагогической шкалы:
   3 «стабильно» -> 5, 2 «иногда» -> 4, 1 «с поддержкой» -> 3,
   0 «не проявляется» -> 1 «способность не сформирована», N -> SIG-STRESS «оценка невозможна». */
const PED_OF={'3':'5','2':'4','1':'3','0':'1','N':'SIG-STRESS'};
/* Варианты ответов, согласованные с формулировкой сферы (обратная связь от 2026-09-29:
   «не проявляется» нельзя было ответить на вопрос про сенсорную переработку).
   Значения те же — 3/2/1/0/N, меняются только подписи. */
const SPHERE_ANS={
 'SPH-SENS':[['3','3 · возрастная норма, без особенностей'],['2','2 · есть особенности (повышенная или сниженная чувствительность)'],
   ['1','1 · занятия возможны только с адаптацией среды и материала'],['0','0 · выраженные особенности мешают занятию'],
   ['N','N · не наблюдалось']],
 'SPH-REG':[['3','3 · фон ровный, справляется сам'],['2','2 · справляется, но не всегда (иногда)'],
   ['1','1 · успокаивается только с поддержкой взрослого'],['0','0 · не справляется, срывы и отказы'],
   ['N','N · не проверялось']],
 'SPH-WOR':[['3','3 · интерес устойчивый, выбирает сам'],['2','2 · интерес избирательный или кратковременный'],
   ['1','1 · включается только по приглашению взрослого'],['0','0 · интерес не проявляется'],
   ['N','N · не проверялось']],
 'SPH-KON':[['3','3 · контакт и совместное внимание устойчивые'],['2','2 · контакт есть, но нестабильный'],
   ['1','1 · только с поддержкой взрослого (слово, жест, аффект)'],['0','0 · контакт не проявляется'],
   ['N','N · не проверялось']],
 'SPH-INI':[['3','3 · инициатива и цепочки устойчивые'],['2','2 · инициатива эпизодическая, цепочки короткие'],
   ['1','1 · только по приглашению взрослого, 1–2 обмена'],['0','0 · инициатива не проявляется'],
   ['N','N · не проверялось']],
 'SPH-COM':[['3','3 · речь и понимание соответствуют возрасту'],['2','2 · речь/понимание фрагментарные'],
   ['1','1 · общается невербально или эхолалиями, понимание ограничено'],['0','0 · средства коммуникации не проявляются'],
   ['N','N · не проверялось']],
 'SPH-SYM':[['3','3 · сюжетная игра со смыслом (2 и более идеи, правила)'],['2','2 · игра фрагментарная: отдельные сюжеты, короткие цепочки'],
   ['1','1 · манипулятивная или процессуальная игра со взрослым'],['0','0 · игра не сформирована'],
   ['N','N · не проверялось']],
 'SPH-MOT':[['3','3 · движения и последовательности планирует сам'],['2','2 · новые движения и планы удаются не всегда'],
   ['1','1 · только с физической или зрительной поддержкой взрослого'],['0','0 · не проявляется'],
   ['N','N · не проверялось']],
 'SPH-VIS':[['3','3 · зрительное внимание и обследование устойчивые'],['2','2 · зрительно находит и удерживает объект не всегда'],
   ['1','1 · только когда взрослый направляет взгляд и руку'],['0','0 · не проявляется'],
   ['N','N · не проверялось']],
};
function sphereAnswerOpts(sp){ return SPHERE_ANS[sp.id]
  || [[3,'3 · стабильно'],[2,'2 · иногда'],[1,'1 · с поддержкой'],[0,'0 · не проявляется'],['N','N · не проверялось']]; }
function countSpheres(){ return (BANK.spheres||[]).filter(sp=>{ const a=(S.answers||{})[sp.id];
  return a && a.value!=='' && a.value!=null; }).length; }
function ansStatus(v){ return STATUS_OF_ANS[String(v)]||''; }
function pedKeyOf(v){ return PED_OF[String(v)]||''; }
function surveyScaleLegend(){
  return `Шкала одна для всех вопросов: <span class="pill S3">3</span> стабильно ·
  <span class="pill S2">2</span> иногда · <span class="pill S1">1</span> с поддержкой ·
  <span class="pill S0">0</span> не проявляется · <span class="pill SN">N</span> не проверялось.
  Подписи вариантов подобраны под формулировку вопроса, значения не меняются.`;
}
function surveyTabsHtml(){
  const counts={spheres:(BANK.spheres||[]).length, dir:(BANK.questionnaire||[]).length,
    sens:sensTotal(), iv2:(BANK.iv2_questions||[]).length};
  return `<div class="svtabbar noprint">`+SURVEY_TABS.map(t=>
    `<button class="svtab${UI.stab===t.id?' on':''}" data-stab="${t.id}">${esc(t.name)} <span class="n">${counts[t.id]||''}</span></button>`
  ).join('')+`</div>`;
}
function vSurvey(){
  const t=UI.stab||'spheres';
  return surveyTabsHtml()
    + ({spheres:spheresTab, dir:dirTab, sens:sensTab, iv2:iv2Tab})[t]();
}
/* ---- вкладка опросника: оценка по 9 сферам (методология версии 2) ---- */
function spheresTab(){
  let html=`<div class="card">
    <h2>Оценка сфер взаимодействия</h2>
    <p class="hint">Девять сфер — методика версии 2 («от общего к частному»): оцените, что ребёнок
    демонстрирует сейчас, и конструктор предложит формулировки, цели, приёмы и рекомендации.
    ${surveyScaleLegend()}</p>
    <div class="notice warn"><b>Правило статуса.</b> Проявил сам, но не всегда — <b>2</b>. Проявил только
    после слова, показа, эмоции взрослого или созданного условия — <b>1</b>. Яркое самостоятельное
    проявление даже за одно наблюдение — <b>3</b>. Не было возможностей, стресс или отказ — <b>N</b>.</div>
    <div class="statusbar">
      <span class="small muted">Оценено сфер: <b>${countSpheres()}</b> из ${(BANK.spheres||[]).length}</span>
      <button class="b gray small" data-survey-clear>Сбросить оценки сфер</button>
      <span class="small muted">Сферы 8–9 (праксис, зрительно-пространственная) опираются на таблицу
      FEDL2i — вкладка «Сенсорный профиль».</span>
    </div>
  </div>`;
  (BANK.spheres||[]).forEach(sp=>{ html+=sphCard(sp); });
  return html;
}
function sphCard(sp){
  const a=(S.answers||{})[sp.id]||{};
  const ans=(a.value!==''&&a.value!=null)? a.value : null;
  const st=ans!=null? ansStatus(ans):'';
  const opts=sphereAnswerOpts(sp).map(([v,l])=>`<label class="${String(ans)===String(v)?'on st-'+st:''}" title="${esc(l)}">
      <input type="radio" name="q_${sp.id}" value="${v}" ${String(ans)===String(v)?'checked':''}> ${esc(l)}</label>`).join('');
  const note=`<textarea data-note="${sp.id}" rows="2" placeholder="Что именно видели: ситуация, действие ребёнка, роль взрослого (слово / показ / условие)">${esc(a.note||'')}</textarea>`;
  const pool=sphereAsPool(sp.id);
  return `<div class="mb sph" data-sph="${sp.id}">
    <div class="hd"><span class="t">${sp.order}. ${esc(sp.name)}</span>
      ${ans!=null? '<span class="pill '+esc(st)+'">'+esc(st)+'</span>':''}
      ${pool.length? '<button class="b ghost small" data-pick="MICRO:'+sp.micro+'" data-pool="'+esc(JSON.stringify(pool.map(p=>p.id)))+'">+ из банка фраз</button>':''}
    </div>
    <div class="bd">
      <div class="qitem${isSimple()?' compact':''}" data-q="${sp.id}">
        <div class="scale">${opts}</div>
        ${isSimple()
          ? `<details ${a.note?'open':''}><summary class="small muted">пример наблюдения${a.note?' ✓':''}</summary>${note}</details>`
          : `<label class="f">Пример наблюдения (факт: что сделал ребёнок, что делал специалист)</label>${note}`}
      </div>
      ${sensMiniBlock(sp)}
      ${ans!=null? sphSugg(sp,ans) : '<div class="small muted" style="margin-top:6px">Поставьте оценку — появятся формулировки, цели, приёмы и рекомендации.</div>'}
    </div></div>`;
}
/* пул фраз банка для сферы: явный список bank_as (когда микроблок делят две сферы) либо микроблок сферы */
function sphereMicros(sid){
  const set={}; const sp=(BANK.sphereIndex||{})[sid]; if(sp&&sp.micro) set[sp.micro]=1;
  const keys=(BANK.sphere_keys||{})[sid]||{};
  Object.keys(keys).forEach(k=>((keys[k]||{}).as||[]).forEach(id=>{
    const p=byId(id); if(p&&p.micro) set[p.micro]=1; }));
  return Object.keys(set);
}
function sphereAsPool(sid){
  const sp=(BANK.sphereIndex||{})[sid]||{};
  const all=(BANK.phrases||[]).filter(p=>p.block==='AS'&&p.active!==false&&phraseV1(p));
  if(sp.bank_as&&sp.bank_as.length){ const set={}; sp.bank_as.forEach(id=>set[id]=1);
    return all.filter(p=>set[p.id]); }
  const ms=sphereMicros(sid);
  return all.filter(p=>ms.indexOf(p.micro)>=0);
}
/* дополнительные формулировки актуального состояния из банка под выбранный ответ
   (в ключе сферы — 1–3 фразы; пул микротемы/сферы дополняет их до полного списка) */
function poolAsFor(sid, ans){
  const st=ansStatus(ans); if(!st) return [];
  const key=((BANK.sphere_keys||{})[sid]||{})[pedKeyOf(ans)]||{};
  const have={}; (key.as||[]).forEach(id=>have[id]=1);
  return sphereAsPool(sid).filter(p=>String(p.status||'').split(',').indexOf(st)>=0 && !have[p.id]);
}
function sphSugg(sp, ans){
  const key=((BANK.sphere_keys||{})[sp.id]||{})[pedKeyOf(ans)];
  const extra=poolAsFor(sp.id, ans);
  return keySuggestions({id:sp.id, key:{}}, ans, key, extra);
}
/* ---- вкладка опросника: подробная оценка DIR (53 пункта) ---- */
function dirTab(){
  const groups=surveyGroups();
  const answered=(BANK.questionnaire||[]).filter(q=>{const a=S.answers[q.id]; return a&&a.value!==''&&a.value!=null;}).length;
  let html = `<div class="card">
    <h2>Подробная оценка: DIR (стадии) и сенсорика</h2>
    <p class="hint">Развёрнутый опросник по стадиям DIR — для углублённой диагностики.
    ${surveyScaleLegend()}</p>
    <div class="notice warn"><b>Правило статуса.</b> Если ребёнок проявил способность только после того, как специалист
      сказал слово, показал действием, использовал аффект или создал условие (например, показал знакомую сюжетную
      игрушку) — это <b>1 «с поддержкой»</b>, а не «стабильно». Яркое самостоятельное проявление даже за одно
      наблюдение допустимо считать <b>3 «стабильно»</b>.</div>
    <p class="hint">После ответа конструктор предлагает готовые формулировки для блоков. Кнопка «+ в документ»
      добавляет фразу, повторное нажатие («✓ убрать») забирает её обратно — если передумали или нажали не то.
      Всё добавленное можно перефразировать прямо в блоках документа.</p>
    <div class="statusbar">
      <button class="b gray small" data-survey-clear>Сбросить ответы DIR</button>
      <span class="small muted">Отвечено: <b id="ansCount">${answered}</b> из ${(BANK.questionnaire||[]).length}</span>
    </div>
  </div>`;
  Object.keys(groups).forEach(gname=>{
    html += `<div class="card"><h3>${esc(gname)}</h3>`;
    groups[gname].forEach(q=>{ html += qItem(q); });
    html += `</div>`;
  });
  return html;
}
/* ---- вкладка опросника: наблюдательные вопросы ИВ2 (свободный ответ) ---- */
function iv2Tab(){
  let html = `<div class="card"><h2>Наблюдательные вопросы ИВ (свободный ответ)</h2>
    <p class="hint">Эти вопросы не имеют шкалы — они помогают собрать фактуру для примеров с занятий.
    Ответы попадают в приложение «Рабочие материалы». Группы свёрнуты — откройте нужную.</p></div>`;
  const iv2g={};
  (BANK.iv2_questions||[]).forEach(q=>{ (iv2g[q.group]=iv2g[q.group]||[]).push(q); });
  Object.keys(iv2g).forEach(g=>{
    const filledN=iv2g[g].filter(q=>String((S.iv2||{})[q.id]||'').trim()).length;
    html += `<div class="card"><details class="help"><summary>${esc(g)} (${iv2g[g].length}${filledN? ' · заполнено '+filledN:''})</summary>`;
    iv2g[g].forEach(q=>{
      html += `<div style="margin:8px 0"><label class="f">${esc(q.text)}</label>
        <textarea data-iv2="${q.id}" rows="2">${esc((S.iv2||{})[q.id]||'')}</textarea></div>`;
    });
    html += `</details></div>`;
  });
  return html;
}
function qItem(q, opts){
  const a = S.answers[q.id]||{};
  const simple = isSimple();
  const list = opts || [[3,'3 · стабильно'],[2,'2 · иногда'],[1,'1 · с поддержкой'],[0,'0 · не проявляется'],['N','N · не проверялось']];
  const st = a.value!==''&&a.value!=null ? ansStatus(a.value) : '';
  const sc = list.map(([v,l])=>`<label class="${String(a.value)===String(v)?'on'+(st?' st-'+st:''):''}">
      <input type="radio" name="q_${q.id}" value="${v}" ${String(a.value)===String(v)?'checked':''}> ${esc(l)}</label>`).join('');
  const note = `<textarea data-note="${q.id}" rows="2" placeholder="На 3 занятии в ситуации свободной игры с песком ребёнок самостоятельно наполнил формочку, перевернул её и посмотрел на педагогу. Педагог не подсказывал.">${esc(a.note||'')}</textarea>`;
  return `<div class="qitem${simple?' compact':''}" data-q="${q.id}">
    <div class="qt">${esc(q.text)}</div>
    ${simple? '' : `<div class="qmeta">${esc(q.source||'Сферы оценки')} · ${esc(q.domain||q.short||'')}${q.micro? ' · микроблок: '+esc((BANK.microIndex[q.micro]||{}).name||q.micro):''}</div>`}
    <div class="scale">${sc}</div>
    ${simple
      ? `<details ${a.note?'open':''}><summary class="small muted">пример с занятия${a.note? ' ✓':''}</summary>${note}</details>`
      : `<label class="f">Пример с занятия (факт: что сделал ребёнок, что делал специалист)</label>${note}`}
    ${a.value!==undefined && a.value!=='' && a.value!==null ? keySuggestions(q,a.value) : ''}
  </div>`;
}
/* подсказки ключа: цветные полосы по блокам документа (AS — самый тёмный оттенок синего,
   цели/приёмы/рекомендации светлее, результаты и следующий период — свои оттенки),
   кнопки «+ в документ» красятся в цвет статуса фразы (обратная связь от 2026-09-29) */
function keySuggestions(q, ans, keyOverride, extraAs){
  const key = keyOverride || (q.key||{})[ans] || (q.key||{})[String(ans)];
  if(!key) return '';
  const secs=[['as','Актуальное состояние'],['goal','Цель'],['meth','Приём'],['rec','Рекомендация'],
              ['res','Результат'],['nxt','Цель на следующий период'],['svc','Служебная отметка']];
  let out='';
  secs.forEach(([k,label])=>{
    let ids = (key[k]||[]).slice();
    if(k==='as' && extraAs && extraAs.length) ids = ids.concat(extraAs.map(p=>p.id));
    ids = ids.filter((x,i)=>ids.indexOf(x)===i);
    if(!ids.length) return;
    out += `<div class="sugg" data-sugg="${k}"><div class="st">${esc(label)} · ${ids.length}</div>`;
    ids.forEach(id=>{
      const p = byId(id) || BANK.svcIndex[id];
      if(!p) return;
      const stc = p.status ? String(p.status).split(',')[0] : '';
      const st = stc.length===2 ? `<span class="pill ${esc(stc)}">${esc(stc)}</span> ` : '';
      out += `<div class="ph">${st}${esc(p.text)} ${addBtn(id, targetFor(k,p))}</div>`;
      if(k==='as' && p.example_hint) out += `<div class="small muted" style="margin:-2px 0 4px">Пример: ${esc(p.example_hint)}</div>`;
    });
    out += `</div>`;
  });
  const stCode = BANK.status_by_answer[String(ans)];
  if(stCode) out = `<div class="small muted" style="margin-top:6px">Статус по ответу:
      <span class="pill ${stCode}">${stCode}</span> ${esc((BANK.statusIndex[stCode]||{}).name||'')}${isSimple()? '': ' — '+esc(((BANK.statusIndex[stCode]||{}).goes_to)||'')}</div>` + out;
  return out;
}
'''
splice('/* ============================================================ ВКЛАДКА 2: ОПРОСНИК */',
       'function targetFor(k, p){', NEW_SURVEY)

# ------------------------------------------------------------------ R11: вкладка 3 — вступление и служебная карточка
rep("""    без рекомендаций. Все 6 микротем обязательны — если данных нет, ставится служебная фраза, микротема не удаляется.</p>""",
"""    без рекомендаций. Шесть обязательных микротем нельзя пропускать — если данных нет, ставится служебная фраза.
    Микротемы 7–8 (праксис, зрительно-пространственная) — дополнительные: заполняются по данным таблицы FEDL2i
    (вкладка «2. Опросник» → «Сенсорный профиль»), пустыми остаются без служебных отметок.</p>""")
rep("""<h3>Общая служебная отметка для блока (не относится к одной микротеме)</h3>""",
"""<h3>Общая служебная отметка для блока (не относится к одной из 6 обязательных микротем)</h3>""")

# ------------------------------------------------------------------ R12: microCard — кнопка «+ фраза» и связи под фразой
rep("""      ${d.items.length? '<span class="pill '+(d.status||'SN')+'">'+d.items.length+' фр.</span>':''} ${filled}""",
"""      <button class="b ghost small" data-pick="MICRO:${m.id}">+ фраза из банка</button>
      ${d.items.length? '<span class="pill '+(d.status||'SN')+'">'+d.items.length+' фр.</span>':''} ${filled}""")
rep("""      <label class="f" style="margin-top:6px">Пример с занятия ${needExample(m.id,it)?'<b style="color:var(--bad)">*</b>':''}</label>
      <textarea data-iex="${m.id}:${i}" rows="2" placeholder="На занятии №__ в ситуации __ ребёнок __. Специалист __ (без вмешательства / сказал / показал / создал условие). Ребёнок __.">${esc(it.example||'')}</textarea>
    </li>`;""",
"""      <label class="f" style="margin-top:6px">Пример с занятия ${needExample(m.id,it)?'<b style="color:var(--bad)">*</b>':''}</label>
      <textarea data-iex="${m.id}:${i}" rows="2" placeholder="На занятии №__ в ситуации __ ребёнок __. Специалист __ (без вмешательства / сказал / показал / создал условие). Ребёнок __.">${esc(it.example||'')}</textarea>
      ${linkedStrip(it)}
    </li>`;""")

# ------------------------------------------------------------------ R13: bankCount — все фразы
rep("""function bankCount(block, micro){ return (BANK.phrases||[]).filter(p=>p.block===block && (!micro||p.micro===micro) && phraseV1(p)).length; }""",
"""function bankCount(block, micro){ return (BANK.phrases||[]).filter(p=>p.block===block && (!micro||p.micro===micro) && p.active!==false).length; }""")

# ------------------------------------------------------------------ R14: вкладка 4 — карточка связей вместо autoGoalsCard
rep("""  return blockCard('GOAL','2. Цели на период реабилитации',
      'Цели ставятся из статусов S2 / S1 / S0 / SN. Для S3 цель не «сформировать», а «расширить» или «перенести в новые ситуации». Нет цели без наблюдения в блоке 1.')
    + blockCard('METH','3. Приёмы работы',""",
"""  return linkedSuggestionsCard(['goal','meth'])
    + blockCard('GOAL','2. Цели на период реабилитации',
      'Цели ставятся из статусов S2 / S1 / S0 / SN. Для S3 цель не «сформировать», а «расширить» или «перенести в новые ситуации». Нет цели без наблюдения в блоке 1.')
    + blockCard('METH','3. Приёмы работы',""")

NEW_LINKED = r'''/* развёрнутые связи: из каждой фразы актуального состояния, взятой из банка,
   видны её цели, приёмы и рекомендации — одной кнопкой добавляются в документ
   (обратная связь от 2026-09-29: «выбрал фразу — предложи соответствующие цели, приёмы, рекомендации») */
function linkedStrip(it){
  if(!it || !it.src) return '';
  const p=byId(it.src); if(!p) return '';
  const rows=[['links_goal','GOAL','цели'],['links_meth','METH','приёмы'],['links_rec','REC','рекомендации']];
  let inner='', n=0;
  rows.forEach(([k,to,label])=>{
    const ids=(p[k]||[]).filter(id=>byId(id));
    if(!ids.length) return; n+=ids.length;
    inner+=`<div class="sugg" data-sugg="${to==='GOAL'?'goal':(to==='METH'?'meth':'rec')}">
      <div class="st">${label}: ${ids.length}</div>`
      + ids.map(id=>{ const lp=byId(id);
          return `<div class="ph">${esc(lp.text)} ${addBtn(id, to==='REC'? 'REC:'+(lp.micro||'RC4play') : to)}</div>`; }).join('')
      + `</div>`;
  });
  if(!n) return '';
  return `<details class="help" style="margin-top:6px"><summary>Связи этой фразы: цели, приёмы, рекомендации (${n})</summary>${inner}</details>`;
}
/* сводная карточка связей по всем фразам актуального состояния — на вкладках 4 и 6 */
function linkedSuggestionsCard(kinds){
  const wantGoal=(kinds||[]).indexOf('goal')>=0, wantRec=(kinds||[]).indexOf('rec')>=0;
  const goals={}, meths={}, recs={};
  Object.keys(S.micro||{}).forEach(mid=>{
    ((S.micro[mid]||{}).items||[]).forEach(it=>{
      if(!it.src) return; const p=byId(it.src); if(!p) return;
      (p.links_goal||[]).forEach(id=>{ if(!goals[id]) goals[id]={id:id, from:[]}; goals[id].from.push(p.id); });
      (p.links_meth||[]).forEach(id=>{ if(!meths[id]) meths[id]={id:id, from:[]}; meths[id].from.push(p.id); });
      (p.links_rec||[]).forEach(id=>{ if(!recs[id]) recs[id]={id:id, from:[]}; recs[id].from.push(p.id); });
    });
  });
  const has=Object.keys(goals).length+Object.keys(meths).length+Object.keys(recs).length;
  if(!has) return '';
  const row=(e,to)=>{ const p=byId(e.id); if(!p) return '';
    const stc=String(p.status||'').split(',')[0];
    return `<div class="ph">${stc.length===2? '<span class="pill '+esc(stc)+'">'+esc(stc)+'</span> ':''}${esc(p.text)}
      ${addBtn(e.id,to)} <span class="small muted">← ${esc(e.from.slice(0,3).join(', '))}${e.from.length>3?'…':''}</span></div>`; };
  let body='';
  if(wantGoal){
    body+=Object.keys(goals).length? `<div class="sugg" data-sugg="goal"><div class="st">Цели из выбранных формулировок · ${Object.keys(goals).length}</div>`
      + Object.keys(goals).map(k=>row(goals[k],'GOAL')).join('') + `</div>` : '';
    body+=Object.keys(meths).length? `<div class="sugg" data-sugg="meth"><div class="st">Приёмы к этим целям · ${Object.keys(meths).length}</div>`
      + Object.keys(meths).map(k=>row(meths[k],'METH')).join('') + `</div>` : '';
  }
  if(wantRec){
    const byTopic={};
    Object.keys(recs).forEach(k=>{ const p=byId(k); if(!p) return; const t=p.micro||'RC4play';
      (byTopic[t]=byTopic[t]||[]).push(recs[k]); });
    Object.keys(byTopic).forEach(t=>{
      body+=`<div class="sugg" data-sugg="rec"><div class="st">Рекомендации · ${esc(microName(t))}</div>`
        + byTopic[t].map(e=>row(e,'REC:'+t)).join('') + `</div>`; });
  }
  if(!body) return '';
  return `<div class="card"><h3>Подсказка: цели, приёмы и рекомендации из выбранных формулировок актуального состояния</h3>
    <p class="hint">Связи банка: наблюдение → цель → приём → рекомендация. Кнопка добавляет фразу в документ
    (повторное нажатие — убирает). В скобках — из какой формулировки актуального состояния следует связь.</p>
    ${body}</div>`;
}
'''
splice('/* авто-подсказка: какие цели вытекают из выбранных формулировок актуального состояния */',
       '/* ============================================================ ВКЛАДКА 5: РЕЗУЛЬТАТЫ */',
       NEW_LINKED)

# ------------------------------------------------------------------ R15: вкладка 6 — карточка связей
rep("""    организовывалось, ставится служебная фраза.</div></div>`;
  (BANK.microblocks||[]).filter(m=>m.block==='REC').forEach(m=>{""",
"""    организовывалось, ставится служебная фраза.</div></div>`;
  html += linkedSuggestionsCard(['rec']);
  (BANK.microblocks||[]).filter(m=>m.block==='REC').forEach(m=>{""")

# ------------------------------------------------------------------ R16: buildDoc — обязательные + заполненные дополнительные микротемы
rep("""  const microBlocks=(BANK.microblocks||[]).filter(microV1).sort((a,b)=>a.order-b.order);
  // 1. Актуальное состояние
  let asParas=[];
  microBlocks.forEach(m=>{
    const d=S.micro[m.id]||{items:[],status:'',service:''};
    let txts=(d.items||[]).map(i=>adapt(i.text)).filter(t=>t&&t.trim());
    if(d.service && BANK.svcIndex[d.service]){
      const st=adapt(BANK.svcIndex[d.service].text);
      if(txts.indexOf(st)<0) txts.push(st);
    }
    if(!txts.length) txts=['[микротема не заполнена]'];""",
"""  const microAll=(BANK.microblocks||[]).filter(m=>m.block==='AS').sort((a,b)=>a.order-b.order);
  // 1. Актуальное состояние: 6 обязательных микротем всегда + дополнительные (AS7prax, AS8vis), если заполнены
  const microBlocks=microAll.filter(m=>m.mandatory!==false).concat(microAll.filter(m=>{
    if(m.mandatory!==false) return false;
    const d=S.micro[m.id]||{}; return (d.items||[]).some(i=>(i.text||'').trim()) || (d.service&&BANK.svcIndex[d.service]);
  }));
  let asParas=[];
  microBlocks.forEach(m=>{
    const d=S.micro[m.id]||{items:[],status:'',service:''};
    let txts=(d.items||[]).map(i=>adapt(i.text)).filter(t=>t&&t.trim());
    if(d.service && BANK.svcIndex[d.service]){
      const st=adapt(BANK.svcIndex[d.service].text);
      if(txts.indexOf(st)<0) txts.push(st);
    }
    if(!txts.length) txts=['[микротема не заполнена]'];""")

# ------------------------------------------------------------------ R17: приложение «Рабочие материалы» — сферы и FEDL2i
rep("""  const answered=(BANK.questionnaire||[]).filter(q=>S.answers[q.id] && S.answers[q.id].value!=='' && S.answers[q.id].value!=null);
  if(answered.length){
    out.push({text:'Ответы по опроснику (стадии DIR)', bold:true});
    answered.forEach(q=>{
      const a=S.answers[q.id];
      out.push({text:q.id+' ['+a.value+'] '+q.text + (a.note? ' — пример: '+a.note : '')});
    });
  }""",
"""  const sphAns=(BANK.spheres||[]).filter(sp=>{const a=S.answers[sp.id]; return a&&a.value!==''&&a.value!=null;});
  if(sphAns.length){
    out.push({text:'Оценка сфер ('+(sphAns.length+' из '+(BANK.spheres||[]).length)+')', bold:true});
    sphAns.forEach(sp=>{ const a=S.answers[sp.id];
      out.push({text:sp.order+'. '+sp.name+' — '+a.value+' ('+((BANK.statusIndex[ansStatus(a.value)]||{}).name||'')+')'
        + (a.note? ' — пример: '+a.note : '')});
    });
  }
  const answered=(BANK.questionnaire||[]).filter(q=>S.answers[q.id] && S.answers[q.id].value!=='' && S.answers[q.id].value!=null);
  if(answered.length){
    out.push({text:'Ответы по опроснику (стадии DIR)', bold:true});
    answered.forEach(q=>{
      const a=S.answers[q.id];
      out.push({text:q.id+' ['+a.value+'] '+q.text + (a.note? ' — пример: '+a.note : '')});
    });
  }
  const sensRows=[];
  sensBlocks().forEach(b=>b.items.forEach(it=>{
    const v=String((S.sens||{})[it.id]||'').trim(); if(!v) return;
    sensRows.push(it.id+'. '+it.name.replace(/[.:\s]+$/,'')+' — '+(it.scale==='text'? v : sensWord(v)));
  }));
  if(sensRows.length){
    out.push({text:'Сенсорный опросник FEDL2i'+((S.header.fill_date||'').trim()? ' (дата заполнения: '+S.header.fill_date.trim()+')':''), bold:true});
    sensRows.forEach(t=>out.push({text:'• '+t}));
  }""")

# ------------------------------------------------------------------ R18: чек-лист 6 обязательных + 2 дополнительные
rep("""  const microAS=(BANK.microblocks||[]).filter(m=>m.block==='AS');
  const filled=microAS.filter(m=>{const x=S.micro[m.id]||{};return (x.items||[]).length||x.service;});
  const withStatus=microAS.filter(m=>{const x=S.micro[m.id]||{};return x.status;});""",
"""  const microAS=(BANK.microblocks||[]).filter(m=>m.block==='AS');
  const microMust=microAS.filter(m=>m.mandatory!==false);
  const microOpt=microAS.filter(m=>m.mandatory===false);
  const filled=microMust.filter(m=>{const x=S.micro[m.id]||{};return (x.items||[]).length||x.service;});
  const withStatus=microMust.filter(m=>{const x=S.micro[m.id]||{};return x.status;});
  const optFilled=microOpt.filter(m=>{const x=S.micro[m.id]||{};return (x.items||[]).length||x.service;});""")
rep("""  res.push({id:'C2', text:'Заполнены все 6 микротем «Актуального состояния» ('+filled.length+'/6).', pass:filled.length===6, sev:'block'});
  res.push({id:'C3', text:'У микротем выбран статус S3/S2/S1/S0/SN ('+withStatus.length+'/6).', pass:withStatus.length===6, sev:'warn'});""",
"""  res.push({id:'C2', text:'Заполнены все '+microMust.length+' обязательных микротем «Актуального состояния» ('+filled.length+'/'+microMust.length+').', pass:filled.length===microMust.length, sev:'block'});
  res.push({id:'C3', text:'У обязательных микротем выбран статус S3/S2/S1/S0/SN ('+withStatus.length+'/'+microMust.length+').', pass:withStatus.length===microMust.length, sev:'warn'});
  res.push({id:'C2b', text:'Дополнительные микротемы по таблице FEDL2i (праксис, зрительно-пространственная) — по наличию данных: заполнено '+optFilled.length+' из '+microOpt.length+'.', pass:null, sev:'manual'});""")

# ------------------------------------------------------------------ R19: простой режим — счётчик сфер, вступление АС, связи, подсказка
rep("""function vASSimple(){
  let html=`<div class="card"><h2>Актуальное состояние</h2>
    <p class="hint">Шесть областей. Выберите оценку области цветными кнопками, добавьте формулировки
    («+ фраза») и приложите пример с занятия. Пустых областей быть не должно: если данных нет —
    кнопка «+ фраза» → служебная отметка внизу списка.</p></div>`;""",
"""function vASSimple(){
  let html=`<div class="card"><h2>Актуальное состояние</h2>
    <p class="hint">Шесть обязательных областей и две дополнительные (праксис, зрительно-пространственная —
    по данным таблицы FEDL2i). Выберите оценку области цветными кнопками, добавьте формулировки
    («+ фраза») и приложите пример с занятия. В шести обязательных областях пустот быть не должно:
    если данных нет — кнопка «+ фраза» → служебная отметка внизу списка.</p></div>`;""")
rep("""  return `<div class="mb"><div class="hd"><span class="t">${m.order}. ${esc(m.name)}</span>
      ${(d.items.length||d.service)?'<span class="pill S3">✓</span>':'<span class="pill S0">не заполнено</span>'}</div>""",
"""  return `<div class="mb"><div class="hd"><span class="t">${m.order}. ${esc(m.name)}${m.mandatory===false?' <span class="small muted">(дополнительно)</span>':''}</span>
      ${(d.items.length||d.service)?'<span class="pill S3">✓</span>':(m.mandatory===false?'<span class="pill SN">не обязательно</span>':'<span class="pill S0">не заполнено</span>')}</div>""")
rep("""      <details><summary class="small muted ${it.example?'':'must'}">пример с занятия${it.example?' ✓':' — обязательно'}</summary>
        <textarea data-iex="${m.id}:${i}" rows="2" placeholder="На занятии №__ в ситуации __ ребёнок __. Специалист __ (без вмешательства / сказал / показал / создал условие).">${esc(it.example||'')}</textarea>
      </details>
      <div class="meta"><button class="b danger small" data-idel="${m.id}:${i}">убрать ✕</button></div></li>`;""",
"""      <details><summary class="small muted ${it.example?'':'must'}">пример с занятия${it.example?' ✓':' — обязательно'}</summary>
        <textarea data-iex="${m.id}:${i}" rows="2" placeholder="На занятии №__ в ситуации __ ребёнок __. Специалист __ (без вмешательства / сказал / показал / создал условие).">${esc(it.example||'')}</textarea>
      </details>
      ${linkedStrip(it)}
      <div class="meta"><button class="b danger small" data-idel="${m.id}:${i}">убрать ✕</button></div></li>`;""")
rep("""function vGoalsSimple(){
  return blockCardSimple('GOAL','2. Цели на период реабилитации',""",
"""function vGoalsSimple(){
  return linkedSuggestionsCard(['goal','meth'])
    + blockCardSimple('GOAL','2. Цели на период реабилитации',""")
rep("""  let html=`<div class="card"><h2>6. Рекомендации</h2>
    <p class="hint">Домашние инструкции родителям: что делать — как делать — зачем. Простыми словами, без терминов.</p></div>`;""",
"""  let html=`<div class="card"><h2>6. Рекомендации</h2>
    <p class="hint">Домашние инструкции родителям: что делать — как делать — зачем. Простыми словами, без терминов.</p></div>`
    + linkedSuggestionsCard(['rec']);""")
rep("""    <p><span class="stepnum">2</span><b>Оценка</b> — 8 вопросов, шкала 3 / 2 / 1 / 0 / N. После ответа
      конструктор предложит готовые формулировки, цели, приёмы и рекомендации.</p>""",
"""    <p><span class="stepnum">2</span><b>Оценка</b> — 9 сфер, шкала 3 / 2 / 1 / 0 / N; там же подробный
      опросник DIR, сенсорный профиль FEDL2i и наблюдательные вопросы ИВ (внутренние вкладки).
      После ответа конструктор предложит готовые формулировки, цели, приёмы и рекомендации.</p>""")

# ------------------------------------------------------------------ R20: block4 — сенсорный опросник и sphereName (перед vHelpSimple)
BLOCK4 = r'''/* ============================================================ СЕНСОРНЫЙ ОПРОСНИК FEDL2i
   Перенос из версии 2 (пакет 2.2.0–2.3.0): таблица индивидуальных особенностей, блоки A–F,
   свои шкалы (sens_scales), привязка блоков к сферам (sens_blocks в листе «Сферы»)
   и сборка текста в «Актуальное состояние». Данные — общие, листы «Сенсорный_опросник»
   и «Сенсорный_шкалы». */
function sphereName(sid){ const sp=(BANK.sphereIndex||{})[sid]; return sp? (sp.short||sp.name) : ''; }
function sensScale(code){ return (BANK.sens_scales||{})[code] || (BANK.sens_scales||{}).yn
  || {name:'да / нет',options:['Да','Нет'],legend:''}; }
function sensBlocks(){ return BANK.sens_fedl||[]; }
function sensBlock(id){ return sensBlocks().find(b=>b.id===id) || null; }
function sensItems(id){ const b=sensBlock(id); return b? b.items : []; }
function sensFilled(){ return Object.keys(S.sens||{}).filter(k=>String(S.sens[k]||'').trim()).length; }
function sensTotal(){ return sensBlocks().reduce((a,b)=>a+b.items.length,0); }
function sensWord(v){ return (BANK.sens_words||{})[v] || v; }
function sensBlocksOf(spOrId){
  const sp=(typeof spOrId==='string')? (BANK.sphereIndex||{})[spOrId] : spOrId;
  if(!sp) return [];
  if(sp.sens_blocks&&sp.sens_blocks.length) return sp.sens_blocks.slice();
  return (sp.id==='SPH-SENS')? ['A'] : [];
}
function sensSpheres(){ return (BANK.spheres||[]).filter(sp=>sensBlocksOf(sp).length); }
function blockSphere(bid){ return (BANK.spheres||[]).find(s=>sensBlocksOf(s).indexOf(bid)>=0) || null; }
function blockShortTitle(b){ return String((b&&b.title)||'').replace(/^[A-F]\.\s*/,''); }
function sensItemPhrase(it,v){
  const name=String(it.name||'').replace(/[.:\s]+$/,'');
  if(it.scale==='react') return name.toLowerCase()+' — '+sensWord(v);
  if(it.scale==='yn'){
    if(/^да/i.test(v)) return name.toLowerCase()+' — да';
    if(/^нет/i.test(v)) return name.toLowerCase()+' — нет';
    return name.toLowerCase()+' — непостоянно';
  }
  return name.toLowerCase()+' — '+String(v).toLowerCase();
}
function sensAutoText(){
  const parts=[];
  sensItems('A').forEach(it=>{
    const v=String((S.sens||{})[it.id]||'').trim();
    if(!v || it.scale==='text') return;
    parts.push(it.name.replace(/[.:\s]+$/,'').toLowerCase()+' — '+sensWord(v));
  });
  const prof=String((S.sens||{})['A8']||'').trim();
  let t='';
  if(parts.length) t='Сенсорная переработка: '+parts.join('; ')+'.';
  if(prof) t+=(t? ' ':'')+'Доминирующий функциональный профиль: '+prof;
  return t;
}
function sensAutoTextFor(spOrId){
  const sp=(typeof spOrId==='string')? (BANK.sphereIndex||{})[spOrId] : spOrId;
  const bl=sensBlocksOf(sp);
  if(!bl.length) return '';
  if(bl.length===1&&bl[0]==='A') return sensAutoText();
  const parts=[];
  bl.forEach(bid=>{ const b=sensBlock(bid); if(!b) return;
    const rows=[]; let free='';
    b.items.forEach(it=>{ const v=String((S.sens||{})[it.id]||'').trim(); if(!v) return;
      if(it.scale==='text') free+=(free? ' ':'')+v;
      else rows.push(sensItemPhrase(it,v)); });
    const inner=rows.concat(free? [free] : []).join('; ');
    if(inner) parts.push(blockShortTitle(b)+': '+inner); });
  return parts.length? 'Индивидуальные особенности. '+parts.join('. ')+'.' : '';
}
function sensRowHtml(it){
  const v=String((S.sens||{})[it.id]||'');
  const sc=sensScale(it.scale);
  let ctl;
  if(it.scale==='text') ctl=`<textarea rows="2" data-sens="${it.id}" placeholder="опишите простыми словами">${esc(v)}</textarea>`;
  else ctl=`<select data-sens="${it.id}"><option value="">—</option>`
    + sc.options.map(o=>`<option value="${esc(o)}"${v===o?' selected':''}>${esc(o)}</option>`).join('') + `</select>`;
  return `<div class="sens-row"><div class="sens-name">${it.id}. ${esc(it.name)}</div><div class="sens-ctl">${ctl}</div></div>`;
}
function sensScaleHtml(scaleCode){
  const sc=sensScale(scaleCode);
  return `<div class="sens-scale">${sc.options.map(o=>`<span>${esc(o)}</span>`).join('')}
    <span>${esc(sc.name)}${sc.legend? ': '+esc(sc.legend):''}</span></div>`;
}
/* «Собрать текст в документ»: готовый абзац из оценок FEDL2i добавляется фразой
   в микротему сферы (src=AUTO:SENS:<сфера>) — текст можно править как обычную фразу. */
function sensApply(sid){
  const t=sensAutoTextFor(sid);
  if(!t){ flash('Заполните пункты блоков '+sensBlocksOf(sid).join(', ')+' в таблице FEDL2i — тогда появится текст'); return false; }
  const sp=(BANK.sphereIndex||{})[sid]||{}; const mid=sp.micro;
  if(!mid || !(BANK.microIndex||{})[mid]){ flash('У сферы «'+sphereName(sid)+'» нет микротемы актуального состояния'); return false; }
  ensureMicro();
  S.micro[mid].items=(S.micro[mid].items||[]).filter(i=>i.src!=='AUTO:SENS:'+sid);
  S.micro[mid].items.push({src:'AUTO:SENS:'+sid, text:t, example:'', status:S.micro[mid].status||'', auto:sid});
  save(); render();
  flash('Текст сферы «'+sphereName(sid)+'» добавлен в «Актуальное состояние» · '+microName(mid));
  return true;
}
function sensDrop(sid){
  const sp=(BANK.sphereIndex||{})[sid]||{}; const mid=sp.micro;
  if(!mid || !S.micro[mid]) return;
  const before=(S.micro[mid].items||[]).length;
  S.micro[mid].items=(S.micro[mid].items||[]).filter(i=>i.src!=='AUTO:SENS:'+sid);
  if(S.micro[mid].items.length!==before){ save(); render(); flash('Автотекст сферы «'+sphereName(sid)+'» убран из документа'); }
}
/* ---- вкладка опросника «Сенсорный профиль FEDL2i»: полная таблица A–F ---- */
function sensTab(){
  const mapTxt=sensBlocks().map(b=>{ const sp=blockSphere(b.id);
    return b.id+' → '+(sp? (sp.order+'. «'+(sp.short||sp.name)+'»') : 'справочно'); }).join('; ');
  let html=`<div class="card"><h2>Сенсорный опросник · индивидуальные особенности (FEDL2i)</h2>
    <p class="hint">Полная таблица индивидуальных особенностей: блоки A–F, ${sensTotal()} пунктов.
    Каждый блок привязан к своей сфере оценки и дополняет её: ${esc(mapTxt)}.
    Мини-таблица блока видна в карточке сферы на вкладке «Оценка: 9 сфер», а готовый текст
    собирается в карточках ниже и одной кнопкой уходит в «Актуальное состояние».
    В сферу оценки идёт только первый столбец таблицы — сами пункты; шкалы и формулировки
    правятся в Банке_фраз.xlsx (листы «Сенсорный_опросник», «Сенсорный_шкалы», «Сферы»).</p>
    <div class="row">
      <div><label class="f">Дата заполнения опросника</label>
        <input type="text" data-h="fill_date" value="${esc(S.header.fill_date||'')}" placeholder="дд.мм.гггг"></div>
    </div>
    <div class="statusbar"><span class="small muted">Заполнено пунктов: <b>${sensFilled()}</b> из ${sensTotal()}</span>
      <button class="b gray small" data-sensclear>Очистить опросник</button></div></div>`;
  sensBlocks().forEach(b=>{
    const scales=[]; b.items.forEach(it=>{ if(scales.indexOf(it.scale)<0) scales.push(it.scale); });
    const sp=blockSphere(b.id);
    html+=`<div class="card sens-blk"><h3>${esc(b.title)} `
      + (sp? `<span class="pill" style="background:var(--sn)">→ сфера ${sp.order}: ${esc(sp.short||sp.name)}</span>`
           : `<span class="pill">справочно</span>`)
      + (sp? ` <button class="b gray small" data-stab="spheres">к сфере</button>`:'') + `</h3>`
      + (b.note? `<p class="hint">${esc(b.note)}</p>`:'')
      + scales.map(sensScaleHtml).join('')
      + b.items.map(sensRowHtml).join('') + `</div>`;
  });
  html+=`<div class="card"><h3>Текст для документа — по сферам, которым принадлежат блоки</h3>
    <p class="hint">Кнопка «Собрать текст в документ» добавляет готовый абзац в микротему
    «Актуального состояния» этой сферы. Текст можно править; повторная сборка заменяет его свежим.</p></div>`;
  sensSpheres().forEach(sp=>{
    const sid=sp.id, bl=sensBlocksOf(sp), t=sensAutoTextFor(sp);
    const mid=sp.micro;
    const cur=(((S.micro||{})[mid]||{}).items||[]).find(i=>i.src==='AUTO:SENS:'+sid);
    html+=`<div class="card"><h3>Текст для документа · ${sp.order}. «${esc(sp.name)}» → ${esc(microName(mid))}</h3>
      ${cur? `<div class="auto-note">${esc(cur.text)}</div>
        <div class="statusbar" style="margin-top:6px">
          <button class="b small" data-sensapply="${sid}">пересобрать из оценок</button>
          <button class="b danger small" data-sensdrop="${sid}">убрать из документа</button></div>`
        : (t? `<div class="auto-note">${esc(t)}</div>
            <div class="statusbar" style="margin-top:6px"><button class="b small" data-sensapply="${sid}">Собрать текст в документ</button></div>`
            : `<div class="small muted">Отметьте пункты блоков ${esc(bl.join(', '))} — появится готовый текст.</div>`)}
      ${cur&&t&&cur.text!==t? `<div class="small muted" style="margin-top:6px">Оценки изменились. Свежий вариант: ${esc(t)}</div>`:''}
    </div>`;
  });
  return html;
}
/* мини-таблица FEDL2i в карточке сферы (вкладка «Оценка: 9 сфер») */
function sensMiniBlock(sp){
  const bl=sensBlocksOf(sp);
  if(!bl.length) return '';
  const sid=sp.id;
  const isA=(bl.length===1&&bl[0]==='A');
  const filledBl=bl.reduce((n,bid)=>n+sensItems(bid).filter(it=>String((S.sens||{})[it.id]||'').trim()).length,0);
  const totalBl=bl.reduce((n,bid)=>n+sensItems(bid).length,0);
  let rows='';
  bl.forEach(bid=>{ const b=sensBlock(bid); if(!b) return;
    const scales=[]; b.items.forEach(it=>{ if(scales.indexOf(it.scale)<0) scales.push(it.scale); });
    rows+=(isA? '' : `<div class="small muted" style="margin:6px 0 2px">${esc(b.title)}</div>`)
      + scales.map(sensScaleHtml).join('') + b.items.map(sensRowHtml).join(''); });
  const t=sensAutoTextFor(sp);
  const mid=sp.micro;
  const cur=(((S.micro||{})[mid]||{}).items||[]).find(i=>i.src==='AUTO:SENS:'+sid);
  const btns=`<div class="statusbar" style="margin-top:6px">
      <button class="b small" data-sensapply="${sid}">${cur? 'пересобрать текст':(isA? 'Собрать текст профиля в документ':'Собрать текст в документ')}</button>
      ${cur? `<button class="b danger small" data-sensdrop="${sid}">убрать</button>`:''}
      <button class="b gray small" data-stab="sens">Открыть таблицу A–F</button>
      <span class="small muted">заполнено ${filledBl} из ${totalBl}</span></div>`;
  if(isA) return `<div class="sens-mini"><div class="small muted" style="margin-bottom:4px">
      Сенсорные системы (блок A таблицы FEDL2i) — оценки общие с вкладкой «Сенсорный профиль»</div>
    ${rows}${cur? `<div class="auto-note">${esc(cur.text)}</div>`:''}${btns}
    ${!cur&&t? '<div class="small muted" style="margin-top:4px">Готов к сборке: '+esc(t)+'</div>':''}</div>`;
  return `<details class="sens-mini" data-sensdet="${sid}"${(S.sensOpen||{})[sid]? ' open':''}>
    <summary class="small muted">Индивидуальные особенности по таблице FEDL2i
      (блоки ${esc(bl.join(', '))}) — заполнено ${filledBl} из ${totalBl}</summary>
    ${rows}${cur? `<div class="auto-note">${esc(cur.text)}</div>`:''}${btns}
    ${!cur&&t? '<div class="small muted" style="margin-top:4px">Готов к сборке: '+esc(t)+'</div>':''}</details>`;
}
'''
insert_before('function vHelpSimple(){', BLOCK4)

# ------------------------------------------------------------------ R21: bind() — подвкладки опросника, FEDL2i, пул модалки
rep("""  const clr=$('[data-survey-clear]'); if(clr) clr.onclick=()=>{ if(confirm('Сбросить все ответы опросника?')){S.answers={};save();render();} };
  document.querySelectorAll('[data-iv2]').forEach(el=>el.oninput=()=>{S.iv2[el.dataset.iv2]=el.value; save();});""",
"""  // подвкладки опросника (Оценка: 9 сфер / Подробно: DIR / Сенсорный профиль / Вопросы ИВ)
  document.querySelectorAll('[data-stab]').forEach(b=>b.onclick=()=>{ UI.stab=b.dataset.stab; saveUI(); TAB='survey'; render(); window.scrollTo(0,0); });
  const clr=$('[data-survey-clear]'); if(clr) clr.onclick=()=>{
    const spheres=(UI.stab||'spheres')==='spheres';
    if(!confirm(spheres? 'Сбросить оценки 9 сфер? Примеры наблюдений у сфер останутся.' : 'Сбросить ответы подробного опросника DIR?')) return;
    if(spheres){ (BANK.spheres||[]).forEach(sp=>{ const a=S.answers[sp.id];
        if(a){ if(a.note) a.value=''; else delete S.answers[sp.id]; } }); }
    else { (BANK.questionnaire||[]).forEach(q=>{ delete S.answers[q.id]; }); }
    save(); render(); };
  document.querySelectorAll('[data-iv2]').forEach(el=>el.oninput=()=>{S.iv2[el.dataset.iv2]=el.value; save();});
  // сенсорный опросник FEDL2i (перенос из v2)
  document.querySelectorAll('[data-sens]').forEach(el=>{
    const ev=(el.tagName==='SELECT')?'onchange':'oninput';
    el[ev]=()=>{ S.sens[el.dataset.sens]=el.value; save(); if(TAB==='survey') render(); }; });
  const sclr=$('[data-sensclear]'); if(sclr) sclr.onclick=()=>{ if(confirm('Очистить все отметки сенсорного опросника FEDL2i?')){ S.sens={}; save(); render(); } };
  document.querySelectorAll('[data-sensapply]').forEach(b=>b.onclick=()=>sensApply(b.dataset.sensapply));
  document.querySelectorAll('[data-sensdrop]').forEach(b=>b.onclick=()=>sensDrop(b.dataset.sensdrop));
  document.querySelectorAll('[data-sensdet]').forEach(el=>el.ontoggle=()=>{ S.sensOpen[el.dataset.sensdet]=el.open; save(); });""")
rep("""  document.querySelectorAll('[data-pick]').forEach(b=>b.onclick=()=>openPicker(b.dataset.pick));""",
"""  document.querySelectorAll('[data-pick]').forEach(b=>b.onclick=()=>{
    let pool=null; if(b.dataset.pool){ try{ pool=JSON.parse(b.dataset.pool); }catch(e){ pool=null; } }
    openPicker(b.dataset.pick, '', pool); });""")

# ------------------------------------------------------------------ R22: модалка подбора — пул сферы и цвет строки по блоку
rep("""function openPicker(to, status){
  PICKER = {to:to, status:status||'', q:''};""",
"""function openPicker(to, status, pool){
  PICKER = {to:to, status:status||'', q:'', pool:(Array.isArray(pool)&&pool.length? pool : null)};""")
rep("""function pickerCandidates(){
  const to=PICKER.to;
  let list=[];
  if(to.indexOf('MICRO:')===0){ const m=to.split(':')[1];
    list=(BANK.phrases||[]).filter(p=>p.block==='AS'&&p.micro===m&&phraseV1(p)); }
  else if(to.indexOf('REC:')===0){ const t=to.split(':')[1];
    list=(BANK.phrases||[]).filter(p=>p.block==='REC'&&p.micro===t&&p.active!==false); }
  else list=(BANK.phrases||[]).filter(p=>p.block===to&&p.active!==false);""",
"""function pickerCandidates(){
  const to=PICKER.to;
  let list=[];
  if(PICKER.pool){ const set={}; PICKER.pool.forEach(id=>set[id]=1);
    list=(BANK.phrases||[]).filter(p=>set[p.id]&&p.active!==false); }
  else if(to.indexOf('MICRO:')===0){ const m=to.split(':')[1];
    list=(BANK.phrases||[]).filter(p=>p.block==='AS'&&p.micro===m&&p.active!==false); }
  else if(to.indexOf('REC:')===0){ const t=to.split(':')[1];
    list=(BANK.phrases||[]).filter(p=>p.block==='REC'&&p.micro===t&&p.active!==false); }
  else list=(BANK.phrases||[]).filter(p=>p.block===to&&p.active!==false);""")
rep('  /* счётчик и легенда кодов — перенос из v2 (запись 45) */\n  let html=\'<div class="small muted" style="margin-bottom:6px">Найдено: \'+list.length+\n    \'. Кнопка «+ добавить» кладёт фразу в «\'+esc(targetName(to))+\'».<br>\'+',
    '  /* счётчик и легенда кодов — перенос из v2 (запись 45) */\n  let html=\'<div class="small muted" style="margin-bottom:6px">Найдено: \'+list.length+\n    (PICKER.pool? \' (пул фраз сферы)\':\'\')+\'. Кнопка «+ добавить» кладёт фразу в «\'+esc(targetName(to))+\'».<br>\'+')
rep("""    html+=`<div class="prow"><div class="ptxt">${p.status&&p.status.length===2? '<span class="pill '+esc(p.status)+'">'+esc(p.status)+'</span> ':''}${esc(p.text)}
      ${meta? '<div class="small muted">'+meta+'</div>':''}</div>
      ${addBtn(p.id, to, '+ добавить')}</div>`;""",
"""    const stc=String(p.status||'').split(',')[0];
    html+=`<div class="prow ${toCls(to)}"><div class="ptxt">${p.status&&p.status.length===2? '<span class="pill '+esc(p.status)+'">'+esc(p.status)+'</span> ':''}${esc(p.text)}
      ${meta? '<div class="small muted">'+meta+'</div>':''}</div>
      ${addBtn(p.id, to, '+ добавить', null, stc)}</div>`;""")
rep("""        const dest = sv.microblock? 'MICRO:'+sv.microblock : 'ASSVC';
        html+=`<div class="prow"><div class="ptxt">${esc(sv.text)}</div>${addBtn(sv.id, dest, '+ отметить')}</div>`;""",
"""        const dest = sv.microblock? 'MICRO:'+sv.microblock : 'ASSVC';
        html+=`<div class="prow to-svc"><div class="ptxt">${esc(sv.text)}</div>${addBtn(sv.id, dest, '+ отметить', null, 'SN')}</div>`;""")
rep("""function toggleAdd(id, to){""",
"""/* цвет строки модалки и кнопок добавления — по блоку документа / статусу фразы */
function toCls(to){
  if(to==='ASSVC') return 'to-svc';
  if(to.indexOf('MICRO:')===0) return 'to-as';
  if(to.indexOf('REC:')===0) return 'to-rec';
  return ({GOAL:'to-goal',METH:'to-meth',RES:'to-res',NEXT:'to-next'})[to]||'to-as';
}
function stColor(st){ const s=String(st||'').split(',')[0];
  return (s==='S3'||s==='S2'||s==='S1'||s==='S0'||s==='SN')? ' st-'+s : ''; }
function toggleAdd(id, to){""")

# ------------------------------------------------------------------ R23: addBtn — цвет по оценке
rep("""function addBtn(id, to, freeLabel, addedLabel){
  const added=isAdded(id,to);
  const nm=esc(targetName(to));
  return '<button class="b small '+(added?'gray':'ghost')+'" data-add="'+esc(id)+'" data-to="'+esc(to)+'" '+
    'title="'+(added?'Убрать из: '+nm:'Добавить в: '+nm)+'">'+
    (added?(addedLabel||'✓ убрать'):(freeLabel||'+ в документ'))+'</button>';
}""",
"""function addBtn(id, to, freeLabel, addedLabel, stOverride){
  const added=isAdded(id,to);
  const nm=esc(targetName(to));
  const p=byId(id);
  const stc=stOverride || (p&&p.status? String(p.status).split(',')[0] : '');
  return '<button class="b small '+(added?'gray':'ghost')+stColor(stc)+'" data-add="'+esc(id)+'" data-to="'+esc(to)+'" '+
    'title="'+(added?'Убрать из: '+nm:'Добавить в: '+nm)+'">'+
    (added?(addedLabel||'✓ убрать'):(freeLabel||'+ в документ'))+'</button>';
}""")

# ------------------------------------------------------------------ R24: банк фраз — весь общий банк
rep("""  /* названия блоков и микроблоков — вместе с кодом, чтобы код не приходилось угадывать (перенос из v2, запись 45) */
  const blocks=(BANK.blocks||[]).map(b=>`<option value="${b.id}">${esc(b.name)} · ${esc(b.id)}</option>`).join('');
  const micros=(BANK.microblocks||[]).filter(m=>!m.v2only)
    .map(m=>`<option value="${m.id}">${esc(m.name)} · ${esc(m.id)}</option>`).join('');""",
"""  /* названия блоков и микроблоков — вместе с кодом, чтобы код не приходилось угадывать (перенос из v2, запись 45).
     С версии 1.3.0 V1 показывает весь общий банк (201 формулировка), включая микротемы сфер 8–9. */
  const blocks=(BANK.blocks||[]).map(b=>`<option value="${b.id}">${esc(b.name)} · ${esc(b.id)}</option>`).join('');
  const micros=(BANK.microblocks||[])
    .map(m=>`<option value="${m.id}">${esc(m.name)} · ${esc(m.id)}</option>`).join('');""")
rep("""  /* V1 показывает только свои формулировки: микротемы AS7prax/AS8vis принадлежат версии 2 */
  const all=(BANK.phrases||[]).length, own=v1PhraseCount();
  const rows=(BANK.phrases||[]).filter(p=>phraseV1(p)
    &&(!fb||p.block===fb)&&(!fm||p.micro===fm)&&(!fs||(p.status||'').indexOf(fs)>=0)
    &&(!ft||(p.text+' '+p.id+' '+(p.tags||'')).toLowerCase().indexOf(ft)>=0));
  const note=$('#bankNote');
  if(note) note.textContent = all>own
    ? 'Показаны формулировки этой версии: '+own+' из '+all+'. Ещё '+(all-own)+
      ' — микротемы «'+v2OnlyMicroNames()+'», они относятся только к Конструктору_ИВ_версия2.html.'
    : '';""",
"""  /* с версии 1.3.0 V1 показывает все формулировки общего банка (обратная связь от 2026-09-29) */
  const all=(BANK.phrases||[]).length, active=v1PhraseCount();
  const rows=(BANK.phrases||[]).filter(p=>p.active!==false
    &&(!fb||p.block===fb)&&(!fm||p.micro===fm)&&(!fs||(p.status||'').indexOf(fs)>=0)
    &&(!ft||(p.text+' '+p.id+' '+(p.tags||'')).toLowerCase().indexOf(ft)>=0));
  const note=$('#bankNote');
  if(note) note.textContent = active<all
    ? 'Показаны активные формулировки общего банка: '+active+' из '+all+' (отключённые скрыты).'
    : '';""")
rep("""    const cn=$('#bankCountSimple'); if(cn) cn.value=rows.length+' из '+v1PhraseCount();""",
"""    const cn=$('#bankCountSimple'); if(cn) cn.value=rows.length+' из '+v1PhraseCount();   // весь общий банк""")

# ------------------------------------------------------------------ R25: загрузка проекта — миграция черновика
rep("""      if(p.doc){ S=p.doc; ensureMicro(); save(); render(); flash('Проект загружен'); }""",
"""      if(p.doc){ S=migrateDoc(p.doc); ensureMicro(); save(); render(); flash('Проект загружен'); }""")
rep("""        if(b.project && b.doc){ S=b.doc; ensureMicro(); save(); render(); flash('Проект загружен'); return; }""",
"""        if(b.project && b.doc){ S=migrateDoc(b.doc); ensureMicro(); save(); render(); flash('Проект загружен'); return; }""")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('правк применено:', n_applied)
print('размер app/template.html: %.1f КБ' % (len(src.encode('utf-8'))/1024))
