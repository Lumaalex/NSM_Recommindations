// Тесты форка «от общего к частному» (v2). Запуск: node tools/test_v2.js
const fs = require('fs');
const path = require('path');
const {loadApp} = require('./_harness.js');
const ROOT = path.resolve(__dirname, '..');
const g = loadApp(path.join(ROOT, 'fork_v2', 'Конструктор_ИВ_версия2.html'), {epilogue: false});

let fails = 0;
const ok = (c, m) => { console.log((c ? '  OK   ' : '  FAIL ') + m); if (!c) fails++; };
const noThrow = (n, f) => { try { const r = f(); ok(true, n); return r; }
  catch (e) { ok(false, n + ' → ' + e.message); return null; } };

console.log('\n== 1. Данные форка ==');
ok(g.BANK.spheres.length === 9, 'сфер: ' + g.BANK.spheres.length);
const SPH_NAMES = ['Сенсорная переработка информации',
  'Эмоциональный фон, саморегуляция, реакция на фрустрацию',
  'Интерес к миру, игрушкам, людям, играм',
  'Контакт, совместное внимание, реакция на общение',
  'Инициатива, цепочки общения, целенаправленность',
  'Коммуникация, речь, понимание, невербальные средства',
  'Игра: уровень, предпочтения, сюжет, правила',
  'Двигательное планирование и праксис',
  'Зрительно-пространственная обработка информации'];
ok(g.BANK.spheres.map(x => x.name).join('|') === SPH_NAMES.join('|'),
   'список сфер 1–9 соответствует утверждённому (формулировки методиста)');
ok(g.BANK.spheres.map(x => x.order).join(',') === '1,2,3,4,5,6,7,8,9', 'нумерация сфер без пропусков');
ok(g.BANK.ped_scale.length === 5, 'баллов шкалы: 5');
ok(g.BANK.ped_scale[0].ped === 5 && g.BANK.ped_scale[0].mkf === 0, 'привязка 5 → МКФ 0');
ok(g.BANK.ped_scale[4].ped === 1 && g.BANK.ped_scale[4].mkf === 4, 'привязка 1 → МКФ 4');
ok(g.BANK.ped_signals.length === 2, 'сигнальных отметок: 2');
ok(Object.keys(g.BANK.sphere_keys).length >= 9, 'ключей сфер: ' + Object.keys(g.BANK.sphere_keys).length);
ok(g.BANK.spheres.every(sp => [5, 4, 3, 2, 1].every(ped => ((g.BANK.sphere_keys || {})[sp.id] || {})[ped])
   && ((g.BANK.sphere_keys || {})[sp.id] || {})['SIG-STRESS']
   && ((g.BANK.sphere_keys || {})[sp.id] || {})['SIG-NOINFO']),
   'у каждой сферы есть ключ на оценки 5…1 и обе сигнальные отметки');

console.log('\n== 1b. Шкала: критерий через поддержку и соответствие V1 (пакет 2.5.0) ==');
ok(g.BANK.ped_scale.every(x => String(x.support || '').length > 20 && String(x.v1 || '').length > 0),
   'у каждого уровня 5…1 есть критерий через поддержку (support) и соответствие V1');
const PW = p => g.BANK.ped_scale.find(x => x.ped === p);
ok(PW(5).v1.indexOf('3 · стабильно') === 0, '5 сформирована ↔ V1 «3 · стабильно» (ресурс, поддержка не нужна)');
ok(PW(4).v1.indexOf('2 · иногда') === 0, '4 лёгкие ↔ V1 «2 · иногда» (сам, но с трудностями/избирательно)');
ok(PW(3).v1.indexOf('1 · с поддержкой') === 0, '3 умеренные ↔ V1 «1 · с поддержкой» (нужна стабильная поддержка)');
ok(PW(2).v1.indexOf('между') === 0, '2 тяжёлые ↔ между V1 «с поддержкой» и «не проявляется» (фрагментарно даже с поддержкой)');
ok(PW(1).v1.indexOf('0 · не проявляется') === 0, '1 не сформирована ↔ V1 «0 · не проявляется» (вообще не замечена)');
ok(g.BANK.ped_signals.every(x => x.v1 === 'N · не проверялось'), 'S0 ↔ V1 «N · не проверялось»');
ok(/поддержка/i.test(PW(5).support) && /ресурс/i.test(PW(5).support), 'критерий 5: поддержка не нужна, ресурс');
ok(/поддержка не нужна/i.test(PW(4).support) && /трудност/i.test(PW(4).support), 'критерий 4: поддержка не нужна, трудности есть');
ok(/Без поддержки не получается/i.test(PW(3).support), 'критерий 3: только со стабильной поддержкой');
const h3 = g.pedHint({ped: 3});
ok(typeof h3 === 'string' && h3.indexOf('Критерий') >= 0 && h3.indexOf('с поддержкой') >= 0,
   'pedHint({ped:3}) показывает критерий и соответствие V1');
const hSig = g.pedHint({signal: 'SIG-STRESS'});
ok(hSig.indexOf('не проверялось') >= 0, 'pedHint для S0 показывает «N · не проверялось»');
ok(g.pedHint({}) === '', 'pedHint без оценки — пустая строка');

console.log('\n== 2. Актуальное состояние: оценки сфер и выпадение фраз ==');
g.S = g.blank();
g.S.header = {fio: 'Тестов Т.', birth: '01.01.2019', period_start: '01.09.2026', period_end: '30.09.2026',
  specialist: 'Петрова А.И.', sessions: '10', direction_name: 'Игровое взаимодействие'};
const scores = {'SPH-SENS': 4, 'SPH-REG': 3, 'SPH-WOR': 4, 'SPH-KON': 2, 'SPH-INI': 3,
                'SPH-COM': 3, 'SPH-SYM': 2, 'SPH-MOT': 4, 'SPH-VIS': 'SIG-NOINFO'};
Object.keys(scores).forEach(sid => {
  const v = scores[sid];
  g.S.scores[sid] = (typeof v === 'number') ? {ped: v, note: 'наблюдение по ' + sid} : {signal: v, note: ''};
});
const kReg = g.keyFor('SPH-REG');
ok((kReg.as || []).length >= 2, 'для оценки 3 выпадают формулировки саморегуляции: ' + (kReg.as || []).length);
const kSig = g.keyFor('SPH-VIS');
ok((kSig.svc || []).length >= 1, 'сигнальная отметка даёт служебную фразу');
(kReg.as || []).forEach(id => g.toggleIn('as', id));
ok(g.S.as.length === (kReg.as || []).length, 'формулировки добавлены в актуальное состояние: ' + g.S.as.length);
g.toggleIn('as', kReg.as[0]); g.toggleIn('as', kReg.as[0]);
ok(g.listHas(g.S.as, kReg.as[0]), 'тумблер добавить/убрать работает в обе стороны');

console.log('\n== 3. Каскад: цели из оценок и фраз, приёмы из целей ==');
const goalIds = [];
Object.keys(g.S.scores).forEach(sid => {
  const sc = g.S.scores[sid];
  const k = ((g.BANK.sphere_keys || {})[sid] || {})[sc.signal || sc.ped];
  if (k) (k.goal || []).forEach(id => { if (goalIds.indexOf(id) < 0) goalIds.push(id); });
});
g.S.as.forEach(it => { const p = g.byId ? g.byId(it.src) : g.BANK.phraseIndex[it.src];
  if (p) (p.links_goal || []).forEach(id => { if (goalIds.indexOf(id) < 0) goalIds.push(id); }); });
ok(goalIds.length >= 6, 'целей предложено: ' + goalIds.length);
goalIds.slice(0, 6).forEach(id => g.toggleIn('goals', id));
ok(g.S.goals.length === 6, 'выбрано целей: 6');
const methIds = [];
g.S.goals.forEach(gl => { const p = g.BANK.phraseIndex[gl.src];
  if (p) (p.links_meth || []).forEach(id => { if (methIds.indexOf(id) < 0) methIds.push(id); }); });
ok(methIds.length >= 4, 'приёмов предложено из целей: ' + methIds.length);
methIds.slice(0, 4).forEach(id => { g.toggleIn('methods', id); });
g.S.methods.forEach(m => m.example = 'На 3 занятии педагог…, ребёнок…');
ok(g.S.methods.every(m => m.example), 'у приёмов проставлены примеры');

console.log('\n== 4. Результаты из архива ==');
g.S.archive = {date: '01.09.2026', scores: {'SPH-SENS': {ped: 3}, 'SPH-REG': {ped: 2}, 'SPH-WOR': {ped: 3},
  'SPH-KON': {ped: 2}, 'SPH-INI': {ped: 1}, 'SPH-COM': {ped: 2}, 'SPH-SYM': {ped: 1},
  'SPH-MOT': {ped: 3}, 'SPH-VIS': {ped: 1}}};
const improved = Object.keys(g.S.scores).filter(sid => {
  const a = (g.S.archive.scores || {})[sid] || {}, c = g.S.scores[sid] || {};
  return a.ped && c.ped && c.ped > a.ped; });
ok(improved.length >= 3, 'сфер с положительной динамикой: ' + improved.length);
improved.forEach(sid => {
  const sp = g.BANK.sphereIndex[sid]; const a = g.S.archive.scores[sid]; const c = g.S.scores[sid];
  g.S.results.push({src: '', example: '', text: 'По сфере «' + sp.name + '»: в начале периода — ' +
    a.ped + '; к концу периода — ' + c.ped + '.'});
});
ok(g.S.results.length >= 3, 'строк «было → стало»: ' + g.S.results.length);

console.log('\n== 5. Рекомендации и литература по профилю ==');
const recIds = [];
Object.keys(g.S.scores).forEach(sid => {
  const sc = g.S.scores[sid];
  const k = ((g.BANK.sphere_keys || {})[sid] || {})[sc.signal || sc.ped];
  if (k) (k.rec || []).forEach(id => { if (recIds.indexOf(id) < 0) recIds.push(id); });
});
ok(recIds.length >= 6, 'рекомендаций предложено: ' + recIds.length);
recIds.slice(0, 8).forEach(id => g.toggleIn('recs', id));
const prio = noThrow('litPriority()', () => g.litPriority());
ok(prio && prio.length >= 2, 'приоритетная литература по профилю: ' + (prio ? prio.length : 0) + ' книг');
g.S.litPriority = (prio || []).slice(0, 3);

console.log('\n== 6. Документ ==');
const doc = noThrow('buildDoc()', () => g.buildDoc());
ok(doc && doc.blocks.length === 7, 'блоков: ' + (doc ? doc.blocks.length : 0));
const uniq = new Set(doc.blocks[0].paras.map(p => p.text));
ok(doc.blocks[0].paras.length === uniq.size && doc.blocks[0].paras.length >= g.S.as.length,
   'актуальное состояние: фразы сгруппированы по сферам без дублей (' + doc.blocks[0].paras.length + ')');
const lit = doc.blocks.find(b => /литератур/i.test(b.title));
ok(lit.paras.filter(p => p.li).length >= g.BANK.literature.length,
   'литература полная + приоритет: ' + lit.paras.filter(p => p.li).length);
ok(lit.paras.some(p => /начать с книг/.test(p.text)), 'приоритетная подборка помечена');
const txt = noThrow('docText()', () => g.docText(doc));
ok(txt && txt.length > 4000, 'текст: ' + (txt ? txt.length : 0) + ' символов');
const zip = noThrow('docx()', () => g.docx());
ok(zip && zip.length > 5000 && zip[0] === 0x50 && zip[1] === 0x4b, 'ZIP-сигнатура .docx на месте');
fs.writeFileSync(path.join(__dirname, '_v2_test.docx'), Buffer.from(zip));

console.log('\n== 7. Рендер всех шагов ==');
ok(g.STAGES.length === 9, 'шагов: ' + g.STAGES.length);
ok(g.STAGES[1].name === '2. Сенсорный опросник', 'шаг 2 — сенсорный опросник');
ok(g.STAGES[7].name === '8. Документ', 'документ — шаг 8');
ok(g.STAGES[8].name === '9. Банк фраз', 'банк фраз — шаг 9 (2.6.0)');
for (let st = 1; st <= 9; st++) {
  g.S.stage = st;
  noThrow('шаг ' + st, () => g.render());
}
console.log('\n== 8. Баг: все тексты актуального состояния в документе ==');
g.S = g.blank();
g.S.scores = {'SPH-REG': {ped: 3}, 'SPH-WOR': {ped: 3}, 'SPH-KON': {ped: 2},
              'SPH-INI': {ped: 4}, 'SPH-SYM': {ped: 4}};
[['AS1sens-S1-01', 'SPH-WOR'], ['AS2emo-S1-03', 'SPH-REG'], ['AS4ini-S2-05', 'SPH-INI'],
 ['AS4ini-S2-01', 'SPH-KON'], ['AS5play-S2-02', 'SPH-SYM']].forEach(([id, sp]) =>
  g.S.as.push({src: id, text: g.BANK.phraseIndex[id].text, example: '', sphere: sp}));
g.S.as.push({src: '', text: 'Своя формулировка без привязки к сфере', example: ''});
const doc8 = g.buildDoc();
ok(doc8.blocks[0].paras.length === 6, 'все 6 текстов актуального состояния в документе (было: только первые)');
ok(new Set(doc8.blocks[0].paras.map(p => p.text)).size === 6, 'без дублей');

console.log('\n== 9. Коды S5..S0 и причины ==');
ok(g.codeOf({ped: 5}) === 'S5' && g.codeOf({ped: 3}) === 'S3' && g.codeOf({ped: 1}) === 'S1',
   'коды соответствуют баллам: 5→S5, 3→S3, 1→S1');
ok(g.codeOf({signal: 'SIG-STRESS'}) === 'S0', 'сигнал → S0');
ok(g.BANK.bank_to_code.S3 === 'S5' && g.BANK.bank_to_code.SN === 'S0', 'обратная привязка к кодам банка');
g.S.scores['SPH-KON'] = {signal: 'SIG-STRESS', reason: 'отказ ребёнка от занятия'};
const doc9 = g.buildDoc();
ok(doc9.blocks[0].paras.some(p => /Причина: отказ ребёнка/.test(p.text)),
   'причина S0 попадает в документ как служебная отметка');

console.log('\n== 10. Группировка подсказок по сферам ==');
const grp = g.groupBySphere([{src: 'GL-03'}, {src: 'GL-07'}, {src: 'GL-10'}], 'goal');
ok(grp.length >= 2, 'цели разносятся по сферам: групп ' + grp.length);
ok(grp.every(x => x.sphere), 'у каждой группы есть сфера');

fs.unlinkSync(path.join(__dirname, '_v2_test.docx'));
console.log('\n== 11. Банк фраз и полнота подсказок ==');
g.S = g.blank();
g.S.scores = {'SPH-SENS': {ped: 4}};
ok(g.STAGES.length === 9 && g.STAGES.map(x => x.n).join(',') === '1,2,3,4,5,6,7,8,9',
   'структура шагов: 1…9, без пропусков (9-й — банк фраз)');
const bankN = g.bankAsFor('SPH-SENS', 'S4').length;
ok(bankN >= 4, 'в банке для сферы «Сенсорика» и кода S4 фраз: ' + bankN);
const poolKon = g.sphereAsPool('SPH-KON').map(p => p.id);
const poolIni = g.sphereAsPool('SPH-INI').map(p => p.id);
ok(poolKon.indexOf('AS4ini-S3-04') < 0 && poolIni.indexOf('AS4ini-S3-04') >= 0,
   'микроблок AS4ini разведён: инициатива (AS4ini-S3-04) — только в сфере «Инициатива»');
ok(poolKon.filter(id => poolIni.indexOf(id) >= 0).length === 0,
   'пулы сфер «Контакт» и «Инициатива» не пересекаются');
ok(g.sphereAsPool('SPH-COM').map(p => p.id).indexOf('AS6com-S1-02') < 0,
   'AS6com-S1-02 (обращение за помощью) относится к сфере «Инициатива», а не «Коммуникация»');
ok(g.sphereAsPool('SPH-MOT').length >= 6 && g.sphereAsPool('SPH-MOT').every(p => p.micro === 'AS7prax'),
   'в сфере «Праксис» формулировок банка: ' + g.sphereAsPool('SPH-MOT').length);
ok(g.sphereAsPool('SPH-VIS').length >= 6 && g.sphereAsPool('SPH-VIS').every(p => p.micro === 'AS8vis'),
   'в сфере «Зрительно-пространственная» формулировок банка: ' + g.sphereAsPool('SPH-VIS').length);
ok(g.bankAsFor('SPH-MOT', 'S5').length >= 2 && g.bankAsFor('SPH-VIS', 'S1').length >= 1,
   'под оценки 5 и 1 в новых сферах есть формулировки');

console.log('\n== 12. Сенсорный опросник FEDL2i (шаг 2) ==');
g.S = g.blank();
ok(g.sensBlocks().map(b => b.id).join('') === 'ABCDEF', 'блоки A–F: ' + g.sensBlocks().map(b => b.id).join(''));
ok(g.sensTotal() === 46, 'пунктов опросника: ' + g.sensTotal());
ok(g.sensScale('react').options.join('|') === '(+1!)|(+1)|(+-)|БО|(-1)|(-1!)',
   'шкала реактивности из файла FEDL2i');
ok(g.sensScale('steps').options.join('|') === '0|0-1|1-3|4-7|7-12|12+', 'шкала шагов из файла FEDL2i');
ok(g.sensItems('A').some(i => i.scale === 'text'), 'в блоке A есть доминирующий профиль (текст)');
ok(g.stageDone(2) === false, 'шаг 2 не отмечен, пока опросник пуст');
g.S.sens = {A1: '(+1)', A2: 'БО', A4: '(-1)', A5: '(+-)', A8: 'ищет сильные вестибулярные нагрузки, плохо переносит шум',
            B1: 'Да', C6: '1-3', D5: 'Да', E1: 'Нет', F3: '(+-)'};
ok(g.stageDone(2) === true, 'шаг 2 отмечен после заполнения');
const at = g.sensAutoText();
ok(/слуховая — повышенная чувствительность/.test(at), 'блок A собирается в текст: ' + at.slice(0, 60) + '…');
ok(/вестибулярная — сниженная чувствительность/.test(at), 'знак оценки отражён верно (−1 = сниженная)');
ok(/Доминирующий функциональный профиль: ищет сильные/.test(at), 'доминирующий профиль добавлен');
ok(!/двигательн|praxis|практическ/i.test(at), 'блоки B–F в текст документа не попадают');
ok(g.sensApply() === true && g.S.asAuto === at, 'кнопка «Собрать текст» записывает профиль');
ok(g.sensBlocksOf('SPH-SENS').join('') === 'A', 'сферу 1 «Сенсорика» дополняет блок A');
ok(g.sensBlocksOf('SPH-COM').join('') === 'CD', 'сферу 6 «Коммуникация» дополняют блоки C и D');
ok(g.sensBlocksOf('SPH-MOT').join('') === 'BF', 'сферу 8 «Праксис» дополняют блоки B и F');
ok(g.sensBlocksOf('SPH-VIS').join('') === 'E', 'сферу 9 «Зрительно-пространственная» дополняет блок E');
ok(g.sensBlocksOf('SPH-REG').length === 0, 'у сферы «Эмоции и регуляция» блоков FEDL2i нет');
ok(g.blockSphere('B').id === 'SPH-MOT' && g.blockSphere('A').id === 'SPH-SENS',
   'каждый блок опросника знает свою сферу');
ok(g.sensSpheres().length === 4, 'сфер, дополняемых опросником: ' + g.sensSpheres().length);
const atMot = g.sensAutoTextFor('SPH-MOT');
ok(/Двигательное планирование: применяет простые физические действия[\s\S]*— да/.test(atMot),
   'блок B собирается в текст сферы 8: ' + atMot.slice(0, 70) + '…');
ok(/Праксис — исполнительные функции: может разработать этапы последовательности — непостоянно/.test(atMot),
   'блок F собирается в тот же текст сферы 8');
ok(!/Сенсорная переработка:/.test(atMot), 'текст сферы 8 не дублирует блок A');
ok(g.sensApply('SPH-MOT') === true && g.S.asAutoMap['SPH-MOT'] === atMot,
   'текст сферы 8 пишется в asAutoMap');
ok(g.autoTextOf('SPH-SENS') === at && g.S.asAuto === at,
   'сфера 1 по-прежнему хранит текст в S.asAuto (совместимость со старыми проектами)');
ok(g.sensApply('SPH-VIS') === true && /зрительно-пространственная/i.test(g.autoTextOf('SPH-VIS')),
   'текст сферы 9 собран из блока E: ' + g.autoTextOf('SPH-VIS').slice(0, 60) + '…');
ok(g.sensApply('SPH-REG') === false, 'у сферы без блоков FEDL2i текст не собирается');
g.S.scores = {'SPH-SENS': {ped: 4}, 'SPH-REG': {ped: 3}};
g.S.as.push({src: 'AS3soc-S2-01', text: g.BANK.phraseIndex['AS3soc-S2-01'].text, example: 'крутился на стуле', sphere: 'SPH-SENS'});
const doc12 = g.buildDoc();
const as12 = doc12.blocks[0].paras.map(p => p.text);
ok(as12.some(t => /Сенсорная переработка: слуховая/.test(t)), 'авто-профиль попал в «Актуальное состояние»');
ok(as12.filter(t => /Сенсорная переработка: слуховая/.test(t)).length === 1, 'без дублей авто-профиля');
ok(as12.some(t => t === g.BANK.phraseIndex['AS3soc-S2-01'].text), 'обычные фразы сферы на месте');
ok(as12.filter(t => t === atMot).length === 1, 'текст сферы 8 (блоки B+F) попал в документ один раз');
g.S.asAuto = '';
ok(!g.buildDoc().blocks[0].paras.some(p => /Сенсорная переработка: слуховая/.test(p.text)),
   'после «убрать» авто-профиль не в документе');
g.S.stage = 2; noThrow('рендер шага «Сенсорный опросник»', () => g.render());

console.log('\n== 13. Шапка: ФИО и дата заполнения ==');
g.S = g.blank();
g.S.header.fio = 'Иванов Пётр';
g.S.header.fill_date = '12.10.2026';
ok(/Иванов_Пётр/.test(g.fileName()) && /12-10-2026/.test(g.fileName()),
   'имя .docx включает ФИО и дату заполнения: ' + g.fileName());
ok(/Иванов_Пётр_12-10-2026/.test(g.projectFileName()),
   'имя проекта включает ФИО и дату: ' + g.projectFileName());
const txt13 = g.docText(g.buildDoc());
ok(/Дата заполнения: 12\.10\.2026/.test(txt13), 'дата заполнения есть в документе');
ok(/^\d{2}\.\d{2}\.\d{4}$/.test(g.todayStr()), 'todayStr(): ' + g.todayStr());
g.S = g.blank();
ok(g.S.header.fill_date === g.todayStr(), 'в новом проекте дата заполнения = сегодня: ' + g.S.header.fill_date);
g.S.stage = 1; noThrow('рендер шага 1 с полем даты', () => g.render());

console.log('\n== 14. Перенос старых проектов на новый список сфер (2.2.0 → 2.3.0) ==');
const oldDoc = {v: 2, appVersion: '2.2.0',
  header: {fio: 'Старых П.', birth: '01.01.2020', fill_date: '01.09.2026', period_start: '01.09.2026',
           period_end: '30.09.2026', specialist: 'Петрова А.И.', sessions: '10',
           direction_name: 'Игровое взаимодействие'},
  scores: {'SPH-SENS': {ped: 4}, 'SPH-REG': {ped: 3}, 'SPH-KON': {ped: 2}, 'SPH-INT': {ped: 4},
           'SPH-SOC': {ped: 3}, 'SPH-SYM': {ped: 2}, 'SPH-IDE': {ped: 3}},
  sens: {A1: '(+1)'},
  asAuto: 'Сенсорная переработка: слуховая — повышенная чувствительность.',
  as: [{src: 'AS4-S3-04', text: 'Инициирует взаимодействие со взрослым.', example: '', sphere: 'SPH-INT'}],
  goals: [{src: 'GL-13', text: 'цель', sphere: 'SPH-INT'}],
  methods: [], results: [], next: [], recs: [], litPriority: [],
  archive: {date: '01.08.2026', scores: {'SPH-INT': {ped: 2}}}, stage: 1};
const nd = g.normalizeDoc(JSON.parse(JSON.stringify(oldDoc)));
ok(nd.scores['SPH-INI'] && nd.scores['SPH-INI'].ped === 4 && !nd.scores['SPH-INT'],
   'оценка старой сферы «Преднамеренность» перенесена в «Инициативу»');
ok(nd.scores['SPH-SENS'].ped === 4 && nd.scores['SPH-SYM'].ped === 2,
   'оценки сфер с сохранёнными id не пострадали');
ok(nd.as[0].sphere === 'SPH-INI' && nd.goals[0].sphere === 'SPH-INI',
   'привязка фраз и целей к сфере перенесена');
ok(nd.as[0].src === 'AS4ini-S3-04' && nd.goals[0].src === 'GL-13',
   'старый код фразы переведён на семантический (AS4-S3-04 → AS4ini-S3-04), цели не меняются');
ok(g.migCode('AS1-S3-01') === 'AS1sens-S3-01' && g.migCode('RC4') === 'RC4play',
   'migCode(): карта переноса кодов работает');
ok(g.migCode('AS1sens-S3-01') === 'AS1sens-S3-01' && g.migCode('') === '',
   'migCode() идемпотентна и безопасна на пустых значениях');
ok(nd.archive.scores['SPH-INI'].ped === 2, 'архивный снимок тоже перенесён');
ok(nd.asAutoMap['SPH-SENS'] === oldDoc.asAuto, 'старый asAuto перенесён в asAutoMap');
ok(Array.isArray(nd.methods) && Array.isArray(nd.litPriority), 'отсутствующие массивы созданы');
ok(g.migrateScores({'SPH-INT': {ped: 5}})['SPH-INI'].ped === 5, 'migrateScores() работает отдельно');
g.S = nd; g.S.stage = 8;
noThrow('рендер документа из перенесённого проекта', () => g.render());
ok(g.buildDoc().blocks[0].paras.some(p => /Сенсорная переработка: слуховая/.test(p.text)),
   'текст профиля из старого проекта виден в документе');

console.log('\n== 15. Шаг 9 «Банк фраз»: правки, localStorage, CSV, импорт, сброс (2.6.0) ==');
g.S = g.blank();
g.S.stage = 9;
noThrow('рендер шага 9', () => g.render());
ok(g.stageDone(9) === false, 'шаг 9 галочкой «готово» не помечается');
const html9 = g.vStage9();
['bank9Add', 'bank9ClearFilters', 'bank9ExportJson', 'bank9ExportCsv', 'bank9Import', 'bank9Reset',
 'f9Block', 'f9Micro', 'f9Status', 'f9Text', 'bank9Table', 'bank9Count', 'bank9Rows']
  .forEach(id => ok(html9.indexOf('id="' + id + '"') >= 0, 'на шаге 9 есть #' + id));
ok(/Справочники банка/.test(html9) && /Служебные фразы/.test(html9), 'на шаге 9 есть справочники банка');
ok(g.bankPhraseCount() === 201, 'в банке активных формулировок: ' + g.bankPhraseCount());

// фильтры шага 9 (состояние BK9)
g.BK9 = {block: 'AS', micro: '', status: '', q: ''};
const nAs = g.bank9Rows().length;
ok(nAs > 0 && nAs < 201 && g.bank9Rows().every(p => p.block === 'AS'), 'фильтр по блоку: ' + nAs + ' фраз');
g.BK9 = {block: '', micro: 'AS5play', status: '', q: ''};
ok(g.bank9Rows().length > 0 && g.bank9Rows().every(p => p.micro === 'AS5play'), 'фильтр по микроблоку');
g.BK9 = {block: '', micro: '', status: 'S3', q: ''};
ok(g.bank9Rows().length > 0 && g.bank9Rows().every(p => String(p.status).split(',').indexOf('S3') >= 0),
   'фильтр по статусу');
g.BK9 = {block: '', micro: '', status: '', q: 'сюжет'};
ok(g.bank9Rows().length > 0 && g.bank9Rows().every(p =>
   (p.text + ' ' + p.id + ' ' + (p.tags || '')).toLowerCase().indexOf('сюжет') >= 0), 'поиск по тексту');
g.BK9 = {block: '', micro: '', status: '', q: ''};
ok(g.bank9Rows().length === g.bankPhraseCount(), 'без фильтров показаны все активные фразы');

// новая фраза: блок, микротема и статус определяются по коду
const np = g.bankNewPhrase('AS5play-S2-TEST');
ok(np && np.block === 'AS' && np.micro === 'AS5play' && np.status === 'S2' && np.source === 'пользователь',
   'bankNewPhrase(): AS5play-S2-TEST → блок AS, микротема AS5play, статус S2');
ok(g.bankNewPhrase('AS5play-S2-TEST') === null, 'вторая фраза с тем же ID не создаётся');
ok(g.bankNewPhrase('') === null, 'без ID фраза не создаётся (prompt в тестах пуст)');
ok(g.bankPhraseCount() === 202, 'фраз в банке стало: ' + g.bankPhraseCount());
ok(g.bankSetField('AS5play-S2-TEST', 'text', 'Отредактированная формулировка') === true
   && g.BANK.phraseIndex['AS5play-S2-TEST'].text === 'Отредактированная формулировка',
   'bankSetField(): текст правится в строке');
ok(g.bankSetField('AS5play-S2-TEST', 'needs_example', false) === true
   && g.BANK.phraseIndex['AS5play-S2-TEST'].needs_example === false, '«требует примера» снимается');
ok(g.bankSetField('AS5play-S2-TEST', 'tags', 'своя тема') === true
   && g.BANK.phraseIndex['AS5play-S2-TEST'].tags === 'своя тема', 'теги правятся');
ok(g.bankSetField('GL-01', 'block', 'METH') === true && g.BANK.phraseIndex['GL-01'].block === 'METH',
   'блок меняется (селект)');
ok(g.bankSetField('нет-такой', 'text', 'x') === false && g.bankSetField('GL-01', 'id', 'x') === false,
   'bankSetField() безопасна: неизвестный ID и поле id отклоняются');
ok(g.bankRenamePhrase('AS5play-S2-TEST', 'AS5play-S2-TEST2') === true
   && !!g.BANK.phraseIndex['AS5play-S2-TEST2'] && !g.BANK.phraseIndex['AS5play-S2-TEST'],
   'bankRenamePhrase(): ID перенесён, индекс обновлён');
ok(g.bankRenamePhrase('AS5play-S2-TEST2', 'AS5play-S2-02') === false, 'дубль существующего ID отклонён');
ok(g.bankRenamePhrase('AS5play-S2-TEST2', '  ') === false, 'пустой ID отклонён');

// localStorage-круг: правки переживают «перезагрузку страницы»
ok(JSON.stringify(g.stripBank(g.BANK)).indexOf('phraseIndex') < 0, 'stripBank() не пишет индексы в хранилище');
const re = g.loadBank();
ok(!!re.phraseIndex['AS5play-S2-TEST2']
   && re.phraseIndex['AS5play-S2-TEST2'].text === 'Отредактированная формулировка',
   'правки банка переживают перезагрузку (localStorage[' + g.LS_BANK + '])');
ok(g.LS_BANK === 'iv_constructor_bank_v2', 'ключ хранилища свой, не общий с V1: ' + g.LS_BANK);

// CSV-круг (экспорт → импорт)
const csv = g.toCsv(g.BANK.phrases);
ok(csv.split('\n')[0].indexOf('ID;Направление;Блок;Микроблок') === 0, 'заголовок CSV на месте');
const back = g.parseCsv(csv);
ok(back.length === g.BANK.phrases.length, 'CSV-круг: строк ' + back.length + ' из ' + g.BANK.phrases.length);
const one = back.find(r => r.id === 'AS5play-S2-TEST2');
ok(one && one.micro === 'AS5play' && one.source === 'пользователь' && one.needs_example === false,
   'своя фраза читается из CSV с полями');
ok(csv.indexOf('"') >= 0 && g.parseCsv('ID;Текст\nX-1;"текст; с точкой запятой"').length === 1,
   'кавычки и разделитель «;» внутри текста переживают CSV-круг');

// импорт строк: слияние по ID и перенос старой нумерации кодов
const r1 = g.mergeBankRows([{id: 'AS1-S3-01', text: 'Старая нумерация из файла', block: 'AS',
                             micro: 'AS1', status: 'S3', tags: ''}]);
ok(r1.updated === 1 && r1.added === 0
   && g.BANK.phraseIndex['AS1sens-S3-01'].text === 'Старая нумерация из файла'
   && g.BANK.phraseIndex['AS1sens-S3-01'].micro === 'AS1sens',
   'старый код AS1-S3-01 перенесён картой code_migration на AS1sens-S3-01');
const r2 = g.mergeBankRows([{id: 'AS5play-S1-NEW', text: 'Импортированная фраза', block: 'AS',
                             micro: 'AS5play', status: 'S1', needs_example: true, active: true}]);
ok(r2.added === 1 && !!g.BANK.phraseIndex['AS5play-S1-NEW'], 'mergeBankRows(): новая строка добавлена');
ok(g.mergeBankRows([{id: '', text: 'без кода'}, null]).added === 0, 'строки без ID игнорируются');
ok(g.sphereAsPool('SPH-SYM').map(p => p.id).indexOf('AS5play-S1-NEW') >= 0,
   'импортированная фраза сразу доступна в подборе фраз шагов');

// удаление
ok(g.bankDeletePhrase('AS5play-S1-NEW') === true && !g.BANK.phraseIndex['AS5play-S1-NEW'],
   'bankDeletePhrase(): фраза удалена');
ok(g.bankDeletePhrase('AS5play-S1-NEW') === false, 'повторное удаление безопасно');
ok(g.sphereAsPool('SPH-SYM').map(p => p.id).indexOf('AS5play-S1-NEW') < 0,
   'удалённая фраза больше не предлагается в шагах');

// колонка «В документ» — кладёт фразу в её блок, не уходя с шага
g.S = g.blank();
g.S.stage = 9;
g.toggleIn('as', 'AS5play-S2-02', {sphere: 'SPH-SYM'});
ok(g.listHas(g.S.as, 'AS5play-S2-02') && g.S.stage === 9,
   '«В документ»: фраза блока AS попала в актуальное состояние, остались на шаге 9');
g.toggleIn('goals', 'GL-01');
ok(g.listHas(g.S.goals, 'GL-01'), '«В документ»: фраза блока GOAL попала в цели');
g.toggleIn('as', 'AS5play-S2-02');
ok(!g.listHas(g.S.as, 'AS5play-S2-02'), 'повторное нажатие убирает фразу из документа');

// JSON-импорт (полная замена банка) и сброс
let replaced = 0;
try { replaced = g.replaceBank({phrases: g.BANK_DEFAULT.phrases.slice(0, 10)}); } catch (e) { replaced = -1; }
ok(replaced === 10 && g.bankPhraseCount() === 10, 'replaceBank(): банк заменён на 10 фраз');
let bad = false;
try { g.replaceBank({}); } catch (e) { bad = true; }
ok(bad, 'replaceBank() отклоняет файл без массива phrases');
g.resetBank();
ok(g.bankPhraseCount() === 201 && !g.BANK.phraseIndex['AS5play-S2-TEST2'],
   'resetBank(): встроенный банк возвращён (201 фраза, своих правок нет)');
ok(!g.loadBank().phraseIndex['AS5play-S2-TEST2'], 'после сброса в localStorage правок банка нет');
ok(g.BANK_DEFAULT.phrases.length === 201 && g.BANK_DEFAULT.phraseIndex === undefined,
   'BANK_DEFAULT правками не испорчен (эталон для сброса)');
ok(g.CSV_COLS.length === 15 && g.bankFileName('json').indexOf('банк_фраз_v2_1.2.0_2.6.0.json') === 0,
   'имя выгрузки банка содержит версию данных и версию форка: ' + g.bankFileName('json'));

// шаг 1 почищен: карточки-дубля банка нет, кнопки в сферах остались
const h1 = g.vStage1();
ok(h1.indexOf('Банк фраз: смотреть и добавлять') < 0, 'в шаге 1 нет карточки-дубля «Банк фраз»');
ok(h1.indexOf('data-bank="AS|') >= 0, 'кнопки «+ из банка фраз» в карточках сфер остались');
ok(g.vStage9().indexOf('Вернуть встроенный банк') >= 0, 'кнопка возврата встроенного банка на шаге 9');

console.log('\n== 16. Чип специалиста в шапке (2.6.0) ==');
g.S = g.blank();
ok(g.specChipText() === 'специалист не указан', 'пустая шапка → «специалист не указан»');
g.S.header.specialist = 'Петрова А.И.';
g.S.header.sessions = '10';
ok(g.specChipText() === 'специалист: Петрова А.И. · занятий: 10', 'чип: ' + g.specChipText());
g.S.header.specialist = '  ';
ok(g.specChipText() === 'занятий: 10', 'без ФИО специалиста: ' + g.specChipText());
g.S.header.sessions = '';
ok(g.specChipText() === 'специалист не указан', 'без обоих полей: ' + g.specChipText());
g.S.header.specialist = 'Иванов И.И.';
noThrow('рендер шага 1 с чипом специалиста', () => { g.S.stage = 1; g.render(); });
[1, 5, 8, 9].forEach(st => noThrow('рендер шага ' + st + ' с чипом', () => { g.S.stage = st; g.render(); }));

console.log('\n' + (fails === 0 ? '✅ ВСЕ ПРОВЕРКИ V2 ПРОЙДЕНЫ' : '❌ ПРОВАЛОВ: ' + fails));
process.exit(fails === 0 ? 0 : 1);
