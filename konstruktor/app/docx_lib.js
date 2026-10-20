/* Общая библиотека сборки .docx (ZIP + WordprocessingML).
   Вставляется в оба интерфейса (v1 и v2) при сборке: маркер DOCX_LIB */
/* ============================================================ ЭКСПОРТ .DOCX (без внешних библиотек) */
const CRC_TBL=(()=>{let t=new Uint32Array(256);for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=c&1?0xEDB88320^(c>>>1):c>>>1;t[n]=c>>>0;}return t;})();
function crc32(u8){let c=0xFFFFFFFF;for(let i=0;i<u8.length;i++)c=CRC_TBL[(c^u8[i])&0xFF]^(c>>>8);return (c^0xFFFFFFFF)>>>0;}
function zipStore(files){
  const enc=new TextEncoder(); const chunks=[]; const central=[]; let offset=0;
  const dt=new Date(); const dosTime=((dt.getHours()<<11)|(dt.getMinutes()<<5)|(dt.getSeconds()/2))&0xFFFF;
  const dosDate=(((dt.getFullYear()-1980)<<9)|((dt.getMonth()+1)<<5)|dt.getDate())&0xFFFF;
  function u16(n){return [n&255,(n>>8)&255];}
  function u32(n){return [n&255,(n>>8)&255,(n>>16)&255,(n>>24)&255];}
  files.forEach(f=>{
    const name=enc.encode(f.name); const data=typeof f.data==='string'?enc.encode(f.data):f.data;
    const crc=crc32(data);
    const lh=[].concat(u32(0x04034b50),u16(20),u16(0x0800),u16(0),u16(dosTime),u16(dosDate),
      u32(crc),u32(data.length),u32(data.length),u16(name.length),u16(0));
    chunks.push(new Uint8Array(lh),name,data);
    const ch=[].concat(u32(0x02014b50),u16(20),u16(20),u16(0x0800),u16(0),u16(dosTime),u16(dosDate),
      u32(crc),u32(data.length),u32(data.length),u16(name.length),u16(0),u16(0),u16(0),u16(0),u32(0),u32(offset));
    central.push(new Uint8Array(ch),name);
    offset+=lh.length+name.length+data.length;
  });
  let cdSize=0; central.forEach(c=>cdSize+=c.length);
  const eocd=new Uint8Array([].concat(u32(0x06054b50),u16(0),u16(0),u16(files.length),u16(files.length),
    u32(cdSize),u32(offset),u16(0)));
  const all=chunks.concat(central,[eocd]);
  const total=all.reduce((n,c)=>n+c.length,0); const out=new Uint8Array(total); let p=0;
  all.forEach(c=>{out.set(c,p);p+=c.length;});
  return out;
}
const X=t=>String(t==null?'':t).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
function runXml(text,o){
  o=o||{}; let rpr='';
  if(o.bold) rpr+='<w:b/>';
  if(o.italic) rpr+='<w:i/>';
  if(o.size) rpr+='<w:sz w:val="'+(o.size*2)+'"/><w:szCs w:val="'+(o.size*2)+'"/>';
  return '<w:r>'+(rpr?'<w:rPr>'+rpr+'</w:rPr>':'')+'<w:t xml:space="preserve">'+X(text)+'</w:t></w:r>';
}
function paraXml(text,o){
  o=o||{}; let ppr='<w:spacing w:after="'+(o.after!=null?o.after:160)+'" w:line="259" w:lineRule="auto"/>';
  if(o.align) ppr+='<w:jc w:val="'+o.align+'"/>';
  if(o.indent) ppr+='<w:ind w:firstLine="709"/>';
  if(o.num) ppr+='<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>';
  return '<w:p><w:pPr>'+ppr+'</w:pPr>'+runXml(text,o)+'</w:p>';
}
function buildDocumentXml(d){
  const A4W=11906, A4H=16838;
  const M={top:1134,right:850,bottom:1134,left:1701};
  let body='';
  body+=paraXml(d.title,{bold:true,size:12,align:'center',after:240});
  // таблица шапки
  const rows=[['ФИО:',d.header.fio],['Дата рождения:',d.header.birth],
    ['Дата начала периода реабилитации:',d.header.period_start],
    ['Дата окончания периода реабилитации:',d.header.period_end],
    ['Специалист:',d.header.specialist],['Количество занятий:',d.header.sessions]];
  body+='<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/>'
    +'<w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    +'<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    +'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    +'<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    +'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    +'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tblBorders></w:tblPr>'
    +'<w:tblGrid><w:gridCol w:w="4200"/><w:gridCol w:w="4800"/></w:tblGrid>';
  rows.forEach(r=>{
    body+='<w:tr>'
      +'<w:tc><w:tcPr><w:tcW w:w="4200" w:type="dxa"/></w:tcPr>'+paraXml(r[0],{after:40})+'</w:tc>'
      +'<w:tc><w:tcPr><w:tcW w:w="4800" w:type="dxa"/></w:tcPr>'+paraXml(r[1]||'',{after:40})+'</w:tc>'
      +'</w:tr>';
  });
  body+='</w:tbl>'+paraXml('',{after:80});
  d.blocks.forEach(b=>{
    body+=paraXml(b.title,{bold:true,size:12,after:120});
    b.paras.forEach(p=>{
      body+= paraXml(p.text,{bold:!!p.bold,italic:!!p.italic,size:b.small?10:12,
        align:'both', num:!!p.li, after:p.li?60:160});
    });
  });
  body+='<w:sectPr><w:pgSz w:w="'+A4W+'" w:h="'+A4H+'"/>'
    +'<w:pgMar w:top="'+M.top+'" w:right="'+M.right+'" w:bottom="'+M.bottom+'" w:left="'+M.left
    +'" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>';
  return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    +'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    +'<w:body>'+body+'</w:body></w:document>';
}
const STYLES_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 +'<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
 +'<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
 +'<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="ru-RU"/></w:rPr></w:rPrDefault>'
 +'<w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="259" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
 +'<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/>'
 +'<w:pPr><w:spacing w:after="160" w:line="259" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr>'
 +'<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
 +'<w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr></w:style>'
 +'<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/></w:style>'
 +'</w:styles>';
const NUM_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 +'<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
 +'<w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/>'
 +'<w:lvlText w:val="%1."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="709" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum>'
 +'<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>';
const CT_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 +'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
 +'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
 +'<Default Extension="xml" ContentType="application/xml"/>'
 +'<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
 +'<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
 +'<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
 +'</Types>';
const RELS_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 +'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
 +'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
 +'</Relationships>';
const DOC_RELS_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 +'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
 +'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
 +'<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
 +'</Relationships>';

function downloadBlob(blob,name){
  const url=URL.createObjectURL(blob); const a=document.createElement('a');
  a.href=url; a.download=name; document.body.appendChild(a); a.click();
  setTimeout(()=>{URL.revokeObjectURL(url); a.remove();},400);
}
