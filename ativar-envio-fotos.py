from pathlib import Path
import json
import re
from urllib.parse import quote

LINK = "https://www.dropbox.com/request/bhpakoaf9v799zwr894h"
LOADER = "(() => {\n  const gallery = document.getElementById('galeriaEnviadas');\n  const message = document.getElementById('mensagemEnviadas');\n  fetch('fotos-enviadas.json', {cache:'no-cache'})\n    .then(r => { if (!r.ok) throw new Error('Lista indisponível'); return r.json(); })\n    .then(list => {\n      if (!Array.isArray(list)) throw new Error('Lista inválida');\n      message.hidden = list.length > 0;\n      for (const item of list) {\n        const img = document.createElement('img');\n        img.src = item.src;\n        img.alt = item.alt || 'Foto registrada pelos convidados';\n        img.loading = 'lazy'; img.decoding = 'async';\n        img.addEventListener('click', () => abrirLightbox(img.src, img.alt));\n        gallery.append(img);\n      }\n    })\n    .catch(() => {message.hidden = false; message.textContent = 'Não foi possível carregar as fotos dos convidados. Tente novamente mais tarde.';});\n})();\n"

def main():
    root = Path(__file__).resolve().parent
    page = root / 'fotos.html'
    if not page.exists():
        raise SystemExit('Coloque este instalador junto de fotos.html.')
    text = page.read_text(encoding='utf-8')
    if '<!-- botao-envio-inicio -->' not in text:
        raise SystemExit('Execute primeiro organizar-galerias.py. Depois execute este instalador.')
    if '</main>' not in text.lower() or '</body>' not in text.lower():
        raise SystemExit('Estrutura da página não reconhecida.')
    folder = root / 'fotos-enviadas'
    folder.mkdir(exist_ok=True)
    photos = [{'src': quote(p.relative_to(root).as_posix(), safe='/'), 'alt':'Foto enviada pelos convidados'}
              for p in sorted(folder.rglob('*'))
              if p.is_file() and p.suffix.lower() in {'.jpg','.jpeg','.png','.webp','.avif','.gif'}
              and not any(part.startswith('.') for part in p.relative_to(folder).parts)]
    (root / 'fotos-enviadas.json').write_text(json.dumps(photos, ensure_ascii=False, indent=2), encoding='utf-8')
    (root / 'galeria-enviadas.js').write_text(LOADER, encoding='utf-8')
    if 'id="galeriaEnviadas"' not in text:
        section = '\n<section id="fotos-enviadas"><div class="container"><h2>Fotos enviadas pelos convidados</h2><p>Mais lembranças compartilhadas por vocês.</p><div id="galeriaEnviadas" class="gallery"></div><div id="mensagemEnviadas" class="empty-message">Esta galeria vai receber as fotos que vocês compartilharem com a gente.</div></div></section>\n'
        match = re.search(r'<section\b[^>]*id="enviar-fotos"[^>]*>', text)
        position = match.start() if match else text.lower().index('</main>')
        text = text[:position] + section + text[position:]
    button = '<!-- botao-envio-inicio -->\n<a class="button" href="' + LINK + '" target="_blank" rel="noopener noreferrer">Envie suas fotos</a><p>O envio é feito pelo Dropbox. Depois, reuniremos as fotos nesta galeria.</p>\n<!-- botao-envio-fim -->'
    text = re.sub(r'<!-- botao-envio-inicio -->.*?<!-- botao-envio-fim -->', button, text, flags=re.S)
    if 'src="galeria-enviadas.js"' not in text:
        position = text.lower().rindex('</body>')
        text = text[:position] + '<script src="galeria-enviadas.js" defer></script>\n' + text[position:]
    page.write_text(text, encoding='utf-8')
    print(f'Pronto! Botão do Dropbox ativado. Terceira galeria criada com {len(photos)} fotos.')
    print('Fotos oficiais, segunda galeria e músicas preservadas.')
    print('Para publicar novas fotos: copie para fotos-enviadas, execute este instalador e faça Commit e Push.')

if __name__ == '__main__':
    main()
