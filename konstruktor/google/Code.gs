/**
 * КОНСТРУКТОР РЕКОМЕНДАЦИЙ — серверная часть Google Apps Script
 * ============================================================
 * Привязывается к Google-таблице, созданной из файла «Банк_фраз.xlsx»
 * (загрузите xlsx на Диск → открыть с помощью Google Таблиц).
 *
 * Установка: см. google/УСТАНОВКА.md
 *   1) Расширения → Apps Script → вставить этот файл как Code.gs
 *   2) добавить HTML-файл с именем Index (содержимое google/Index.html)
 *   3) один раз выполнить функцию setup()
 *   4) Развернуть → Веб-приложение (доступ: «Все») → раздать ссылку специалистам
 *
 * Таблица = мастер-база: правите листы — веб-приложение подхватывает при следующем открытии.
 */

var CFG = {
  docsFolder: 'Заключения ИВ',
  draftsSheet: 'Черновики',
  proposalsSheet: 'Предложения фраз',
  sheets: {
    phrases: 'Фразы', survey: 'Опросник_ключ', iv2: 'ИВ2_наблюдения', statuses: 'Статусы',
    support: 'Поддержка', blocks: 'Блоки', micro: 'Микроблоки', abilities: 'Способности',
    service: 'Служебные_фразы', linkmap: 'Карта_связей', checklist: 'Чек-лист',
    lit: 'Литература', directions: 'Направления'
  }
};

/* ------------------------------------------------------------------ ТОЧКА ВХОДА */
function doGet(e) {
  var t = HtmlService.createTemplateFromFile('Index');
  t.bankJson = JSON.stringify(readBank()).replace(/</g, '\\u003c');
  return t.evaluate()
    .setTitle('Конструктор рекомендаций')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, viewport-fit=cover')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/* ------------------------------------------------------------------ СЛУЖЕБНОЕ */
function ss_() { return SpreadsheetApp.getActiveSpreadsheet(); }

function sheetRows_(name, must) {
  var sh = ss_().getSheetByName(name);
  if (!sh) return [];
  var values = sh.getDataRange().getValues();
  var hi = -1;
  for (var i = 0; i < Math.min(8, values.length); i++) {
    var cells = values[i].map(function (c) { return String(c == null ? '' : c).trim(); });
    var hit = (must || ['ID']).some(function (m) { return cells.indexOf(m) >= 0; });
    if (hit && cells.filter(function (c) { return c; }).length >= 2) { hi = i; break; }
  }
  if (hi < 0) return [];
  var headers = values[hi].map(function (c) { return String(c == null ? '' : c).trim(); });
  var out = [];
  for (var r = hi + 1; r < values.length; r++) {
    var row = values[r];
    if (!row.some(function (c) { return String(c == null ? '' : c).trim(); })) continue;
    var o = {};
    for (var cIdx = 0; cIdx < headers.length; cIdx++) o[headers[cIdx]] = row[cIdx];
    out.push(o);
  }
  return out;
}
function s_(o, k, d) { var v = o[k]; return (v == null || v === '') ? (d == null ? '' : d) : String(v).trim(); }
function yn_(v, d) { if (v == null || v === '') return !!d; return ['да', '1', 'true', 'yes', '+'].indexOf(String(v).trim().toLowerCase()) >= 0; }
function idl_(v) { if (!v) return []; return String(v).split(/[;,]/).map(function (x) { return x.trim(); }).filter(Boolean); }
function parseKey_(v) {
  var res = {as: [], goal: [], meth: [], rec: [], res: [], nxt: [], svc: []};
  if (!v) return res;
  String(v).split('|').forEach(function (part) {
    var i = part.indexOf(':');
    if (i < 0) return;
    var k = part.slice(0, i).trim().toLowerCase();
    var vals = part.slice(i + 1).split(/[;,]/).map(function (x) { return x.trim(); }).filter(Boolean);
    if (res[k] !== undefined) res[k] = vals;
  });
  return res;
}

/* ------------------------------------------------------------------ ЧТЕНИЕ БАНКА ИЗ ТАБЛИЦЫ */
function readBank() {
  var bank = {
    meta: {version: 'google-1.0', updated: Utilities.formatDate(new Date(), 'Europe/Moscow', 'yyyy-MM-dd'),
      title: 'Конструктор рекомендаций',
      standard: 'Верхнеуровневые блоки не пропускаются. Пропускаются только формулировки внутри блока — вместо них ставится служебная отметка.'},
    directions: [], blocks: [], microblocks: [], statuses: [], support_types: [], abilities: [],
    phrases: [], service_phrases: [], literature: [], checklist: [], link_map: [],
    questionnaire: [], iv2_questions: [],
    status_by_answer: {'3': 'S3', '2': 'S2', '1': 'S1', '0': 'S0', 'N': 'SN'},
    doc_structure: {header_fields: [], title: 'Индивидуальные рекомендации по направлению «{direction}»'}
  };

  sheetRows_(CFG.sheets.phrases).forEach(function (r) {
    var id = s_(r, 'ID'), text = s_(r, 'Текст формулировки');
    if (!id || !text) return;
    bank.phrases.push({
      id: id, dir: s_(r, 'Направление', 'IV'), block: s_(r, 'Блок', 'AS'), micro: s_(r, 'Микроблок'),
      ability: s_(r, 'Способность'), status: s_(r, 'Статус'), text: text, source: s_(r, 'Источник'),
      needs_example: yn_(r['Требует примера'], true), example_hint: s_(r, 'Подсказка: какой пример нужен'),
      links_goal: idl_(r['Цели(ID)']), links_meth: idl_(r['Приёмы(ID)']), links_rec: idl_(r['Рекомендации(ID)']),
      tags: s_(r, 'Теги/домен'), active: yn_(r['Активна'], true)
    });
  });

  sheetRows_(CFG.sheets.survey).forEach(function (r) {
    var id = s_(r, 'ID'), text = s_(r, 'Пункт опросника');
    if (!id || !text) return;
    var stage = parseInt(r['Стадия DIR'], 10); if (isNaN(stage)) stage = 0;
    bank.questionnaire.push({
      id: id, dir: 'IV', source: s_(r, 'Источник', 'DIR'), stage: stage, domain: s_(r, 'Домен'),
      micro: s_(r, 'Микроблок'), text: text, scale: true, note: '',
      key: {'3': parseKey_(r['Ключ: 3 (стабильно)']), '2': parseKey_(r['Ключ: 2 (иногда)']),
            '1': parseKey_(r['Ключ: 1 (с поддержкой)']), '0': parseKey_(r['Ключ: 0 (не проявляется)']),
            'N': parseKey_(r['Ключ: N (не проверялось)'])}
    });
  });

  sheetRows_(CFG.sheets.iv2).forEach(function (r) {
    var id = s_(r, 'ID'), text = s_(r, 'Вопрос');
    if (!id || !text) return;
    bank.iv2_questions.push({id: id, dir: 'IV', source: 'ИВ2', group: s_(r, 'Раздел'), text: text,
      scale: false, micro: '', key: {}});
  });

  sheetRows_(CFG.sheets.statuses).forEach(function (r) {
    var code = s_(r, 'Код'); if (!code) return;
    bank.statuses.push({code: code, name: s_(r, 'Название'), definition: s_(r, 'Когда ставим'),
      rule: s_(r, 'Правило'), goes_to: s_(r, 'Куда попадает')});
  });

  sheetRows_(CFG.sheets.support, ['Тип поддержки']).forEach(function (r) {
    var name = s_(r, 'Тип поддержки'); if (!name) return;
    bank.support_types.push({id: name.toLowerCase().replace(/\W+/g, '').slice(0, 8), name: name,
      examples: s_(r, 'Примеры')});
  });

  sheetRows_(CFG.sheets.blocks).forEach(function (r) {
    var id = s_(r, 'ID'); if (!id) return;
    var order = parseInt(r['№'], 10); if (isNaN(order)) order = bank.blocks.length + 1;
    bank.blocks.push({id: id, order: order, name: s_(r, 'Название блока'),
      mandatory: yn_(r['Обязателен'], true), hint: s_(r, 'Что пишем')});
  });

  sheetRows_(CFG.sheets.micro).forEach(function (r) {
    var id = s_(r, 'ID'); if (!id) return;
    var order = parseInt(r['№'], 10); if (isNaN(order)) order = bank.microblocks.length + 1;
    var svc = s_(r, 'Служебная фраза (ID)');
    bank.microblocks.push({id: id, block: s_(r, 'Блок'), order: order, name: s_(r, 'Название микротемы'),
      mandatory: yn_(r['Обязателен'], true), service: svc || null});
  });

  sheetRows_(CFG.sheets.abilities).forEach(function (r) {
    var id = s_(r, 'ID'); if (!id) return;
    var stage = parseInt(r['Стадия DIR'], 10); if (isNaN(stage)) stage = 0;
    bank.abilities.push({id: id, name: s_(r, 'Способность'), micro: s_(r, 'Микроблок'), stage: stage});
  });

  sheetRows_(CFG.sheets.service).forEach(function (r) {
    var id = s_(r, 'ID'); if (!id) return;
    var micro = s_(r, 'Микроблок');
    bank.service_phrases.push({id: id, microblock: (micro === '—' ? null : (micro || null)),
      situation: s_(r, 'Ситуация'), text: s_(r, 'Формулировка')});
  });

  sheetRows_(CFG.sheets.linkmap, ['Маркер / способность']).forEach(function (r) {
    var m = s_(r, 'Маркер / способность'); if (!m) return;
    bank.link_map.push({marker: m, stable: s_(r, 'Если стабильно'), sometimes: s_(r, 'Если иногда'),
      goal: s_(r, 'Цель'), method: s_(r, 'Приём'), rec: s_(r, 'Рекомендация')});
  });

  sheetRows_(CFG.sheets.checklist, ['№', 'Проверка перед выдачей документа']).forEach(function (r) {
    var text = s_(r, 'Проверка перед выдачей документа'); if (!text) return;
    var imp = s_(r, 'Важность').toLowerCase();
    bank.checklist.push({id: s_(r, '№') || ('C' + (bank.checklist.length + 1)), text: text,
      severity: imp.indexOf('обязат') >= 0 ? 'block' : 'warn'});
  });

  sheetRows_(CFG.sheets.lit, ['№', 'Издание']).forEach(function (r) {
    var t = s_(r, 'Издание'); if (t) bank.literature.push(t);
  });

  sheetRows_(CFG.sheets.directions).forEach(function (r) {
    var id = s_(r, 'ID'); if (!id) return;
    bank.directions.push({id: id, name: s_(r, 'Название'), short: s_(r, 'Коротко'),
      subject_default: s_(r, 'Термин по умолчанию', 'ребёнок'), active: yn_(r['Наполнено'], false),
      note: s_(r, 'Примечание')});
  });

  if (!bank.blocks.length) bank.blocks = [
    {id: 'AS', order: 1, name: 'Актуальное состояние', mandatory: true, hint: ''},
    {id: 'GOAL', order: 2, name: 'Цели на период реабилитации', mandatory: true, hint: ''},
    {id: 'METH', order: 3, name: 'Приёмы работы', mandatory: true, hint: ''},
    {id: 'RES', order: 4, name: 'Результаты', mandatory: true, hint: ''},
    {id: 'NEXT', order: 5, name: 'Цели на следующий период', mandatory: true, hint: ''},
    {id: 'REC', order: 6, name: 'Рекомендации', mandatory: true, hint: ''},
    {id: 'LIT', order: 7, name: 'Рекомендуемая литература', mandatory: true, hint: ''}];
  return bank;
}

/* ------------------------------------------------------------------ ПАПКА И СЛУЖЕБНЫЕ ЛИСТЫ */
function docsFolder_() {
  var it = DriveApp.getFoldersByName(CFG.docsFolder);
  if (it.hasNext()) return it.next();
  return DriveApp.createFolder(CFG.docsFolder);
}
function ensureSheet_(name, headers) {
  var sh = ss_().getSheetByName(name);
  if (!sh) sh = ss_().insertSheet(name);
  if (sh.getLastRow() === 0) sh.appendRow(headers);
  return sh;
}
function setup() {
  ensureSheet_(CFG.draftsSheet, ['Имя', 'Обновлён', 'JSON']);
  ensureSheet_(CFG.proposalsSheet, ['Дата', 'Автор', 'Блок', 'Микроблок', 'Статус', 'Текст',
    'Цели(ID)', 'Приёмы(ID)', 'Рекомендации(ID)', 'Комментарий', 'Статус модерации']);
  docsFolder_();
  return 'Готово: созданы листы «' + CFG.draftsSheet + '», «' + CFG.proposalsSheet +
         '» и папка «' + CFG.docsFolder + '».';
}

/* ------------------------------------------------------------------ ЧЕРНОВИКИ */
function listDrafts() {
  var sh = ss_().getSheetByName(CFG.draftsSheet);
  if (!sh) return [];
  var v = sh.getDataRange().getValues();
  var out = [];
  for (var i = 1; i < v.length; i++) if (v[i][0]) out.push({name: String(v[i][0]), updated: String(v[i][1])});
  return out;
}
function saveDraft(name, json) {
  if (!name) throw new Error('Укажите имя черновика');
  if (String(json).length > 49000) throw new Error('Черновик больше 49 000 символов — разгрузите примеры наблюдений');
  var sh = ensureSheet_(CFG.draftsSheet, ['Имя', 'Обновлён', 'JSON']);
  var v = sh.getDataRange().getValues();
  var stamp = Utilities.formatDate(new Date(), 'Europe/Moscow', 'dd.MM.yyyy HH:mm');
  for (var i = 1; i < v.length; i++) {
    if (String(v[i][0]) === name) { sh.getRange(i + 1, 2).setValue(stamp); sh.getRange(i + 1, 3).setValue(json); return {name: name, updated: stamp}; }
  }
  sh.appendRow([name, stamp, json]);
  return {name: name, updated: stamp};
}
function loadDraft(name) {
  var sh = ss_().getSheetByName(CFG.draftsSheet);
  if (!sh) return null;
  var v = sh.getDataRange().getValues();
  for (var i = 1; i < v.length; i++) if (String(v[i][0]) === name) return String(v[i][2]);
  return null;
}
function deleteDraft(name) {
  var sh = ss_().getSheetByName(CFG.draftsSheet);
  if (!sh) return false;
  var v = sh.getDataRange().getValues();
  for (var i = 1; i < v.length; i++) {
    if (String(v[i][0]) === name) { sh.deleteRow(i + 1); return true; }
  }
  return false;
}

/* ------------------------------------------------------------------ ПРЕДЛОЖЕНИЯ ФРАЗ */
function proposePhrase(obj) {
  var sh = ensureSheet_(CFG.proposalsSheet, ['Дата', 'Автор', 'Блок', 'Микроблок', 'Статус', 'Текст',
    'Цели(ID)', 'Приёмы(ID)', 'Рекомендации(ID)', 'Комментарий', 'Статус модерации']);
  sh.appendRow([
    Utilities.formatDate(new Date(), 'Europe/Moscow', 'dd.MM.yyyy HH:mm'),
    obj.author || '', obj.block || '', obj.micro || '', obj.status || '', obj.text || '',
    (obj.links_goal || []).join(';'), (obj.links_meth || []).join(';'), (obj.links_rec || []).join(';'),
    obj.comment || '', 'на модерации']);
  return 'Предложение отправлено методисту';
}

/* ------------------------------------------------------------------ ГОТОВЫЙ ДОКУМЕНТ */
function createGoogleDoc(docJson) {
  var d = JSON.parse(docJson);
  var doc = DocumentApp.create(fileName_(d));
  var body = doc.getBody();
  body.clear();
  var fam = {FONT_FAMILY: 'Times New Roman', FONT_SIZE: 12};
  var title = body.appendParagraph(d.title || '');
  title.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
  title.setAttributes({FONT_FAMILY: 'Times New Roman', FONT_SIZE: 14, BOLD: true});
  var rows = [['ФИО:', d.header.fio], ['Дата рождения:', d.header.birth],
    ['Дата начала периода реабилитации:', d.header.period_start],
    ['Дата окончания периода реабилитации:', d.header.period_end],
    ['Специалист:', d.header.specialist], ['Количество занятий:', d.header.sessions]];
  var tbl = body.appendTable(rows);
  tbl.setBorderWidth(1);
  tbl.setColumnWidth(0, 220);
  (d.blocks || []).forEach(function (b) {
    var h = body.appendParagraph(b.title);
    h.setAttributes({FONT_FAMILY: 'Times New Roman', FONT_SIZE: 12, BOLD: true});
    (b.paras || []).forEach(function (p) {
      var par;
      if (p.li) par = body.appendListItem(p.text);
      else {
        par = body.appendParagraph(p.text);
        par.setAlignment(DocumentApp.HorizontalAlignment.JUSTIFY);
      }
      var attrs = {FONT_FAMILY: 'Times New Roman', FONT_SIZE: b.small ? 10 : 12};
      if (p.bold) attrs.BOLD = true;
      if (p.italic) attrs.ITALIC = true;
      par.setAttributes(attrs);
    });
  });
  body.getParagraphs().forEach(function (p) { if (!p.getText()) return; });
  doc.saveAndClose();
  var file = DriveApp.getFileById(doc.getId());
  try { file.moveTo(docsFolder_()); } catch (e) { /* уже в папке */ }
  return {url: doc.getUrl(), id: doc.getId(), name: doc.getName()};
}
function saveDocx(base64, name) {
  var blob = Utilities.newBlob(Utilities.base64Decode(base64),
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', name);
  var file = docsFolder_().createFile(blob);
  return {url: file.getUrl(), id: file.getId(), name: name};
}
function fileName_(d) {
  var fio = String((d.header && d.header.fio) || 'без_ФИО').trim().replace(/\s+/g, '_');
  return 'Заключение_ИВ_' + fio + '_' + String(((d.header && d.header.period_end) || '')).replace(/\./g, '-');
}
