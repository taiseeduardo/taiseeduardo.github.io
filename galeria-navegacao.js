(() => {
  const box = document.getElementById('lightbox');
  const photo = document.getElementById('lightboxImage');
  let gallery = document.getElementById('galeriaCasamento');
  if (!box || !photo || !gallery || document.getElementById('foto-anterior')) return;
  let current = 0;
  const images = () => Array.from(gallery.querySelectorAll('img'));
  const count = document.createElement('div');
  count.id = 'contador-fotos';
  count.setAttribute('role', 'status');
  function updateCount() { count.textContent = `${current + 1} / ${images().length}`; }
  function move(direction) {
    const list = images();
    if (!list.length) return;
    current = (current + direction + list.length) % list.length;
    photo.src = list[current].src;
    photo.alt = list[current].alt;
    updateCount();
  }
  function button(id, label, symbol, direction) {
    const element = document.createElement('button');
    element.id = id;
    element.type = 'button';
    element.className = 'seta-foto';
    element.setAttribute('aria-label', label);
    element.textContent = symbol;
    element.addEventListener('click', event => {
      event.stopPropagation();
      move(direction);
    });
    box.append(element);
  }
  button('foto-anterior', 'Foto anterior', '❮', -1);
  button('foto-proxima', 'Próxima foto', '❯', 1);
  box.append(count);
  document.addEventListener('click', event => {
    if (event.target.tagName !== 'IMG' || !event.target.closest('.gallery')) return;
    gallery = event.target.closest('.gallery');
    current = images().indexOf(event.target);
    updateCount();
  });
  document.addEventListener('keydown', event => {
    if (!box.classList.contains('active')) return;
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault();
      move(event.key === 'ArrowRight' ? 1 : -1);
    }
  });
  const style = document.createElement('style');
  style.textContent = `
    .seta-foto {position:absolute; top:50%; transform:translateY(-50%);
      z-index:102; width:48px; height:56px; padding:0; border:1px solid #ffffff70;
      border-radius:12px; background:#0009; color:white; cursor:pointer; font-size:28px;}
    .seta-foto:hover {background:#333e;}
    .seta-foto:focus-visible {outline:3px solid white; outline-offset:3px;}
    #foto-anterior {left:12px;} #foto-proxima {right:12px;}
    #contador-fotos {position:absolute; bottom:16px; left:50%; transform:translateX(-50%);
      padding:6px 14px; border-radius:20px; background:#000b; color:white;
      font:16px Georgia,serif; pointer-events:none;}
    @media(max-width:600px) {.seta-foto {width:44px; height:48px; font-size:23px;}
      #foto-anterior {left:6px;} #foto-proxima {right:6px;}}
  `;
  document.head.append(style);
})();
