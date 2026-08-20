from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Union

from scripts.console import SUCCESS, WARNING
from scripts.process_checks import is_process_running
from scripts.task_codes import ALREADY_RUNNING_EXIT_CODE


ASF_ROOT_DIR = Path.home() / 'Downloads' / 'ASF'
DEFAULT_ASF_PATH = ASF_ROOT_DIR / 'Core' / 'ArchiSteamFarm.exe'


def start_asf(executable_path: Union[str, Path] = DEFAULT_ASF_PATH) -> int:
    executable = Path(executable_path).expanduser().resolve(strict=True)

    if not executable.is_file():
        raise FileNotFoundError(f'Executavel nao encontrado: {executable}')

    if is_process_running(executable.name, executable_path=executable):
        WARNING(f'ArchiSteamFarm ja esta em execucao: {executable}')
        return ALREADY_RUNNING_EXIT_CODE

    result = subprocess.run([str(executable)], cwd=str(executable.parent), check=False)

    SUCCESS(f'ArchiSteamFarm finalizado: {executable}')
    return result.returncode


def main() -> int:
    return start_asf()


if __name__ == '__main__':
    raise SystemExit(main())
