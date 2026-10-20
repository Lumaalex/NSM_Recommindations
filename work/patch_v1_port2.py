# -*- coding: utf-8 -*-
"""
Пакет «V1 1.2.0», часть 2: вкладка «Банк фраз» в V1 показывает только то, что относится к V1.

A7  формулировки микротем AS7prax / AS8vis (флаг v2only) не показываются в таблице банка V1,
    фильтр «Микроблок» их не предлагает, рядом — понятная пометка «относится только к версии 2».
    (Раньше вкладка «Банк фраз» показывала все 201 формулировку, включая 14 недоступных в V1.)
A8  ensureMicro() не создаёт в черновике пустые микротемы, которых в V1 нет.
A9  счётчики банка: «всего фраз» = доступно в V1, «показано» = с учётом фильтров.
"""
import io, os, sys

TPL = os.path.join('konstruktor', 'app', 'template.html')
with io.open(TPL, encoding='utf-8') as f:
    src = f.read()
orig = src
R = []

# ---------------------------------------------------------------- A7: хелперы
R.append((
"""function phraseV1(p){ return !!p && p.active!==false && !(p.block==='AS' && microV2Only(p.micro)); }""",
"""function phraseV1(p){ return !!p && p.active!==false && !(p.block==='AS' && microV2Only(p.micro)); }
/* сколько формулировок доступно именно в V1 и какие микротемы принадлежат только версии 2 */
function v1PhraseCount(){ return (BANK.phrases||[]).filter(phraseV1).length; }
function v2OnlyMicroNames(){ return (BANK.microblocks||[]).filter(m=>m.v2only)
  .map(m=>m.name+' ('+m.id+')').join(', '); }""", 'A7 хелперы'))

# ---------------------------------------------------------------- A8: ensureMicro
A8_OLD = "  (BANK.microblocks||[]).forEach(m=>{\n" \
         "    if(m.block!=='AS') return;\n" \
         "    if(!S.micro[m.id]) S.micro[m.id]={status:'', items:[], service:''};\n" \
         "  });"
R.append((
A8_OLD,
"""  (BANK.microblocks||[]).forEach(m=>{
    if(!microV1(m)) return;   // микротемы только для версии 2 (AS7prax, AS8vis) в V1 не создаём
    if(!S.micro[m.id]) S.micro[m.id]={status:'', items:[], service:''};
  });""", 'A8 ensureMicro'))

# ---------------------------------------------------------------- A7: фильтр «Микроблок»
R.append((
"""  const micros=(BANK.microblocks||[]).map(m=>`<option value="${m.id}">${esc(m.name)} · ${esc(m.id)}</option>`).join('');""",
"""  const micros=(BANK.microblocks||[]).filter(m=>!m.v2only)
    .map(m=>`<option value="${m.id}">${esc(m.name)} · ${esc(m.id)}</option>`).join('');""", 'A7 фильтр микроблоков'))

# ---------------------------------------------------------------- A9: счётчики в продвинутом режиме
R.append((
"""      <span class="small muted">Всего фраз: <b>${BANK.phrases.length}</b></span>""",
"""      <span class="small muted">Всего фраз: <b id="bankCount">${v1PhraseCount()}</b> ·
        показано: <b id="bankRows">${v1PhraseCount()}</b></span>""", 'A9 счётчики'))

# ---------------------------------------------------------------- A7: пометка под фильтрами (продвинутый)
R.append((
"""    </div>
    <div class="scroll"><table class="bank" id="bankTable"></table></div>
  </div>""",
"""    </div>
    <div class="small muted" id="bankNote" style="margin:6px 0"></div>
    <div class="scroll"><table class="bank" id="bankTable"></table></div>
  </div>""", 'A7 пометка (продвинутый)'))

# ---------------------------------------------------------------- A7: пометка под фильтрами (простой)
R.append((
"""      <div><label class="f">Найдено</label><input type="text" id="bankCountSimple" readonly value=""></div>
    </div>
    <div class="scroll"><table class="bank" id="bankTable"></table></div>""",
"""      <div><label class="f">Найдено</label><input type="text" id="bankCountSimple" readonly value=""></div>
    </div>
    <div class="small muted" id="bankNote" style="margin:6px 0"></div>
    <div class="scroll"><table class="bank" id="bankTable"></table></div>""", 'A7 пометка (простой)'))

# ---------------------------------------------------------------- A7/A9: renderBankTable
R.append((
"""  const rows=(BANK.phrases||[]).filter(p=>(!fb||p.block===fb)&&(!fm||p.micro===fm)&&(!fs||(p.status||'').indexOf(fs)>=0)
    &&(!ft||(p.text+' '+p.id+' '+(p.tags||'')).toLowerCase().indexOf(ft)>=0));""",
"""  /* V1 показывает только свои формулировки: микротемы AS7prax/AS8vis принадлежат версии 2 */
  const all=(BANK.phrases||[]).length, own=v1PhraseCount();
  const rows=(BANK.phrases||[]).filter(p=>phraseV1(p)
    &&(!fb||p.block===fb)&&(!fm||p.micro===fm)&&(!fs||(p.status||'').indexOf(fs)>=0)
    &&(!ft||(p.text+' '+p.id+' '+(p.tags||'')).toLowerCase().indexOf(ft)>=0));
  const note=$('#bankNote');
  if(note) note.textContent = all>own
    ? 'Показаны формулировки этой версии: '+own+' из '+all+'. Ещё '+(all-own)+
      ' — микротемы «'+v2OnlyMicroNames()+'», они относятся только к Конструктору_ИВ_версия2.html.'
    : '';""", 'A7 фильтр таблицы'))

R.append((
"""    const cn=$('#bankCountSimple'); if(cn) cn.value=rows.length+' из '+BANK.phrases.length;""",
"""    const cn=$('#bankCountSimple'); if(cn) cn.value=rows.length+' из '+v1PhraseCount();""", 'A9 найдено (простой)'))

R.append((
"""  $('#bankCount')&&($('#bankCount').textContent=rows.length);""",
"""  const br=$('#bankRows'); if(br) br.textContent=rows.length;""", 'A9 показано (продвинутый)'))

for old, new, label in R:
    n = src.count(old)
    if n != 1:
        print('!! ЯКОРЬ НЕ НАЙДЕН ИЛИ НЕ ОДИН (%d) — %s' % (n, label)); sys.exit(1)
    src = src.replace(old, new, 1)
    print('   ok  %s' % label)

if src == orig:
    print('!! ничего не изменилось'); sys.exit(1)
with io.open(TPL, 'w', encoding='utf-8') as f:
    f.write(src)
print('Записано: %s (%d → %d байт)' % (TPL, len(orig), len(src)))
