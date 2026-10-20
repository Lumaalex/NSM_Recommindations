// Общая обвязка: запускает клиентский код конструктора V2 вне браузера (Node).
// Используется в tools/test_v2.js. Клиент сам экспортирует API в window.V2API.
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
  const code = scripts.join('\n;\n');

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
  sandbox.window = sandbox;
  sandbox.scrollTo = () => {};
  sandbox.addEventListener = () => {};
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox, {filename: 'app.js'});
  const app = sandbox.V2API;
  if (!app) throw new Error('приложение не экспортировало window.V2API');
  app.__localStorageKeys = () => Object.keys(store);
  return app;
}

/** Собирает .docx тем же кодом, которым это делает браузер (через g.docx()). */
function docxBytes(g) {
  const d = g.buildDoc();
  return {bytes: Buffer.from(g.docx()), doc: d, name: g.fileName(d)};
}

module.exports = {loadApp, docxBytes, makeEl};
