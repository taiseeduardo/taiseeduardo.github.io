"""Instala as páginas e atualiza as listas. Execute junto de fotos.html."""
import json
from pathlib import Path
import re
from urllib.parse import quote

JS = r'''(() => {
  const gallery = document.getElementById('galeriaPaginada');
  if (!gallery) return;
  const pager = document.getElementById('paginacaoFotos');
  const message = document.getElementById('mensagemFotos');
  const box = document.getElementById('lightbox');
  const photo = document.getElementById('lightboxImage');
  const close = document.getElementById('closeLightbox');
  let list = [], page = 0, current = 0, lastFocus;
  const size = 50;
  const counter = document.createElement('span');
  counter.className = 'contador-paginado'; counter.setAttribute('role','status');
  box.append(counter);
  function hide() {
    box.classList.remove('active'); photo.removeAttribute('src');
    if (lastFocus) lastFocus.focus();
  }
  function show(index) {
    current = (index + list.length) % list.length;
    photo.src = list[current].src;
    photo.alt = list[current].alt || 'Foto do casamento';
    counter.textContent = `${current + 1} / ${list.length}`;
    box.classList.add('active');
  }
  function control(label, text, callback, parent) {
    const button = document.createElement('button'); button.type = 'button';
    button.textContent = text; button.setAttribute('aria-label',label);
    button.addEventListener('click', event => {event.stopPropagation(); callback();});
    parent.append(button); return button;
  }
  const previous = control('Foto anterior','❮',()=>show(current-1),box);
  const next = control('Próxima foto','❯',()=>show(current+1),box);
  previous.className='seta-paginada anterior'; next.className='seta-paginada proxima';
  close.onclick = hide;
  close.setAttribute('role','button'); close.setAttribute('tabindex','0');
  close.setAttribute('aria-label','Fechar foto');
  close.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();hide();}});
  box.addEventListener('click',e=>{if(e.target===box)hide();});
  document.addEventListener('keydown',e=>{
    if(!box.classList.contains('active'))return;
    if(e.key==='Escape')hide();
    if(e.key==='ArrowRight'||e.key==='ArrowLeft'){
      e.preventDefault();show(current+(e.key==='ArrowRight'?1:-1));
    }
    if(e.key==='Tab'){
      const controls=[close,previous,next];
      const i=controls.indexOf(document.activeElement);
      e.preventDefault();controls[(i+(e.shiftKey?-1:1)+controls.length)%controls.length].focus();
    }
  });
  function render(scroll=false) {
    gallery.replaceChildren(); pager.replaceChildren();
    const start = page * size;
    list.slice(start,start+size).forEach((item,offset)=>{
      const img=document.createElement('img');
      img.src=item.src; img.alt=item.alt || 'Foto do casamento';
      img.loading='lazy'; img.decoding='async';
      const link=document.createElement('button');link.type='button';link.className='abrir-foto';
      link.setAttribute('aria-label',`Abrir foto ${start+offset+1}`);
      link.append(img);
      link.addEventListener('click',()=>{lastFocus=link;show(start+offset);close.focus();});
      gallery.append(link);
    });
    const pages=Math.ceil(list.length/size);
    if(pages>1){
      const prev=control('Página anterior','← Anterior',()=>{page--;render(true);},pager);
      prev.disabled=page===0;
      const count=document.createElement('span');count.setAttribute('role','status');
      count.tabIndex=-1;count.textContent=`Página ${page+1} de ${pages} · ${list.length} fotos`;pager.append(count);
      const forward=control('Próxima página','Próxima →',()=>{page++;render(true);},pager);
      forward.disabled=page===pages-1;
      if(scroll)count.focus({preventScroll:true});
    }
    if(scroll)document.getElementById('albumFotos').scrollIntoView({block:'start'});
  }
  fetch(gallery.dataset.list,{cache:'no-cache'})
    .then(r=>{if(!r.ok)throw new Error('Lista indisponível');return r.json();})
    .then(data=>{
      if(!Array.isArray(data))throw new Error('Lista inválida');
      list=data.filter(item=>item && typeof item.src==='string');
      message.textContent=list.length?'':'As fotos desta galeria serão adicionadas em breve.';
      message.hidden=list.length>0;render();
    })
    .catch(()=>{message.hidden=false;message.textContent='Não foi possível carregar as fotos. Atualize a página para tentar novamente.';});
})();
'''

CSS = '''
.atalhos-albuns {display:flex; flex-wrap:wrap; justify-content:center; gap:10px; margin:25px auto 0;}
.atalhos-albuns a,.paginacao-fotos button {padding:12px 18px; border:1px solid #d8cfc2; border-radius:24px; background:#fffaf4; color:#2b2118; text-decoration:none; font:inherit; min-height:44px;}
.atalhos-albuns a[aria-current="page"] {background:#2b2118; color:#fffaf4;}
.paginacao-fotos {display:flex; flex-wrap:wrap; align-items:center; justify-content:center; gap:14px; margin-top:30px; font-size:18px;}
.paginacao-fotos button {cursor:pointer;} .paginacao-fotos button:disabled {opacity:.4;cursor:default;}
#galeriaPaginada .abrir-foto {display:block; min-width:0; width:100%; padding:0; border:0; background:transparent; cursor:pointer;}
#galeriaPaginada .abrir-foto img {display:block; width:100%;}
.seta-paginada {position:absolute;top:50%;transform:translateY(-50%);width:44px;height:50px;background:#000a;color:white;border:1px solid #fff8;border-radius:10px;font-size:26px;cursor:pointer;z-index:102;}
.seta-paginada.anterior {left:8px;} .seta-paginada.proxima {right:8px;}
.contador-paginado {position:absolute;bottom:16px;left:50%;transform:translateX(-50%);padding:8px 15px;background:#000b;color:white;border-radius:20px;}
#albumFotos {scroll-margin-top:90px;}
@media(max-width:600px){#galeriaPaginada {grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;}#galeriaPaginada img {height:auto;aspect-ratio:1;object-fit:cover;border-radius:10px;}.atalhos-albuns {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));}.atalhos-albuns a {font-size:16px;}}
'''


def main():
    root=Path(__file__).resolve().parent
    source=root/'fotos.html'
    if not source.exists():
        raise SystemExit('Coloque este instalador na pasta do site, junto de fotos.html.')
    template=source.read_text(encoding='utf-8')
    if not all(tag in template.lower() for tag in ['</head>','</body>','</main>','</header>']):
        raise SystemExit('Estrutura da página não reconhecida. Nenhuma alteração feita.')
    if 'id="lightbox"' not in template:
        raise SystemExit('Não encontrei o visualizador de fotos. Nenhuma alteração feita.')
    backup=root/'fotos-antes-da-paginacao.html.bak'
    if not backup.exists():backup.write_text(template,encoding='utf-8')
    albums=[('fotos.html','fotos-casamento','Fotos por Thiago'),
            ('fotos-convidados.html','fotos-convidados','Fotos dos convidados'),
            ('fotos-enviadas.html','fotos-enviadas','Fotos enviadas pelos convidados')]
    # Retira os carregadores antigos para que não baixem as galerias completas.
    def remove_loader(match):
        return '' if 'function carregarGaleria' in match.group(0) else match.group(0)
    template=re.sub(r'<script\b[^>]*>.*?</script>',remove_loader,template,flags=re.S|re.I)
    template=re.sub(r'<script\b[^>]*src=["\'](?:galeria-navegacao|galeria-convidados|galeria-enviadas|galerias-paginadas)\.js["\'][^>]*>\s*</script>','',template,flags=re.I)
    template=re.sub(r'<style id="estilo-paginacao">.*?</style>','',template,flags=re.S)
    for filename,folder,title in albums:
        directory=root/folder
        manifest=root/(folder+'.json')
        if directory.exists():
            photos=[{'src':quote(p.relative_to(root).as_posix(),safe='/'),'alt':title}
                    for p in sorted(directory.rglob('*'))
                    if p.is_file() and p.suffix.lower() in {'.jpg','.jpeg','.png','.webp','.avif','.gif'}
                    and not any(part.startswith('.') for part in p.relative_to(directory).parts)]
            manifest.write_text(json.dumps(photos,ensure_ascii=False,indent=2),encoding='utf-8')
        elif not manifest.exists():
            directory.mkdir();manifest.write_text('[]',encoding='utf-8')
        links=''.join('<a href="'+name+'"'+(' aria-current="page"' if name==filename else '')+'>'+label+'</a>' for name,_,label in albums)
        links+='<a href="fotos-enviadas.html#enviar-fotos">Envie suas fotos</a>'
        header='<header><div class="small-label">Taís &amp; Eduardo</div><h1>'+title+'</h1><p class="subtitle">As lembranças do nosso grande dia.</p><div class="atalhos-albuns" role="navigation" aria-label="Álbuns de fotos">'+links+'</div></header>'
        main='<main><section id="albumFotos"><div class="container"><h2>'+title+'</h2><p id="mensagemFotos" role="status">Carregando fotos…</p><div class="gallery" id="galeriaPaginada" data-list="'+folder+'.json"></div><div id="paginacaoFotos" class="paginacao-fotos" role="navigation" aria-label="Páginas de fotos"></div></div></section>'
        if filename=='fotos-enviadas.html':
            main+='<section id="enviar-fotos"><div class="container"><h2>Compartilhe suas fotos</h2><p>Registrou algum momento especial? Compartilhe com a gente!</p><a class="button" href="https://www.dropbox.com/request/bhpakoaf9v799zwr894h" target="_blank" rel="noopener noreferrer">Envie suas fotos</a><p>Depois do envio, reuniremos as fotos nesta galeria.</p></div></section>'
        main+='</main>'
        page=re.sub(r'<header\b[^>]*>.*?</header>',lambda _:header,template,count=1,flags=re.S|re.I)
        page=re.sub(r'<main\b[^>]*>.*?</main>',lambda _:main,page,count=1,flags=re.S|re.I)
        page=page.replace('href="#fotos-casamento"','href="fotos.html"')
        page=re.sub(r'<title\b[^>]*>.*?</title>','<title>'+title+' — Taís &amp; Eduardo</title>',page,count=1,flags=re.S|re.I)
        pos=page.lower().index('</head>');page=page[:pos]+'<style id="estilo-paginacao">'+CSS+'</style>\n'+page[pos:]
        pos=page.lower().rindex('</body>');page=page[:pos]+'<script src="galerias-paginadas.js" defer></script>\n'+page[pos:]
        (root/filename).write_text(page,encoding='utf-8')
    (root/'galerias-paginadas.js').write_text(JS,encoding='utf-8')
    print('Pronto! Três álbuns em páginas separadas, com até 50 fotos por página.')
    print('Músicas e arquivos de fotos preservados. Faça Commit e Push das alterações.')
    print('Para cadastrar novas fotos em qualquer pasta, execute este mesmo instalador novamente.')


if __name__=='__main__':main()
