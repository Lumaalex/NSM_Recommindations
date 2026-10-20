# -*- coding: utf-8 -*-
"""Доделка пакета 1.3.0: (1) вернуть surveyGroups/stageName в раздел опросника,
(2) удалить мёртвые countCore/vSurveySimple (простой режим теперь ходит в vSurvey)."""
import io
PATH = 'app/template.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global src
    c = src.count(old)
    assert c == cnt, 'вхождений %d (ожидалось %d): %r' % (c, cnt, old[:80])
    src = src.replace(old, new)

# (1) surveyGroups + stageName — перед spheresTab
rep("""/* ---- вкладка опросника: оценка по 9 сферам (методология версии 2) ---- */
function spheresTab(){""",
"""function surveyGroups(){
  const g={};
  (BANK.questionnaire||[]).forEach(q=>{
    const key = q.source==='Сенсорика' ? 'Сенсорная переработка информации' : ('Стадия '+q.stage+': '+stageName(q.stage));
    (g[key]=g[key]||[]).push(q);
  });
  return g;
}
function stageName(n){
  return ({0:'индивидуальные особенности',1:'Совместное внимание и саморегуляция',2:'Контакт и общение',
    3:'Преднамеренность и обоюдная коммуникация',4:'Решение социальных проблем, регуляция настроения и самосознание',
    5:'Формирование символов, использование слов и понятий. Эмоциональные идеи',
    6:'Логический, абстрактный и эмоциональный интеллект'})[n]||'';
}
/* ---- вкладка опросника: оценка по 9 сферам (методология версии 2) ---- */
function spheresTab(){""")

# (2) мёртвый код простого режима
i = src.index('function countCore(){ return (BANK.survey_core||[]).filter')
j = src.index('function vASSimple(){', i)
dead = src[i:j]
assert 'vSurveySimple' in dead and len(dead) < 2000, len(dead)
src = src[:i] + src[j:]

io.open(PATH, 'w', encoding='utf-8').write(src)
print('готово, размер %.1f КБ' % (len(src.encode('utf-8'))/1024))
