from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from scripts.console import ERROR, INFO, SUCCESS, TASK, WARNING
from scripts.task_codes import ALREADY_RUNNING_EXIT_CODE


ROOT_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Task:
    name: str
    module: str
    separate_terminal: bool = False


TASKS = [
    Task('Organizar Downloads', 'scripts.organize_downloads'),
    Task('Alterar papel de parede', 'scripts.set_wallpaper'),
    Task('Iniciar ArchiSteamFarm', 'scripts.start_asf', separate_terminal=True),
    Task('Iniciar ASFclaim', 'scripts.start_asfclaim', separate_terminal=True),
]


@dataclass(frozen=True)
class RunningTask:
    task: Task
    process: subprocess.Popen[bytes]


def run_task(task: Task) -> RunningTask | None:
    TASK(f'Executando: {task.name}')

    command = [sys.executable, '-B', '-m', task.module]

    if task.separate_terminal:
        process = subprocess.Popen(
            command,
            cwd=ROOT_DIR,
            creationflags=getattr(subprocess, 'CREATE_NEW_CONSOLE', 0),
        )
        INFO(f'Terminal aberto: {task.name} (PID {process.pid})')
        return RunningTask(task, process)

    subprocess.run(command, cwd=ROOT_DIR, check=True)
    return None


def wait_for_terminal_tasks(running_tasks: list[RunningTask]) -> int:
    if not running_tasks:
        return 0

    INFO('Aguardando tarefas em terminais separados. Use Ctrl+C aqui para encerrar todas.')

    exit_code = 0
    for running_task in running_tasks:
        return_code = running_task.process.wait()
        if return_code == ALREADY_RUNNING_EXIT_CODE:
            WARNING(f'Ignorado: {running_task.task.name} ja estava em execucao.')
            continue

        if return_code != 0 and exit_code == 0:
            exit_code = return_code

        message = f'Finalizado: {running_task.task.name} (codigo {return_code})'
        if return_code == 0:
            SUCCESS(message)
        else:
            ERROR(message)

    return exit_code


def terminate_terminal_tasks(running_tasks: list[RunningTask]) -> None:
    for running_task in running_tasks:
        process = running_task.process
        if process.poll() is not None:
            continue

        WARNING(f'Encerrando: {running_task.task.name} (PID {process.pid})')
        terminate_process_tree(process.pid)


def terminate_process_tree(pid: int) -> None:
    if sys.platform == 'win32':
        subprocess.run(
            ['taskkill', '/PID', str(pid), '/T', '/F'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return

    subprocess.run(['kill', str(pid)], check=False)


def main() -> int:
    running_tasks: list[RunningTask] = []

    try:
        for task in TASKS:
            running_task = run_task(task)
            if running_task:
                running_tasks.append(running_task)

        return wait_for_terminal_tasks(running_tasks)
    except KeyboardInterrupt:
        WARNING('Interrompido pelo usuario.')
        terminate_terminal_tasks(running_tasks)
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
