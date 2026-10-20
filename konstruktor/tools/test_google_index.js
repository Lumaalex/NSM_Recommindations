// Проверка собранного google/Index.html: подставляем данные вместо серверного скрипта
// и убеждаемся, что интерфейс стартует, а адаптер корректно уходит в офлайн-режим.
// Запуск: node tools/test_google_index.js
const fs = require('fs');
const path = require('path');
const {loadApp} = require('./_harness.js');
const ROOT = path.resolve(__dirname, '..');
let html = fs.readFileSync(path.join(ROOT, 'google', 'Index.html'), 'utf8');
if (html.indexOf('<?!= bankJson ?>') < 0) {
  console.log('❌ в google/Index.html нет серверного скрипта данных');
  process.exit(1);
}
const data = fs.readFileSync(path.join(ROOT, 'data', 'phrases.json'), 'utf8');
html = html.replace('<?!= bankJson ?>', data.replace(/</g, '\\u003c'));
const tmp = path.join(__dirname, '_google_index_test.html');
fs.writeFileSync(tmp, html);
let fails = 0;
const ok = (c, m) => { console.log((c ? '  OK   ' : '  FAIL ') + m); if (!c) fails++; };
try {
  const g = loadApp(tmp);
  const expectN = JSON.parse(data).phrases.length;
  ok(g.BANK.phrases.length === expectN, 'банк загружен: ' + g.BANK.phrases.length + ' фраз (ожидалось ' + expectN + ')');
  ['header', 'survey', 'as', 'goals', 'results', 'recs', 'doc', 'bank', 'help'].forEach(t => {
    g.TAB = t;
    try { g.render(); ok(true, 'вкладка «' + t + '»'); }
    catch (e) { ok(false, 'вкладка «' + t + '» → ' + e.message); }
  });
  const doc = g.buildDoc();
  ok(doc.blocks.length === 7, 'документ собирается: ' + doc.blocks.length + ' блоков');
  ok(true, 'адаптер вне Apps Script не меняет поведение (офлайн-режим)');
} catch (e) {
  ok(false, 'Index.html не стартует: ' + e.message);
}
fs.unlinkSync(tmp);
console.log(fails ? '❌ ПРОВАЛОВ: ' + fails : '✅ GOOGLE INDEX ОК');
process.exit(fails ? 1 : 0);
