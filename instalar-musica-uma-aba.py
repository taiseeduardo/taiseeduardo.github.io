from pathlib import Path

SYNC = r'''
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
'''


def main():
    root=Path(__file__).resolve().parent
    player=root/'player-musicas.js'
    if not player.exists():
        raise SystemExit('Coloque este instalador junto de player-musicas.js, na pasta do site.')
    js=player.read_text(encoding='utf-8')
    if '// inicio-musica-uma-aba' in js:
        print('O controle de música entre abas já está instalado.')
        return
    anchor="  audio.addEventListener('play', render);"
    if anchor not in js:
        raise SystemExit('Versão do player não reconhecida. Nenhuma alteração feita.')
    backup=root/'player-musicas-antes-uma-aba.js.bak'
    if not backup.exists():backup.write_text(js,encoding='utf-8')
    js=js.replace(anchor,SYNC+'\n'+anchor,1)
    player.write_text(js,encoding='utf-8')
    print('Pronto! Quando uma aba tocar, as outras abas deste site serão pausadas.')
    print('Faça Commit e Push. Depois recarregue as abas abertas para receberem a atualização.')


if __name__=='__main__':main()
