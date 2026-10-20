/* ============================================================ АДАПТЕР GOOGLE APPS SCRIPT
   Встраивается в google/Index.html при сборке (tools/build_google.py).
   Вне среды Apps Script (открытый файл на компьютере) адаптер ничего не меняет —
   конструктор работает как прежде, офлайн.                                       */
(function () {
  if (typeof google === 'undefined' || !google.script || !google.script.run) {
    window.GC_BACKEND = 'local';
    return;
  }
  window.GC_BACKEND = 'google';

  function gas(fn) {
    var args = [].slice.call(arguments, 1);
    return new Promise(function (res, rej) {
      var r = google.script.run;
      r.withSuccessHandler(function (x) { res(x); })
       .withFailureHandler(function (e) { rej(new Error((e && e.message) || String(e))); })[fn].apply(r, args);
    });
  }
  function b64(u8) {
    var s = '', CH = 0x8000;
    for (var i = 0; i < u8.length; i += CH) s += String.fromCharCode.apply(null, u8.subarray(i, i + CH));
    return btoa(s);
  }
  function linkNote(url, label) {
    var wrap = document.getElementById('docwrap') || document.querySelector('main');
    if (!wrap) return;
    var div = document.createElement('div');
    div.className = 'notice ok';
    div.innerHTML = 'Готово: <a href="' + url + '" target="_blank" rel="noopener">' + esc(label) +
      '</a> — откроется в Google Диске / Docs. Ссылку можно переслать семье или специалисту.';
    wrap.insertBefore(div, wrap.firstChild);
    div.scrollIntoView({block: 'nearest'});
  }

  /* ---- черновики хранятся в Google Таблице, лист «Черновики» ---- */
  saveProject = function () {
    var name = prompt('Имя черновика в таблице (лист «Черновики»):', S.header.fio || 'черновик');
    if (!name) return;
    gas('saveDraft', name, JSON.stringify({v: 1, doc: S}))
      .then(function (r) { flash('Черновик сохранён: ' + r.name + ' (' + r.updated + ')'); })
      .catch(function (e) { alert('Не удалось сохранить черновик: ' + e.message); });
  };
  loadProject = function () {
    gas('listDrafts').then(function (list) {
      if (!list.length) { alert('В таблице пока нет черновиков.'); return null; }
      var name = prompt('Доступные черновики:\n' + list.map(function (d) {
        return '• ' + d.name + ' (' + d.updated + ')';
      }).join('\n') + '\n\nВведите имя для загрузки:', list[0].name);
      if (!name) return null;
      return gas('loadDraft', name).then(function (txt) {
        if (!txt) { alert('Черновик не найден'); return; }
        var p = JSON.parse(txt);
        if (p && p.doc) { S = p.doc; ensureMicro(); save(); render(); flash('Черновик загружен: ' + name); }
      });
    }).catch(function (e) { alert('Ошибка загрузки: ' + e.message); });
  };

  /* ---- .docx уходит в папку Drive «Заключения ИВ» ---- */
  exportDocx = function () {
    var d = buildDoc();
    var zip = zipStore([
      {name: '[Content_Types].xml', data: CT_XML},
      {name: '_rels/.rels', data: RELS_XML},
      {name: 'word/document.xml', data: buildDocumentXml(d)},
      {name: 'word/styles.xml', data: STYLES_XML},
      {name: 'word/numbering.xml', data: NUM_XML},
      {name: 'word/_rels/document.xml.rels', data: DOC_RELS_XML}
    ]);
    flash('Собираю .docx и отправляю на Диск…');
    gas('saveDocx', b64(zip), fileName(d))
      .then(function (r) { flash('.docx сохранён на Диске'); linkNote(r.url, r.name + '.docx'); })
      .catch(function (e) { alert('Ошибка сохранения .docx: ' + e.message); });
  };

  /* ---- банк фраз в Google-режиме читается из таблицы; правки уходят на модерацию ---- */
  persistBank = function () {
    flash('Google-режим: банк читается из Google Таблицы. Отправьте правку кнопкой «Предложить фразу».');
  };
  function propose() {
    var text = prompt('Текст новой формулировки:'); if (!text) return;
    var block = prompt('Блок (AS / GOAL / METH / RES / NEXT / REC):', 'AS') || 'AS';
    var micro = prompt('Микроблок (AS1…AS6, RC1…RC6; можно оставить пустым):', '') || '';
    var status = prompt('Статус (S3 / S2 / S1 / S0 / SN):', 'S2') || 'S2';
    var author = prompt('Ваше имя (увидит методист):', '') || '';
    gas('proposePhrase', {text: text, block: block, micro: micro, status: status, author: author,
        links_goal: [], links_meth: [], links_rec: [], comment: 'предложено из веб-конструктора'})
      .then(function (m) { flash(m); })
      .catch(function (e) { alert('Ошибка отправки: ' + e.message); });
  }

  /* ---- дополнительные кнопки после каждой отрисовки ---- */
  var baseRender = render;
  render = function () {
    baseRender();
    var tb = document.querySelector('.toolbar');
    if (tb && !document.getElementById('btnGdoc')) {
      var b1 = document.createElement('button');
      b1.className = 'b'; b1.id = 'btnGdoc'; b1.textContent = 'Создать Google Doc';
      b1.onclick = function () {
        flash('Создаю Google Doc…');
        gas('createGoogleDoc', JSON.stringify(buildDoc()))
          .then(function (r) { flash('Google Doc создан'); linkNote(r.url, r.name); })
          .catch(function (e) { alert('Ошибка создания дока: ' + e.message); });
      };
      tb.insertBefore(b1, tb.children[1] || null);
    }
    var addBank = document.getElementById('bankAdd');
    if (addBank && !document.getElementById('btnPropose')) {
      var b2 = document.createElement('button');
      b2.className = 'b ghost small'; b2.id = 'btnPropose';
      b2.textContent = 'Предложить фразу методисту';
      b2.onclick = propose;
      addBank.parentNode.insertBefore(b2, addBank.nextSibling);
    }
    var gb = document.querySelector('.card .hint');
    if (window.GC_BACKEND === 'google' && gb && gb.textContent.indexOf('Google-режим') < 0 &&
        document.getElementById('bankAdd')) {
      var note = document.createElement('div');
      note.className = 'notice info';
      note.textContent = 'Google-режим: банк фраз читается из этой таблицы. Правки специалистов попадают ' +
        'на лист «Предложения фраз» и включаются методистом после проверки.';
      addBank.closest('.card').insertBefore(note, addBank.parentNode);
    }
  };
})();
