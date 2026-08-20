from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Union

from scripts.console import SUCCESS, WARNING
from scripts.process_checks import is_process_running
from scripts.task_codes import ALREADY_RUNNING_EXIT_CODE


ASF_ROOT_DIR = Path.home() / 'Downloads' / 'ASF'
DEFAULT_ASFCLAIM_PATH = ASF_ROOT_DIR / 'ASFclaim' / 'start.bat'


def start_asfclaim(batch_path: Union[str, Path] = DEFAULT_ASFCLAIM_PATH) -> int:
    batch_file = Path(batch_path).expanduser().resolve(strict=True)

    if not batch_file.is_file():
        raise FileNotFoundError(f'Batch nao encontrado: {batch_file}')

    if is_process_running('cmd.exe', command_contains=batch_file):
        WARNING(f'ASFclaim ja esta em execucao: {batch_file}')
        return ALREADY_RUNNING_EXIT_CODE

    result = subprocess.run(
        ['cmd.exe', '/d', '/c', str(batch_file)],
        cwd=str(batch_file.parent),
        stdin=subprocess.DEVNULL,
        check=False,
    )

    SUCCESS(f'ASFclaim finalizado: {batch_file}')
    return result.returncode


def main() -> int:
    return start_asfclaim()


if __name__ == '__main__':
    raise SystemExit(main())
