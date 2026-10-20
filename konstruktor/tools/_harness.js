// Общая обвязка: запускает клиентский код конструктора вне браузера (Node).
// Используется в tools/test_app.js и tools/make_example.js
const fs = require('fs');
const vm = require('vm');

function makeEl(tag) {
  const store = {tagName: tag || 'div', innerHTML: '', textContent: '', value: '', checked: false,
                 style: new Proxy({setProperty() {}, removeProperty() {}}, {
                   get: (t, p) => (p in t ? t[p] : makeEl()),
                   set: (t, p, v) => { t[p] = v; return true; } }),
                 dataset: {}, children: []};
  const fn = function () { return makeEl(); };
  return new Proxy(fn, {
    get(t, p) {
      if (p in store) return store[p];
      if (p === 'length') return 0;
      if (p === Symbol.toPrimitive) return () => '';
      if (p === 'then') return undefined;
      return makeEl();
    },
    set(t, p, v) { store[p] = v; t[p] = v; return true; },
    apply() { return makeEl(); }
  });
}

const EPILOGUE = `
;globalThis.__app = {
  get BANK(){return BANK}, set BANK(v){BANK=v},
  get S(){return S}, set S(v){S=v},
  get TAB(){return TAB}, set TAB(v){TAB=v},
  get UI(){return UI}, set UI(v){UI=v},
  get BANK_DEFAULT(){return BANK_DEFAULT},
  render, bind, ensureMicro, adapt, hasPhrase, addMicroItem, addItem, addRecItem, byId,
  buildDoc, docPlainText, runChecklist, buildDocumentXml, zipStore, toCsv, parseCsv, fileName,
  isAdded, removeFrom, targetName, addBtn, migrateDoc, normalizeState,
  blockName, microName, v1PhraseCount, v2OnlyMicroNames, syncHdrChips,
  countSpheres, sphereAnswerOpts, poolAsFor, sphereAsPool, sphSugg, keySuggestions,
  sensAutoTextFor, sensApply, sensDrop, sensFilled, sensTotal, sensBlocksOf,
  linkedSuggestionsCard, linkedStrip,
  get SPHERE_ANS(){return SPHERE_ANS}, get PED_OF(){return PED_OF}, get CORE2SPH(){return CORE2SPH},
  get CT_XML(){return CT_XML}, get RELS_XML(){return RELS_XML}, get STYLES_XML(){return STYLES_XML},
  get NUM_XML(){return NUM_XML}, get DOC_RELS_XML(){return DOC_RELS_XML},
  vHeader, vSurvey, vAS, vGoals, vResults, vRecs, vDoc, vBank, vHelp,
};`;

function loadApp(htmlPath, opts) {
  opts = opts || {};
  const html = fs.readFileSync(htmlPath, 'utf8');
  const dm = html.match(/<script id="bank-data" type="application\/json">([\s\S]*?)<\/script>/);
  if (!dm) throw new Error('в HTML не найден блок bank-data');
  const DATA = dm[1].replace(/\\u003c/g, '<');
  JSON.parse(DATA);
  const scripts = [];
  const re = /<script(?![^>]*type="application\/json")[^>]*>([\s\S]*?)<\/script>/g;
  let m;
  while ((m = re.exec(html)) !== null) scripts.push(m[1]);
  const code = scripts.join('\n;\n') + (opts.epilogue === false ? '' : EPILOGUE);

  const store = {};
  const sandbox = {
    console, JSON, Math, Date, Object, Array, String, Number, Boolean, RegExp, Error, Promise,
    parseInt, parseFloat, isNaN,
    TextEncoder: require('util').TextEncoder,
    URL: {createObjectURL: () => 'blob:x', revokeObjectURL: () => {}},
    Blob: class { constructor(parts, opt) { this.parts = parts; this.opt = opt; } },
    FileReader: class { readAsText() {} },
    navigator: {clipboard: {writeText: () => Promise.resolve()}},
    localStorage: {getItem: k => (k in store ? store[k] : null),
                   setItem: (k, v) => { store[k] = String(v); },
                   removeItem: k => { delete store[k]; }},
    setTimeout: () => 0, clearTimeout: () => {},
    alert: () => {}, confirm: () => true, prompt: () => null,
    window: {scrollTo: () => {}, addEventListener: () => {}, print: () => {}},
  };
  sandbox.document = {
    documentElement: makeEl('html'),
    getElementById: id => (id === 'bank-data' ? {textContent: DATA} : makeEl()),
    createElement: t => makeEl(t),
    querySelector: () => makeEl(),
    querySelectorAll: () => [],
    body: makeEl('body'),
    addEventListener: () => {},
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox, {filename: 'app.js'});
  const app = sandbox.__app || (sandbox.window && (sandbox.window.V2API || sandbox.window.__app));
  if (!app) throw new Error('приложение не инициализировалось');
  return app;
}

/** Собирает .docx тем же кодом, которым это делает браузер. */
function docxBytes(g) {
  const d = g.buildDoc();
  const zip = g.zipStore([
    {name: '[Content_Types].xml', data: g.CT_XML},
    {name: '_rels/.rels', data: g.RELS_XML},
    {name: 'word/document.xml', data: g.buildDocumentXml(d)},
    {name: 'word/styles.xml', data: g.STYLES_XML},
    {name: 'word/numbering.xml', data: g.NUM_XML},
    {name: 'word/_rels/document.xml.rels', data: g.DOC_RELS_XML},
  ]);
  return {bytes: Buffer.from(zip), doc: d, name: g.fileName(d)};
}

module.exports = {loadApp, docxBytes, makeEl};
