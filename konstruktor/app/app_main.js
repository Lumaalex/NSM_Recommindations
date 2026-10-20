"use strict";
/* ==========================================================================
   ОСНОВНАЯ ВЕРСИЯ КОНСТРУКТОРА (мейн, v3.2.0). Поток наследует форк V2
   «от общего к частному»: оценка сфер → шаблонные фразы → цели → приёмы →
   результаты (сравнение с архивным снимком) → цели на следующий период →
   рекомендации → документ. Отличия 3.2.0 от V2 2.6.0: зелёная палитра «ИВ»;
   шкала сфер 0…6 (вместо 5…1 и S0); обязательное текстовое пояснение при
   оценке «не проявляется»; удалено поле example; добавлен шаг 8 «Наблюдения
   с занятий»; банк фраз перенесён внутрь последнего шага.
   ========================================================================== */
const V2VER = '3.3.0';   // режим «Редактор банка»: банк фраз как отдельный инструмент из трёх секций
let BANK_RETURN_STAGE = 9;   // шаг, на который возвращаемся из банка фраз
/* Формат файлов проекта основной версии — СВОЙ, не совместим с проектами старого форка V2
   (несовместимы шкалы сфер 0…6 и 5…1): чужие файлы отвергаются при загрузке. */
const PROJECT_TAG = 'iv-constructor-main-3_2';
const SNAPSHOT_TAG = PROJECT_TAG + '-snapshot';
/* Встроенный банк сборки — эталон для кнопки «Вернуть встроенный банк». */
const BANK_DEFAULT = JSON.parse(document.getElementById('bank-data').textContent);
/* --- перенос старых кодов банка на семантические (2.4.0: AS1→AS1sens, AS4→AS4ini, RC1→RC1home…).
   Объявления стоят ДО loadBank() — иначе TDZ-ошибка на первой загрузке. --- */
const CODE_MIG = BANK_DEFAULT.code_migration||{};
const migCode = id => (id && CODE_MIG[id]) || id;
/* Правки банка живут в этом браузере; ключ СВОЙ — не общий со старым форком V2. */
/* Ключи localStorage с префиксом версии: у основной 3.2.0 СВОИ ключи,
   черновики и правки банка старого форка V2 2.6.0 не подхватываются —
   форматы проектов и шкал сфер (5…1 и 0…6) несовместимы. */
const LS_BANK='iv_constructor_bank_main_3_2';
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
  const M=CODE_MIG; if(!b) return b;
  if(Object.keys(M).length){
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
  }
  const legacyScale=!(b.ped_scale||[]).some(x=>x.ped===0);
  if(legacyScale){
    const map={0:1,1:2,2:2,3:3,4:3,5:4,6:5};
    const defaults=BANK_DEFAULT.sphere_keys||{};
    b.sphere_keys=b.sphere_keys||{};
    Object.keys(b.sphere_keys).forEach(sid=>{
      if(['SPH-MOT','SPH-VIS'].includes(sid)) return;
      const old=b.sphere_keys[sid]||{}, next={};
      Object.keys(map).forEach(ns=>{
        const os=String(map[ns]), item=JSON.parse(JSON.stringify(old[os]||{}));
        ['as','goal','meth','rec','res','nxt','svc'].forEach(k=>{ if(!Array.isArray(item[k])) item[k]=[]; });
        const n=Number(ns);
        if(n<=2||n>=5) item.goal=[];
        if(n===6) item.meth=[];
        const def=((defaults[sid]||{})[ns])||{};
        if(!item.meth.length&&n!==6) item.meth=(def.meth||[]).slice();
        next[ns]=item;
      });
      ['SIG-STRESS','SIG-NOINFO'].forEach(k=>{ if(old[k]) next[k]=old[k]; });
      b.sphere_keys[sid]=next;
    });
    if(defaults['SPH-SENS']) b.sphere_keys['SPH-SENS']=JSON.parse(JSON.stringify(defaults['SPH-SENS']));
    delete b.sphere_keys['SPH-MOT']; delete b.sphere_keys['SPH-VIS'];
    b.ped_scale=JSON.parse(JSON.stringify(BANK_DEFAULT.ped_scale||[]));
  }
  b.spheres=(b.spheres||[]).filter(sp=>!['SPH-MOT','SPH-VIS'].includes(sp.id));
  const sens=(b.spheres||[]).find(sp=>sp.id==='SPH-SENS');
  if(sens) sens.sens_blocks=['A'];
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
const byId = id => BANK.phraseIndex[id];
const esc = t => String(t==null?'':t).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const $ = (s,r)=> (r||document).querySelector(s);
const $$ = (s,r)=> Array.prototype.slice.call((r||document).querySelectorAll(s));

/* ------------------------------------------------------- настройки оформления */
/* Настройки оформления (тема, размер шрифта) — общий ключ с форком V2: формат одинаковый,
   удобно, когда оба клиента на одном компьютере выглядят одинаково. Черновик проекта и правки
   банка — СВОИ ключи (см. LS_DOC / LS_BANK): форматы несовместимы со старым V2. */
const LS_UI='iv_constructor_ui';
const FS_STEPS=[0.85,1,1.15,1.3,1.5];
let UI=(function(){ try{ const o=JSON.parse(localStorage.getItem(LS_UI)||'null');
  if(o&&typeof o==='object') return {theme:o.theme==='dark'?'dark':'light',
    fsIdx:Math.min(FS_STEPS.length-1,Math.max(0,o.fsIdx|0))}; }catch(e){}
  return {theme:'light',fsIdx:1}; })();
function applyUI(){
  document.documentElement.setAttribute('data-theme',UI.theme);
  document.documentElement.style.setProperty('--fs',FS_STEPS[UI.fsIdx]);
  const t=$('#btnTheme'); if(t) t.textContent=UI.theme==='dark'?'Светлая тема':'Тёмная тема';
  const l=$('#fsLabel'); if(l) l.textContent=Math.round(FS_STEPS[UI.fsIdx]*100)+'%';
}
function saveUI(){ try{ localStorage.setItem(LS_UI,JSON.stringify(UI)); }catch(e){} }

/* ------------------------------------------------------- состояние */
/* Черновик проекта основной версии — отдельный ключ: старый форк V2 2.6.0 хранит
   черновик в iv_constructor_v2_doc; форматы несовместимы (шкалы сфер разные). */
const LS_DOC='iv_constructor_main_3_2_doc';
function blank(){ return {
  v:2, appVersion:V2VER, header:{fio:'',birth:'',fill_date:todayStr(),period_start:'',period_end:'',specialist:'',
               sessions:'', direction_name:'Игровое взаимодействие'},
  scores:{},          // sphereId -> {ped: 0..6 | signal:'SIG-…'}; сенсорная сфера оценивается опросником
  observations:{},    // sphereId -> наблюдение с занятия
  sens:{},            // itemId (FEDL2i A1…F5) -> значение шкалы
  sensOpen:{},        // sphereId -> раскрыта ли мини-таблица FEDL2i в карточке сферы
  asAuto:'',          // автотекст сенсорного профиля (блок A) — для обратной совместимости
  asAutoMap:{},       // sphereId -> автотекст из блоков FEDL2i, дополняющих сферу
  as:[], goals:[], methods:[], results:[], next:[], recs:[],   // {src,text,example,sphere}
  litPriority:[], archive:null, stage:1
}; }
/* --- перенос старых проектов/снимков на текущий набор сфер (список сфер изменён в 2.3.0) --- */
const migSid = sid => (BANK.sphere_migration||{})[sid] || sid;
/* CODE_MIG и migCode объявлены выше — до loadBank() */
function migrateScores(scores,sourceVersion){ const out={};
  const legacy=!sourceVersion || parseInt(String(sourceVersion).split('.')[0],10)<3;
  const map={1:0,2:2,3:3,4:5,5:6};
  Object.keys(scores||{}).forEach(sid=>{
    const target=migSid(sid); if(!BANK.sphereIndex[target]) return;
    if(target==='SPH-SENS') return;
    const raw=scores[sid];
    if(typeof raw==='number'||(typeof raw==='string'&&/^\d+$/.test(raw))){
      const value=Number(raw); if(legacy&&value===0) return;
      out[target]=legacy&&map[value]!==undefined?map[value]:value;
    }
    else if(raw&&typeof raw==='object'){
      const item=Object.assign({},raw);
      if(legacy&&item.signal===undefined&&item.ped===0) return;
      if(legacy&&typeof item.ped==='number'&&map[item.ped]!==undefined) item.ped=map[item.ped];
      out[target]=item;
    } else out[target]=raw;
  });
  return out; }
function normalizeDoc(d){
  if(!d||typeof d!=='object') return blank();
  ['as','goals','methods','results','next','recs','litPriority'].forEach(k=>{ if(!Array.isArray(d[k])) d[k]=[]; });
  if(!d.sens||typeof d.sens!=='object') d.sens={};
  if(!d.observations||typeof d.observations!=='object') d.observations={};
  const migratedObservations={};
  Object.keys(d.observations).forEach(sid=>{
    const target=migSid(sid), value=String(d.observations[sid]||'').trim();
    if(value) migratedObservations[target]=migratedObservations[target]
      ? migratedObservations[target]+'\n'+value : value;
  });
  d.observations=migratedObservations;
  if(!d.asAutoMap||typeof d.asAutoMap!=='object') d.asAutoMap={};
  if(d.asAuto&&!d.asAutoMap['SPH-SENS']) d.asAutoMap['SPH-SENS']=d.asAuto;
  Object.keys(d.scores||{}).forEach(sid=>{
    const target=migSid(sid), note=String((d.scores[sid]||{}).note||'').trim();
    if(note&&!d.observations[target]) d.observations[target]=note;
  });
  const appendObservation=(sid,text)=>{
    const t=String(text||'').trim(); if(!sid||!t) return;
    const prev=String(d.observations[sid]||'').trim();
    if(!prev) d.observations[sid]=t;
    else if(!prev.includes(t)) d.observations[sid]=prev+'\n'+t;
  };
  const phraseSpheres={};
  const keyKinds={as:'as',goals:'goal',methods:'meth',results:'res',next:'nxt',recs:'rec'};
  Object.keys(BANK.sphere_keys||{}).forEach(sid=>Object.keys((BANK.sphere_keys||{})[sid]||{}).forEach(level=>{
    const key=(BANK.sphere_keys[sid]||{})[level]||{};
    Object.keys(keyKinds).forEach(arrName=>(key[keyKinds[arrName]]||[]).forEach(id=>{
      const code=migCode(id); if(!phraseSpheres[code]) phraseSpheres[code]=migSid(sid);
    }));
  }));
  ['as','goals','methods','results','next','recs'].forEach(arrName=>(d[arrName]||[]).forEach(it=>{
    if(!it||!it.example) return;
    const src=it.src?migCode(it.src):'';
    const sid=migSid(it.sphere||(src?phraseSpheres[src]||'':''));
    appendObservation(sid,it.example);
  }));
  d.scores=migrateScores(d.scores,d.appVersion);
  Object.keys(d.scores||{}).forEach(sid=>{
    if(d.scores[sid]&&typeof d.scores[sid]==='object') delete d.scores[sid].note;
  });
  if(d.archive&&d.archive.scores) d.archive.scores=migrateScores(d.archive.scores,d.appVersion);
  d.appVersion=V2VER;
  ['as','goals','methods','results','next','recs'].forEach(k=>(d[k]||[]).forEach(it=>{
    if(it&&it.sphere) it.sphere=migSid(it.sphere);
    if(it&&it.src) it.src=migCode(it.src);
    if(it&&Object.prototype.hasOwnProperty.call(it,'example')) delete it.example; }));
  return d;
}
let S=(function(){ try{ const r=localStorage.getItem(LS_DOC); if(r){ const d=JSON.parse(r);
  if(d&&d.v===2) return normalizeDoc(d); } }catch(e){} return blank(); })();
function save(){ try{ localStorage.setItem(LS_DOC,JSON.stringify(S)); }catch(e){}
  const el=$('#saveinfo'); if(el) el.textContent=''; }
let flashT=null;
function flash(msg){ let el=$('#flash'); if(!el){ el=document.createElement('div'); el.id='flash';
  el.className='notice info'; el.style.position='fixed'; el.style.left='50%'; el.style.transform='translateX(-50%)';
  el.style.bottom='14px'; el.style.zIndex='80'; el.style.maxWidth='92vw'; document.body.appendChild(el); }
  el.textContent=msg; el.style.display='block';
  clearTimeout(flashT); flashT=setTimeout(()=>{ el.style.display='none'; },2600); }

/* ------------------------------------------------------- шкала */
const pedOf = sid => (S.scores[sid]||{}).ped;
const sigOf = sid => (S.scores[sid]||{}).signal;
function pedInfo(ped){ return (BANK.ped_scale||[]).find(x=>x.ped===ped); }
/* Единая шкала оценивает объём необходимой поддержки. */
function pedHint(sc){
  if(!sc) return '';
  if(sc.signal){ const g=(BANK.ped_signals||[]).find(x=>x.id===sc.signal);
    return g? `<div class="small muted" style="margin-top:4px"><b>Ориентир:</b> ${esc(g.text)}</div>`:''; }
  const i=pedInfo(sc.ped); if(!i) return '';
  return `<div class="small muted" style="margin-top:4px"><b>Ориентир:</b> ${esc(i.support||i.text)}</div>`;
}
function scoreOf(obj, sid){ const v=(obj||{})[sid]; if(v===undefined||v===null||v==='') return {};
  if(typeof v==='number') return {ped:v}; if(typeof v==='string') return {signal:v}; return v; }
function keyFor(sid){ const sc=S.scores[sid]||{};
  if(sc.signal) return ((BANK.sphere_keys||{})[sid]||{})[sc.signal] || {};
  if(typeof sc.ped==='number') return ((BANK.sphere_keys||{})[sid]||{})[sc.ped] || {};
  return {}; }

/* ------------------------------------------------------- коды v2 и карты сфер */
function codeOf(sc){ if(!sc||(typeof sc.ped!=='number'&&!sc.signal)) return '';
  if(sc.signal) return 'S0';
  const i=pedInfo(sc.ped); return i? (i.code||('L'+sc.ped)) : ''; }
function bankToCode(st){ return (BANK.bank_to_code||{})[String(st).split(',')[0]] || ''; }
function sphereMaps(){
  const m={as:{},goal:{},meth:{},rec:{}};
  (BANK.spheres||[]).forEach(sp=>{
    const keys=(BANK.sphere_keys||{})[sp.id]||{};
    Object.keys(keys).forEach(k=>{ const kk=keys[k]||{};
      ['as','goal','meth','rec'].forEach(kind=>(kk[kind]||[]).forEach(id=>{
        if(!m[kind][id]) m[kind][id]=sp.id; })); });
  });
  return m;
}
let SPH_MAPS=null; function maps(){ if(!SPH_MAPS) SPH_MAPS=sphereMaps(); return SPH_MAPS; }
function sphereOfId(kind,id){ return (maps()[kind]||{})[id]||null; }
function sphereName(sid){ const sp=BANK.sphereIndex[sid]; return sp? (sp.short||sp.name) : ''; }
function sphereChip(sid){ return sid? '<span class="pill" style="background:var(--sn)">'+esc(sphereName(sid))+'</span>' : ''; }
function groupBySphere(entries, kind){
  const byS={}; entries.forEach(en=>{ const sid=en.sphere||sphereOfId(kind,en.src)||'';
    (byS[sid]=byS[sid]||[]).push(en); });
  const out=Object.keys(byS).map(sid=>({sphere:sid, entries:byS[sid]}));
  out.sort((a,b)=>{ const oa=a.sphere?((BANK.sphereIndex[a.sphere]||{}).order||99):99;
    const ob=b.sphere?((BANK.sphereIndex[b.sphere]||{}).order||99):99; return oa-ob; });
  return out;
}

/* ------------------------------------------------------- список сущностей с тумблером */
function listHas(arr,src){ return arr.some(i=>i.src===src); }
function toggleIn(arrName, src, extra){
  const arr=S[arrName];
  const i=arr.findIndex(x=>x.src===src);
  if(i>=0){ arr.splice(i,1); flash('Убрано'); }
  else { arr.push(Object.assign({src:src, text:src? (byId(src)||{}).text||'' : '', example:''}, extra||{}));
    flash('Добавлено'); }
  save(); render();
  if(PK2) renderBank2();
}
function addBtnV2(arrName, src, freeLabel, sphere){
  const on=listHas(S[arrName],src);
  return '<button class="b small '+(on?'gray':'ghost')+'" data-tg="'+arrName+'|'+esc(src)+(sphere? '|'+sphere:'')+'">'+
    (on? '✓ убрать' : (freeLabel||'+ добавить'))+'</button>';
}
function suggRow(en, arrName, withExample, sphere){
  return '<div class="suggrow"><div class="tx">'+esc(en.text)+'</div>'+ 
    (en.src? addBtnV2(arrName, en.src, en.label||'+ добавить', sphere||en.sphere) : '')+'</div>';
}
function suggBlock(title, entries, arrName, withExample, sphere, kind){
  if(!entries.length) return '';
  let out='<div class="small muted" style="margin:8px 0 4px">'+esc(title)+'</div>';
  const groups = sphere? [{sphere:sphere, entries:entries}] : groupBySphere(entries, kind||'goal');
  groups.forEach(g=>{
    if(!sphere && g.sphere) out+='<div class="small" style="margin:9px 0 3px;color:var(--acc);font-weight:700">'+
      esc(sphereName(g.sphere))+'</div>';
    g.entries.forEach(en=>{ out+=suggRow(en, arrName, withExample, sphere||g.sphere); });
  });
  return out;
}

/* ------------------------------------------------------- БАНК ФРАЗ (модалка) */
let PK2=null;
function pkArr(){ return {AS:'as',GOAL:'goals',METH:'methods',RES:'results',NEXT:'next',REC:'recs'}[PK2.block]; }
function openBank(block, sphere){
  PK2={block:block||'AS', sphere:sphere||'', status:'', q:''};
  const ov=document.createElement('div'); ov.id='pickerOv'; ov.className='pickov';
  ov.innerHTML='<div class="pick"><div class="pickhd"><b>Банк фраз</b>'+
    '<button class="b gray small" id="pkClose">закрыть ✕</button></div>'+
    '<div class="pickfilters"><div class="row">'+
    '<div><label class="f">Блок документа</label><select id="pkBlock">'+
    ['AS','GOAL','METH','RES','NEXT','REC'].map(b=>{ const nm=((BANK.blocks||[]).find(x=>x.id===b)||{}).name||b;
      return '<option value="'+b+'" '+(b===PK2.block?'selected':'')+'>'+esc(nm)+' · '+b+'</option>'; }).join('')+
    '</select></div>'+
    '<div><label class="f">Сфера (для актуального состояния)</label><select id="pkSphere"><option value="">любая</option>'+
    (BANK.spheres||[]).map(sp=>'<option value="'+sp.id+'" '+(sp.id===PK2.sphere?'selected':'')+'>'+esc(sp.short||sp.name)+'</option>').join('')+
    '</select></div></div>'+
    '<input type="text" id="pkQ" placeholder="поиск по тексту фразы…">'+
    '<div id="pkStatus" class="scale" style="margin-top:8px"></div></div>'+
    '<div id="pkBody" class="pickbody"></div></div>';
  document.body.appendChild(ov);
  ov.onclick=e=>{ if(e.target===ov) closeBank(); };
  $('#pkClose').onclick=closeBank;
  $('#pkBlock').onchange=e=>{ PK2.block=e.target.value; renderBank2(); };
  $('#pkSphere').onchange=e=>{ PK2.sphere=e.target.value; renderBank2(); };
  $('#pkQ').oninput=e=>{ PK2.q=e.target.value.toLowerCase().trim(); renderBank2(); };
  renderBank2();
  setTimeout(()=>{ const i=$('#pkQ'); if(i) i.focus(); },50);
}
function closeBank(){ PK2=null; const ov=$('#pickerOv'); if(ov) ov.remove(); }
document.addEventListener('keydown', e=>{ if(e.key==='Escape' && PK2) closeBank(); });
function renderBank2(){
  if(!PK2) return;
  $('#pkStatus').innerHTML=['','S5','S4','S3','S2','S1','S0'].map(c=>
    '<label class="'+(PK2.status===c?'on':'')+'" data-pkst="'+c+'">'+(c||'все')+'</label>').join('');
  $$('[data-pkst]').forEach(l=>l.onclick=()=>{ PK2.status=l.dataset.pkst; renderBank2(); });
  let list=(BANK.phrases||[]).filter(p=>p.block===PK2.block&&p.active!==false);
  if(PK2.block==='AS'&&PK2.sphere){ const pool={}; sphereAsPool(PK2.sphere).forEach(p=>pool[p.id]=1);
    list=list.filter(p=>pool[p.id]); }
  if(PK2.status){ const want=CODE_STATUSES[PK2.status]||[];
    list=list.filter(p=>String(p.status||'').split(',').some(x=>want.indexOf(x.trim())>=0)); }
  if(PK2.q) list=list.filter(p=>(p.text+' '+(p.tags||'')).toLowerCase().indexOf(PK2.q)>=0);
  let html='<div class="small muted" style="margin-bottom:6px">Найдено: '+list.length+
    '. Кнопка «+ добавить» кладёт фразу в текущий блок документа.<br>Код фразы: блок · микротема · статус · номер — '+
    'например <b>AS5play-S2-07</b> = «Актуальное состояние», микротема «Игра» (AS5play), статус S2 (иногда), фраза 07.</div>';
  if(!list.length) html+='<div class="muted small" style="padding:10px">Ничего не найдено — измените фильтры.</div>';
  list.forEach(p=>{
    const bc=(BANK.bank_to_code||{})[String(p.status||'').split(',')[0]]||'';
    const sphere=PK2.block==='AS'? (PK2.sphere||sphereOfId('as',p.id)) : null;
    html+='<div class="prow"><div class="ptxt">'+(bc? '<span class="pill cd cd-'+esc(bc)+'">'+esc(bc)+'</span> ':'')+
      esc(p.text)+'<div class="small muted">'+esc(p.block)+(p.micro? ' · '+esc(p.micro):'')+
      (sphere? ' · '+esc(sphereName(sphere)):'')+'</div></div>'+
      addBtnV2(pkArr(), p.id, '+ добавить', sphere||undefined)+'</div>';
  });
  $('#pkBody').innerHTML=html;
  $$('#pkBody [data-tg]').forEach(b=>b.onclick=()=>{ const parts=b.dataset.tg.split('|');
    toggleIn(parts[0], parts[1], parts[2]? {sphere:parts[2]} : undefined); });
}

/* ------------------------------------------------------- ШАГИ */
const STAGES=[
  {n:1, name:'1. Актуальное состояние'},
  {n:2, name:'2. Сенсорный опросник'},
  {n:3, name:'3. Цели'},
  {n:4, name:'4. Приёмы'},
  {n:5, name:'5. Результаты'},
  {n:6, name:'6. Следующий период'},
  {n:7, name:'7. Рекомендации'},
  {n:8, name:'8. Наблюдения с занятий'},
  {n:9, name:'9. Итоговый документ'},
  {n:10, name:'10. Редактор банка'},  // скрытый шаг: открывается кнопкой «Банк фраз» в шапке
  {n:11, name:'11. Таблица фраз'},     // скрытый шаг: табличный вид с прямой правкой (кнопка в редакторе)
];
function stageDone(n){
  if(n===1) return (BANK.spheres||[]).some(sp=>sp.id!=='SPH-SENS'&&(()=>{const x=scoreOf(S.scores,sp.id);return typeof x.ped==='number'||x.signal;})());
  if(n===2) return sensFilled()>0;
  if(n===3) return S.as.length>0 || S.goals.length>0;
  if(n===4) return S.goals.length>0;
  if(n===5) return S.methods.length>0;
  if(n===6) return (S.next||[]).length>0;
  if(n===7) return S.recs.length>0;
  if(n===8) return Object.values(S.observations||{}).some(x=>String(x||'').trim());
  return false;   // шаги «Документ» и «Банк фраз» галочкой не помечаются
}
/* Чип специалиста в шапке — ФИО · дата заполнения · специалист и занятий видно всегда */
function specChipText(){
  const h=S.header||{};
  const sp=String(h.specialist||'').trim(), sn=String(h.sessions||'').trim();
  if(!sp&&!sn) return 'специалист не указан';
  if(!sp) return 'занятий: '+sn;
  return 'специалист: '+sp+(sn? ' · занятий: '+sn : '');
}
function render(){
  if(!STAGES.some(st=>st.n===S.stage)) S.stage=1;
  const nav=$('#steps'); nav.innerHTML='';
  STAGES.forEach(st=>{
    if(st.n>=10) return;   // редактор банка и таблица — скрытые шаги, открываются кнопкой в шапке
    const b=document.createElement('button');
    b.textContent=st.name; b.className=(S.stage===st.n?'on ':'')+(stageDone(st.n)?'done':'');
    b.onclick=()=>{ S.stage=st.n; save(); render(); window.scrollTo(0,0); };
    nav.appendChild(b);
  });
  const fns={1:vStage1,2:vSensStage,3:vStage2,4:vStage3,5:vStage4,6:vStage5,7:vStage6,8:vStageObservations,9:vStage7,10:vEditor,11:vStage9};
  $('#main').innerHTML=(fns[S.stage]||vStage1)();
  const hf=$('#hdrFio'); if(hf) hf.textContent=(S.header.fio||'').trim()||'ФИО не указано';
  const hd=$('#hdrDate'); if(hd) hd.textContent='заполнено: '+((S.header.fill_date||'').trim()||'—');
  const hs=$('#hdrSpec'); if(hs) hs.textContent=specChipText();   // специалист виден на любом шаге
  bind();
}


/* ============================================================ БАНК ФРАЗ (внутри последнего шага)
   Полный банк формулировок внутри конструктора.
   Таблица всех формулировок с фильтрами (блок/микроблок/статус/поиск), правкой прямо
   в строке (ID, блок, микроблок, статус, текст, теги, «требует примера»), добавлением
   и удалением фраз, экспортом и импортом JSON/CSV. Правки хранятся в этом браузере
   (localStorage[LS_BANK] — свой ключ основной версии, не общий со старым форком V2),
   переживают перезагрузку страницы и сразу влияют на подбор фраз во всех шагах.
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
/* ============================================================ РЕДАКТОР БАНКА (режим, v3.3.0)
   Кардинально новый способ работы с банком фраз — отдельный режим вместо таблицы.
   Три секции-конструктора:
     1. Актуальное состояние: сфера → оценка (0…6) → все фразы этой ячейки + добавление своих;
     2. Конструктор целей: выбранные цели + связанные приёмы/рекомендации + новые цели;
     3. Приёмы: по каждой цели — её приёмы + добавление новых приёмов.
   Новые фразы получают ID автоматически (следующий свободный номер GL-/MT- или серии
   микротема-статус-NN) и сразу попадают в подбор конструктора. Готовый банк выгружается
   кнопкой «Экспорт JSON» — тот же формат, что принимает tools/build_main.py.                */
let RB={open:false, sph:'', ped:null, goalSel:{}, methSel:{}};
try{ const r=localStorage.getItem('iv_constructor_main_3_2_rb'); if(r){ const d=JSON.parse(r);
  if(d&&typeof d==='object') RB=Object.assign(RB,d); } }catch(e){}
const LS_RB='iv_constructor_main_3_2_rb';
function rbSave(){ try{ localStorage.setItem(LS_RB, JSON.stringify(RB)); }catch(e){} }
function rbSphereMicros(sid){ const sp=BANK.sphereIndex[sid]||{}; return sp.micro? [sp.micro] : []; }
function rbPhrasesFor(sid,ped){
  const k=((BANK.sphere_keys||{})[sid]||{})[String(ped)]||{};
  const ids=(k.as||[]).filter(id=>byId(id));
  const micros=rbSphereMicros(sid);
  const want=['S3','S2','S1','S0','SN'][ped];   // соответствие оценки статусу фразы
  (BANK.phrases||[]).forEach(p=>{ if(p.active!==false && p.block==='AS' && micros.indexOf(p.micro)>=0
    && String(p.status||'').split(',')[0]===want && ids.indexOf(p.id)<0) ids.push(p.id); });
  return ids;
}
function rbGoalsFor(sid,ped){ const k=((BANK.sphere_keys||{})[sid]||{})[String(ped)]||{};
  return (k.goal||[]).filter(id=>byId(id)); }
function rbMethsForGoal(gid){ const p=byId(gid); if(!p) return [];
  const linked=(p.links_meth||[]).filter(id=>byId(id));
  const sid=sphereOfId('goal',gid)||''; const sc=S.scores[sid]||{};
  const k=((BANK.sphere_keys||{})[sid]||{})[typeof sc.ped==='number'?sc.ped:'']||{};
  const extra=(k.meth||[]).filter(id=>byId(id)&&linked.indexOf(id)<0);
  return {linked:linked, extra:extra}; }
function rbRecsForGoal(gid){ const p=byId(gid); if(!p) return [];
  return (p.links_rec||[]).filter(id=>byId(id)); }
function rbNextId(prefix){ let n=1,id; while(byId(id=prefix+'-'+String(n).padStart(2,'0'))) n++; return id; }
function rbNextSeriesId(micro,status){
  const pre=(micro||'AS1sens')+'-'+status+'-'; let n=1,id;
  while(byId(id=pre+String(n).padStart(2,'0'))) n++; return id; }
/* создание фразы через редактор (без prompt) */
function rbAddPhrase(opts){
  const o=opts||{};
  if(!String(o.text||'').trim()){ flash('Заполните формулировку фразы'); return null; }
  let id=o.id;
  if(o.block==='GOAL'){ id=id||rbNextId('GL'); }
  else if(o.block==='METH'){ id=id||rbNextId('MT'); }
  else { id=id||rbNextSeriesId(o.micro,o.status||'S2'); }
  if(byId(id)){ alert('Такой ID уже есть: '+id); return null; }
  const p={id:id, dir:'IV', block:o.block||'AS', micro:o.micro||'', ability:o.ability||'',
    status:o.status||(o.block==='GOAL'?'S2,S1,S0':o.block==='METH'?'S3,S2,S1,S0,SN':'S2'),
    text:String(o.text).trim(), source:'пользователь', needs_example:o.needs_example!==false,
    example_hint:o.example_hint||'', links_goal:o.links_goal||[], links_meth:o.links_meth||[],
    links_rec:o.links_rec||[], tags:o.tags||'', active:true};
  BANK.phrases.push(p); SPH_MAPS=null; BANK=indexBank(BANK); persistBank();
  flash('Фраза добавлена: '+p.id); return p;
}
/* привязка фразы к ячейке ключа сферы (as/goal/meth/rec — по блоку фразы) */
function rbBindPhraseToCell(sid,ped,phraseId){
  const keys=BANK.sphere_keys&&BANK.sphere_keys[sid]; if(!keys) return false;
  const k=keys[String(ped)]; if(!k) return false;
  const p=byId(phraseId); if(!p) return false;
  const bucket=p.block==='GOAL'?'goal':p.block==='METH'?'meth':p.block==='REC'?'rec':'as';
  k[bucket]=k[bucket]||[]; if(k[bucket].indexOf(phraseId)>=0) return false;
  k[bucket].push(phraseId); persistBank(); flash('Фраза '+phraseId+' привязана к сфере («'+ped+'»)'); return true;
}
function rbBindMethodToGoal(goalId,methId){
  const g=byId(goalId); if(!g) return false;
  g.links_meth=g.links_meth||[]; if(g.links_meth.indexOf(methId)>=0) return false;
  g.links_meth.push(methId); persistBank(); flash('Приём '+methId+' привязан к цели '+goalId); return true;
}
/* ------- карточки секций ------- */
function rbCardSphere(){
  const sphs=(BANK.spheres||[]).filter(sp=>sp.id!=='SPH-SENS');
  const sel=RB.sph&&BANK.sphereIndex[RB.sph]? RB.sph : '';
  const opts='<option value="">— выберите сферу —</option>'+sphs.map(sp=>
    '<option value="'+esc(sp.id)+'"'+(sp.id===sel?' selected':'')+'>'+esc(sp.order+'. '+sp.name)+'</option>').join('');
  let out='<div class="card"><h2>1 · Актуальное состояние</h2><p class="hint">'+
    'Выберите сферу и оценку (0…6) — редактор покажет все фразы этой ячейки: те, что привязаны в ключе сферы, '+
    'и подходящие по статусу из микроблока сферы. Здесь же можно добавить свои фразы — ID присваивается автоматически.</p>'+
    '<div class="filters"><div><label class="f">Сфера</label><select id="rbSphere">'+opts+'</select></div></div>';
  if(!sel) return out+'</div>';
  const sp=BANK.sphereIndex[sel];
  const peds=[0,1,2,3,4,5,6].map(p=>{ const i=pedInfo(p);
    return '<label class="'+(RB.ped===p?'on':'')+'" data-rbped="'+esc(sel)+'|'+p+'"><b>'+p+'</b>'+esc(i?i.name:'')+'</label>'; }).join('');
  out+='<div class="peds" style="margin:8px 0">'+peds+'</div>';
  if(typeof RB.ped!=='number') return out+'<p class="small muted">Выберите оценку сферы.</p></div>';
  const ids=rbPhrasesFor(sel,RB.ped);
  out+='<div class="small muted" style="margin-bottom:6px">Фраз на оценке '+RB.ped+': <b>'+ids.length+'</b></div>';
  out+=ids.map(id=>{ const p=byId(id); const on=listHas(S.as,id);
    return '<div class="rbrow"><span class="rbid">'+esc(p.id)+'</span><div class="tx">'+esc(p.text)+'</div>'+
      addBtnV2('as',id,on?'✓ в документе':'+ в документ',sel)+'</div>'; }).join('')||
    '<p class="small muted">Для этой ячейки фраз пока нет — добавьте свою ниже.</p>';
  out+='<details class="rbadd"'+(ids.length?'':' open')+'><summary>+ Добавить фразу в эту ячейку ('+esc(sel)+', оценка '+RB.ped+')</summary>'+
    '<div class="row"><div style="flex:2"><label class="f">Формулировка</label>'+
    '<input type="text" id="rbAsText" placeholder="Что ребёнок демонстрирует — наблюдаемо, без оценок «необходимо»"></div>'+
    '<div><label class="f">Статус</label><select id="rbAsStatus">'+
    ['S3','S2','S1','S0','SN'].map(c=>'<option value="'+c+'"'+(c===['S3','S2','S1','S0','SN'][RB.ped]?' selected':'')+'>'+c+' — '+esc(statusName(c))+'</option>').join('')+
    '</select></div></div>'+
    '<div class="row"><div><label class="f">Микроблок</label><select id="rbAsMicro">'+
    ((BANK.microblocks||[]).filter(m=>m.block==='AS').map(m=>'<option value="'+esc(m.id)+'"'+(m.id===(sp.micro||'')?' selected':'')+'>'+esc(m.name)+'</option>').join(''))+
    '</select></div><div><label class="f">Подсказка примера</label><input type="text" id="rbAsHint" placeholder="что зафиксировать на занятии"></div></div>'+
    '<button class="b small" id="rbAsAdd" style="margin-top:6px">Добавить фразу</button>'+
    '<div class="small muted" style="margin-top:4px">ID получит вид '+esc(sp.micro||'AS1sens')+'-S2-NN (следующий свободный номер серии) и фраза сразу попадёт в подбор на шаге оценки.</div>'+
    '</details>';
  return out+'</div>';
}
function rbCardGoals(){
  const sphs=(BANK.spheres||[]).filter(sp=>sp.id!=='SPH-SENS');
  const pool={}; const seen={};
  sphs.forEach(sp=>{ for(let p=0;p<=6;p++){ rbGoalsFor(sp.id,p).forEach(id=>{ if(!seen[id]){ seen[id]=1; pool[id]=sp.id; } }); } });
  (BANK.phrases||[]).forEach(x=>{ if(x.block==='GOAL'&&x.active!==false&&!seen[x.id]){ seen[x.id]=1; pool[x.id]=''; } });
  const ids=Object.keys(pool).sort((a,b)=>a.localeCompare(b));
  let out='<div class="card"><h2>2 · Конструктор целей</h2><p class="hint">'+
    'Отмечайте цели — они попадут в документ («Цели на период»). Под каждой выбранной целью редактор показывает '+
    'связанные приёмы и рекомендации, которые можно подхватить сразу. Внизу — форма новой цели (ID вида GL-NN присваивается автоматически).</p>';
  out+=ids.map(id=>{ const p=byId(id); const on=listHas(S.goals,id);
    const chip=p.sphere||pool[id];
    return '<div class="rbrow"><span class="rbid">'+esc(id)+'</span>'+
      (chip?sphereChip(chip):'')+'<div class="tx">'+esc(p.text)+'</div>'+addBtnV2('goals',id,on?'✓ убрать':'+ цель',chip||undefined)+'</div>'; }).join('');
  const chosen=S.goals.filter(x=>x.src&&byId(x.src));
  if(chosen.length){
    out+='<h3 style="margin-top:14px">Связанные приёмы и рекомендации к выбранным целям</h3>';
    chosen.forEach(g=>{ const p=byId(g.src); const lm=(p.links_meth||[]).filter(id=>byId(id));
      const lr=(p.links_rec||[]).filter(id=>byId(id));
      out+='<div class="rbgrp"><div class="small" style="font-weight:700;color:var(--acc)">'+esc(p.id)+': '+esc(p.text.slice(0,80))+(p.text.length>80?'…':'')+'</div>';
      if(lm.length) out+='<div class="rbchips">'+lm.map(id=>'<button class="b ghost small" data-rbaddmeth="'+esc(id)+'|'+esc(g.sphere||'')+'">+ приём '+esc(id)+'</button>').join(' ')+'</div>';
      if(lr.length) out+='<div class="rbchips">'+lr.map(id=>'<button class="b ghost small" data-rbaddrec="'+esc(id)+'|'+esc(g.sphere||'')+'">+ рекомендация '+esc(id)+'</button>').join(' ')+'</div>';
      if(!lm.length&&!lr.length) out+='<div class="small muted">Связей в банке нет — добавьте приём вручную в секции 3.</div>';
      out+='</div>'; });
  }
  out+='<details class="rbadd"><summary>+ Новая цель</summary>'+
    '<div class="row"><div style="flex:2"><label class="f">Формулировка цели</label><input type="text" id="rbGoalText" placeholder="Развить / укрепить … (цель выводится из оценки 3–4)</div>'+
    '<div><label class="f">Сфера</label><select id="rbGoalSphere"><option value="">— не привязывать —</option>'+
    sphs.map(sp=>'<option value="'+esc(sp.id)+'"'+(sp.id===RB.sph?' selected':'')+'>'+esc(sp.name)+'</option>').join('')+'</select></div></div>'+
    '<div class="small muted" id="rbGoalBindNote"></div>'+
    '<button class="b small" id="rbGoalAdd" style="margin-top:6px">Добавить цель (ID: GL-'+String(rbNextId('GL').slice(3))+')</button>'+
    '<div class="small muted" style="margin-top:4px">Если выбрана сфера и оценка — цель сразу привяжется к её ключу и будет предлагаться на этом уровне.</div>'+
    '</details></div>';
  return out;
}
function rbCardMethods(){
  const chosen=S.goals.filter(x=>x.src&&byId(x.src));
  let out='<div class="card"><h2>3 · Приёмы работы</h2><p class="hint">'+
    'По каждой выбранной цели — все приёмы, привязанные к ней в банке. Отмеченные приёмы попадают в документ. '+
    'Новый приём можно создать прямо здесь: он привяжется к выбранной цели (ID вида MT-NN автоматически).</p>';
  if(!chosen.length) out+='<p class="small muted">Сначала отметьте хотя бы одну цель в секции 2.</p>';
  chosen.forEach(g=>{ const p=byId(g.src); const lm=(p.links_meth||[]).filter(id=>byId(id));
    out+='<div class="rbgrp"><div class="small" style="font-weight:700;color:var(--acc)">Цель '+esc(p.id)+': '+esc(p.text.slice(0,80))+(p.text.length>80?'…':'')+'</div>';
    out+=lm.map(id=>{ const m=byId(id); const on=listHas(S.methods,id);
      return '<div class="rbrow"><span class="rbid">'+esc(id)+'</span><div class="tx">'+esc(m.text)+'</div>'+addBtnV2('methods',id,on?'✓ убрать':'+ приём',g.sphere||undefined)+'</div>'; }).join('')||
      '<div class="small muted">К этой цели приёмов в банке нет.</div>';
    out+='<details class="rbadd"><summary>+ Новый приём к цели '+esc(p.id)+'</summary>'+
      '<div class="row"><div style="flex:2"><label class="f">Формулировка приёма</label><input type="text" id="rbMethText_'+esc(p.id)+'" placeholder="Что конкретно делает специалист"></div>'+
      '<div><label class="f">Привязать ещё к целям</label><input type="text" id="rbMethMore_'+esc(p.id)+'" placeholder="через запятую: GL-03, GL-04"></div></div>'+
      '<button class="b small" data-rbaddmethnew="'+esc(p.id)+'" style="margin-top:6px">Добавить приём (ID: '+esc(rbNextId('MT'))+')</button></details>';
    out+='</div>'; });
  const orphanMeths=(BANK.phrases||[]).filter(x=>x.block==='METH'&&x.active!==false);
  out+='<details class="rbadd"><summary>Все приёмы банка ('+orphanMeths.length+')</summary>'+
    orphanMeths.map(m=>{ const on=listHas(S.methods,m.id);
      return '<div class="rbrow"><span class="rbid">'+esc(m.id)+'</span><div class="tx">'+esc(m.text)+'</div>'+addBtnV2('methods',m.id,on?'✓ убрать':'+ приём')+'</div>'; }).join('')+
    '</details>';
  return out+'</div>';
}
function vEditor(){
  return '<div class="card editor-hd"><h2>Редактор банка фраз</h2>'+
    '<p class="hint">Отдельный режим работы с банком: фразы смотрятся и добавляются не плоской таблицей, а по логике документа — '+
    'сферы и оценки → цели → приёмы. Все изменения хранятся в этом браузере и сразу действуют на обычный конструктор. '+
    'Готовый банк выгружайте кнопкой «Экспорт JSON» и кладите файл в <span class="kbd">data/phrases_main.json</span>, '+
    'затем <span class="kbd">python tools/build_main.py</span>.</p>'+
    '<div class="statusbar">'+
      '<button class="b gray small" id="edBack" data-goto="'+BANK_RETURN_STAGE+'">← Вернуться к документу</button>'+
      '<button class="b ghost small" id="edExportJson">Экспорт JSON</button>'+
      '<button class="b ghost small" id="edImport">Импорт JSON / CSV</button>'+
      '<button class="b ghost small" id="edOpenTable">Табличный вид (правка)</button>'+
      '<button class="b ghost small" id="edMentor">Фразы наставника</button>'+
      '<button class="b danger small" id="edReset">Вернуть встроенный банк</button>'+
      '<span class="small muted">Фраз активных: <b>'+bankPhraseCount()+'</b> · целей в документе: <b>'+S.goals.length+'</b></span>'+
    '</div></div>'+ rbCardSphere() + rbCardGoals() + rbCardMethods();
}
function bindEditor(){
  const sp=$('#rbSphere'); if(sp) sp.onchange=()=>{ RB.sph=sp.value; RB.ped=null; rbSave(); render(); };
  $$('[data-rbped]').forEach(l=>l.onclick=()=>{ const a=l.dataset.rbped.split('|');
    RB.sph=a[0]; RB.ped=parseInt(a[1],10); rbSave(); render(); });
  const ba=$('#rbAsAdd'); if(ba) ba.onclick=()=>{
    const t=$('#rbAsText'), st=$('#rbAsStatus'), mi=$('#rbAsMicro'), hn=$('#rbAsHint');
    const p=rbAddPhrase({block:'AS', micro:mi?mi.value:'', status:st?st.value:'S2',
      text:t?t.value:'', example_hint:hn?hn.value:''});
    if(p){ rbBindPhraseToCell(RB.sph,RB.ped,p.id); SPH_MAPS=null; render(); } };
  const ga=$('#rbGoalAdd'); if(ga) ga.onclick=()=>{
    const t=$('#rbGoalText'), s=$('#rbGoalSphere');
    const p=rbAddPhrase({block:'GOAL', text:t?t.value:''});
    if(p){ if(s&&s.value){ const sid=s.value, sc=S.scores[sid]||{};
        if(typeof sc.ped==='number') rbBindPhraseToCell(sid,sc.ped,p.id); }
      toggleIn('goals',p.id,{sphere:(s&&s.value)||RB.sph||''}); } };
  $$('[data-rbaddmeth]').forEach(b=>b.onclick=()=>{ const a=b.dataset.rbaddmeth.split('|');
    toggleIn('methods',a[0],a[1]?{sphere:a[1]}:undefined); });
  $$('[data-rbaddrec]').forEach(b=>b.onclick=()=>{ const a=b.dataset.rbaddrec.split('|');
    toggleIn('recs',a[0],a[1]?{sphere:a[1]}:undefined); });
  $$('[data-rbaddmethnew]').forEach(b=>b.onclick=()=>{ const gid=b.dataset.rbaddmethnew;
    const t=$('#rbMethText_'+gid), more=$('#rbMethMore_'+gid);
    const p=rbAddPhrase({block:'METH', text:t?t.value:''});
    if(!p) return;
    rbBindMethodToGoal(gid,p.id);
    String(more&&more.value||'').split(/[,;]/).map(s=>s.trim()).filter(Boolean)
      .forEach(g2=>{ if(byId(g2)) rbBindMethodToGoal(g2,p.id); });
    const g=byId(gid);
    toggleIn('methods',p.id,{sphere:(S.goals.find(x=>x.src===gid)||{}).sphere||''}); });
  const ej=$('#edExportJson'); if(ej) ej.onclick=exportBankJson;
  const ei=$('#edImport'); if(ei) ei.onclick=()=>{ const f=$('#fileBank'); if(f) f.click(); };
  const et=$('#edOpenTable'); if(et) et.onclick=()=>{ S.stage=11; save(); render(); window.scrollTo(0,0); };
  const em=$('#edMentor'); if(em) em.onclick=()=>openBank('AS','');
  const er=$('#edReset'); if(er) er.onclick=()=>{
    if(confirm('Вернуть встроенный банк? Все правки банка в этом браузере будут потеряны.')) resetBank(); };
}

function vStage9(){
  const blocks=(BANK.blocks||[]).map(b=>'<option value="'+esc(b.id)+'"'+(BK9.block===b.id?' selected':'')+'>'
    +esc(b.name)+' · '+esc(b.id)+'</option>').join('');
  const micros=(BANK.microblocks||[]).map(m=>'<option value="'+esc(m.id)+'"'+(BK9.micro===m.id?' selected':'')+'>'
    +esc(m.name)+' · '+esc(m.id)+'</option>').join('');
  const stats=(BANK.statuses||[]).map(s=>'<option value="'+esc(s.code)+'"'+(BK9.status===s.code?' selected':'')+'>'
    +esc(s.code)+' — '+esc(s.name)+'</option>').join('');
  return `<div class="card"><div class="statusbar"><button class="b gray small" data-goto="${BANK_RETURN_STAGE}">← Вернуться к работе</button><button class="b ghost small" data-goto="10">← К редактору банка</button></div></div>`+`<div class="card">
    <h2>Банк фраз — табличный вид</h2>
    <p class="hint">Мастер-копия банка — файл <span class="kbd">data/phrases_main.json</span> (версия данных ${esc((BANK.meta||{}).version||'?')}).
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
    <div class="notice info" style="margin-top:8px">Правки банка на этом шаге не меняют мастер-копию
    <span class="kbd">data/phrases_main.json</span>: они живут в этом браузере и в выгруженном JSON/CSV.
    Чтобы правка стала общей для всех — «Экспорт JSON» из этого шага, положить файл в
    <span class="kbd">data/phrases_main.json</span> и пересобрать конструктор
    (<span class="kbd">python tools/build_main.py</span>).</div>
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
  return 'банк_фраз_main_'+((BANK.meta||{}).version||'x')+'_'+V2VER+'.'+ext;
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

/* ------------------------------------------------------- ШАГ 1: шапка + актуальное состояние (оценка сфер) */
function vStage1(){
  const h=S.header;
  let html=`<div class="card"><h2>Шапка документа</h2>
    <div class="row">
      <div><label class="f">ФИО</label><input type="text" data-h="fio" value="${esc(h.fio)}"></div>
      <div><label class="f">Дата рождения</label><input type="text" data-h="birth" value="${esc(h.birth)}"></div>
      <div><label class="f">Дата заполнения</label><input type="text" data-h="fill_date"
        value="${esc(h.fill_date||'')}" placeholder="дд.мм.гггг"></div>
    </div>
    <div class="row">
      <div><label class="f">Период: начало</label><input type="text" data-h="period_start" value="${esc(h.period_start)}"></div>
      <div><label class="f">окончание</label><input type="text" data-h="period_end" value="${esc(h.period_end)}"></div>
      <div><label class="f">Специалист</label><input type="text" data-h="specialist" value="${esc(h.specialist)}"></div>
      <div><label class="f">Занятий</label><input type="text" data-h="sessions" value="${esc(h.sessions)}"></div>
    </div></div>`;
  /* Основной экран: шапка, сенсорный профиль и оценки остальных сфер. */
  html+=`<div class="card"><h2>Актуальное состояние</h2>
  </div>`;
  (BANK.spheres||[]).forEach(sp=>{ html+=sphereCard(sp); });
  html+=`<div class="card"><div class="statusbar">
    <button class="b gray small" data-archsave>Сохранить снимок начала периода</button>
    <button class="b" data-goto="3">Дальше: цели →</button>
    <button class="b gray small" data-clearscores>Сбросить оценки</button>
    <span class="small muted">Оценено сфер: ${(BANK.spheres||[]).filter(sp=>sp.id!=='SPH-SENS'&&(()=>{const x=scoreOf(S.scores,sp.id);return typeof x.ped==='number'||x.signal;})()).length} из ${(BANK.spheres||[]).filter(sp=>sp.id!=='SPH-SENS').length}</span>
  </div></div>`;
  return html;
}
const CODE_STATUSES={L0:['S0'],L1:['S0','S1'],L2:['S1','S2'],L3:['S1'],L4:['S1','S2'],L5:['S2'],L6:['S3'],S0:['SN']};
function sphereMicros(sid){
  const set={}; const sp=BANK.sphereIndex[sid]; if(sp&&sp.micro) set[sp.micro]=1;
  const keys=(BANK.sphere_keys||{})[sid]||{};
  Object.keys(keys).forEach(k=>((keys[k]||{}).as||[]).forEach(id=>{
    const p=byId(id); if(p&&p.micro) set[p.micro]=1; }));
  return Object.keys(set);
}
/* Пул фраз банка для сферы: явный список bank_as (когда микроблок делят две сферы)
   либо все фразы микроблоков сферы. */
function sphereAsPool(sid){
  const sp=BANK.sphereIndex[sid]||{};
  const all=(BANK.phrases||[]).filter(p=>p.block==='AS'&&p.active!==false);
  if(sp.bank_as&&sp.bank_as.length){ const set={}; sp.bank_as.forEach(id=>set[id]=1);
    return all.filter(p=>set[p.id]); }
  const ms=sphereMicros(sid);
  return all.filter(p=>ms.indexOf(p.micro)>=0);
}
function bankAsFor(sid, code){
  const want=CODE_STATUSES[code]||[];
  if(!want.length) return [];
  return sphereAsPool(sid).filter(p=>want.indexOf(String(p.status||'').split(',')[0])>=0);
}
function sphereCard(sp){
  if(sp.id==='SPH-SENS') return `<div class="sph"><div class="hd"><span class="t">${sp.order}. Переработка сенсорной информации</span></div><div class="bd">${sensMiniBlock(sp)}</div></div>`;
  const sc=scoreOf(S.scores,sp.id);
  const code=codeOf(sc);
  const peds=`${[0,1,2,3,4,5,6].map(p=>{ const i=pedInfo(p);
    return `<label class="${sc.ped===p&&!sc.signal?'on':''}" data-ped="${sp.id}|${p}">
      <b>${p}</b>${esc(i?i.name:'')}</label>`; }).join('')}`;
  const sigOn=!!sc.signal;
  const reasons=(BANK.ped_reasons||[]).map(r=>`<option ${sc.reason===r?'selected':''}>${esc(r)}</option>`).join('');
  const reason0=sc.ped===0? `<div style="margin-top:8px"><label class="f" for="reason0-${esc(sp.id)}">Почему способность не проявляется?</label>
    <select id="reason0-${esc(sp.id)}" data-reason0="${esc(sp.id)}" style="max-width:420px">
      <option value="">Выберите причину…</option>
      <option value="age" ${sc.reason==='age'?'selected':''}>Пока недоступно по возрасту ребёнка</option>
      <option value="support" ${sc.reason==='support'?'selected':''}>Недостаточно условий и поддержки других сфер</option>
    </select></div>`:'';
  const key=keyFor(sp.id);
  const asEntries=(key.as||[]).map(id=>{ const p=byId(id); return p? {src:id,text:p.text,pill:code,
    hint:p.example_hint}:null; }).filter(Boolean);
  if(code && ['L0','L1','L2','L3','L4','L5','L6'].includes(code)){
    const have={}; asEntries.forEach(e=>have[e.src]=1);
    bankAsFor(sp.id, code).forEach(p=>{ if(!have[p.id])
      asEntries.push({src:p.id,text:p.text,pill:code,hint:p.example_hint}); });
  }
  return `<div class="sph"><div class="hd"><span class="t">${sp.order}. ${esc(sp.name)}</span></div><div class="bd">
    <div class="peds">${peds}</div>
    ${reason0}
    <div class="peds" style="margin-top:6px">
      <label class="sig ${sigOn?'on':''}" data-sigtoggle="${sp.id}">Оценка невозможна</label>
      ${sigOn? `<select data-reason="${sp.id}" style="max-width:280px"><option value="">укажите причину…</option>${reasons}</select>`:''}
    </div>
    ${ (typeof sc.ped==='number'||sc.signal)? suggBlock('Предложенные формулировки:', asEntries,'as',false, sp.id):''}
    <div class="statusbar" style="margin-top:6px">
    <button class="b gray small" data-bank="AS|${sp.id}">+ другие формулировки</button>
    </div>
    </div></div>`;
}

/* ------------------------------------------------------- ШАГ 2: сенсорный опросник FEDL2i */
function sensScale(code){ return (BANK.sens_scales||{})[code] || (BANK.sens_scales||{}).yn
  || {name:'да / нет',options:['Да','Нет'],legend:''}; }
function sensBlocks(){ return BANK.sens_fedl||[]; }
function sensBlock(id){ return sensBlocks().find(b=>b.id===id) || null; }
function sensItems(id){ const b=sensBlock(id); return b? b.items : []; }
function sensFilled(){ return Object.keys(S.sens||{}).filter(k=>String(S.sens[k]||'').trim()).length; }
function sensTotal(){ return sensBlocks().reduce((a,b)=>a+b.items.length,0); }
function sensWord(v){ return (BANK.sens_words||{})[v] || v; }
/* --- какие блоки таблицы FEDL2i дополняют сферу (поле sens_blocks в листе «Сферы») --- */
function sensBlocksOf(spOrId){
  const sp=(typeof spOrId==='string')? BANK.sphereIndex[spOrId] : spOrId;
  if(!sp) return [];
  if(sp.id==='SPH-SENS') return ['A'];
  if(sp.sens_blocks&&sp.sens_blocks.length) return sp.sens_blocks.slice();
  return (sp.id==='SPH-SENS')? ['A'] : [];   // обратная совместимость со старыми сборками банка
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
/* В документ собирается текст тех блоков FEDL2i, которые привязаны к сфере */
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
  const sp=(typeof spOrId==='string')? BANK.sphereIndex[spOrId] : spOrId;
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
function autoTextOf(sid){ return sid==='SPH-SENS'? String(S.asAuto||'') : String((S.asAutoMap||{})[sid]||''); }
function setAutoText(sid,t){ S.asAutoMap=S.asAutoMap||{}; S.asAutoMap[sid]=t; if(sid==='SPH-SENS') S.asAuto=t; }
function dropAutoText(sid){ S.asAutoMap=S.asAutoMap||{}; delete S.asAutoMap[sid]; if(sid==='SPH-SENS') S.asAuto=''; }
function sensApply(sid){
  sid=sid||'SPH-SENS';
  const t=sensAutoTextFor(sid);
  if(!t){ flash('Заполните пункты блоков '+sensBlocksOf(sid).join(', ')+' в опроснике — тогда появится текст'); return false; }
  setAutoText(sid,t); save(); render();
  flash('Текст сферы «'+sphereName(sid)+'» попадёт в «Актуальное состояние» · 3');
  return true;
}
function sensRowHtml(it){
  const v=String((S.sens||{})[it.id]||'');
  const sc=sensScale(it.scale);
  let ctl;
  if(it.scale==='text') ctl=`<textarea rows="2" data-sens="${it.id}" placeholder="опишите простыми словами">${esc(v)}</textarea>`;
  else ctl=`<select data-sens="${it.id}"><option value="">—</option>`
    + sc.options.map(o=>`<option value="${esc(o)}"${v===o?' selected':''}>${esc(o)}</option>`).join('') + `</select>`;
  return `<div class="sens-row"><div class="sens-name">${esc(it.name)}</div><div class="sens-ctl">${ctl}</div></div>`;
}
function sensScaleHtml(scaleCode){
  const sc=sensScale(scaleCode);
  return `<div class="sens-scale">${sc.options.map(o=>`<span>${esc(o)}</span>`).join('')}</div>`;
}
function sensAutoCardHolder(){ return $('#sensAutoCards'); }
function sensAutoCardOne(sp){
  const sid=sp.id, bl=sensBlocksOf(sp), t=sensAutoTextFor(sp), stored=autoTextOf(sid);
  return `<div class="card"${sid==='SPH-SENS'? ' id="sensAutoCard"':''}>
    <h3>Текст для документа · ${sp.order}. «${esc(sp.name)}»</h3>
    <p class="hint">Собирается из блоков ${esc(bl.join(', '))} таблицы FEDL2i и попадает в «Актуальное состояние» · 3
    первым абзацем этой сферы. Текст можно править и убрать.</p>
    ${stored? `<div class="auto-note">${esc(stored)}</div>
      <div class="statusbar" style="margin-top:6px">
        <button class="b small" data-sensapply="${sid}">пересобрать из оценок</button>
        <button class="b danger small" data-sensdrop="${sid}">убрать из документа</button></div>`
      : (t? `<div class="statusbar"><button class="b small" data-sensapply="${sid}">Собрать текст в документ</button></div>`
          : `<div class="small muted">Отметьте пункты блоков ${esc(bl.join(', '))} — появится готовый текст.</div>`)}
    ${stored&&t&&stored!==t? `<div class="small muted" style="margin-top:6px">Оценки изменились. Свежий вариант: ${esc(t)}</div>`:''}
  </div>`;
}
function sensAutoCard(){ return sensSpheres().map(sensAutoCardOne).join(''); }
function vSensStage(){
  let html=`<div class="card"><h2>Сенсорный опросник</h2>
    <div class="statusbar"><span class="small muted">Заполнено: ${sensFilled()} из ${sensTotal()}</span>
      <button class="b gray small" data-sensclear>Очистить</button></div></div>`;
  sensBlocks().forEach(b=>{
    const scales=[]; b.items.forEach(it=>{ if(scales.indexOf(it.scale)<0) scales.push(it.scale); });
    html+=`<div class="card sens-blk"><h3>${esc(b.title)}</h3>`
      + scales.map(sensScaleHtml).join('')
      + b.items.map(sensRowHtml).join('') + `</div>`;
  });
  html+=`<div class="card"><div class="statusbar">
    <button class="b gray small" data-goto="1">← К актуальному состоянию</button>
    <button class="b" data-goto="3">Дальше: цели →</button></div></div>`;
  return html;
}

function sensMiniBlock(sp){
  if(sp.id!=='SPH-SENS') return '';
  const bl=['A'];
  let rows='';
  bl.forEach(bid=>{ const b=sensBlock(bid); if(!b) return;
    const scales=[]; b.items.forEach(it=>{ if(scales.indexOf(it.scale)<0) scales.push(it.scale); });
    rows+=scales.map(sensScaleHtml).join('') + b.items.map(sensRowHtml).join(''); });
  return `<div class="sens-mini">${rows}
    <button class="b gray small" data-goto="2">Открыть сенсорный опросник</button></div>`;
}

/* ------------------------------------------------------- ШАГ 3: цели */
function vStage2(){
  const entries=[]; const seen={};
  const push=(id,sphere)=>{ if(!seen[id]&&byId(id)){ seen[id]=1;
    entries.push({src:id,text:byId(id).text,sphere:sphere,pill:codeOf(scoreOf(S.scores,sphere)),label:'+ цель'}); } };
  (BANK.spheres||[]).forEach(sp=>{
    if(sp.id==='SPH-SENS') return;
    const sc=scoreOf(S.scores,sp.id); const code=codeOf(sc);
    if(!code) return;
    if(sc.signal||![3,4].includes(sc.ped)) return;
    const k=((BANK.sphere_keys||{})[sp.id]||{})[sc.ped]||{};
    (k.goal||[]).forEach(id=>push(id,sp.id));
  });
  S.as.forEach(it=>{ const score=scoreOf(S.scores,it.sphere); if(typeof score.ped==='number'&&![3,4].includes(score.ped)) return; const p=byId(it.src); if(p) (p.links_goal||[])
    .forEach(id=>{ if(!seen[id]) push(id, it.sphere||sphereOfId('as',it.src)); }); });
  let html=`<div class="card"><h2>Цели на период реабилитации</h2>
    </div>`;
  html+=`<div class="card">${suggBlock('Предложенные цели:', entries,'goals',false,null,'goal')}
    <div class="statusbar" style="margin-top:8px">
      <button class="b gray small" data-bank="GOAL">+ другие фразы</button>
      <button class="b ghost small" data-own="goals">+ своя цель</button></div>
    <div id="ownbox_goals" style="display:none"><textarea id="ownText_goals" rows="2" placeholder="Своя формулировка цели"></textarea>
      <button class="b small" data-ownadd="goals" style="margin-top:6px">добавить</button></div></div>`;
  html+=chosenList('goals','Выбранные цели','Дальше: приёмы →',4);
  return html;
}

/* ------------------------------------------------------- ШАГ 3: приёмы */
function vStage3(){
  const entries=[]; const seen={};
  const push=(id,sphere)=>{ if(!seen[id]&&byId(id)){ seen[id]=1;
    entries.push({src:id,text:byId(id).text,sphere:sphere,label:'+ приём'}); } };
  S.goals.forEach(g=>{ const p=byId(g.src); if(p) (p.links_meth||[])
    .forEach(id=>push(id, g.sphere||sphereOfId('goal',g.src))); });
  (BANK.spheres||[]).forEach(sp=>{ const sc=scoreOf(S.scores,sp.id); const code=codeOf(sc);
    if(sp.id==='SPH-SENS'||!code||code==='S0'||sc.ped===6) return;
    const k=((BANK.sphere_keys||{})[sp.id]||{})[sc.ped]||{};
    (k.meth||[]).forEach(id=>push(id,sp.id)); });
  let html=`<div class="card"><h2>Приёмы работы и поддержка</h2>
    <p class="hint">Здесь собраны приёмы к выбранным целям и поддержка по оценённым сферам. При оценках 0–2 это способы создать условия и сопровождать проявления, а не автоматические цели. К каждому выбранному приёму добавьте пример с занятия.</p></div>`;
  html+=`<div class="card">${suggBlock('Предложенные приёмы:', entries,'methods',true,null,'meth')}
    <div class="statusbar" style="margin-top:8px">
      <button class="b gray small" data-bank="METH">+ другие фразы</button>
      <button class="b ghost small" data-own="methods">+ свой приём</button></div>
    <div id="ownbox_methods" style="display:none"><textarea id="ownText_methods" rows="2" placeholder="Свой приём"></textarea>
      <button class="b small" data-ownadd="methods" style="margin-top:6px">добавить</button></div></div>`;
  html+=chosenList('methods','Выбранные приёмы','Дальше: результаты →',5);
  return html;
}

/* ------------------------------------------------------- ШАГ 4: результаты из архива */
function vStage4(){
  let html=`<div class="card"><h2>Результаты: было → стало</h2>
    <p class="hint">Результаты собираются сравнением с архивным снимком оценки (например, начало курса).
    Сохраните снимок в начале периода — и здесь появится динамика по сферам и готовые формулировки «стало».</p>
    <div class="archbar">
      <button class="b small" data-archsave>Сохранить снимок в проект</button>
      <button class="b small" id="archFile">Сохранить снимок в файл</button>
      <button class="b ghost small" id="archLoad">Загрузить снимок из файла</button>
      ${S.archive? `<span class="small muted">Архив от ${esc(S.archive.date)}</span>
        <button class="b gray small" id="archUse">сравнить с архивом</button>
        <button class="b danger small" id="archDrop">убрать архив</button>`:''}
    </div></div>`;
  if(S.archive){
    html+=`<div class="card"><h3>Динамика сфер</h3>`;
    (BANK.spheres||[]).forEach(sp=>{
      const a=scoreOf(S.archive.scores,sp.id); const c=scoreOf(S.scores,sp.id);
      const ah=typeof a.ped==='number', ch=typeof c.ped==='number';
      const av=ah?a.ped:0, cv=ch?c.ped:0;
      if(!ah&&!ch) return;
      const d=cv-av;
      html+=`<div class="dyn"><div><div class="small muted">было: ${a.signal? esc(a.signal): (ah? esc((pedInfo(av)||{}).name):'оценка не ставилась')}</div>
        <div class="small muted">стало: ${c.signal? esc(c.signal): (ch? esc((pedInfo(cv)||{}).name):'оценка не ставилась')}</div></div>
        <div class="${d>0?'up':(d<0?'down':'same')}">${d>0? '▲ +'+d : (d<0? '▼ '+d : '=')}</div>
        <div>${esc(sp.short||sp.name)}</div>
        <button class="b gray small" data-dynrow="${sp.id}">в текст результатов</button></div>`;
    });
    html+=`</div>`;
    const resIds=[]; const seen={};
    Object.keys(S.scores).forEach(sid=>{
      const a=scoreOf(S.archive.scores,sid); const c=scoreOf(S.scores,sid);
      if(typeof a.ped==='number'&&typeof c.ped==='number'&&c.ped>a.ped){
        const k=((BANK.sphere_keys||{})[sid]||{})[c.ped]; if(k) (k.res||[]).concat(k.as||[]).forEach(id=>{
          if(!seen[id]&&byId(id)){ seen[id]=1; resIds.push(id); } });
        ['RS-01','RS-05','RS-09','RS-10','RS-18'].map(migCode).forEach(id=>{
          if(!seen[id]){ seen[id]=1; resIds.push(id); } });
      }
    });
    const entries=resIds.map(id=>{ const p=byId(id); return {src:id,text:p.text,label:'+ в результаты'}; });
    html+=`<div class="card">${suggBlock('Формулировки устойчивых изменений (только то, что стало стабильно):',
      entries,'results',true)}
      <div class="statusbar"><button class="b gray small" data-bank="RES">+ другие фразы</button>
      <button class="b gray small" data-svcadd="RES|SV-NOREZ">служебная: изменений нет</button>
      <button class="b ghost small" data-own="results">+ своя формулировка</button></div>
      <div id="ownbox_results" style="display:none"><textarea id="ownText_results" rows="2"></textarea>
        <button class="b small" data-ownadd="results" style="margin-top:6px">добавить</button></div></div>`;
  } else {
    html+=`<div class="card">
      <div class="statusbar"><button class="b gray small" data-bank="RES">+ другие фразы</button>
      <button class="b gray small" data-svcadd="RES|SV-NOREZ">служебная: значимых изменений не зафиксировано</button>
      <button class="b ghost small" data-own="results">+ своя формулировка</button></div>
      <div id="ownbox_results" style="display:none"><textarea id="ownText_results" rows="2"></textarea>
        <button class="b small" data-ownadd="results" style="margin-top:6px">добавить</button></div></div>`;
  }
  html+=chosenList('results','Выбранные результаты','Дальше: цели на следующий период →',5);
  return html;
}

/* ------------------------------------------------------- ШАГ 5: рекомендации + литература */
function vStage5(){
  let html=`<div class="card"><h2>Цели на следующий период</h2>
    <p class="hint">Отдельный блок документа. Собирается из текущих целей, которые не закрыты результатами,
    и из сфер с оценкой 2–4; правится вручную.</p></div>`;
  html+=nextCard();
  html+=`<div class="card"><div class="statusbar">
    <button class="b" data-goto="7">Дальше: рекомендации →</button></div></div>`;
  return html;
}
function nextCard(){
  let lis='';
  (S.next||[]).forEach((it,i)=>{
    lis+=`<li><textarea data-itemtext="next:${i}" rows="2">${esc(it.text)}</textarea>
      <div class="meta"><button class="b danger small" data-itemdel="next:${i}">убрать ✕</button></div></li>`;
  });
  return `<div class="card"><h3>Цели на следующий период (${(S.next||[]).length})</h3>
    <p class="hint">Отдельный блок документа. Собирается из текущих целей, которые не закрыты результатами,
    и из сфер с оценкой 2–4. Здесь же правится вручную.</p>
    <div class="statusbar">
      <button class="b gray small" data-bank="NEXT">+ другие фразы</button>
      <button class="b small" data-nextgen>сформировать из текущих целей</button>
      ${S.nextPrev? '<button class="b gray small" data-nextundo>отменить последнюю генерацию</button>':''}
      <button class="b ghost small" data-own="next">+ своя цель</button>
    </div>
    <div id="ownbox_next" style="display:none"><textarea id="ownText_next" rows="2" placeholder="Своя цель на следующий период"></textarea>
      <button class="b small" data-ownadd="next" style="margin-top:6px">добавить</button></div>
    <ul class="items">${lis||'<li class="muted">Пока пусто.</li>'}</ul></div>`;
}
function vStage6(){
  const entries=[]; const seen={};
  const push=(id,sphere)=>{ if(!seen[id]&&byId(id)){ seen[id]=1;
    entries.push({src:id,text:byId(id).text,sphere:sphere,label:'+ рекомендация'}); } };
  (BANK.spheres||[]).forEach(sp=>{ const sc=scoreOf(S.scores,sp.id); const code=codeOf(sc);
    if(!code) return;
    const k=((BANK.sphere_keys||{})[sp.id]||{})[sc.signal||sc.ped]||{};
    (k.rec||[]).forEach(id=>push(id,sp.id)); });
  S.as.forEach(it=>{ const p=byId(it.src); if(p) (p.links_rec||[])
    .forEach(id=>{ if(!seen[id]) push(id, it.sphere||sphereOfId('as',it.src)); }); });
  S.goals.forEach(g=>{ const p=byId(g.src); if(p) (p.links_rec||[])
    .forEach(id=>{ if(!seen[id]) push(id, g.sphere||sphereOfId('goal',g.src)); }); });
  let html=`<div class="card"><h2>Рекомендации родителям</h2>
    <p class="hint">Сгруппированы по сферам; у выбранных рекомендаций видно, к какой сфере они относятся.
    Формулировки уже на языке родителя.</p></div>`;
  html+=`<div class="card">${suggBlock('Предложенные рекомендации:', entries,'recs',false,null,'rec')}
    <div class="statusbar">
      <button class="b gray small" data-bank="REC">+ другие фразы</button>
      <button class="b ghost small" data-own="recs">+ своя рекомендация</button></div>
    <div id="ownbox_recs" style="display:none"><textarea id="ownText_recs" rows="2"></textarea>
      <button class="b small" data-ownadd="recs" style="margin-top:6px">добавить</button></div></div>`;
  // литература: приоритетная подборка по профилю
  const prio=litPriority();
  html+=`<div class="card"><h3>Литература: приоритетная подборка по профилю</h3>
    <p class="hint">Отмеченные книги попадут в документ первыми с пометкой «рекомендуем начать»;
    полный утверждённый список центра прикладывается следом целиком.</p>`;
  prio.forEach(t=>{ html+=`<div class="suggrow"><div class="tx">${esc(t)}</div>
    <button class="b small ${S.litPriority.indexOf(t)>=0?'gray':'ghost'}" data-lit="${esc(t)}">
    ${S.litPriority.indexOf(t)>=0? '✓ в подборке':'+ в подборку'}</button></div>`; });
  html+=`</div>`;
  html+=chosenList('recs','Выбранные рекомендации','Дальше: наблюдения →',8);
  return html;
}
function litPriority(){
  const out=[]; const seen={};
  const spheres=(BANK.spheres||[]).filter(sp=>{ const sc=S.scores[sp.id]||{}; return typeof sc.ped==='number'&&sc.ped<=4; });
  spheres.sort((a,b)=> (S.scores[a.id].ped)-(S.scores[b.id].ped));
  spheres.forEach(sp=>{
    ((BANK.lit_rules||{})[sp.id]||[]).forEach(sub=>{
      (BANK.literature||[]).forEach(t=>{
        if(t.indexOf(sub)>=0 && !seen[t]){ seen[t]=1; out.push(t); } });
    });
  });
  return out.slice(0,6);
}

/* ------------------------------------------------------- общий список выбранного */
function chosenList(arrName,title,nextLabel,nextStage){
  const kind={goals:'goal',methods:'meth',recs:'rec'}[arrName]||null;
  const arr=S[arrName]||[];
  let lis='';
  arr.forEach((it,i)=>{
    const sph=it.sphere|| (it.src&&kind? sphereOfId(kind,it.src):null);
    lis+=`<li><textarea data-itemtext="${arrName}:${i}" rows="2">${esc(it.text)}</textarea>
      ${sph? '<div class="meta">'+sphereChip(sph)+'</div>':''}
      <div class="meta"><button class="b danger small" data-itemdel="${arrName}:${i}">убрать ✕</button></div></li>`;
  });
  return `<div class="card"><h3>${esc(title)} (${arr.length})</h3>
    <ul class="items">${lis||'<li class="muted">Пока ничего не выбрано.</li>'}</ul>
    <div class="statusbar"><button class="b" data-goto="${nextStage}">${esc(nextLabel)}</button></div></div>`;
}

/* ------------------------------------------------------- ШАГ 8: наблюдения перед документом */
function vStageObservations(){
  const missingWhy=(BANK.spheres||[]).filter(sp=>sp.id!=='SPH-SENS').filter(sp=>{
    const sc=scoreOf(S.scores,sp.id); return sc.ped===0&&!['age','support'].includes(sc.reason);
  });
  let html='<div class="card"><h2>Наблюдения с занятий</h2>'+
    (missingWhy.length? '<div class="notice err">Для оценки «Не проявляется» укажите причину в «Актуальном состоянии»: '+
      missingWhy.map(sp=>esc(sp.name)).join(', ')+'.</div>':'')+'</div>';
  (BANK.spheres||[]).forEach(sp=>{
    const sc=scoreOf(S.scores,sp.id), sensor=sp.id==='SPH-SENS';
    if(sensor){
      const text=sensAutoTextFor(sp);
      if(!text&&!String((S.observations||{})[sp.id]||'').trim()) return;
      html+=`<div class="card"><h3>${sp.order}. Переработка сенсорной информации</h3>
        ${text? `<div class="small">${esc(text)}</div>`:''}
        <label class="f">Наблюдение с занятия</label>
        <textarea rows="3" data-observation="${sp.id}">${esc((S.observations||{})[sp.id]||'')}</textarea></div>`;
      return;
    }
    if(typeof sc.ped!=='number'&&!sc.signal) return;
    const rating=sc.signal? 'Оценка невозможна' : `<b>${sc.ped}</b> · ${(pedInfo(sc.ped)||{}).name||''}`;
    const selected=(S.as||[]).filter(it=>(it.sphere||sphereOfId('as',it.src))===sp.id).map(it=>it.text).filter(Boolean);
    html+=`<div class="card"><h3>${sp.order}. ${esc(sp.name)}</h3>
      <div class="small">${sc.signal?esc(rating):rating}</div>
      ${selected.length? `<ul class="items">${selected.map(t=>`<li>${esc(t)}</li>`).join('')}</ul>`:''}
      <label class="f">Наблюдение с занятия</label>
      <textarea rows="3" data-observation="${sp.id}">${esc((S.observations||{})[sp.id]||'')}</textarea></div>`;
  });
  html+='<div class="card"><div class="statusbar"><button class="b gray small" data-goto="7">← К рекомендациям</button><button class="b" data-goto="9" '+
    (missingWhy.length?'disabled title="Сначала укажите причину оценки «Не проявляется»"':'')+'>Дальше: документ →</button></div></div>';
  return html;
}

/* ------------------------------------------------------- ШАГ 9: документ */
function buildDoc(){
  const B=[];
  const asParas=[];
  const sphereByPhrase={};
  (BANK.spheres||[]).forEach(sp=>{
    const keys=(BANK.sphere_keys||{})[sp.id]||{};
    Object.keys(keys).forEach(ped=>{ ((keys[ped]||{}).as||[]).forEach(id=>{
      if(!sphereByPhrase[id]) sphereByPhrase[id]=sp.id; }); });
  });
  const used={};
  const noManifestReason={
    age:'Пока недоступно по возрасту ребёнка.',
    support:'Недостаточно условий и поддержки других сфер для проявления этой способности.'
  };
  const sphereOf=i=> i.sphere || sphereByPhrase[i.src] ||
    ((byId(i.src)||{}).micro ? ((BANK.spheres||[]).find(sp=>sp.micro===byId(i.src).micro)||{}).id : null);
  (BANK.spheres||[]).forEach(sp=>{
    const items=[];
    S.as.forEach((i,idx)=>{ if(!used[idx]&&sphereOf(i)===sp.id){ used[idx]=1; items.push(i); } });
    const sc=scoreOf(S.scores,sp.id);
    const sig = sc.signal? (BANK.ped_signals||[]).find(x=>x.id===sc.signal) : null;
    const svc = sig? sig.svc : null;
    let texts=items.map(i=>i.text).filter(t=>t&&t.trim());
    const at=(sp.id==='SPH-SENS'? sensAutoTextFor(sp):autoTextOf(sp.id)).trim();
    if(at) texts = texts.some(x=>x===at)? texts : [at].concat(texts);
    if(svc&&BANK.svcIndex[svc]&&texts.indexOf(BANK.svcIndex[svc].text)<0)
      texts.push(BANK.svcIndex[svc].text+(sc.reason? ' Причина: '+sc.reason+'.':''));
    if(!texts.length&&svc&&BANK.svcIndex[svc])
      texts.push(BANK.svcIndex[svc].text+(sc.reason? ' Причина: '+sc.reason+'.':''));
    const observation=String((S.observations||{})[sp.id]||'').trim();
    const evaluated=sp.id==='SPH-SENS' ? (!!at||!!observation) : (typeof sc.ped==='number'||!!sc.signal);
    if(evaluated){
      let label=`${sp.order}. ${sp.id==='SPH-SENS'?'Переработка сенсорной информации':sp.name}`;
      if(sp.id!=='SPH-SENS') label+=' — '+(sc.signal?'Оценка невозможна':`${sc.ped}. ${(pedInfo(sc.ped)||{}).name||''}`);
      asParas.push({text:label,bold:true});
      if(sp.id!=='SPH-SENS'&&sc.ped===0)
        asParas.push({text:'Причина: '+(noManifestReason[sc.reason]||'[укажите причину, почему способность не проявляется]')});
    }
    texts.forEach(t=>asParas.push({text:t}));
    if(observation) asParas.push({text:'Наблюдение с занятия: '+observation});
  });
  S.as.forEach((i,idx)=>{ if(!used[idx]&&i.text&&i.text.trim()&&!asParas.some(x=>x.text===i.text))
    asParas.push({text:i.text}); });
  if(!asParas.length) asParas.push({text:'[актуальное состояние не заполнено]'});
  B.push({title:'Актуальное состояние', paras:asParas});
  const simple=arr=>{ const out=[]; (arr||[]).forEach(it=>{ if(it.text&&it.text.trim()) out.push({text:it.text}); });
    if(!out.length) out.push({text:'[блок не заполнен]'}); return out; };
  B.push({title:'Цели на период реабилитации:', paras:simple(S.goals)});
  B.push({title:'Приёмы работы:', paras:simple(S.methods)});
  B.push({title:'Результаты:', paras:simple(S.results)});
  const nextParas=simple(S.next);
  B.push({title:'Цели на следующий период:', paras:nextParas});
  const recParas=(S.recs||[]).map(i=>({text:i.text})).filter(p=>p.text&&p.text.trim());
  if(!recParas.length) recParas.push({text:'[блок не заполнен]'});
  B.push({title:'Рекомендации:', paras:recParas});
  const litParas=[];
  if(S.litPriority.length){
    litParas.push({text:'Рекомендуем начать с книг по профилю трудностей:', bold:true});
    S.litPriority.forEach(t=>litParas.push({text:t, li:true}));
    litParas.push({text:'Полный утверждённый список литературы центра:', bold:true});
  }
  (BANK.literature||[]).forEach(t=>litParas.push({text:t, li:true}));
  B.push({title:'Рекомендуемая литература:', paras:litParas});
  return {title:'Индивидуальные рекомендации по направлению «'+(S.header.direction_name||'Игровое взаимодействие')+'»',
          header:S.header, blocks:B};
}
function dateSlug(d){ return String(d||'').trim().replace(/\./g,'-'); }
function fileName(){
  const fio=(S.header.fio||'без_ФИО').trim().replace(/\s+/g,'_');
  const d=dateSlug(S.header.fill_date)||dateSlug(S.header.period_end);
  return 'Заключение_ИВ_main_'+fio+(d? '_'+d : '')+'.docx';
}
function projectFileName(){
  const fio=(S.header.fio||'черновик').trim().replace(/\s+/g,'_');
  const d=dateSlug(S.header.fill_date);
  return 'проект_main_'+fio+(d? '_'+d : '')+'.json';
}
function todayStr(){ const d=new Date();
  return ('0'+d.getDate()).slice(-2)+'.'+('0'+(d.getMonth()+1)).slice(-2)+'.'+d.getFullYear(); }
function v2Checklist(){
  const scoredSpheres=(BANK.spheres||[]).filter(sp=>sp.id!=='SPH-SENS');
  const nSph=scoredSpheres.length;
  const scored=scoredSpheres.filter(sp=>{ const sc=scoreOf(S.scores,sp.id); return typeof sc.ped==='number'||sc.signal; }).length;
  const noManifestMissing=scoredSpheres.filter(sp=>{ const sc=scoreOf(S.scores,sp.id); return sc.ped===0&&!['age','support'].includes(sc.reason); }).length;
  const terms=(S.recs||[]).filter(i=>/со-регуляция|коммуникативн|праксис|вестибулярн|проприоцеп/i.test(i.text)).length;
  return [
    {pass:scored===nSph, sev:'block',
     text:'Оценены все сферы ('+scored+'/'+nSph+'); сигнальные отметки стоят там, где оценить нельзя.'},
    {pass:noManifestMissing===0, sev:'block',
     text:'У оценок «Не проявляется» указана причина ('+noManifestMissing+' без причины).'},
    {pass:S.as.length>0, sev:'block',
     text:'Добавлены формулировки актуального состояния ('+S.as.length+').'},
    {pass:S.goals.length>0, sev:'block', text:'Есть цели ('+S.goals.length+'), выведенные из оценок и фраз.'},
    {pass:S.methods.length>0, sev:'block', text:'Есть приёмы под цели ('+S.methods.length+').'},
    {pass:S.results.length>0, sev:'block',
     text:'Результаты заполнены ('+S.results.length+'): по снимку периода или вручную.'},
    {pass:S.recs.length>0&&terms===0, sev:'warn',
     text:'Рекомендации родителям без терминов ('+S.recs.length+')'+(terms? ', подозрительных: '+terms:'')+'.'},
    {pass:(S.next||[]).length>0, sev:'warn',
     text:'Цели на следующий период: '+(S.next||[]).length+' (шаг 5). Пусто допустимо только осознанно.'},
    {pass:null, sev:'manual', text:'Проверьте вручную: нет ли противоречий между сферами и блоками документа.'},
  ];
}
function checklistCard(){
  const rows=v2Checklist();
  const fails=rows.filter(r=>r.pass===false&&r.sev==='block').length;
  const warns=rows.filter(r=>r.pass===false&&r.sev==='warn').length;
  const head = fails
    ? '<div class="notice err">Обязательных замечаний: <b>'+fails+'</b> — документ выдавать рано.</div>'
    : (warns ? '<div class="notice warn">Обязательные пункты выполнены. Предупреждений: '+warns+'.</div>'
    : '<div class="notice ok">Структурные пункты пройдены. Перед выдачей проверьте формулировки и данные.</div>');
  return '<div class="card"><h3>Самопроверка перед выдачей</h3>'+head+rows.map(r=>{
    const cls=r.pass===null?'soft':(r.pass?'pass':'fail');
    const ic=r.pass===null?'!':(r.pass?'✓':'✕');
    return '<div class="check '+cls+'"><span class="ic">'+ic+'</span><span>'+esc(r.text)+'</span></div>';
  }).join('')+'</div>';
}
function vStage7(){
  const d=buildDoc();
  let html=`<div class="toolbar"><button class="b" id="btnDocx">Скачать .docx</button>
    <button class="b ghost" id="btnCopy">Копировать текст</button>
    <button class="b ghost" id="btnPrint">Печать / PDF</button>
    <button class="b gray small" id="btnOpenBank9">Банк фраз</button>
    <span class="spacer" style="flex:1"></span>
    <span class="small muted filename">${esc(fileName())}</span></div>`;
  html+='<div id="docwrap">'+docHtml(d)+'</div>';
  return html;
}
function docHtml(d){
  let h=`<div class="doc"><h1>${esc(d.title)}</h1>`;
  const rows=[['ФИО:',d.header.fio],['Дата рождения:',d.header.birth],['Дата заполнения:',d.header.fill_date],
    ['Дата начала периода реабилитации:',d.header.period_start],
    ['Дата окончания периода реабилитации:',d.header.period_end],
    ['Специалист:',d.header.specialist],['Количество занятий:',d.header.sessions]];
  h+=`<table class="hdr">${rows.map(r=>`<tr><td style="width:44%">${esc(r[0])}</td><td>${esc(r[1]||'')}</td></tr>`).join('')}</table>`;
  d.blocks.forEach(b=>{
    h+=`<h2>${esc(b.title)}</h2>`;
    b.paras.filter(p=>!p.li).forEach(p=>{ h+=`<p${p.italic?' style="font-style:italic"':''}>${p.bold?'<b>':''}${esc(p.text)}${p.bold?'</b>':''}</p>`; });
    const lis=b.paras.filter(p=>p.li);
    if(lis.length) h+=`<ol class="lit">${lis.map(p=>`<li>${esc(p.text)}</li>`).join('')}</ol>`;
  });
  return h+'</div>';
}
function docText(d){
  let t=d.title+'\n\n';
  [['ФИО',d.header.fio],['Дата рождения',d.header.birth],['Дата заполнения',d.header.fill_date],
   ['Начало периода',d.header.period_start],
   ['Окончание периода',d.header.period_end],['Специалист',d.header.specialist],['Занятий',d.header.sessions]]
    .forEach(r=>t+=r[0]+': '+r[1]+'\n');
  t+='\n';
  d.blocks.forEach(b=>{ t+=b.title+'\n'; b.paras.forEach(p=>t+=(p.li?' • ':'')+p.text+'\n'); t+='\n'; });
  return t;
}

/* ------------------------------------------------------- события */
function bind(){
  $$('[data-h]').forEach(el=>el.oninput=()=>{ S.header[el.dataset.h]=el.value; save();
    if(el.dataset.h==='fio'){ const hf=$('#hdrFio'); if(hf) hf.textContent=(el.value||'').trim()||'ФИО не указано'; }
    if(el.dataset.h==='fill_date'){ const hd=$('#hdrDate');
      if(hd) hd.textContent='заполнено: '+((el.value||'').trim()||'—'); }
    if(el.dataset.h==='specialist'||el.dataset.h==='sessions'){ const hs=$('#hdrSpec');
      if(hs) hs.textContent=specChipText(); } });
  $$('[data-ped]').forEach(l=>l.onclick=()=>{ const [sid,p]=l.dataset.ped.split('|');
    const n=parseInt(p,10), prev=scoreOf(S.scores,sid);
    S.scores[sid]={ped:n,...(n===0&&prev.ped===0&&prev.reason?{reason:prev.reason}:{})}; save(); render(); });
  const cs=$('[data-clearscores]'); if(cs) cs.onclick=()=>{
    if(confirm('Сбросить все оценки сфер в «Актуальном состоянии»? Добавленные формулировки и выбранные блоки останутся.')){
      S.scores={}; save(); render(); flash('Оценки сброшены'); } };
  $$('[data-sigtoggle]').forEach(l=>l.onclick=()=>{ const sid=l.dataset.sigtoggle;
    const cur=scoreOf(S.scores,sid);
    if(cur.signal){ delete S.scores[sid]; if(cur.note) S.scores[sid]={note:cur.note}; }
    else { S.scores[sid]={signal:(BANK.ped_signals||[])[0].id, reason:'', note:cur.note||''}; }
    save(); render(); });
  $$('[data-reason]').forEach(sel=>sel.onchange=()=>{ const sid=sel.dataset.reason;
    S.scores[sid]=S.scores[sid]||{}; S.scores[sid].reason=sel.value; save(); });
  $$('[data-reason0]').forEach(sel=>sel.onchange=()=>{ const sid=sel.dataset.reason0;
    S.scores[sid]=S.scores[sid]||{}; S.scores[sid].reason=sel.value; save(); });
  $$('[data-observation]').forEach(el=>el.oninput=()=>{ S.observations=S.observations||{};
    S.observations[el.dataset.observation]=el.value; save(); });
  $$('[data-tg]').forEach(b=>b.onclick=()=>{ const parts=b.dataset.tg.split('|');
    toggleIn(parts[0], parts[1], parts[2]? {sphere:parts[2]} : undefined); });
  $$('[data-bank]').forEach(b=>b.onclick=()=>{ const parts=b.dataset.bank.split('|');
    openBank(parts[0], parts[1]||''); });
  $$('select[data-sens]').forEach(el=>el.onchange=()=>{
    S.sens[el.dataset.sens]=el.value; save(); render(); });
  $$('textarea[data-sens]').forEach(el=>el.oninput=()=>{
    S.sens[el.dataset.sens]=el.value; save();
    const card=sensAutoCardHolder(); if(card) card.innerHTML=sensAutoCard(); });
  $$('details[data-sensdet]').forEach(d=>d.ontoggle=()=>{ S.sensOpen=S.sensOpen||{};
    S.sensOpen[d.dataset.sensdet]=d.open; save(); });
  $$('[data-sensapply]').forEach(b=>b.onclick=()=>sensApply(b.dataset.sensapply||'SPH-SENS'));
  $$('[data-sensdrop]').forEach(b=>b.onclick=()=>{ const sid=b.dataset.sensdrop||'SPH-SENS';
    dropAutoText(sid); save(); render(); flash('Текст сферы «'+sphereName(sid)+'» убран из документа'); });
  const scl=$('[data-sensclear]'); if(scl) scl.onclick=()=>{
    if(confirm('Очистить опросник FEDL2i? Собранные тексты сфер тоже будут убраны.')){
      S.sens={}; S.asAuto=''; S.asAutoMap={}; save(); render(); flash('Опросник очищен'); } };
  $$('[data-goto]').forEach(b=>b.onclick=()=>{ S.stage=parseInt(b.dataset.goto,10); save(); render(); window.scrollTo(0,0); });
  $$('[data-own]').forEach(b=>b.onclick=()=>{ const arr=b.dataset.own; const box=$('#ownbox_'+arr);
    if(!box) return;
    if(!b.dataset.base) b.dataset.base=b.textContent;
    const open=box.style.display==='none';
    box.style.display=open?'block':'none';
    b.textContent=open? 'скрыть ввод ▴' : b.dataset.base;
    b.classList.toggle('gray',open); b.classList.toggle('ghost',!open);
    if(open){ const ta=$('#ownText_'+arr); if(ta) ta.focus(); } });
  $$('[data-ownadd]').forEach(b=>b.onclick=()=>{ const arr=b.dataset.ownadd;
    const ta=$('#ownText_'+arr); const t=(ta||{}).value||''; if(!t.trim()) return;
    S[arr].push({src:'',text:t.trim(),example:''}); if(ta) ta.value=''; save(); render(); });
  $$('[data-itemtext]').forEach(el=>el.oninput=()=>{ const [arr,i]=el.dataset.itemtext.split(':');
    S[arr][+i].text=el.value; save(); });
  $$('[data-itemdel]').forEach(b=>b.onclick=()=>{ const [arr,i]=b.dataset.itemdel.split(':');
    S[arr].splice(+i,1); save(); render(); });
  $$('[data-svcadd]').forEach(b=>b.onclick=()=>{ const [arr,sid]=b.dataset.svcadd.split('|');
    const sv=BANK.svcIndex[sid]; if(sv) S[arr].push({src:sid,text:sv.text,example:''}); save(); render(); });
  $$('[data-lit]').forEach(b=>b.onclick=()=>{ const t=b.dataset.lit;
    const i=S.litPriority.indexOf(t); if(i>=0) S.litPriority.splice(i,1); else S.litPriority.push(t);
    save(); render(); });
  $$('[data-dynrow]').forEach(b=>b.onclick=()=>{ const sid=b.dataset.dynrow;
    const sp=BANK.sphereIndex[sid]; const a=scoreOf(S.archive.scores,sid); const c=scoreOf(S.scores,sid);
    const was=typeof a.ped==='number'? (pedInfo(a.ped)||{}).name : 'оценка не ставилась';
    const now=typeof c.ped==='number'? (pedInfo(c.ped)||{}).name : (c.signal||'');
    S.results.push({src:'', example:'', text:'По сфере «'+sp.name+'»: в начале периода — '+was+
      '; к концу периода — '+now+'.'+(c.note? ' Наблюдение: '+c.note:'')});
    save(); render(); flash('Строка «было → стало» добавлена в результаты'); });
  $$('[data-archsave]').forEach(as1=>as1.onclick=()=>{
    S.archive={date:new Date().toLocaleDateString('ru-RU'), scores:JSON.parse(JSON.stringify(S.scores)),
      sens:JSON.parse(JSON.stringify(S.sens||{})), as:S.as.map(i=>({src:i.src,text:i.text}))};
    save(); render(); flash('Снимок оценки сохранён в этом проекте'); });
  const af=$('#archFile'); if(af) af.onclick=()=>{
    const snap={project:SNAPSHOT_TAG, version:V2VER,
      date:new Date().toLocaleDateString('ru-RU'),
      header:S.header, scores:JSON.parse(JSON.stringify(S.scores)),
      sens:JSON.parse(JSON.stringify(S.sens||{})), asAuto:S.asAuto||'',
      asAutoMap:JSON.parse(JSON.stringify(S.asAutoMap||{})),
      as:S.as.map(i=>({src:i.src,text:i.text}))};
    downloadBlob(new Blob([JSON.stringify(snap,null,2)],{type:'application/json'}),
      'снимок_оценки_'+(S.header.fio||'без_ФИО').replace(/\s+/g,'_')+'_'+snap.date.replace(/\./g,'-')+'.json');
    flash('Снимок сохранён в файл'); };
  const al=$('#archLoad'); if(al) al.onclick=()=>$('#fileArch').click();
  const au=$('#archUse'); if(au) au.onclick=()=>{ S.stage=5; save(); render(); };
  const ad=$('#archDrop'); if(ad) ad.onclick=()=>{ S.archive=null; save(); render(); };
  const ng=$('[data-nextgen]'); if(ng) ng.onclick=()=>{
    S.nextPrev=JSON.parse(JSON.stringify(S.next||[]));
    const list=S.goals.map(g=>({src:g.src,sphere:g.sphere,text:'Продолжать: '+g.text,example:''}));
    (BANK.spheres||[]).forEach(sp=>{ const sc=scoreOf(S.scores,sp.id);
      if(sc.ped===3||sc.ped===4){
        const k=((BANK.sphere_keys||{})[sp.id]||{})[sc.ped]||{};
        (k.goal||[]).slice(0,1).forEach(id=>{ const p=byId(id);
          if(p&&!list.some(x=>x.src===id)) list.push({src:id,sphere:sp.id,text:p.text,example:''}); });
      } });
    S.next=list; save(); render();
    flash('Цели следующего периода сформированы: '+list.length+'. Отменить — кнопка рядом.'); };
  const nu=$('[data-nextundo]'); if(nu) nu.onclick=()=>{
    S.next=S.nextPrev||[]; S.nextPrev=null; save(); render(); flash('Генерация отменена'); };
  const bd=$('#btnDocx'); if(bd) bd.onclick=exportDocx;
  const bc=$('#btnCopy'); if(bc) bc.onclick=()=>{ const t=docText(buildDoc());
    if(navigator.clipboard&&navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(()=>flash('Текст скопирован'));
    else flash('Скопируйте вручную: '+t.slice(0,40)+'…'); };
  const bp=$('#btnPrint'); if(bp) bp.onclick=()=>window.print();
  const bb=$('#btnOpenBank9'); if(bb) bb.onclick=()=>{ BANK_RETURN_STAGE=9; S.stage=10; save(); render(); window.scrollTo(0,0); };
  if(S.stage===11) bindBank9();         // скрытый шаг «Таблица фраз» — таблица и её кнопки
  if(S.stage===10) bindEditor();        // скрытый шаг «Редактор банка» — три секции-конструктора
}
function exportDocx(){
  const d=buildDoc();
  const zip=zipStore([
    {name:'[Content_Types].xml',data:CT_XML},
    {name:'_rels/.rels',data:RELS_XML},
    {name:'word/document.xml',data:buildDocumentXml(d)},
    {name:'word/styles.xml',data:STYLES_XML},
    {name:'word/numbering.xml',data:NUM_XML},
    {name:'word/_rels/document.xml.rels',data:DOC_RELS_XML}]);
  downloadBlob(new Blob([zip],{type:'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}),
    fileName());
  flash('Файл .docx сохранён');
}

/* ------------------------------------------------------- черновики */
$('#btnSave').onclick=()=>{ const blob=new Blob([JSON.stringify({project:PROJECT_TAG,version:V2VER,doc:S},null,2)],
  {type:'application/json'}); downloadBlob(blob,projectFileName()); };
$('#btnLoad').onclick=()=>$('#fileProject').click();
$('#fileProject').onchange=e=>{ const f=e.target.files[0]; if(!f) return;
  const r=new FileReader(); r.onload=()=>{ try{ const p=JSON.parse(r.result);
    if(p.project===PROJECT_TAG&&p.doc){ S=normalizeDoc(p.doc); save(); render();
      flash('Проект загружен'+(p.version? ' (версия '+p.version+')':'')); }
    else if(p.doc&&p.doc.v===2){ alert('Это проект старого форка V2 — шкалы сфер несовместимы (5…1 и 0…6). Откройте конструктор V2 2.6.0.'); }
    else alert('Это не проект основной версии'); }
    catch(err){ alert('Не читается: '+err.message); } }; r.readAsText(f,'utf-8'); e.target.value=''; };
$('#fileArch').onchange=e=>{ const f=e.target.files[0]; if(!f) return;
  const r=new FileReader(); r.onload=()=>{ try{ const p=JSON.parse(r.result);
    const src=(p.doc&&p.doc.scores)? p.doc.scores : (p.scores||null);
    if(!src) throw new Error('в файле нет оценок сфер');
    S.archive={date:(p.date||new Date().toLocaleDateString('ru-RU')), scores:migrateScores(src,p.version||(p.doc&&p.doc.appVersion)),
      asAutoMap:(p.asAutoMap||null)};
    save(); render(); flash('Архив загружен: '+Object.keys(src).length+' сфер'); }
    catch(err){ alert('Не читается архив: '+err.message); } }; r.readAsText(f,'utf-8'); e.target.value=''; };
/* Кнопка «Банк фраз» в шапке ведёт на шаг полного банка с правками.
   Окно подбора с фильтром по блоку/сфере/коду осталось на кнопках «+ другие фразы» внутри шагов. */
$('#fileBank').onchange=e=>{ const f=e.target.files[0]; if(f) importBankFile(f); e.target.value=''; };
$('#btnNew').onclick=()=>{ if(confirm('Начать новый документ? Текущий черновик основной версии будет очищен.')){
  S=blank(); S.header.fill_date=todayStr(); save(); render(); flash('Новый документ'); } };
const themeBtn=$('#btnTheme'); if(themeBtn) themeBtn.onclick=()=>{
  UI.theme=UI.theme==='dark'?'light':'dark'; saveUI(); applyUI();
};
/* «Банк фраз» в шапке: доступен с любого шага; возврат — на тот шаг, откуда открыли */
const bankTopBtn=$('#btnBankTop'); if(bankTopBtn) bankTopBtn.onclick=()=>{
  if(S.stage<10) BANK_RETURN_STAGE=S.stage;   // из редактора (10) и таблицы (11) возврат — туда, откуда зашли
  S.stage=10; save(); render(); window.scrollTo(0,0);
};

/* Общая библиотека сборки .docx (ZIP + WordprocessingML).
   Вставляется в оба интерфейса (v1 и v2) при сборке: маркер DOCX_LIB */
/* ============================================================ ЭКСПОРТ .DOCX (без внешних библиотек) */
const CRC_TBL=(()=>{let t=new Uint32Array(256);for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=c&1?0xEDB88320^(c>>>1):c>>>1;t[n]=c>>>0;}return t;})();
function crc32(u8){let c=0xFFFFFFFF;for(let i=0;i<u8.length;i++)c=CRC_TBL[(c^u8[i])&0xFF]^(c>>>8);return (c^0xFFFFFFFF)>>>0;}
function zipStore(files){
  const enc=new TextEncoder(); const chunks=[]; const central=[]; let offset=0;
  const dt=new Date(); const dosTime=((dt.getHours()<<11)|(dt.getMinutes()<<5)|(dt.getSeconds()/2))&0xFFFF;
  const dosDate=(((dt.getFullYear()-1980)<<9)|((dt.getMonth()+1)<<5)|dt.getDate())&0xFFFF;
  function u16(n){return [n&255,(n>>8)&255];}
  function u32(n){return [n&255,(n>>8)&255,(n>>16)&255,(n>>24)&255];}
  files.forEach(f=>{
    const name=enc.encode(f.name); const data=typeof f.data==='string'?enc.encode(f.data):f.data;
    const crc=crc32(data);
    const lh=[].concat(u32(0x04034b50),u16(20),u16(0x0800),u16(0),u16(dosTime),u16(dosDate),
      u32(crc),u32(data.length),u32(data.length),u16(name.length),u16(0));
    chunks.push(new Uint8Array(lh),name,data);
    const ch=[].concat(u32(0x02014b50),u16(20),u16(20),u16(0x0800),u16(0),u16(dosTime),u16(dosDate),
      u32(crc),u32(data.length),u32(data.length),u16(name.length),u16(0),u16(0),u16(0),u16(0),u32(0),u32(offset));
    central.push(new Uint8Array(ch),name);
    offset+=lh.length+name.length+data.length;
  });
  let cdSize=0; central.forEach(c=>cdSize+=c.length);
  const eocd=new Uint8Array([].concat(u32(0x06054b50),u16(0),u16(0),u16(files.length),u16(files.length),
    u32(cdSize),u32(offset),u16(0)));
  const all=chunks.concat(central,[eocd]);
  const total=all.reduce((n,c)=>n+c.length,0); const out=new Uint8Array(total); let p=0;
  all.forEach(c=>{out.set(c,p);p+=c.length;});
  return out;
}
const X=t=>String(t==null?'':t).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
function runXml(text,o){
  o=o||{}; let rpr='';
  if(o.bold) rpr+='<w:b/>';
  if(o.italic) rpr+='<w:i/>';
  if(o.size) rpr+='<w:sz w:val="'+(o.size*2)+'"/><w:szCs w:val="'+(o.size*2)+'"/>';
  return '<w:r>'+(rpr?'<w:rPr>'+rpr+'</w:rPr>':'')+'<w:t xml:space="preserve">'+X(text)+'</w:t></w:r>';
}
function paraXml(text,o){
  o=o||{}; let ppr='<w:spacing w:after="'+(o.after!=null?o.after:160)+'" w:line="259" w:lineRule="auto"/>';
  if(o.align) ppr+='<w:jc w:val="'+o.align+'"/>';
  if(o.indent) ppr+='<w:ind w:firstLine="709"/>';
  if(o.num) ppr+='<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>';
  return '<w:p><w:pPr>'+ppr+'</w:pPr>'+runXml(text,o)+'</w:p>';
}
function buildDocumentXml(d){
  const A4W=11906, A4H=16838;
  const M={top:1134,right:850,bottom:1134,left:1701};
  let body='';
  body+=paraXml(d.title,{bold:true,size:12,align:'center',after:240});
  // таблица шапки
  const rows=[['ФИО:',d.header.fio],['Дата рождения:',d.header.birth],
    ['Дата начала периода реабилитации:',d.header.period_start],
    ['Дата окончания периода реабилитации:',d.header.period_end],
    ['Специалист:',d.header.specialist],['Количество занятий:',d.header.sessions]];
  body+='<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/>'
    +'<w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    +'<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    +'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    +'<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    +'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    +'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tblBorders></w:tblPr>'
    +'<w:tblGrid><w:gridCol w:w="4200"/><w:gridCol w:w="4800"/></w:tblGrid>';
  rows.forEach(r=>{
    body+='<w:tr>'
      +'<w:tc><w:tcPr><w:tcW w:w="4200" w:type="dxa"/></w:tcPr>'+paraXml(r[0],{after:40})+'</w:tc>'
      +'<w:tc><w:tcPr><w:tcW w:w="4800" w:type="dxa"/></w:tcPr>'+paraXml(r[1]||'',{after:40})+'</w:tc>'
      +'</w:tr>';
  });
  body+='</w:tbl>'+paraXml('',{after:80});
  d.blocks.forEach(b=>{
    body+=paraXml(b.title,{bold:true,size:12,after:120});
    b.paras.forEach(p=>{
      body+= paraXml(p.text,{bold:!!p.bold,italic:!!p.italic,size:b.small?10:12,
        align:'both', num:!!p.li, after:p.li?60:160});
    });
  });
  body+='<w:sectPr><w:pgSz w:w="'+A4W+'" w:h="'+A4H+'"/>'
    +'<w:pgMar w:top="'+M.top+'" w:right="'+M.right+'" w:bottom="'+M.bottom+'" w:left="'+M.left
    +'" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>';
  return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    +'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    +'<w:body>'+body+'</w:body></w:document>';
}
const STYLES_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 +'<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
 +'<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
 +'<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="ru-RU"/></w:rPr></w:rPrDefault>'
 +'<w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="259" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
 +'<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/>'
 +'<w:pPr><w:spacing w:after="160" w:line="259" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr>'
 +'<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
 +'<w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr></w:style>'
 +'<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/></w:style>'
 +'</w:styles>';
const NUM_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 +'<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
 +'<w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/>'
 +'<w:lvlText w:val="%1."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="709" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum>'
 +'<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>';
const CT_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 +'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
 +'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
 +'<Default Extension="xml" ContentType="application/xml"/>'
 +'<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
 +'<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
 +'<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
 +'</Types>';
const RELS_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 +'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
 +'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
 +'</Relationships>';
const DOC_RELS_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 +'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
 +'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
 +'<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
 +'</Relationships>';

function downloadBlob(blob,name){
  const url=URL.createObjectURL(blob); const a=document.createElement('a');
  a.href=url; a.download=name; document.body.appendChild(a); a.click();
  setTimeout(()=>{URL.revokeObjectURL(url); a.remove();},400);
}

/* экспорт для тестов */
if (typeof window !== 'undefined') window.V2API = {
  get S(){return S}, set S(v){S=v}, get BANK(){return BANK}, set BANK(v){BANK=v},
  get __dom(){return document;},   // мини-DOM песочницы для тестов (в браузере — обычный document)
  render, buildDoc, docText, fileName, save,
  get STAGES(){return STAGES}, stageDone, v2Checklist, todayStr, projectFileName,
  PROJECT_TAG, SNAPSHOT_TAG, V2VER,
  sensAutoText, sensFilled, sensTotal, sensScale, sensItems, sensBlocks, sensApply,
  sensBlocksOf, sensSpheres, blockSphere, sensAutoTextFor, autoTextOf, setAutoText, dropAutoText,
  sphereAsPool, bankAsFor, sphereMicros, normalizeDoc, migrateScores, migCode,
  toggleIn, listHas, litPriority, keyFor, blank, codeOf, scoreOf, sphereOfId, sphereName, groupBySphere,
  pedInfo, pedHint,
  vStage1, vStageObservations, vStage9, renderBank9, bindBank9Table, bindBank9, bank9Rows, bankPhraseCount, blockName, microName,
  vEditor, bindEditor, rbCardSphere, rbCardGoals, rbCardMethods, rbPhrasesFor, rbGoalsFor, rbMethsForGoal,
  rbAddPhrase, rbBindPhraseToCell, rbBindMethodToGoal, rbNextId, rbNextSeriesId, rbSave,
  get RB(){return RB}, set RB(v){RB=v}, get LS_RB(){return LS_RB},
  statusName, bankNewPhrase, bankRenamePhrase, bankSetField, bankDeletePhrase, mergeBankRows,
  replaceBank, resetBank, importBankFile, exportBankJson, exportBankCsv, bankFileName,
  toCsv, parseCsv, splitCsvLine, persistBank, stripBank, loadBank, indexBank, migrateBankLegacy,
  specChipText, openBank, closeBank,
  get BK9(){return BK9}, set BK9(v){BK9=v}, get LS_BANK(){return LS_BANK}, get LS_DOC(){return LS_DOC},
  get BANK_DEFAULT(){return BANK_DEFAULT}, get CODE_MIG(){return CODE_MIG}, get CSV_COLS(){return CSV_COLS},
  docx:()=>zipStore([{name:'[Content_Types].xml',data:CT_XML},{name:'_rels/.rels',data:RELS_XML},
    {name:'word/document.xml',data:buildDocumentXml(buildDoc())},{name:'word/styles.xml',data:STYLES_XML},
    {name:'word/numbering.xml',data:NUM_XML},{name:'word/_rels/document.xml.rels',data:DOC_RELS_XML}])
};
const _nj=$('#nojs'); if(_nj) _nj.remove();
const _av=$('#appver'); if(_av) _av.textContent=V2VER;
document.title='Конструктор ИВ · основная версия · v'+V2VER;
if(!S.header.fill_date) S.header.fill_date=todayStr();
applyUI(); save(); render();