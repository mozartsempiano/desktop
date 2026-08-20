from __future__ import annotations

import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
from typing import Union

from scripts.console import INFO, SUCCESS, WARNING


DOWNLOADS_DIR = Path.home() / 'Downloads'
PICTURES_DIR = Path.home() / 'Pictures'
FONTS_DIR = DOWNLOADS_DIR / 'Fontes'

FONT_EXTENSIONS = {
    '.dfont',
    '.eot',
    '.fnt',
    '.fon',
    '.otf',
    '.pfb',
    '.pfm',
    '.ttc',
    '.ttf',
    '.woff',
    '.woff2',
}
IMAGE_EXTENSIONS = {
    '.avif',
    '.bmp',
    '.gif',
    '.heic',
    '.heif',
    '.jpeg',
    '.jpg',
    '.png',
    '.svg',
    '.tif',
    '.tiff',
    '.webp',
}
ZIP_EXTENSIONS = {'.zip'}
TAR_EXTENSIONS = {'.tar', '.tar.bz2', '.tar.gz', '.tar.xz', '.tbz2', '.tgz', '.txz'}
SEVEN_ZIP_EXTENSIONS = {'.7z', '.rar'}


def organize_downloads(
    downloads_dir: Union[str, Path] = DOWNLOADS_DIR,
    pictures_dir: Union[str, Path] = PICTURES_DIR,
    fonts_dir: Union[str, Path] = FONTS_DIR,
) -> None:
    source_dir = Path(downloads_dir).expanduser()
    image_dir = Path(pictures_dir).expanduser()
    font_dir = Path(fonts_dir).expanduser()

    if not source_dir.is_dir():
        raise FileNotFoundError(f'Pasta de downloads nao encontrada: {source_dir}')

    image_dir.mkdir(parents=True, exist_ok=True)
    font_dir.mkdir(parents=True, exist_ok=True)

    moved_count = 0

    for file_path in sorted(source_dir.iterdir(), key=lambda path: path.name.casefold()):
        if not file_path.is_file():
            continue

        destination_dir = get_destination_dir(file_path, image_dir, font_dir)
        if destination_dir is None:
            continue

        move_file(file_path, destination_dir)
        moved_count += 1

    SUCCESS(f'Organizacao de downloads concluida. Arquivos movidos: {moved_count}')


def get_destination_dir(file_path: Path, image_dir: Path, font_dir: Path) -> Path | None:
    if is_font_file(file_path) or is_font_archive(file_path):
        return font_dir

    if is_image_file(file_path):
        return image_dir

    return None


def is_font_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in FONT_EXTENSIONS


def is_image_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in IMAGE_EXTENSIONS


def is_font_archive(file_path: Path) -> bool:
    name = file_path.name.casefold()
    suffix = file_path.suffix.lower()

    if suffix in ZIP_EXTENSIONS:
        return zip_contains_font(file_path)

    if any(name.endswith(extension) for extension in TAR_EXTENSIONS):
        return tar_contains_font(file_path)

    if suffix in SEVEN_ZIP_EXTENSIONS:
        return seven_zip_contains_font(file_path)

    return False


def zip_contains_font(file_path: Path) -> bool:
    try:
        with zipfile.ZipFile(file_path) as archive:
            return any(is_font_name(item.filename) for item in archive.infolist())
    except (OSError, zipfile.BadZipFile):
        WARNING(f'Ignorando arquivo zip invalido: {file_path}')
        return False


def tar_contains_font(file_path: Path) -> bool:
    try:
        with tarfile.open(file_path) as archive:
            return any(is_font_name(item.name) for item in archive.getmembers() if item.isfile())
    except (OSError, tarfile.TarError):
        WARNING(f'Ignorando arquivo tar invalido: {file_path}')
        return False


def seven_zip_contains_font(file_path: Path) -> bool:
    executable = find_7zip()
    if executable is None:
        WARNING(f'Ignorando arquivo compactado sem 7z para inspecao: {file_path}')
        return False

    result = subprocess.run(
        [executable, 'l', '-slt', str(file_path)],
        capture_output=True,
        text=True,
        errors='replace',
        check=False,
    )

    if result.returncode != 0:
        WARNING(f'Ignorando arquivo compactado invalido: {file_path}')
        return False

    return any(
        is_font_name(line.split('=', 1)[1].strip())
        for line in result.stdout.splitlines()
        if line.startswith('Path = ')
    )


def find_7zip() -> str | None:
    for executable in ('7z', '7za', '7zr'):
        path = shutil.which(executable)
        if path:
            return path

    return None


def is_font_name(name: str) -> bool:
    return Path(name).suffix.lower() in FONT_EXTENSIONS


def move_file(file_path: Path, destination_dir: Path) -> Path:
    if file_path.parent.resolve() == destination_dir.resolve():
        INFO(f'Arquivo ja esta no destino: {file_path}')
        return file_path

    destination = get_available_path(destination_dir / file_path.name)

    if file_path.resolve() == destination.resolve():
        INFO(f'Arquivo ja esta no destino: {file_path}')
        return destination

    shutil.move(str(file_path), str(destination))
    SUCCESS(f'Movido: {file_path} -> {destination}')
    return destination


def get_available_path(path: Path) -> Path:
    if not path.exists():
        return path

    counter = 1
    while True:
        candidate = path.with_name(f'{path.stem} ({counter}){path.suffix}')
        if not candidate.exists():
            return candidate
        counter += 1


def main() -> int:
    organize_downloads()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
