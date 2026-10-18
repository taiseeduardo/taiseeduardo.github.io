(() => {
  'use strict';
  if (document.getElementById('player-musicas')) return;
  const box = document.createElement('div');
  box.id = 'player-musicas';
  const button = document.createElement('button');
  button.type = 'button';
  button.disabled = true;
  button.textContent = 'Carregando músicas…';
  const status = document.createElement('span');
  status.setAttribute('role', 'status');
  box.append(button, status);
  document.body.append(box);
  const audio = new Audio();
  audio.preload = 'none';
  audio.volume = 0.45;
  let tracks = [], index = 0, failures = 0, busy = false;
  function shuffle(list) {
    for (let i = list.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [list[i], list[j]] = [list[j], list[i]];
    }
  }
  function render() {
    button.textContent = audio.paused ? '▶ Ouvir músicas' : '⏸ Pausar música';
    button.setAttribute('aria-label', audio.paused ? 'Ouvir músicas' : 'Pausar música');
    button.setAttribute('aria-pressed', String(!audio.paused));
  }
  function select() {
    audio.src = tracks[index];
  }
  async function play() {
    if (busy) return;
    busy = true;
    try {
      await audio.play();
      status.textContent = '';
    } catch (error) {
      if (error.name === 'NotAllowedError') {
        status.textContent = 'Toque no botão para ouvir.';
      } else if (error.name !== 'AbortError') {
        // O evento error trata arquivos inválidos e tenta a próxima faixa.
        status.textContent = 'Não foi possível tocar. Tente novamente.';
      }
    } finally {
      busy = false;
      render();
    }
  }
  function next() {
    index++;
    if (index >= tracks.length) {
      const previous = tracks[tracks.length - 1];
      shuffle(tracks);
      if (tracks.length > 1 && tracks[0] === previous) {
        [tracks[0], tracks[1]] = [tracks[1], tracks[0]];
      }
      index = 0;
    }
    select();
    play();
  }
  button.addEventListener('click', () => {
    if (audio.paused) { failures = 0; play(); }
    else audio.pause();
  });
  audio.addEventListener('play', render);
  audio.addEventListener('pause', render);
  audio.addEventListener('ended', () => { failures = 0; next(); });
  audio.addEventListener('error', () => {
    failures++;
    if (failures >= tracks.length) {
      status.textContent = 'Não foi possível carregar as músicas.';
      render();
      return;
    }
    // Aguarda a tentativa anterior terminar antes de mudar de faixa.
    setTimeout(() => { busy = false; next(); }, 100);
  });
  fetch('musicas.json', {cache: 'no-cache'})
    .then(response => {
      if (!response.ok) throw new Error('Lista indisponível');
      return response.json();
    })
    .then(list => {
      if (!Array.isArray(list)) throw new Error('Lista inválida');
      tracks = list.filter(src => typeof src === 'string' && src.startsWith('musicas/'));
      if (!tracks.length) {
        button.textContent = '♫ Músicas em breve';
        return;
      }
      shuffle(tracks);
      select();
      button.disabled = false;
      render();
      play();
    })
    .catch(() => {
      button.textContent = '♫ Música indisponível';
      status.textContent = 'Não foi possível carregar a lista.';
    });
})();
