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

  // inicio-musica-uma-aba
  const tabId = Date.now().toString(36) + Math.random().toString(36).slice(2);
  const ownershipKey = 'taiseeduardo-musica-aba-v1';
  let channel;
  try {
    if ('BroadcastChannel' in window) channel = new BroadcastChannel(ownershipKey);
  } catch (_) {}
  let ownership = null;
  function receiveOwnership(message) {
    if (!message || typeof message.id !== 'string' || typeof message.time !== 'number') return;
    // Resolve também duas abas que tentem começar praticamente juntas.
    const newer = !ownership || message.time > ownership.time ||
      (message.time === ownership.time && message.id > ownership.id);
    if (!newer) return;
    ownership = message;
    if (message.id !== tabId && !audio.paused) {
      audio.pause();
      status.textContent = 'Música tocando em outra aba.';
    }
  }
  if (channel) channel.addEventListener('message', event => receiveOwnership(event.data));
  window.addEventListener('storage', event => {
    if (event.key !== ownershipKey || !event.newValue) return;
    try { receiveOwnership(JSON.parse(event.newValue)); } catch (_) {}
  });
  audio.addEventListener('play', () => {
    try {
      const stored = JSON.parse(localStorage.getItem(ownershipKey));
      if (stored && typeof stored.time === 'number' && (!ownership || stored.time > ownership.time)) {
        ownership = stored;
      }
    } catch (_) {}
    const message = {id:tabId, time:Math.max(Date.now(), (ownership ? ownership.time : 0) + 1)};
    ownership = message;
    if (channel) channel.postMessage(message);
    try { localStorage.setItem(ownershipKey, JSON.stringify(message)); } catch (_) {}
  });
  // fim-musica-uma-aba

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
