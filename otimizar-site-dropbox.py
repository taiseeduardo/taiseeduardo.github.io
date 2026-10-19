"""macOS: python3 otimizar-site-dropbox.py --dropbox '/caminho/Dropbox/Originais casamento'

Copie o arquivo para a pasta do site. Não publique antes de o Dropbox terminar de sincronizar.
Os links de visualização são configurados no Dropbox e inseridos em download-originais.json.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.parse import quote, urlparse

ALBUMS = [('fotos-casamento', 'Tiago Pacheco', 'fotos.html'),
          ('fotos-convidados', 'Convidados', 'fotos-convidados.html'),
          ('fotos-enviadas', 'Enviadas pelo site', 'fotos-enviadas.html')]
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.heic', '.heif', '.webp', '.avif', '.gif'}
CONFIG = 'download-originais.json'
STATE = '.estado-otimizacao-fotos.json'
WEB = '_web'
# As páginas e download-originais.js são arquivos permanentes do site.
PREVIEW_SETTINGS = {'max_pixels': 1600, 'jpeg_quality': 80}



def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(path)


def visible_photos(folder):
    if not folder.exists():
        return []
    return [p for p in sorted(folder.rglob('*'))
            if p.is_file() and not p.is_symlink() and p.suffix.lower() in EXTENSIONS
            and not any(part.startswith('.') for part in p.relative_to(folder).parts)
            and p.relative_to(folder).parts[0] != WEB]


def archive_copy(source, destination):
    source_hash = digest(source)
    if destination.exists() and digest(destination) != source_hash:
        destination = destination.with_name(destination.stem + '-' + source_hash[:12] + destination.suffix)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        temporary = destination.with_name(destination.name + '.copiando')
        shutil.copy2(source, temporary)
        if digest(temporary) != source_hash:
            raise RuntimeError(f'Cópia não confere: {source.name}. O original foi mantido.')
        temporary.replace(destination)
    if digest(destination) != source_hash:
        raise RuntimeError(f'O original não foi verificado: {source.name}')
    return destination, source_hash


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dropbox', help='Pasta local sincronizada do Dropbox para os originais.')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    if not (root / 'fotos.html').is_file():
        raise SystemExit('Coloque o instalador junto de fotos.html.')
    sips = shutil.which('sips')
    if not sips:
        raise SystemExit('Execute no Mac: o programa usa a ferramenta sips que vem no macOS.')
    config_path = root / CONFIG
    config = json.loads(config_path.read_text(encoding='utf-8')) if config_path.exists() else {'links': {}}
    state_path = root / STATE
    state = json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else {'previews': {}}
    folder_input = args.dropbox or state.get('pasta_dropbox')
    if not folder_input:
        folder_input = input('Cole o caminho da pasta LOCAL do Dropbox para guardar os originais: ').strip()
    if not folder_input:
        raise SystemExit('Nenhuma pasta informada. Nada foi alterado.')
    folder_input = folder_input.strip().strip("\"'")
    archive = Path(folder_input).expanduser().resolve()
    if archive == root or root in archive.parents or archive in root.parents:
        raise SystemExit('A pasta dos originais precisa ficar fora da pasta do site e não pode conter o site.')
    if state.get('pasta_dropbox') and Path(state['pasta_dropbox']).resolve() != archive:
        raise SystemExit('A pasta de originais mudou. Preserve o arquivo de configuração e use a mesma pasta.')
    for key in state.get('previews', {}):
        if not (archive / key).is_file():
            raise SystemExit('Um original arquivado não está disponível localmente: ' + key + '. Aguarde a sincronização do Dropbox. Nenhuma foto foi removida.')
    for link in config.get('links', {}).values():
        if not link:
            continue
        parsed = urlparse(link)
        if parsed.scheme != 'https' or not (parsed.hostname == 'dropbox.com' or (parsed.hostname or '').endswith('.dropbox.com')):
            raise SystemExit('Use links HTTPS do Dropbox em ' + CONFIG)
    archive.mkdir(parents=True, exist_ok=True)
    for folder, _, page in ALBUMS:
        if not (root / page).is_file():
            raise SystemExit('Instale primeiro as três galerias paginadas. Nada foi removido.')
        web = root / folder / WEB
        if web.exists() and not state_path.exists():
            raise SystemExit(f'A pasta {folder}/{WEB} já existe sem registro deste instalador. Nada foi removido.')
    print('Copiando e verificando os originais no Dropbox local…', flush=True)
    incoming = []
    for folder, _, _ in ALBUMS:
        (archive / folder).mkdir(parents=True, exist_ok=True)
        for source in visible_photos(root / folder):
            destination, original_hash = archive_copy(source, archive / folder / source.relative_to(root / folder))
            incoming.append((source, destination, original_hash))
    # Nesta etapa ainda não substituímos nem apagamos fotos da pasta do site.
    planned = []
    manifests = {}
    updated_state = {'previews': {}, 'pasta_dropbox': str(archive)}
    with tempfile.TemporaryDirectory(prefix='previews-casamento-') as temp:
        staging = Path(temp)
        for folder, label, _ in ALBUMS:
            manifests[folder] = []
            for original in visible_photos(archive / folder):
                relative = original.relative_to(archive / folder)
                # JPEGs produzidos pelo conversor antigo duplicam os HEIC já arquivados.
                if relative.parts[0] == 'compatibilidade-heic':
                    counterpart = (archive / folder).joinpath(*relative.parts[1:])
                    counterpart = counterpart.with_name(counterpart.name[:-4])
                    if counterpart.exists():
                        continue
                original_hash = digest(original)
                key = folder + '/' + relative.as_posix()
                name = hashlib.sha256(key.encode('utf-8')).hexdigest()[:24]
                extension = '.gif' if original.suffix.lower() == '.gif' else '.jpg'
                site_relative = Path(folder) / WEB / (name + extension)
                target = root / site_relative
                old = state.get('previews', {}).get(key, {})
                if (old.get('original_sha256') == original_hash
                        and old.get('settings', {'max_pixels': 1600, 'jpeg_quality': 80}) == PREVIEW_SETTINGS
                        and target.exists()
                        and old.get('preview_sha256') == digest(target)):
                    staged = target
                else:
                    staged = staging / folder / (name + extension)
                    staged.parent.mkdir(parents=True, exist_ok=True)
                    if extension == '.gif':
                        shutil.copy2(original, staged)
                    else:
                        result = subprocess.run([sips, '-Z', str(PREVIEW_SETTINGS['max_pixels']), '-s', 'format', 'jpeg',
                                                 '-s', 'formatOptions', str(PREVIEW_SETTINGS['jpeg_quality']), str(original), '--out', str(staged)],
                                                capture_output=True, text=True)
                        if result.returncode or not staged.exists() or staged.stat().st_size == 0:
                            raise RuntimeError('Não consegui converter ' + key + '. Os originais continuam preservados.\n' + result.stderr)
                    print('Preparada: ' + key, flush=True)
                planned.append((staged, target))
                updated_state['previews'][key] = {'original_sha256': original_hash,
                                                  'preview_sha256': digest(staged),
                                                  'arquivo_site': site_relative.as_posix(),
                                                  'settings': dict(PREVIEW_SETTINGS)}
                manifests[folder].append({'src': quote(site_relative.as_posix(), safe='/'), 'alt': 'Foto do casamento'})
        removed = {p.resolve() for p, _, _ in incoming}
        generated = {p.resolve() for folder, _, _ in ALBUMS for p in (root / folder / WEB).rglob('*') if p.is_file()}
        retained_size = sum(p.stat().st_size for p in root.rglob('*')
                            if p.is_file() and not p.is_symlink()
                            and not any(part.startswith('.') for part in p.relative_to(root).parts)
                            and p.resolve() not in removed and p.resolve() not in generated)
        projected = retained_size + sum(p.stat().st_size for p, _ in planned)
        print(f'Tamanho projetado do site: {projected / 1024**2:.1f} MB', flush=True)
        if projected > 900 * 1024**2:
            raise RuntimeError('O site ainda ficaria acima de 900 MB. Nenhum original foi removido da pasta do site.')
        # Confere novamente antes de substituir as cópias locais pelos arquivos de visualização.
        for source, archived, original_hash in incoming:
            if digest(source) != original_hash or digest(archived) != original_hash:
                raise RuntimeError('Uma foto mudou durante o processamento. Nada foi removido: ' + source.name)
        for staged, target in planned:
            if staged == target:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + '.tmp')
            shutil.copyfile(staged, temporary)
            temporary.replace(target)
        for folder, _, _ in ALBUMS:
            write_json(root / (folder + '.json'), manifests[folder])
        for folder, _, _ in ALBUMS:
            config.setdefault('links', {}).setdefault(folder, '')
        write_json(config_path, config)
        write_json(state_path, updated_state)
        ignore_path = root / '.gitignore'
        ignore = ignore_path.read_text(encoding='utf-8') if ignore_path.exists() else ''
        if STATE not in ignore.splitlines():
            ignore_path.write_text(ignore.rstrip() + '\n' + STATE + '\n', encoding='utf-8')
        # Só remove da pasta publicada os arquivos já copiados e verificados no Dropbox.
        for source, _, _ in incoming:
            source.unlink()
        keep = {target.resolve() for _, target in planned}
        for folder, _, _ in ALBUMS:
            for old in (root / folder / WEB).rglob('*'):
                if old.is_file() and old.resolve() not in keep:
                    old.unlink()
    print(f"\nPronto! Originais preservados no Dropbox local; cópias JPEG de até {PREVIEW_SETTINGS['max_pixels']} pixels, qualidade {PREVIEW_SETTINGS['jpeg_quality']}.")
    print('As cópias são comprimidas. Os originais arquivados são idênticos, verificados por SHA-256.')
    print('Aguarde o aplicativo Dropbox concluir a sincronização.')
    print('No Dropbox, crie links das três pastas como PODE VISUALIZAR e coloque-os no arquivo ' + CONFIG + '.')
    print('O código não configura nem verifica permissões da conta Dropbox.')
    print('Depois faça Commit e Push. As exclusões no Git removem os originais da publicação atual, não do histórico.')
    print('Para atualizar fotos, use apenas: python3 otimizar-site-dropbox.py')
    print('Não execute os atualizadores antigos: eles não conhecem este novo fluxo de originais e cópias leves.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError) as error:
        raise SystemExit(str(error))
