(() => {
  const page = location.pathname.split('/').pop();
  const albums = {'fotos.html':'fotos-casamento','fotos-convidados.html':'fotos-convidados','fotos-enviadas.html':'fotos-enviadas'};
  const key = albums[page];
  if (!key || document.getElementById('baixar-originais')) return;
  fetch('download-originais.json', {cache:'no-cache'})
    .then(r => {if(!r.ok)throw new Error();return r.json();})
    .then(config => {
      const url=config.links && config.links[key];
      if(!url)return;
      const parsed=new URL(url);
      if(parsed.protocol!=='https:' || !(parsed.hostname==='dropbox.com' || parsed.hostname.endsWith('.dropbox.com')))return;
      const area=document.createElement('div');
      const link=document.createElement('a');
      link.id='baixar-originais';link.className='button';link.href=url;
      link.target='_blank';link.rel='noopener noreferrer';
      const caption=document.createElement('p');caption.style.fontSize='16px';
      function translate(){
        const en=document.documentElement.lang.startsWith('en');
        link.textContent=en?'Download original photos':'Baixar fotos em qualidade original';
        caption.textContent=en?'Full-quality files on Dropbox. The gallery uses lighter copies.':'Arquivos em qualidade original no Dropbox. A galeria usa cópias mais leves.';
      }
      area.append(link,caption);document.querySelector('header').append(area);
      translate();new MutationObserver(translate).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
    }).catch(()=>{});
})();
