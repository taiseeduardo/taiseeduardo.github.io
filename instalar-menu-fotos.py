from pathlib import Path

CSS = '''
/* inicio-menu-galerias */
#menu-galerias {display:flex; flex-wrap:wrap; justify-content:center; gap:10px;
  max-width:960px; margin:28px auto 0; scroll-margin-top:100px;}
#menu-galerias a {display:inline-flex; align-items:center; justify-content:center;
  min-height:44px; padding:10px 18px; border:1px solid var(--line, #d8cfc2);
  border-radius:24px; color:var(--text, #2b2118); background:var(--card, #fffaf4);
  text-decoration:none; font-size:17px; line-height:1.3;}
#menu-galerias a:hover {border-color:var(--accent, #8a6a4f);}
#menu-galerias a:focus-visible, .voltar-menu-fotos:focus-visible {
  outline:2px solid var(--accent, #8a6a4f); outline-offset:4px;}
#fotos-casamento, #fotos-convidados, #fotos-enviadas, #enviar-fotos {scroll-margin-top:100px;}
.voltar-menu-fotos {display:inline-block; margin:30px 0 0; padding:12px 18px;
  color:var(--text, #2b2118); font-size:17px; text-underline-offset:4px;}
@media(max-width:600px) {
  #menu-galerias {display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px;}
  #menu-galerias a {font-size:15px; padding:12px 8px;}
}
@media(prefers-reduced-motion:reduce) {html {scroll-behavior:auto;}}
/* fim-menu-galerias */
'''


def main():
    root = Path(__file__).resolve().parent
    page = root / 'fotos.html'
    if not page.exists():
        raise SystemExit('Coloque instalar-menu-fotos.py junto de fotos.html, na pasta do site.')
    text = page.read_text(encoding='utf-8')
    targets = [('fotos-casamento','Fotos por Thiago'),
               ('fotos-convidados','Fotos dos convidados'),
               ('fotos-enviadas','Fotos enviadas'),
               ('enviar-fotos','Envie suas fotos')]
    missing = [target for target, _ in targets if f'id="{target}"' not in text]
    if missing:
        raise SystemExit('Execute primeiro organizar-galerias.py e ativar-envio-fotos.py. Depois execute este instalador.')
    if '</header>' not in text.lower() or '</head>' not in text.lower():
        raise SystemExit('Estrutura da página não reconhecida. Nenhuma alteração feita.')
    backup = root / 'fotos-antes-do-menu.html.bak'
    if not backup.exists():
        backup.write_text(text, encoding='utf-8')
    if 'id="menu-galerias"' not in text:
        menu = '\n<div id="menu-galerias" role="navigation" aria-label="Galerias de fotos">\n'
        menu += '\n'.join(f'<a href="#{target}">{label}</a>' for target,label in targets)
        menu += '\n</div>\n'
        position = text.lower().index('</header>')
        text = text[:position] + menu + text[position:]
    if '/* inicio-menu-galerias */' not in text:
        position = text.lower().index('</head>')
        text = text[:position] + '<style>\n' + CSS + '</style>\n' + text[position:]
    for target, _ in targets:
        start = text.index(f'id="{target}"')
        end = text.lower().find('</section>', start)
        if end < 0:
            raise SystemExit('Não encontrei o fim da seção. A página não foi alterada.')
        if 'class="voltar-menu-fotos"' not in text[start:end]:
            link = '\n<a class="voltar-menu-fotos" href="#menu-galerias">↑ Voltar ao topo</a>\n'
            text = text[:end] + link + text[end:]
    page.write_text(text, encoding='utf-8')
    print('Pronto! Menu com quatro botões e links para voltar ao topo instalados.')
    print('Fotos, músicas e setas preservadas. Faça Commit e Push das alterações.')


if __name__ == '__main__':
    main()
