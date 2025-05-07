#!/usr/bin/env python3
import click
import datetime
import time
import os
import sys
import platform
from typing import Optional


def get_notification_command():
    """Возвращает команду для уведомлений в зависимости от ОС."""
    system = platform.system()
    if system == "Darwin":  # macOS
        return "say"
    elif system == "Linux":
        return "notify-send"
    elif system == "Windows":
        return "powershell -c (New-Object Media.SoundPlayer 'C:\\Windows\\Media\\notify.wav').PlaySync()"
    return None


def play_notification(message: str):
    """Воспроизводит уведомление в зависимости от ОС."""
    command = get_notification_command()
    if command:
        if platform.system() == "Windows":
            os.system(command)
        else:
            os.system(f"{command} '{message}'")


def pluralize_seconds(n):
    """Возвращает 'секунда', 'секунды' или 'секунд' в зависимости от числа."""
    if 11 <= n % 100 <= 14:
        return "секунд"
    last_digit = n % 10
    if last_digit == 1:
        return "секунда"
    elif 2 <= last_digit <= 4:
        return "секунды"
    else:
        return "секунд"


def format_time(seconds: int) -> str:
    """Форматирует время в читаемый вид."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def counter(minutes: int, notice: str = "Работаем", pause_event: Optional[click.Context] = None):
    """Счетчик с возможностью паузы и прогресс-баром."""
    total_seconds = minutes * 60
    start_time = datetime.datetime.now()
    finish_time = start_time + datetime.timedelta(minutes=minutes)
    
    with click.progressbar(length=total_seconds, label=notice) as bar:
        while datetime.datetime.now() < finish_time:
            if pause_event and pause_event.paused:
                click.echo("\nПауза. Нажмите Enter для продолжения...")
                input()
                pause_event.paused = False
                start_time = datetime.datetime.now() - datetime.timedelta(seconds=bar.pos)
                finish_time = start_time + datetime.timedelta(minutes=minutes)
            
            remaining = finish_time - datetime.datetime.now()
            remaining_seconds = int(remaining.total_seconds())
            
            if remaining_seconds < 0:
                break
                
            bar.update(1)
            time.sleep(1)
    
    play_notification(f"{notice} завершено")


def sets_of_pomodoros(pomodoros: list, size: int) -> list:
    """Разбивает список помидоров на сеты."""
    return [pomodoros[i:i + size] for i in range(0, len(pomodoros), size)]


def set_pomodoro(sets: list, work_min: int, break_min: int, relax_min: int, pause_event: Optional[click.Context] = None):
    """Выполняет набор помидоров с перерывами."""
    for index, set in enumerate(sets, 1):
        click.clear()
        for i, j in enumerate(set, 1):
            click.echo(f"Сессия {index}")
            play_notification(f"Сессия {index}. Помодоро {i}")
            click.echo(f'Помодоро {i}: {"🍅" * j}')
            
            try:
                counter(work_min, pause_event=pause_event)
                sys.stdout.write("\033[F\033[K")
                sys.stdout.flush()
                counter(break_min, notice="Отдыхаем", pause_event=pause_event)
            except KeyboardInterrupt:
                if click.confirm("Хотите прервать текущий помодоро?"):
                    return
                continue
                
            click.clear()
        counter(relax_min, notice="Большой отдых", pause_event=pause_event)


class PomodoroContext(click.Context):
    """Контекст для хранения состояния паузы."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paused = False


@click.command()
@click.option(
    "--work-min", type=int, default=25, help="Длительность одного помидора (в минутах)."
)
@click.option(
    "--break-min",
    type=int,
    default=5,
    help="Длительность короткого перерыва (в минутах).",
)
@click.option(
    "--relax-min",
    type=int,
    default=15,
    help="Длительность длинного перерыва (в минутах).",
)
@click.option("--pomodoros", type=int, default=8, help="Общее количество помидоров.")
@click.option(
    "--size",
    type=int,
    default=4,
    help="Размер одного сета (кол-во помидоров до длинного перерыва).",
)
@click.confirmation_option(prompt="Запускаем?")
def cli(work_min, break_min, relax_min, pomodoros, size):
    """Помодоро в терминале. Легкая настройка и адаптация для любых ваших задач"""
    try:
        if not all(x > 0 for x in [work_min, break_min, relax_min, pomodoros, size]):
            raise click.BadParameter("Все значения должны быть положительными числами")
            
        if pomodoros < size:
            raise click.BadParameter("Количество помидоров должно быть больше или равно размеру сета")
            
        ctx = PomodoroContext(cli)
        all_pomodoros = list(range(1, pomodoros + 1))
        sets = sets_of_pomodoros(all_pomodoros, size)
        set_pomodoro(sets, work_min, break_min, relax_min, pause_event=ctx)
        play_notification("Конец")
        
    except KeyboardInterrupt:
        click.echo("\nПрограмма прервана пользователем")
    except Exception as e:
        click.echo(f"Произошла ошибка: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
