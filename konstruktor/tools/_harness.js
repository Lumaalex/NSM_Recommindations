// Общая обвязка: запускает клиентский код конструктора V2 вне браузера (Node).
// Используется в tools/test_v2.js. Клиент сам экспортирует API в window.V2API.
const fs = require('fs');
const vm = require('vm');

/* Мини-DOM: хранит элементы по id, позволяет тестам кликать по кнопкам и читать innerHTML.
   Реальные элементы лежат в reg (id -> el); children — это ключи reg (порядковый номер),
   чтобы обход был стабильным при перерендере. Элементы шаблонного HTML (в т.ч. вне body)
   регистрируются через __register — так getElementById находит #btnSave, #fileBank и т.п. */
function makeDom() {
  const reg = {}; let seq = 0;
  function mk(tag) {
    const key = 'k' + (++seq);
    const el = {__key: key, tagName: (tag || 'div').toUpperCase(), innerHTML: '', textContent: '',
      value: '', checked: false, disabled: false, dataset: {}, children: [],
      style: {setProperty() {}, removeProperty() {}, getPropertyValue() { return ''; }},
      className: '', type: '', files: [], onclick: null, onchange: null, oninput: null,
      setAttribute(k, v) { if (k === 'id') { this.id = v; reg[v] = this; } this[k] = v; },
      getAttribute(k) { return this[k]; },
      appendChild(c) { this.children.push((c && c.__key) || c); return c; },
      removeChild(c) { const i = this.children.indexOf((c && c.__key) || c); if (i >= 0) this.children.splice(i, 1); },
      remove() { const par = this.parentNode; if (par) { const i = par.children.indexOf(this.__key); if (i >= 0) par.children.splice(i, 1); } },
      click() { if (this.onclick) this.onclick({target: this}); },
      focus() {}, addEventListener() {}, querySelector(s) { return findIn(this, s); },
      querySelectorAll(s) { return findAllIn(this, s); }};
    return el;
  }
  function kids(el) { return (el.children || []).map(k => reg[k]).filter(Boolean); }
  function walk(root, out) { kids(root).forEach(c => { out.push(c); walk(c, out); }); return out; }
  function matches(el, sel) {
    if (sel[0] === '#') return el.id === sel.slice(1);
    if (sel[0] === '[') { const m = sel.match(/^\[([^\]=]+)(?:=["']?([^"'\]]*)["']?)?\]$/);
      if (!m) return false; const attr = m[1], val = m[2];
      const dv = /^data-(.+)$/.exec(attr);
      const cur = dv ? (el.dataset || {})[dv[1].replace(/-([a-z])/g, (x, c) => c.toUpperCase())] : el[attr];
      return val === undefined ? cur !== undefined : String(cur) === val; }
    if (sel[0] === '.') return String(el.className || '').split(/\s+/).indexOf(sel.slice(1)) >= 0;
    return String(el.tagName).toLowerCase() === sel.toLowerCase();
  }
  function findIn(root, sel) { const all = walk(root, []); for (const e of all) if (matches(e, sel)) return e; return null; }
  function findAllIn(root, sel) { return walk(root, []).filter(e => matches(e, sel)); }
  const body = mk('body');
  const dom = {
    body, documentElement: mk('html'), title: '',
    createElement: t => mk(t),
    getElementById(id) { return reg[id] || findIn(body, '#' + id) || null; },
    querySelector: s => (s[0] === '#' && reg[s.slice(1)]) || findIn(body, s),
    querySelectorAll: s => findAllIn(body, s),
    addEventListener() {},
    __set(node, html) { node.innerHTML = html; node.children = [];   // упрощённый парсер: id="…" и data-атрибуты
      const re = /id="([^"]+)"/g; let m; while ((m = re.exec(html))) {
        if (reg[m[1]]) { node.children.push(reg[m[1]].__key); continue; }
        const kid = mk('div'); kid.id = m[1]; kid.parentNode = node; node.children.push(kid.__key); reg[m[1]] = kid; }
      // регистрация data-атрибутов (data-goto, data-own и т.п.) — селекторы вида [data-x="y"] в тестах
      const dre = /<(button|input|select|span|div|a|td|th|li)\b([^>]*)>/gi; let dm;
      while ((dm = dre.exec(html))) {
        const attrs = dm[2];
        if (!/\sid="/.test(attrs)) continue;
        const am = /\sid="([^"]+)"/.exec(attrs);
        const el = reg[am[1]]; if (!el) continue;
        const are = /data-([a-z0-9-]+)="([^"]*)"/gi; let a;
        while ((a = are.exec(attrs))) {
          const camel = a[1].replace(/-([a-z0-9])/g, (x, c) => c.toUpperCase());
          el['data-' + a[1]] = a[2]; el.dataset[camel] = a[2];
        } } },
    __register(ids) { ids.forEach(id => { if (!reg[id]) { const kid = mk('div'); kid.id = id; reg[id] = kid; } }); },
    __reg: reg,
  };
  return dom;
}

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
  const dom = makeDom();
  // регистрируем все id из шаблонного HTML (шапка, кнопки вне #main, file-инпуты)
  dom.__register((html.match(/id="([^"]+)"/g) || []).map(s => s.slice(4, -1)));
  // перехват записи innerHTML у ВСЕХ элементов: парсим id="…" и регистрируем их (реалистичный ререндер)
  function wrap(el) {
    if (!el) return el;
    return new Proxy(el, {
      get(t, p) {
        const v = t[p];
        if (typeof v === 'function') return v.bind(t);
        if (p === 'children') return (t.children || []).map(k => reg2wrap(k));
        if (p === 'parentNode') return wrap(t.parentNode);
        return v;
      },
      set(t, p, v) {
        if (p === 'innerHTML') { dom.__set(t, String(v)); return true; }
        if (p === 'onclick' || p === 'onchange' || p === 'oninput') { t[p] = (v && v.__raw) ? v.__raw : v; return true; }
        t[p] = v; return true;
      },
    });
  }
  function reg2wrap(k) { const e = dom.__reg[k]; return e ? wrap(e) : null; }
  dom.body = wrap(dom.body);
  const origCreate = dom.createElement;
  dom.createElement = t => wrap(origCreate(t));
  const origGet = dom.getElementById;
  dom.getElementById = id => wrap(origGet(id));
  const origQs = dom.querySelector;
  dom.querySelector = s => wrap(origQs(s));
  const origQsa = dom.querySelectorAll;
  dom.querySelectorAll = s => origQsa(s).map(wrap);
  sandbox.document = Object.create(dom);
  sandbox.document.getElementById = id => (id === 'bank-data' ? {textContent: DATA} : dom.getElementById(id));
  sandbox.window = sandbox;
  sandbox.scrollTo = () => {};
  sandbox.addEventListener = () => {};
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox, {filename: 'app.js'});
  sandbox.__dom = dom;   // доступ к мини-DOM из тестов
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
