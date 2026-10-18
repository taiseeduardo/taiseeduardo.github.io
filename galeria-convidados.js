(() => {
  const gallery = document.getElementById('galeriaConvidados');
  const message = document.getElementById('mensagemConvidados');
  fetch('fotos-convidados.json', {cache:'no-cache'})
    .then(r => { if (!r.ok) throw new Error('Lista indisponível'); return r.json(); })
    .then(list => {
      if (!Array.isArray(list)) throw new Error('Lista inválida');
      message.hidden = list.length > 0;
      for (const item of list) {
        const img = document.createElement('img');
        img.src = item.src;
        img.alt = item.alt || 'Foto registrada pelos convidados';
        img.loading = 'lazy'; img.decoding = 'async';
        img.addEventListener('click', () => abrirLightbox(img.src, img.alt));
        gallery.append(img);
      }
    })
    .catch(() => {message.hidden = false; message.textContent = 'Não foi possível carregar as fotos dos convidados. Tente novamente mais tarde.';});
})();
