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
    # state:
    #     stdscr
    #     gamewin
    #     gameborder
    #     scoreboard
    #     score

    # sprites:
    #     boat
    pass


class Exit (Exception):
    pass


def main():
    global state
    state = Container()

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
    state.stdscr = curses.initscr()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    state.stdscr.keypad(1)
    state.stdscr.nodelay(1)

    state.scoreboard = curses.newwin(2, 80, 0, 0)
    state.scoreboard.border(0, 0, 0, " ", 0, 0, curses.ACS_VLINE, curses.ACS_VLINE)

    state.gameborder = curses.newwin(22, 80, 2, 0)
    state.gameborder.border(0, 0, 0, 0, curses.ACS_LTEE, curses.ACS_RTEE)
    state.gameborder.refresh()

    state.gamewin = curses.newwin(20, 78, 3, 1)
    state.gamewin.keypad(1)
    state.gamewin.nodelay(1)
    state.gamewin.bkgd("~", curses.color_pair(1))

    state.score = 0

    load_sprites()


def cleanup():
    curses.nocbreak()
    state.stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    print "done"


def load_sprites():
    global sprites
    sprites = Container()
    sprites.boat = boat.split("\n")


def step():
    state.ch = state.gamewin.getch()
    if state.ch == ord('q'):
        raise Exit()

    state.score += 1
    draw()


def draw():
    draw_score()
    #state.gameborder.border(0, 0, 0, 0, curses.ACS_LTEE, curses.ACS_RTEE)
    #state.gameborder.refresh()
    draw_game()




def draw_score():
    state.scoreboard.addstr(1, 3, "Score:", curses.A_BOLD)
    state.scoreboard.addstr(1, 10, str(state.score))
    state.scoreboard.refresh()


def draw_game():
    state.gamewin.addstr(1, 1, ".....".encode("utf-8"), curses.color_pair(2))
    state.gamewin.addstr(1, 1, unicode(state.ch).encode("utf-8"), curses.color_pair(2))
    draw_sprite(state.gamewin, 10, 10, sprites.boat, curses.color_pair(2))
    state.gamewin.refresh()

def draw_sprite(win, y, x, sprite, attrs=0):
    max_y, max_x = win.getmaxyx()
    for i,row in enumerate(sprite):
        if y + i < max_y and y + i >= 0:
            for j,char in enumerate(row):
                if char != " " and x + j < max_x and x + j >= 0:
                    char = char.encode("utf-8")
                    win.addstr(y + i, x + j, char, attrs)


if __name__ == "__main__":
    main()
