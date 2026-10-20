// Тесты ОСНОВНОЙ версии конструктора (мейн, v3.2.0). Запуск: node tools/test_main.js
const fs = require('fs');
const path = require('path');
const {loadApp} = require('./_harness.js');
const ROOT = path.resolve(__dirname, '..');
const g = loadApp(path.join(ROOT, 'main', 'Конструктор_ИВ_основная_3.2.0.html'));

let fails = 0;
const ok = (c, m) => { console.log((c ? '  OK   ' : '  FAIL ') + m); if (!c) fails++; };
const noThrow = (n, f) => { try { const r = f(); ok(true, n); return r; }
  catch (e) { ok(false, n + ' → ' + e.message); return null; } };

console.log('\n== 1. Данные основной версии ==');
ok(g.BANK.meta.version === '1.3.0', 'версия данных банка: ' + g.BANK.meta.version);
ok(g.BANK.spheres.length === 7, 'сфер оценки: ' + g.BANK.spheres.length + ' (в 3.2.0 шкала сфер — 7)');
ok(g.BANK.ped_scale.map(x => x.ped).join(',') === '0,1,2,3,4,5,6', 'шкала сфер 0…6: ' + g.BANK.ped_scale.map(x => x.ped).join(','));
ok(g.BANK.phrases.length === 201 && g.bankPhraseCount() === 197,
   'всего фраз в файле: ' + g.BANK.phrases.length + ', активных в подборе: ' + g.bankPhraseCount() + ' (4 деактивированы)');
ok(Object.keys(g.BANK.sphere_keys).length >= 7, 'ключей сфер: ' + Object.keys(g.BANK.sphere_keys).length);
const missKey = g.BANK.spheres.filter(sp => {
  const k = (g.BANK.sphere_keys || {})[sp.id] || {};
  return !([0,1,2,3,4,5,6].every(p => k[p]) && k['SIG-STRESS'] && k['SIG-NOINFO']);
});
ok(missKey.length === 0, 'у каждой сферы есть ключ на 0…6 и обе сигнальные отметки' +
  (missKey.length ? ' → нет у: ' + missKey.map(s => s.id).join(',') : ''));
ok(g.STAGES.length === 10 && g.STAGES.filter(st => st.n !== 10).length === 9,
   'шагов в навигации: 9 + скрытый шаг «Банк фраз» (STAGES.length = ' + g.STAGES.length + ')');
ok(g.STAGES[7].name.indexOf('Наблюдения') >= 0, 'шаг 8 — «' + g.STAGES[7].name + '» (новое в 3.2.0)');
ok(g.STAGES[8].name.indexOf('Итоговый документ') >= 0, 'шаг 9 — «' + g.STAGES[8].name + '» (банк перенесён внутрь)');

console.log('\n== 2. Оценка сфер и выпадение фраз ==');
g.S = g.blank();
g.S.header = {fio: 'Тестов Т.', birth: '01.01.2019', period_start: '01.09.2026', period_end: '30.09.2026',
  specialist: 'Петрова А.И.', sessions: '10', direction_name: 'Игровое взаимодействие'};
const SPH = g.BANK.spheres.map(s => s.id);
SPH.forEach(sid => { g.S.scores[sid] = {ped: 3, note: 'наблюдение по ' + sid}; });
const kSome = g.keyFor(SPH[1]);
ok((kSome.as || []).length >= 1, 'для средней оценки выпадают формулировки (' + (kSome.as || []).length + ')');
(kSome.as || []).forEach(id => g.toggleIn('as', id));
ok(g.S.as.length === (kSome.as || []).length, 'формулировки добавлены в актуальное состояние');
g.toggleIn('as', kSome.as[0]); g.toggleIn('as', kSome.as[0]);
ok(g.listHas(g.S.as, kSome.as[0]), 'тумблер добавить/убрать работает в обе стороны');
g.S.scores[SPH[0]] = {ped: 0, note: '', reason: 'ребёнок не был готов к оценке сферы'};
const k0 = g.keyFor(SPH[0]);
ok(!!k0, 'ключ для оценки 0 существует');

console.log('\n== 3. Каскад: цели из оценок, приёмы из целей ==');
const goalIds = [];
SPH.forEach(sid => {
  const sc = g.S.scores[sid];
  const k = ((g.BANK.sphere_keys || {})[sid] || {})[sc.signal || sc.ped];
  if (k) (k.goal || []).forEach(id => { if (goalIds.indexOf(id) < 0) goalIds.push(id); });
});
g.S.as.forEach(it => { const p = g.BANK.phraseIndex[it.src];
  if (p) (p.links_goal || []).forEach(id => { if (goalIds.indexOf(id) < 0) goalIds.push(id); }); });
ok(goalIds.length >= 3, 'целей предложено: ' + goalIds.length);
goalIds.slice(0, 6).forEach(id => g.toggleIn('goals', id));
const methIds = [];
g.S.goals.forEach(gl => { const p = g.BANK.phraseIndex[gl.src];
  if (p) (p.links_meth || []).forEach(id => { if (methIds.indexOf(id) < 0) methIds.push(id); }); });
ok(methIds.length >= 2, 'приёмов предложено из целей: ' + methIds.length);
methIds.slice(0, 4).forEach(id => g.toggleIn('methods', id));
g.S.methods.forEach(m => m.example = 'На 3 занятии педагог…, ребёнок…');
ok(g.S.methods.every(m => m.example), 'у приёмов проставлены примеры');

console.log('\n== 4. Рекомендации и литература ==');
const recIds = [];
SPH.forEach(sid => {
  const sc = g.S.scores[sid];
  const k = ((g.BANK.sphere_keys || {})[sid] || {})[sc.signal || sc.ped];
  if (k) (k.rec || []).forEach(id => { if (recIds.indexOf(id) < 0) recIds.push(id); });
});
ok(recIds.length >= 3, 'рекомендаций предложено: ' + recIds.length);
recIds.slice(0, 6).forEach(id => g.toggleIn('recs', id));
const prio = noThrow('litPriority()', () => g.litPriority());
ok(prio && prio.length >= 1, 'приоритетная литература по профилю: ' + (prio ? prio.length : 0));

console.log('\n== 5. Документ ==');
g.S.obs = (g.S.obs || []);
if (g.S.obs.push) g.S.obs.push({text: 'На занятии №3 ребёнок сам подошёл к педагогу с игрушкой.'});
const doc = noThrow('buildDoc()', () => g.buildDoc());
ok(doc && doc.blocks.length === 7, 'обязательных блоков документа: ' + (doc ? doc.blocks.length : 0));
const txt = noThrow('docText()', () => g.docText(doc));
ok(txt && txt.length > 3000, 'текст документа: ' + (txt ? txt.length : 0) + ' символов');
const zip = noThrow('docx()', () => g.docx());
ok(zip && zip.length > 5000 && zip[0] === 0x50 && zip[1] === 0x4b, 'ZIP-сигнатура .docx на месте');
fs.writeFileSync(path.join(__dirname, '_main_test.docx'), Buffer.from(zip));
fs.unlinkSync(path.join(__dirname, '_main_test.docx'));

console.log('\n== 6. Рендер всех шагов ==');
for (let st = 1; st <= 9; st++) { g.S.stage = st; noThrow('рендер шага ' + st, () => g.render()); }
g.S.stage = 10; noThrow('рендер скрытого шага «Банк фраз» (10)', () => g.render());
g.S.stage = 9; g.render();
const navBtns = (g.STAGES || []).filter(st => st.n !== 10).length;
ok(navBtns === 9, 'в навигации 9 кнопок, шаг «Банк фраз» скрыт (STAGES c фильтром): ' + navBtns);

console.log('\n== 7. Банк фраз: правки, localStorage, CSV, сброс ==');
g.resetBank();
ok(g.bankPhraseCount() === 197, 'после сброса встроенный банк: ' + g.bankPhraseCount() + ' активных фраз');
const np = g.bankNewPhrase('AS5play-S2-TESTM');
ok(np && np.block === 'AS' && np.micro === 'AS5play' && np.status === 'S2', 'новая фраза создаётся из кода');
ok(g.bankSetField('AS5play-S2-TESTM', 'text', 'Проверочная формулировка') === true
   && g.BANK.phraseIndex['AS5play-S2-TESTM'].text === 'Проверочная формулировка', 'правка текста фразы');
const csv = g.toCsv(g.BANK.phrases);
const back = g.parseCsv(csv);
ok(back.length === g.BANK.phrases.length, 'CSV-круг замкнут: ' + back.length + ' строк');
g.resetBank();
ok(g.bankPhraseCount() === 197 && !g.BANK.phraseIndex['AS5play-S2-TESTM'], 'resetBank(): правки сняты');

console.log('\n== 8. Имена файлов и версия ==');
g.S = g.blank();
g.S.header.fio = 'Иванов Пётр'; g.S.header.fill_date = '12.10.2026';
ok(/Иванов_Пётр/.test(g.fileName()), 'имя .docx включает ФИО: ' + g.fileName());
ok(/^Заключение_ИВ_main_/.test(g.fileName()), '.docx с префиксом основной версии: ' + g.fileName());
ok(/^проект_main_Иванов_Пётр_12-10-2026\.json$/.test(g.projectFileName()), 'имя файла проекта: ' + g.projectFileName());
ok(g.PROJECT_TAG === 'iv-constructor-main-3_2' && g.SNAPSHOT_TAG === 'iv-constructor-main-3_2-snapshot',
   'метка формата проекта (не совместима со старой V2): ' + g.PROJECT_TAG);
ok(g.bankFileName('json').indexOf('1.3.0') >= 0, 'выгрузка банка содержит версию данных: ' + g.bankFileName('json'));


console.log('\n== 9. Изоляция хранилищ от старого форка V2 ==');
g.S = g.blank();
g.S.header.fio = 'Изоляция Тест';
g.save();
g.persistBank();
const LSK = g.__localStorageKeys();
const has = k => LSK.indexOf(k) >= 0;
ok(!has('iv_constructor_v2_doc'), 'черновик НЕ пишется в ключ старого V2 (iv_constructor_v2_doc)');
ok(has('iv_constructor_main_3_2_doc'), 'черновик пишется в собственный ключ ' + g.LS_DOC);
ok(has('iv_constructor_bank_main_3_2'), 'правки банка пишутся в собственный ключ ' + g.LS_BANK);
ok(!has('iv_constructor_bank_v2'), 'правки банка НЕ пишутся в ключ старого V2');
ok(g.LS_BANK === 'iv_constructor_bank_main_3_2' && g.LS_DOC === 'iv_constructor_main_3_2_doc',
   'ключи банка и черновика изолированы от старого V2: ' + g.LS_BANK + ' / ' + g.LS_DOC);

console.log('\n' + (fails === 0 ? '✅ ВСЕ ПРОВЕРКИ ОСНОВНОЙ ВЕРСИИ (3.2.0) ПРОЙДЕНЫ' : '❌ ПРОВАЛОВ: ' + fails));
process.exit(fails === 0 ? 0 : 1);
