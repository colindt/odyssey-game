#!/usr/bin/env python
#coding=utf-8

import curses
import time
import locale

locale.setlocale(locale.LC_ALL, '')


boat = u"""\
 ┏━┓
┏┛ ┗┓
┃   ┃
┗━━━┛"""


class Container (object):
    # windows:
    #     stdscr
    #     gamewin
    #     gameborder
    #     scoreboard

    # state:
    #     score
    #     ch
    #     x
    #     y
    #     min_x
    #     max_x

    # sprites:
    #     boat
    pass


class Exit (Exception):
    pass


def main():
    init()

    try:
        while True:
            step()
            time.sleep(1.0/30)
    except (KeyboardInterrupt, Exit) as e:
        pass
    finally:
        cleanup()


def init():
    global state, windows, sprites
    state = Container()
    windows = Container()
    sprites = Container()

    windows.stdscr = curses.initscr()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    windows.stdscr.keypad(1)
    windows.stdscr.nodelay(1)

    windows.scoreboard = curses.newwin(2, 80, 0, 0)
    windows.scoreboard.border(0, 0, 0, " ", 0, 0, curses.ACS_VLINE, curses.ACS_VLINE)

    windows.gameborder = curses.newwin(22, 80, 2, 0)
    windows.gameborder.border(0, 0, 0, 0, curses.ACS_LTEE, curses.ACS_RTEE)
    windows.gameborder.refresh()

    windows.gamewin = curses.newwin(20, 78, 3, 1)
    windows.gamewin.keypad(1)
    windows.gamewin.nodelay(1)
    windows.gamewin.bkgd("~", curses.color_pair(1))

    state.score = 0
    state.x = 35
    state.y = 16
    state.min_x = 0
    state.max_x = 73

    load_sprites()


def cleanup():
    curses.nocbreak()
    windows.stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    print "done"


def load_sprites():
    sprites.boat = boat.split("\n")


def step():
    state.ch = windows.gamewin.getch()
    if state.ch == ord('q'):
        raise Exit()

    elif state.ch == curses.KEY_LEFT:
        state.x -= 1
        if state.x < state.min_x:
            state.x = state.min_x

    elif state.ch == curses.KEY_RIGHT:
        state.x += 1
        if state.x > state.max_x:
            state.x = state.max_x

    state.score += 1
    draw()


def draw():
    draw_score()
    draw_game()




def draw_score():
    windows.scoreboard.addstr(1, 3, "Score:", curses.A_BOLD)
    windows.scoreboard.addstr(1, 10, str(state.score))
    windows.scoreboard.refresh()


def draw_game():
    windows.gamewin.clear()
    windows.gamewin.addstr(1, 1, ".....".encode("utf-8"), curses.color_pair(2))
    windows.gamewin.addstr(1, 1, unicode(state.ch).encode("utf-8"), curses.color_pair(2))
    draw_sprite(windows.gamewin, state.y, state.x, sprites.boat, curses.color_pair(2))
    windows.gamewin.refresh()

def draw_sprite(win, y, x, sprite, attrs=0):
    h, w = win.getmaxyx()
    for i,row in enumerate(sprite):
        if y + i < h and y + i >= 0:
            for j,char in enumerate(row):
                if char != " " and char != "\n" and x + j < w and x + j >= 0:
                    char = char.encode("utf-8")
                    if y + i == h - 1 and x + j == w - 1:
                        win.insstr(y + i, x + j, char, attrs)
                    else:
                        win.addstr(y + i, x + j, char, attrs)


if __name__ == "__main__":
    main()
