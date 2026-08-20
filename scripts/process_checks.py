from __future__ import annotations

import ntpath
import subprocess
import sys
from pathlib import Path
from typing import Union


def is_process_running(
    process_name: str,
    *,
    executable_path: Union[str, Path, None] = None,
    command_contains: Union[str, Path, None] = None,
) -> bool:
    if sys.platform != 'win32':
        return False

    process_records = _query_processes(process_name)
    expected_executable = _normalize_path(executable_path) if executable_path else None
    command_needle = str(command_contains).casefold() if command_contains else None

    for process in process_records:
        path_matches = (
            expected_executable is None
            or _normalize_path(process.get('ExecutablePath', '')) == expected_executable
        )
        command_matches = (
            command_needle is None
            or command_needle in process.get('CommandLine', '').casefold()
        )

        if path_matches and command_matches:
            return True

    return False


def _query_processes(process_name: str) -> list[dict[str, str]]:
    if not process_name.strip():
        raise ValueError('Nome do processo nao pode ficar vazio.')

    escaped_name = process_name.replace("'", "''")
    query = f"name='{escaped_name}'"

    try:
        result = subprocess.run(
            [
                'wmic',
                'process',
                'where',
                query,
                'get',
                'Name,ExecutablePath,CommandLine',
                '/format:list',
            ],
            capture_output=True,
            text=True,
            errors='replace',
            check=False,
        )
    except FileNotFoundError as error:
        raise RuntimeError('wmic nao foi encontrado neste Windows.') from error

    if result.returncode != 0:
        error_output = (result.stderr or result.stdout).strip()
        raise RuntimeError(f'Falha ao verificar processos: {error_output}')

    return _parse_wmic_list(result.stdout)


def _parse_wmic_list(output: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}

    for raw_line in output.splitlines():
        line = raw_line.strip()

        if not line:
            if current:
                records.append(current)
                current = {}
            continue

        if '=' not in line:
            continue

        key, value = line.split('=', 1)
        current[key] = value

    if current:
        records.append(current)

    return records


def _normalize_path(path: Union[str, Path]) -> str:
    return ntpath.normcase(ntpath.normpath(str(path).strip().strip('"')))
