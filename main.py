#!/usr/bin/env python3
import click
import datetime
import time
import os
import sys


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


def counter(min, notice="Работаем"):
    today = datetime.datetime.now()
    # print(f"Старт подомодоро {num}:", today.strftime('%d-%m-%Y %HH-%MM-%SS'))
    finish_time = today + datetime.timedelta(minutes=min)
    while datetime.datetime.now() < finish_time:
        remaining = finish_time - datetime.datetime.now()
        remaining_str = str(remaining).split(".")[0]
        # print(f"{notice} {remaining_str}", end="\r", flush=True)
        click.echo(f"\r{notice}: {click.style(remaining_str, fg='green')}", nl=False)

        time.sleep(1)
    click.echo("\a")
    # print(f"\a\nКонец: {datetime.datetime.now().strftime('%d-%m-%Y %HH-%MM-%SS')}")
    # os.system(f'say Время закончено')


def sets_of_pomodoros(pomodoros, size):
    return [pomodoros[i : i + size] for i in range(0, len(pomodoros), size)]


def set_pomodoro(sets, work_min, break_min, relax_min):
    for index, set in enumerate(sets, 1):
        click.clear()
        for i, j in enumerate(set, 1):
            click.echo(f"Сессия {index}")
            os.system(f"say Сессия {index}. Помодоро {i}")
            click.echo(f'Помодоро {i}: {"🍅" * j}')
            counter(work_min)
            sys.stdout.write("\033[F\033[K")
            sys.stdout.flush()
            counter(break_min, notice="Отдыхаем")
            click.clear()
        counter(relax_min, notice="Большой отдых")


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
    # click.clear()
    all_pomodoros = list(range(1, pomodoros + 1))
    sets = sets_of_pomodoros(all_pomodoros, size)
    set_pomodoro(sets, work_min, break_min, relax_min)
    os.system(f"say Конец")


if __name__ == "__main__":
    cli()
