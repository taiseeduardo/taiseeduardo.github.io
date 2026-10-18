"""Execute junto do fotos.html. Opcional: python3 organizar-galerias.py URL_DO_FORMULARIO"""
import html as html_module
import json
from pathlib import Path
import re
import sys
from urllib.parse import quote, urlparse

LOADER = r'''(() => {
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
'''


def main():
    root = Path(__file__).resolve().parent
    page = root / 'fotos.html'
    if not page.is_file():
        raise SystemExit('Coloque organizar-galerias.py na pasta do site, junto de fotos.html.')
    text = page.read_text(encoding='utf-8')
    if '</main>' not in text.lower() or '</body>' not in text.lower():
        raise SystemExit('Estrutura da página não reconhecida. Nenhum arquivo alterado.')
    link = sys.argv[1] if len(sys.argv) > 1 else None
    if link and (urlparse(link).scheme != 'https' or not urlparse(link).netloc):
        raise SystemExit('O link do formulário precisa começar com https://.')
    backup = root / 'fotos-antes-das-galerias.html.bak'
    if not backup.exists():
        backup.write_text(text, encoding='utf-8')
    folder = root / 'fotos-convidados'
    folder.mkdir(exist_ok=True)
    extensions = {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif'}
    photos = [{'src':quote(p.relative_to(root).as_posix(), safe='/'),
               'alt':'Foto registrada pelos convidados'}
              for p in sorted(folder.rglob('*'))
              if p.is_file() and p.suffix.lower() in extensions
              and not any(part.startswith('.') for part in p.relative_to(folder).parts)]
    (root / 'fotos-convidados.json').write_text(json.dumps(photos, ensure_ascii=False, indent=2), encoding='utf-8')
    (root / 'galeria-convidados.js').write_text(LOADER, encoding='utf-8')
    # Remove o atributo de tradução só dos textos substituídos, evitando que idioma.js os restaure.
    text = re.sub(r'<h2\b[^>]*data-i18n="fotosCasamentoTitulo"[^>]*>.*?</h2>',
                  '<h2>Fotos por Thiago</h2>', text, count=1, flags=re.S)
    text = re.sub(r'<p\b[^>]*data-i18n="fotosCasamentoTexto"[^>]*>.*?</p>',
                  '<p>Os registros oficiais do nosso grande dia.</p>', text, count=1, flags=re.S)
    section = '''
    <!-- inicio-galerias-convidados -->
    <section id="fotos-convidados">
      <div class="container">
        <h2>Fotos dos convidados</h2>
        <p>Nosso dia pelo olhar de quem celebrou com a gente.</p>
        <div id="galeriaConvidados" class="gallery"></div>
        <div id="mensagemConvidados" class="empty-message">Em breve, mais lembranças compartilhadas pelos nossos convidados.</div>
      </div>
    </section>
    <section id="enviar-fotos">
      <div class="container">
        <h2>Compartilhe suas fotos</h2>
        <p>Registrou algum momento especial? Compartilhe com a gente!</p>
        <!-- botao-envio-inicio -->
        <p>Em breve, você poderá enviar suas fotos por aqui.</p>
        <!-- botao-envio-fim -->
      </div>
    </section>
    <!-- fim-galerias-convidados -->
'''
    if '<!-- inicio-galerias-convidados -->' not in text:
        position = text.lower().index('</main>')
        text = text[:position] + section + text[position:]
    if link:
        button = '<!-- botao-envio-inicio -->\n<a class="button" href="' + html_module.escape(link, quote=True) + '" target="_blank" rel="noopener noreferrer">Envie suas fotos</a>\n<!-- botao-envio-fim -->'
        text = re.sub(r'<!-- botao-envio-inicio -->.*?<!-- botao-envio-fim -->', button, text, flags=re.S)
    if 'src="galeria-convidados.js"' not in text:
        position = text.lower().rindex('</body>')
        text = text[:position] + '<script src="galeria-convidados.js" defer></script>\n' + text[position:]
    page.write_text(text, encoding='utf-8')
    # As setas passam a navegar pela galeria onde a foto foi aberta.
    navigation = root / 'galeria-navegacao.js'
    if navigation.exists():
        js = navigation.read_text(encoding='utf-8')
        js = js.replace("const gallery = document.getElementById('galeriaCasamento');",
                        "let gallery = document.getElementById('galeriaCasamento');")
        js = js.replace("gallery.addEventListener('click', event => {\n    if (event.target.tagName !== 'IMG') return;",
                        "document.addEventListener('click', event => {\n    if (event.target.tagName !== 'IMG' || !event.target.closest('.gallery')) return;\n    gallery = event.target.closest('.gallery');")
        navigation.write_text(js, encoding='utf-8')
    print(f'Pronto! Fotos por Thiago e Fotos dos convidados separadas. {len(photos)} fotos de convidados cadastradas.')
    print('Fotos oficiais e músicas preservadas. Faça Commit e Push das alterações.')
    if not link:
        print('Para ativar o envio depois: python3 organizar-galerias.py "LINK_DO_FORMULARIO"')


if __name__ == '__main__':
    main()
