#!/usr/bin/env python
#coding=utf-8

import curses
import time
import locale
import random

locale.setlocale(locale.LC_ALL, '')


boat = u"""\
x┏━┓
┏┛ ┗┓
┃   ┃
┗━━━┛\
""".replace(" ", u"\xA0").replace("x", " ")

#┌─┐
#│ │
#└─┘
#⚘⌂

islands = [
u"""\
xxxx┌───┐
x┌──┘  ⚘└┐
┌┘ ⚘  ⌂  │
│   ⚘   ┌┘
└┐     ┌┘
x│ ⌂ ⚘┌┘
x└────┘\
""".replace(" ", u"\xA0").replace("x", " "),

u"""\
xx┌─────┐
x┌┘ ⌂ ⌂ └┐
┌┘       │
│   ⌂   ┌┘
└┐      │
x└┐  ⌂┌─┘
xx└───┘\
""".replace(" ", u"\xA0").replace("x", " "),

u"""\
xx┌────────┐
┌─┘     ⌂  │
│   ⌂  ⚘  ┌┘
│    ⚘  ⚘ │
└┐  ⚘  ⌂  └┐
x└─────────┘\
""".replace(" ", u"\xA0").replace("x", " "),

u"""\
┌─┐
└─┘\
""".replace(" ", u"\xA0").replace("x", " "),

u"""\
┌──┐
│⌂┌┘
└─┘\
""".replace(" ", u"\xA0").replace("x", " "),

u"""\
x┌─┐
┌┘ │
└──┘\
""".replace(" ", u"\xA0").replace("x", " "),

u"""\
┌─┐
│ └┐
└──┘\
""".replace(" ", u"\xA0").replace("x", " "),

u"""\
┌──┐
└┐⚘│
x└─┘\
""".replace(" ", u"\xA0").replace("x", " "),

u"""\
xxxxx┌────┐
xxxxx│   ⚘└┐
xxx┌─┘ ⚘⌂  │
┌──┘⚘      └┐
│     ⌂   ⚘┌┘
│ ⌂ ┌──┐  ┌┘
└┐ ┌┘xx│⌂┌┘
x└─┘xxx└─┘\
""".replace(" ", u"\xA0").replace("x", " "),

u"""\
┌──────────┐
└┐⌂    ⚘   └──┐
x└──┐        ⌂└┐
xxx┌┘  ⌂      ⚘│
xx┌┘  ┌──┐     └┐
xx│ ⚘ │xx│  ⚘   │
xx│   └──┘⌂    ⌂│
xx└┐  ⌂      ┌──┘
xxx└───┐   ┌─┘
xxxxxxx└───┘\
""".replace(" ", u"\xA0").replace("x", " "),
]


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
    #     health
    #     islands[]
    #     last_island_spawn_step
    #     crashed
    #     tridents[]

    # sprites:
    #     boat
    #     face
    #     health[0..8]
    #     nbsp
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

    random.seed()

    windows.stdscr = curses.initscr()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)    # water
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK) # boat
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # health
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  # islands
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)  # death messages
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)   # tridents

    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    windows.stdscr.keypad(1)
    windows.stdscr.nodelay(1)

    windows.scoreboard = curses.newwin(2, 80, 0, 0)

    windows.gameborder = curses.newwin(22, 80, 2, 0)
    windows.gameborder.border(0, 0, 0, 0, curses.ACS_LTEE, curses.ACS_RTEE)
    windows.gameborder.refresh()

    windows.gamewin = curses.newwin(20, 78, 3, 1)
    windows.gamewin.keypad(1)
    windows.gamewin.nodelay(1)
    windows.gamewin.bkgd("~", curses.color_pair(1))
    load_sprites()

    reset()


def reset():
    windows.scoreboard.clear()
    windows.scoreboard.border(0, 0, 0, " ", 0, 0, curses.ACS_VLINE, curses.ACS_VLINE)

    state.stepnum = 0

    state.score = 0
    state.x = 35
    state.y = 16
    state.min_x = 0
    state.max_x = 73
    state.health = 25

    state.islands = []
    state.last_island_spawn_step = -100

    state.tridents = []

    state.crashed = False


def cleanup():
    curses.nocbreak()
    windows.stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    print "done"


def load_sprites():
    sprites.boat = boat.split("\n")
    sprites.health = [[u"⠀"],[u"⠁"],[u"⠃"],[u"⠇"],[u"⡇"],[u"⡏"],[u"⡟"],[u"⡿"],[u"⣿"]]
    sprites.face = [[u"☻"]]
    sprites.nbsp = [[u"\xA0"]]
    sprites.trident = [[u"♆"]]
    sprites.skull = [[u"☠"]]

    sprites.islands = []
    for i in islands:
        sprites.islands.append(i.split("\n"))


def step():
    state.ch = windows.gamewin.getch()

    if state.ch == ord('q'):
        raise Exit()

    if state.crashed or state.health <= 0:
        if state.ch != -1 and state.ch != curses.KEY_LEFT and state.ch != curses.KEY_RIGHT:
            reset()
    else:
        handle_input()

        # move islands
        if state.stepnum % 3 == 0:
            for i in state.islands:
                i.y += 1
            while state.islands and state.islands[0].y > windows.gamewin.getmaxyx()[0]:
                state.islands = state.islands[1:]

        # spawn islands
        if state.stepnum - state.last_island_spawn_step > 10 and random.randrange(15) == 0:
            i = Container()
            i.y = -10
            i.x = random.randrange(67)
            i.sprite = random.choice(sprites.islands)
            state.islands.append(i)
            state.last_island_spawn_step = state.stepnum

        # move tridents
        if state.stepnum % 2 == 0:
            for t in state.tridents:
                t.y += 1
            while state.tridents and state.tridents[0].y > windows.gamewin.getmaxyx()[0]:
                state.tridents = state.tridents[1:]

        # spawn tridents
        if random.randrange(5) == 0:
            t = Container()
            t.y = -10
            t.x = random.randrange(windows.gamewin.getmaxyx()[1])
            state.tridents.append(t)

        # handle score
        if state.stepnum % 15 == 0:
            state.score += 1

    draw()

    state.stepnum += 1


def handle_input():
    if state.ch == curses.KEY_LEFT:
        state.x -= 1
        if state.x < state.min_x:
            state.x = state.min_x

    elif state.ch == curses.KEY_RIGHT:
        state.x += 1
        if state.x > state.max_x:
            state.x = state.max_x

    elif state.ch == ord('h'):
        state.health -= 1


def draw():
    draw_score()
    draw_game()


def draw_score():
    windows.scoreboard.addstr(1, 3, "Score:", curses.A_BOLD)
    windows.scoreboard.addstr(1, 10, str(state.score))
    windows.scoreboard.addstr(1, 20, "Crew Remaining:", curses.A_BOLD)
    windows.scoreboard.addstr(1, 36, str(state.health) + u"\xA0".encode("utf-8"))
    windows.scoreboard.refresh()


def draw_game():
    windows.gamewin.clear()
    #windows.gamewin.addstr(1, 1, ".....".encode("utf-8"), curses.color_pair(2))

    for i in state.islands:
        draw_sprite(windows.gamewin, i.y, i.x, i.sprite, curses.color_pair(4))
    #windows.gamewin.addstr(1, 1, windows.gamewin.instr(state.y,state.x,5), curses.color_pair(2))

    for t in state.tridents:
        draw_sprite(windows.gamewin, t.y, t.x, sprites.trident, curses.color_pair(6))

    draw_sprite(windows.gamewin, state.y, state.x, sprites.boat, curses.color_pair(2), True)
    draw_health()

    if state.crashed:
        windows.gamewin.addstr( 8, 25, "                            ".replace(" ", u"\xA0").encode("utf-8"), curses.color_pair(5))
        windows.gamewin.addstr( 9, 25, "        YOU CRASHED!        ".replace(" ", u"\xA0").encode("utf-8"), curses.color_pair(5) | curses.A_BOLD)
        windows.gamewin.addstr(10, 25, "  Press any key to restart  ".replace(" ", u"\xA0").encode("utf-8"), curses.color_pair(5))
        windows.gamewin.addstr(11, 25, "                            ".replace(" ", u"\xA0").encode("utf-8"), curses.color_pair(5))
    elif state.health <= 0:
        windows.gamewin.addstr( 8, 25, "                            ".replace(" ", u"\xA0").encode("utf-8"), curses.color_pair(5))
        windows.gamewin.addstr( 9, 25, "         YOU DIED!          ".replace(" ", u"\xA0").encode("utf-8"), curses.color_pair(5) | curses.A_BOLD)
        windows.gamewin.addstr(10, 25, "  Press any key to restart  ".replace(" ", u"\xA0").encode("utf-8"), curses.color_pair(5))
        windows.gamewin.addstr(11, 25, "                            ".replace(" ", u"\xA0").encode("utf-8"), curses.color_pair(5))

    windows.gamewin.refresh()


def draw_health():
    face = sprites.face if state.health > 0 else sprites.skull
    draw_sprite(windows.gamewin, state.y+1, state.x+2, face, curses.color_pair(3))

    hp = state.health - 1
    hp1 = 8 if hp >= 8 else max(hp, 0)
    hp2 = 8 if hp >= 16 else max(hp - 8, 0)
    hp3 = max(hp - 16, 0)

    draw_sprite(windows.gamewin, state.y+2, state.x+1, sprites.health[hp1], curses.color_pair(3))
    draw_sprite(windows.gamewin, state.y+2, state.x+2, sprites.health[hp2], curses.color_pair(3))
    draw_sprite(windows.gamewin, state.y+2, state.x+3, sprites.health[hp3], curses.color_pair(3))


def draw_sprite(win, y, x, sprite, attrs=0, collision=False):
    h, w = win.getmaxyx()
    for i,row in enumerate(sprite):
        if y + i < h and y + i >= 0:
            for j,char in enumerate(row):
                if char != " " and x + j < w and x + j >= 0:
                    char = char.encode("utf-8")

                    if collision:
                        at = win.instr(y + i, x + j, 1)

                        if win.inch(y + i, x + j) == 9798: # hit by trident. TODO: better collision detection
                            state.health -= 1
                            new_tridents = []
                            for t in state.tridents:
                                if t.y != y + i or t.x != x + j:
                                    new_tridents.append(t)
                            state.tridents = new_tridents

                        elif at != u"~".encode("utf-8"):
                            state.health = 0
                            state.crashed = True

                    if y + i == h - 1 and x + j == w - 1:
                        win.insstr(y + i, x + j, char, attrs)
                    else:
                        win.addstr(y + i, x + j, char, attrs)


if __name__ == "__main__":
    main()
