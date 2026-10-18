(() => {
  const pairs = [
    ['Fotos por Tiago Pacheco','Photos by Tiago Pacheco'],
    ['Fotos dos convidados','Guest photos'],
    ['Fotos enviadas pelos convidados','Photos submitted by guests'],
    ['Fotos enviadas','Submitted photos'],
    ['Envie suas fotos','Send your photos'],
    ['Compartilhe suas fotos','Share your photos'],
    ['As lembranças do nosso grande dia.','Memories of our big day.'],
    ['Registrou algum momento especial? Compartilhe com a gente!','Captured a special moment? Share it with us!'],
    ['Depois do envio, reuniremos as fotos nesta galeria.','After you submit your photos, we will add them to this gallery.'],
    ['Carregando fotos…','Loading photos…'],
    ['As fotos desta galeria serão adicionadas em breve.','Photos will be added to this gallery soon.'],
    ['Não foi possível carregar as fotos. Atualize a página para tentar novamente.','Unable to load the photos. Refresh the page to try again.'],
    ['Página anterior','Previous page'], ['Próxima página','Next page'],
    ['← Anterior','← Previous'], ['Próxima →','Next →'],
    ['Foto anterior','Previous photo'], ['Próxima foto','Next photo'],
    ['Fechar foto','Close photo'], ['Foto do casamento','Wedding photo'],
    ['Álbuns de fotos','Photo albums'], ['Páginas de fotos','Photo pages'],
    ['Carregando músicas…','Loading music…'], ['▶ Ouvir músicas','▶ Play music'],
    ['⏸ Pausar música','⏸ Pause music'], ['Ouvir músicas','Play music'],
    ['Pausar música','Pause music'], ['♫ Músicas em breve','♫ Music coming soon'],
    ['♫ Música indisponível','♫ Music unavailable'],
    ['Toque no botão para ouvir.','Tap the button to listen.'],
    ['Não foi possível tocar. Tente novamente.','Unable to play. Please try again.'],
    ['Não foi possível carregar as músicas.','Unable to load the music.'],
    ['Não foi possível carregar a lista.','Unable to load the playlist.'],
    ['Música tocando em outra aba.','Music is playing in another tab.'],
    ['↑ Voltar ao topo','↑ Back to top'],
    ['Os registros oficiais do nosso grande dia.','The official photos from our big day.'],
    ['Nosso dia pelo olhar de quem celebrou com a gente.','Our day through the eyes of those who celebrated with us.'],
    ['Mais lembranças compartilhadas por vocês.','More memories shared by you.'],
    ['Em breve, mais lembranças compartilhadas pelos nossos convidados.','More memories from our guests are coming soon.'],
    ['Esta galeria vai receber as fotos que vocês compartilharem com a gente.','This gallery will feature the photos you share with us.'],
    ['O envio é feito pelo Dropbox. Depois, reuniremos as fotos nesta galeria.','Photos are submitted through Dropbox. We will then add them to this gallery.'],
    ['Foto registrada pelos convidados','Photo taken by a guest'],
    ['Foto enviada pelos convidados','Photo submitted by a guest']
  ];
  const translations = new Map();
  for (const pair of pairs) for (const text of pair) translations.set(text,pair);
  translations.set('Fotos por Thiago',pairs[0]);
  translations.set('Fotos por Tiago',pairs[0]);
  function translate(value,en) {
    const key=value.trim();
    if(translations.has(key))return translations.get(key)[en?1:0];
    let match=key.match(/^(?:Página|Page) (\d+) (?:de|of) (\d+) · (\d+) (?:fotos|photos)$/);
    if(match)return en?`Page ${match[1]} of ${match[2]} · ${match[3]} photos`:`Página ${match[1]} de ${match[2]} · ${match[3]} fotos`;
    match=key.match(/^(?:Abrir foto|Open photo) (\d+)$/);
    if(match)return `${en?'Open photo':'Abrir foto'} ${match[1]}`;
    match=key.match(/^(Fotos por (?:Thiago|Tiago(?: Pacheco)?)|Photos by Tiago Pacheco|Fotos dos convidados|Guest photos|Fotos enviadas pelos convidados|Photos submitted by guests) — Taís & Eduardo$/);
    if(match)return translate(match[1],en)+' — Taís & Eduardo';
    return value;
  }
  let pending=false;
  const observer=new MutationObserver(()=>{
    if(pending)return;pending=true;
    queueMicrotask(()=>{pending=false;apply();});
  });
  function watch(){observer.observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['lang','aria-label','alt']});}
  function apply(){
    observer.disconnect();
    try {
      const en=document.documentElement.lang.toLowerCase().startsWith('en');
      const walker=document.createTreeWalker(document.documentElement,NodeFilter.SHOW_TEXT);
      let node;
      while((node=walker.nextNode())){
        if(!node.parentElement || node.parentElement.closest('script,style'))continue;
        const value=translate(node.nodeValue,en);
        if(value!==node.nodeValue)node.nodeValue=value;
      }
      document.querySelectorAll('[aria-label],[alt]').forEach(element=>{
        for(const attr of ['aria-label','alt']){
          const current=element.getAttribute(attr);
          if(current===null)continue;
          const value=translate(current,en);
          if(current!==value)element.setAttribute(attr,value);
        }
      });
    } finally {watch();}
  }
  apply();
})();
