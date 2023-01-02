import asyncio
import curses
from itertools import cycle
import time
import random
import os


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def read_controls(canvas):
    rows_direction = columns_direction = 0
    space_pressed = False
    canvas.nodelay(True)

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -10

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 10

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 10

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -10

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True
    
    return rows_direction, columns_direction, space_pressed


async def animate_spaceship(canvas, row, column):
    animations =[]
    for filename in os.listdir('animations'):
        with open(f'animations/{filename}', 'r') as file:
            animations.append(file.read())

    rows, columns = get_frame_size(animations[0])               #Размеры корабля
    column = column - columns // 2
    max_row, max_column = canvas.getmaxyx()

    for animation in cycle(animations):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        if 0 < row + rows_direction < max_row:
            row += rows_direction
        elif row + rows_direction <= 0:
            row = 1
        elif row + rows_direction >= max_row:
            row = max_row - rows - 1

        if 0 < column + columns_direction < max_column:
            column += columns_direction
        elif column + columns_direction <= 0:
            column = 1
        elif column + columns_direction >= max_column:
            column = max_column - columns - 1

        
        draw_frame(canvas, row, column, animation)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, animation, negative=True)


def draw_frame(canvas, start_row, start_column, text, negative=False):
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break
                
            if symbol == ' ':
                continue

            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*'):
    while True:
        for _ in range(random.randint(1,10)):
            await asyncio.sleep(0)
        
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(2):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


def draw(canvas):
    height, width = curses.window.getmaxyx(canvas)
    curses.curs_set(False)
    canvas.border()
    coroutines = [blink(
        canvas,
        random.randint(1, height-1),
        random.randint(1, width-1),
        random.choice('+*.:')) for _ in range(1,20)]
    coroutines.append(fire(canvas, height / 2, width / 2))
    coroutines.append(animate_spaceship(canvas, height / 2, width / 2))
    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)

        TIC_TIMEOUT = 0.1
        time.sleep(TIC_TIMEOUT)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
