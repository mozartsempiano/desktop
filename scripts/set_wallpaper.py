from __future__ import annotations

import ctypes
import json
import random
import sys
import urllib.request
from pathlib import Path
from typing import Any, Union

from scripts.console import INFO, SUCCESS


SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02
GITHUB_CONTENTS_URL = 'https://api.github.com/repos/mozartsempiano/wallpapers/contents/photography?ref=main'
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp'}
REQUEST_TIMEOUT_SECONDS = 30
WALLPAPER_CACHE_DIR = Path(__file__).resolve().parents[1] / '.cache' / 'wallpapers'


def set_wallpaper(image_path: Union[str, Path]) -> None:
    if sys.platform != 'win32':
        raise RuntimeError('Este script so pode alterar o papel de parede no Windows.')

    image_file = Path(image_path).expanduser()

    if not image_file.is_file():
        raise FileNotFoundError(f'Imagem do papel de parede nao encontrada: {image_file}')

    image_file = image_file.resolve(strict=True)

    user32 = ctypes.WinDLL('user32', use_last_error=True)
    system_parameters_info = user32.SystemParametersInfoW
    system_parameters_info.argtypes = [
        ctypes.c_uint,
        ctypes.c_uint,
        ctypes.c_wchar_p,
        ctypes.c_uint,
    ]
    system_parameters_info.restype = ctypes.c_bool

    changed = system_parameters_info(
        SPI_SETDESKWALLPAPER,
        0,
        str(image_file),
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE,
    )

    if not changed:
        error_code = ctypes.get_last_error()
        raise ctypes.WinError(error_code)

    SUCCESS(f'Papel de parede alterado: {image_file}')


def download_random_wallpaper() -> Path:
    wallpapers = list_remote_wallpapers()
    selected = random.choice(wallpapers)
    target = WALLPAPER_CACHE_DIR / selected['name']

    if target.is_file():
        INFO(f'Wallpaper aleatorio selecionado do cache: {target}')
        return target

    WALLPAPER_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    download_file(selected['download_url'], target)
    INFO(f'Wallpaper aleatorio baixado: {target}')
    return target


def list_remote_wallpapers() -> list[dict[str, str]]:
    request = urllib.request.Request(
        GITHUB_CONTENTS_URL,
        headers={
            'Accept': 'application/vnd.github+json',
            'User-Agent': 'desktop-scripts',
        },
    )

    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        contents: Any = json.load(response)

    if not isinstance(contents, list):
        raise RuntimeError('Resposta inesperada ao listar wallpapers no GitHub.')

    wallpapers = [
        {
            'name': item['name'],
            'download_url': item['download_url'],
        }
        for item in contents
        if item.get('type') == 'file'
        and Path(item.get('name', '')).suffix.lower() in IMAGE_EXTENSIONS
        and item.get('download_url')
    ]

    if not wallpapers:
        raise RuntimeError('Nenhum wallpaper compativel foi encontrado no repositorio.')

    return wallpapers


def download_file(url: str, target: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={'User-Agent': 'desktop-scripts'},
    )
    temporary_target = target.with_name(f'{target.name}.download')

    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        temporary_target.write_bytes(response.read())

    temporary_target.replace(target)


def main() -> int:
    set_wallpaper(download_random_wallpaper())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
