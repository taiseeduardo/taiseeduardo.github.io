"""Converte HEIC/HEIF no macOS e atualiza as galerias existentes."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    root = Path(__file__).resolve().parent
    updater = root / 'instalar-galerias-paginadas.py'
    if not (root / 'fotos.html').is_file() or not updater.is_file():
        raise SystemExit('Coloque este arquivo junto de fotos.html e instalar-galerias-paginadas.py.')
    folders = [root / name for name in ('fotos-casamento', 'fotos-convidados', 'fotos-enviadas')]
    sources = []
    for folder in folders:
        if not folder.is_dir():
            continue
        for photo in sorted(folder.rglob('*')):
            relative = photo.relative_to(folder)
            if (photo.is_file() and photo.suffix.lower() in {'.heic', '.heif'}
                    and not any(part.startswith('.') for part in relative.parts)
                    and relative.parts[0] != 'compatibilidade-heic'):
                sources.append((folder, photo))
    sips = shutil.which('sips')
    if sources and not sips:
        raise SystemExit('A conversão usa sips, ferramenta que já vem no macOS. Execute este comando no seu Mac.')
    converted = skipped = failed = 0
    for folder, photo in sources:
        relative = photo.relative_to(folder)
        target = folder / 'compatibilidade-heic' / relative.parent / (photo.name + '.jpg')
        if (target.is_file() and target.stat().st_size > 0
                and target.stat().st_mtime_ns >= photo.stat().st_mtime_ns):
            skipped += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        # O arquivo temporário fica fora das galerias até a conversão terminar.
        with tempfile.TemporaryDirectory(prefix='converter-heic-') as temp:
            output = Path(temp) / 'foto.jpg'
            result = subprocess.run([sips, '-s', 'format', 'jpeg', '-s', 'formatOptions', '95',
                                     str(photo), '--out', str(output)], capture_output=True, text=True)
            if result.returncode != 0 or not output.is_file() or output.stat().st_size == 0:
                failed += 1
                print(f'Não consegui converter: {photo.relative_to(root)}', flush=True)
                print((result.stderr or result.stdout).strip(), flush=True)
                continue
            shutil.copyfile(output, target)
            converted += 1
            print(f'Convertida: {photo.name}', flush=True)
    print(f'HEIC/HEIF: {converted} convertidas, {skipped} já atualizadas, {failed} com erro.', flush=True)
    print('Os arquivos HEIC originais foram preservados. As cópias JPEG mantêm a resolução.', flush=True)
    subprocess.run([sys.executable, str(updater)], cwd=root, check=True)
    if failed:
        print('As conversões que falharam não aparecem na galeria. Confira os nomes acima.')
    print('Faça Commit e Push das cópias JPEG e dos demais arquivos alterados.')


if __name__ == '__main__':
    main()
