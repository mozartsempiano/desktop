from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from scripts.console import ERROR, INFO, SUCCESS, TASK, WARNING
from scripts.task_codes import ALREADY_RUNNING_EXIT_CODE


ROOT_DIR = Path(__file__).resolve().parent
LOGS_DIR = ROOT_DIR / 'logs'


@dataclass(frozen=True)
class Task:
    name: str
    module: str
    background: bool = False
    log_name: str | None = None


TASKS = [
    Task('Organizar Downloads', 'scripts.organize_downloads'),
    Task('Alterar papel de parede', 'scripts.set_wallpaper'),
    Task('Iniciar ArchiSteamFarm', 'scripts.start_asf', background=True, log_name='asf.log'),
    Task('Iniciar ASFclaim', 'scripts.start_asfclaim', background=True, log_name='asfclaim.log'),
]


@dataclass(frozen=True)
class RunningTask:
    task: Task
    process: subprocess.Popen[bytes]
    log_path: Path


def run_task(task: Task) -> RunningTask | None:
    TASK(f'Executando: {task.name}')

    command = [sys.executable, '-B', '-m', task.module]

    if task.background:
        log_path = prepare_task_log(task)
        with log_path.open('a', encoding='utf-8') as log_file:
            process = subprocess.Popen(
                command,
                cwd=ROOT_DIR,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
            )

        INFO(f'Background iniciado: {task.name} (PID {process.pid}, log: {log_path})')
        return RunningTask(task, process, log_path)

    subprocess.run(command, cwd=ROOT_DIR, check=True)
    return None


def prepare_task_log(task: Task) -> Path:
    if not task.log_name:
        raise ValueError(f'Tarefa em background sem log configurado: {task.name}')

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / task.log_name

    with log_path.open('a', encoding='utf-8') as log_file:
        log_file.write(f'\n==== {datetime.now():%Y-%m-%d %H:%M:%S} | {task.name} ====\n')

    return log_path


def wait_for_background_tasks(running_tasks: list[RunningTask]) -> int:
    if not running_tasks:
        return 0

    INFO('Aguardando tarefas em background. Use Ctrl+C aqui para encerrar todas.')

    exit_code = 0
    pending_tasks = list(running_tasks)

    while pending_tasks:
        for running_task in pending_tasks[:]:
            return_code = running_task.process.poll()
            if return_code is None:
                continue

            pending_tasks.remove(running_task)
            exit_code = handle_finished_background_task(running_task, return_code, exit_code)

        if pending_tasks:
            time.sleep(0.5)

    return exit_code


def handle_finished_background_task(
    running_task: RunningTask,
    return_code: int,
    current_exit_code: int,
) -> int:
    exit_code = current_exit_code

    if return_code == ALREADY_RUNNING_EXIT_CODE:
        WARNING(f'Ignorado: {running_task.task.name} ja estava em execucao. Log: {running_task.log_path}')
        return exit_code

    if return_code != 0 and exit_code == 0:
        exit_code = return_code

    message = f'Finalizado: {running_task.task.name} (codigo {return_code}, log: {running_task.log_path})'
    if return_code == 0:
        SUCCESS(message)
    else:
        ERROR(message)

    return exit_code


def terminate_background_tasks(running_tasks: list[RunningTask]) -> None:
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

        return wait_for_background_tasks(running_tasks)
    except KeyboardInterrupt:
        WARNING('Interrompido pelo usuario.')
        terminate_background_tasks(running_tasks)
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
