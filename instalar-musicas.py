#!/usr/bin/env python3
"""Execute na pasta do site: python3 instalar-musicas.py"""
import json
from pathlib import Path
from urllib.parse import quote

JS = r'''(() => {
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
'''

CSS = '''#player-musicas {
  position:fixed; bottom: max(16px, env(safe-area-inset-bottom)); right:16px;
  z-index:90; max-width:calc(100vw - 32px); padding:10px 14px;
  background:#fffaf4; color:#2b2118; border:1px solid #d8cfc2;
  border-radius:20px; box-shadow:0 3px 16px #0002;
  font-family:Georgia,serif; text-align:center;
}
#player-musicas button {
  background:transparent; color:inherit; border:0; padding:8px;
  font:inherit; font-size:15px; cursor:pointer; min-height:44px;
}
#player-musicas button:focus-visible {outline:2px solid #8a6a4f; border-radius:8px;}
#player-musicas button:disabled {cursor:default; opacity:.65;}
#player-musicas span {display:block; font-size:12px; max-width:240px;}
#player-musicas span:empty {display:none;}
body {padding-bottom:110px;}
'''


def main():
    root = Path(__file__).resolve().parent
    pages = [root / name for name in ('index.html', 'fotos.html')]
    for page in pages:
        if not page.is_file():
            raise SystemExit('Coloque instalar-musicas.py na pasta do site, junto de index.html e fotos.html.')
        if '</head>' not in page.read_text(encoding='utf-8').lower():
            raise SystemExit(f'Não encontrei o cabeçalho em {page.name}. Nenhuma alteração feita.')
    folder = root / 'musicas'
    folder.mkdir(exist_ok=True)
    extensions = {'.mp3', '.m4a', '.aac', '.ogg', '.wav', '.flac'}
    tracks = [quote(p.relative_to(root).as_posix(), safe='/')
              for p in sorted(folder.rglob('*'))
              if p.is_file() and p.suffix.lower() in extensions
              and not any(part.startswith('.') for part in p.relative_to(folder).parts)]
    (root / 'musicas.json').write_text(json.dumps(tracks, ensure_ascii=False, indent=2), encoding='utf-8')
    (root / 'player-musicas.js').write_text(JS, encoding='utf-8')
    (root / 'player-musicas.css').write_text(CSS, encoding='utf-8')
    for page in pages:
        html = page.read_text(encoding='utf-8')
        if 'src="player-musicas.js"' in html:
            continue
        position = html.lower().index('</head>')
        tags = '  <link rel="stylesheet" href="player-musicas.css">\n  <script src="player-musicas.js" defer></script>\n'
        page.write_text(html[:position] + tags + html[position:], encoding='utf-8')
    print(f'Pronto! Player instalado nas duas páginas. {len(tracks)} músicas cadastradas.')
    if not tracks:
        print('Coloque os áudios na pasta musicas e execute este mesmo comando novamente.')
    print('As fotos e fotos-casamento.json foram preservados.')


if __name__ == '__main__':
    main()
