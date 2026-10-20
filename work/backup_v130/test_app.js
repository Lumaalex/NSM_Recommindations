// Тестовый прогон клиентской логики конструктора без браузера.
// Запуск: node tools/test_app.js
const fs = require('fs');
const path = require('path');
const {loadApp, docxBytes} = require('./_harness.js');

const ROOT = path.resolve(__dirname, '..');
const HTML = path.join(ROOT, 'Конструктор_рекомендаций.html');
const g = loadApp(HTML);

let fails = 0;
function ok(cond, msg) { console.log((cond ? '  OK   ' : '  FAIL ') + msg); if (!cond) fails++; }
function noThrow(name, fn) {
  try { const r = fn(); ok(true, name); return r; }
  catch (e) { ok(false, name + ' → ' + e.message + (process.env.STACK ? '\n' + e.stack : '')); return null; }
}

console.log('\n== 1. Данные и состояние ==');
ok(g.BANK.phrases.length > 100, 'банк загружен: ' + g.BANK.phrases.length + ' фраз');
ok(g.BANK.questionnaire.length > 40, 'опросник: ' + g.BANK.questionnaire.length + ' пунктов');
ok(g.BANK.iv2_questions.length > 40, 'вопросы ИВ2: ' + g.BANK.iv2_questions.length);
ok(Object.keys(g.BANK.phraseIndex).length === g.BANK.phrases.length, 'индекс фраз построен');
ok(g.BANK.blocks.filter(b => b.mandatory).length === 7, 'обязательных блоков: 7');
ok(g.BANK.microblocks.filter(m => m.block === 'AS' && !m.v2only).length === 6,
   'микротем актуального состояния в классической версии: 6');
ok(g.BANK.microblocks.filter(m => m.v2only).length === 2,
   'микротем только для v2 (сферы 8–9): ' + g.BANK.microblocks.filter(m => m.v2only).length);
ok(g.BANK.phrases.filter(p => p.block === 'AS' && p.micro === 'AS7prax').length >= 6,
   'формулировки праксиса (AS7prax) в банке есть');

console.log('\n== 1b. Перенос из v2: человекочитаемые коды и область видимости V1 (запись 46) ==');
ok(g.blockName('AS') === 'Актуальное состояние', 'blockName(AS) = ' + g.blockName('AS'));
ok(g.blockName('REC') === 'Рекомендации', 'blockName(REC) = ' + g.blockName('REC'));
ok(g.microName('AS5play').indexOf('Игра') === 0, 'microName(AS5play) = ' + g.microName('AS5play'));
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


console.log('\n== 2. Рендер всех вкладок ==');
['header', 'survey', 'as', 'goals', 'results', 'recs', 'doc', 'bank', 'help'].forEach(tab => {
  g.TAB = tab;
  noThrow('вкладка «' + tab + '»', () => g.render());
});

console.log('\n== 3. Заполнение документа (имитация работы специалиста) ==');
g.S.header = {fio: 'Тестов Тест Тестович', birth: '01.02.2019', period_start: '19.07.2026',
              period_end: '01.08.2026', specialist: 'Иванова А.Б.', sessions: '10',
              direction_name: 'Игровое взаимодействие'};
g.S.includeWorklog = true;
const q = g.BANK.questionnaire;
q.forEach((item, i) => { g.S.answers[item.id] = {value: [3, 2, 1, 0, 'N'][i % 5], note: 'пример наблюдения ' + item.id}; });
let added = 0;
q.forEach(item => {
  const a = g.S.answers[item.id]; if (!a) return;
  const key = (item.key || {})[String(a.value)]; if (!key) return;
  (key.as || []).forEach(id => { if (!g.hasPhrase('AS', id)) { g.addMicroItem(item.micro || 'AS1sens', id); added++; } });
  (key.goal || []).forEach(id => { if (!g.hasPhrase('GOAL', id)) g.addItem('GOAL', id); });
  (key.meth || []).forEach(id => { if (!g.hasPhrase('METH', id)) g.addItem('METH', id); });
  (key.rec || []).forEach(id => { const p = g.byId(id); if (p && !g.hasPhrase('REC', id)) g.addRecItem(p.micro || 'RC4play', id); });
  (key.res || []).forEach(id => { if (!g.hasPhrase('RES', id)) g.addItem('RES', id); });
  (key.nxt || []).forEach(id => { if (!g.hasPhrase('NEXT', id)) g.addItem('NEXT', id); });
});
ok(added > 10, 'по ключу добавлено формулировок в актуальное состояние: ' + added);
ok(g.S.blocks.GOAL.length > 5, 'целей подобрано: ' + g.S.blocks.GOAL.length);
ok(g.S.blocks.METH.length > 5, 'приёмов подобрано: ' + g.S.blocks.METH.length);
Object.keys(g.S.micro).forEach(k => { g.S.micro[k].status = 'S2';
  g.S.micro[k].items.forEach(it => { it.example = 'На 3 занятии в ситуации свободной игры ребёнок…'; }); });
g.S.blocks.METH.forEach(it => it.example = 'Педагог предъявил знакомую игрушку и сделал паузу…');

console.log('\n== 4. Сборка документа ==');
const doc = noThrow('buildDoc()', () => g.buildDoc());
ok(doc && doc.blocks.length === 8, 'блоков в документе: ' + (doc ? doc.blocks.length : 0) + ' (7 + приложение)');
ok(doc && doc.blocks[0].paras.length >= 6, 'абзацев в актуальном состоянии: ' + (doc ? doc.blocks[0].paras.length : 0));
const lit = doc && doc.blocks.find(b => /литератур/i.test(b.title));
ok(lit && lit.paras.filter(p => p.li).length === g.BANK.literature.length,
   'литература: ' + (lit ? lit.paras.filter(p => p.li).length : 0) + ' позиций');
ok(doc.blocks[doc.blocks.length - 1].title.indexOf('Приложение') === 0, 'приложение «Рабочие материалы» есть');
const plain = noThrow('docPlainText()', () => g.docPlainText(doc));
ok(plain && plain.length > 3000, 'текстовая версия: ' + (plain ? plain.length : 0) + ' символов');
ok(doc.blocks[0].paras.every(p => p.text && p.text.indexOf('[микротема не заполнена]') < 0),
   'незаполненных микротем нет');

console.log('\n== 5. Чек-лист ==');
const chk = noThrow('runChecklist()', () => g.runChecklist(doc));
ok(chk && chk.length >= 12, 'пунктов чек-листа: ' + (chk ? chk.length : 0));
ok(chk.filter(c => c.pass === false && c.sev === 'block').length === 0, 'обязательных замечаний нет');
chk.filter(c => c.pass === false).forEach(c => console.log('       предупреждение: ' + c.text));

console.log('\n== 6. Генерация .docx (ZIP + OOXML) ==');
const res = noThrow('сборка .docx', () => docxBytes(g));
ok(res && res.bytes.length > 5000, 'размер файла: ' + (res ? res.bytes.length : 0) + ' байт');
const out = path.join(__dirname, '_test_output.docx');
fs.writeFileSync(out, res.bytes);
ok(res.bytes[0] === 0x50 && res.bytes[1] === 0x4b, 'сигнатура ZIP (PK) на месте');
ok(/\.docx$/.test(res.name), 'имя файла: ' + res.name);

console.log('\n== 7. CSV импорт/экспорт ==');
const csv = noThrow('toCsv()', () => g.toCsv(g.BANK.phrases));
ok(csv.split('\n').length === g.BANK.phrases.length + 1, 'CSV строк: ' + (csv.split('\n').length - 1));
const parsed = noThrow('parseCsv()', () => g.parseCsv(csv));
ok(parsed.length === g.BANK.phrases.length, 'из CSV прочитано: ' + parsed.length);
ok(parsed.filter((p, i) => p.text !== g.BANK.phrases[i].text).length === 0, 'тексты совпадают после цикла CSV');
ok(parsed.every(p => Array.isArray(p.links_goal)), 'связи читаются как массивы');
ok(parsed.filter(p => p.needs_example !== g.BANK.phrases[parsed.indexOf(p)].needs_example).length === 0,
   'флаг «требует примера» сохраняется');

console.log('\n== 8. Адаптация текста (род и термин) ==');
g.S.gender = 'f'; g.S.subject = 'ребёнок';
ok(g.adapt('Склонен к возбуждению, он уходит из контакта, его нужно поддержать.').indexOf('Склонна') === 0,
   'женский род: ' + g.adapt('Склонен к возбуждению, он уходит.'));
g.S.subject = 'подопечный';
const rep = g.adapt('Ребёнок проявляет интерес. Интерес ребёнка устойчив. Помощь нужна ребёнку и ребёнком.');
ok(rep === 'Подопечный проявляет интерес. Интерес подопечного устойчив. Помощь нужна подопечному и подопечным.',
   'замена термина по падежам: ' + rep);
g.S.subject = 'Иван';
ok(g.adapt('Ребёнок играет. Интерес ребёнка.').indexOf('Иван') === 0,
   'произвольный термин (имя): ' + g.adapt('Ребёнок играет.'));
g.S.gender = 'm'; g.S.subject = 'ребёнок';

console.log('\n== 9. Целостность ключа опросника и связей банка ==');
const broken = [];
g.BANK.questionnaire.forEach(item => {
  Object.entries(item.key || {}).forEach(([ans, key]) => {
    ['as', 'goal', 'meth', 'rec', 'res', 'nxt'].forEach(k => (key[k] || []).forEach(id => {
      if (!g.byId(id)) broken.push(item.id + '/' + ans + '/' + k + ':' + id);
    }));
    (key.svc || []).forEach(id => { if (!g.BANK.svcIndex[id]) broken.push(item.id + '/svc:' + id); });
  });
});
ok(broken.length === 0, 'битых ссылок в ключе: ' + broken.length + (broken.length ? ' → ' + broken.slice(0, 5) : ''));
const brokenLinks = [];
g.BANK.phrases.forEach(p => ['links_goal', 'links_meth', 'links_rec'].forEach(k =>
  (p[k] || []).forEach(id => { if (!g.byId(id)) brokenLinks.push(p.id + ':' + id); })));
ok(brokenLinks.length === 0, 'битых связей в банке: ' + brokenLinks.length);

console.log('\n== 10. Пустой документ (свежий черновик) ==');
const savedState = g.S;
g.S = {v: 1, direction: 'IV', subject: 'ребёнок', gender: 'm', showSubheads: false, includeWorklog: false,
  header: {fio: '', birth: '', period_start: '', period_end: '', specialist: '', sessions: '',
           direction_name: 'Игровое взаимодействие'},
  answers: {}, iv2: {}, micro: {}, asService: '', blocks: {GOAL: [], METH: [], RES: [], NEXT: [], REC: []},
  recTopics: {}, lit: [], notes: {}};
g.ensureMicro();
ok(!g.S.micro.AS7prax && !g.S.micro.AS8vis,
   'ensureMicro() не создаёт в черновике V1 микротемы версии 2 (AS7prax/AS8vis)');
ok(Object.keys(g.S.micro).length === 6,
   'микротем актуального состояния в черновике V1: ' + Object.keys(g.S.micro).length);
const emptyDoc = noThrow('buildDoc() на пустом документе', () => g.buildDoc());
ok(emptyDoc && emptyDoc.blocks.length === 7, 'пустой документ собирается, блоков: ' + (emptyDoc ? emptyDoc.blocks.length : 0));
noThrow('docPlainText() на пустом', () => g.docPlainText(emptyDoc));
noThrow('buildDocumentXml() на пустом', () => g.buildDocumentXml(emptyDoc));
const emptyChk = noThrow('runChecklist() на пустом', () => g.runChecklist(emptyDoc));
ok(emptyChk.filter(c => c.pass === false).length >= 5,
   'на пустом документе чек-лист даёт замечания: ' + emptyChk.filter(c => c.pass === false).length);
['header', 'survey', 'as', 'goals', 'results', 'recs', 'doc', 'bank', 'help'].forEach(t => {
  g.TAB = t; noThrow('рендер «' + t + '» на пустом', () => g.render()); });
g.S.asService = 'SV-STRESS';
g.S.micro.AS3soc.service = 'SV-SEN';
const withSvc = noThrow('buildDoc() со служебными отметками', () => g.buildDoc());
ok(withSvc.blocks[0].paras.some(p => p.italic), 'общая служебная отметка попала в блок');
ok(withSvc.blocks[0].paras.some(p => /сенсорной информации/i.test(p.text)), 'служебная фраза микротемы попала в блок');
g.S = savedState;

console.log('\n== 11. Переключатель «добавить / убрать» ==');
const fresh = {v:1, direction:'IV', subject:'ребёнок', gender:'m', showSubheads:false, includeWorklog:false,
  header:{fio:'Т',birth:'',period_start:'',period_end:'',specialist:'',sessions:'',direction_name:'Игровое взаимодействие'},
  answers:{}, iv2:{}, micro:{}, asService:'', blocks:{GOAL:[],METH:[],RES:[],NEXT:[],REC:[]}, recTopics:{}, lit:[], notes:{}};
g.S = JSON.parse(JSON.stringify(fresh)); g.ensureMicro();
ok(!g.isAdded('AS4ini-S2-01','MICRO:AS4ini'), 'до добавления isAdded=false');
g.addMicroItem('AS4ini','AS4ini-S2-01');
ok(g.isAdded('AS4ini-S2-01','MICRO:AS4ini'), 'после добавления isAdded=true');
ok(g.removeFrom('AS4ini-S2-01','MICRO:AS4ini')===true, 'removeFrom вернул true');
ok(!g.isAdded('AS4ini-S2-01','MICRO:AS4ini') && g.S.micro.AS4ini.items.length===0, 'фраза убрана из микротемы');
g.addItem('GOAL','GL-07');
ok(g.isAdded('GL-07','GOAL'), 'цель добавлена');
ok(g.removeFrom('GL-07','GOAL')===true && g.S.blocks.GOAL.length===0, 'цель убрана');
g.addRecItem('RC4play','RC-05');
ok(g.isAdded('RC-05','REC:RC4play'), 'рекомендация добавлена');
ok(g.removeFrom('RC-05','REC:RC4play')===true && (g.S.recTopics.RC4play||[]).length===0, 'рекомендация убрана');
g.S.micro.AS3soc.service='SV-SEN';
ok(g.isAdded('SV-SEN','MICRO:AS3soc'), 'служебная отметка микротемы видна как добавленная');
ok(g.removeFrom('SV-SEN','MICRO:AS3soc')===true && g.S.micro.AS3soc.service==='', 'служебная отметка снята');
g.S.asService='SV-STRESS';
ok(g.isAdded('SV-STRESS','ASSVC'), 'общая служебная отметка видна как добавленная');
ok(g.removeFrom('SV-STRESS','ASSVC')===true && g.S.asService==='', 'общая служебная отметка снята');
g.addMicroItem('AS1sens','AS1sens-S2-01'); g.S.micro.AS1sens.items[0].text='фраза изменена вручную';
ok(g.removeFrom('AS1sens-S2-01','MICRO:AS1sens')===true, 'изменённая вручную фраза убирается после подтверждения');
ok(g.targetName('MICRO:AS4ini').indexOf('актуальное состояние')===0, 'targetName микротемы: '+g.targetName('MICRO:AS4ini'));
ok(g.targetName('GOAL')==='цели на период', 'targetName блока целей');
ok(g.targetName('REC:RC4play').indexOf('рекомендации')===0, 'targetName темы рекомендаций');
const bFree=g.addBtn('GL-01','GOAL');
ok(bFree.indexOf('+ в документ')>=0 && bFree.indexOf('disabled')<0, 'кнопка свободной фразы активна');
g.addItem('GOAL','GL-01');
const bOn=g.addBtn('GL-01','GOAL');
ok(bOn.indexOf('убрать')>=0 && bOn.indexOf('disabled')<0, 'кнопка добавленной фразы активна и предлагает убрать');
ok(bOn.indexOf('title="Убрать из:')>=0, 'у кнопки добавленной фразы подсказка «Убрать из …»');
g.S = savedState;

console.log('\n' + (fails === 0 ? '✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ' : '❌ ПРОВАЛОВ: ' + fails));
process.exit(fails === 0 ? 0 : 1);
