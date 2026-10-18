(() => {
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
