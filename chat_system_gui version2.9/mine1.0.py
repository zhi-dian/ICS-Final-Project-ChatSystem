from random import *
from graphics import *

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

Map = []
n, m = 20, 20
N, M = 400, 400
Bomb: int = 40
remain = n * m - Bomb
B = []
dx = [-1, -1, -1, 0, 0, 1, 1, 1]
dy = [-1, 0, 1, -1, 1, -1, 0, 1]
win = GraphWin("mine", M, N + 50)
uncovered = []


def init():
    for i in range(n):
        tmp = []
        tmp2 = []
        for j in range(m):
            tmp.append(-1)
            tmp2.append(-1)
        Map.append(tmp)
        uncovered.append(tmp2)
    for i in range(Bomb):
        cnd = randint(0, n * m - 1)
        while cnd in B:
            cnd = randint(0, n * m - 1)
        B.append(cnd)
        Map[cnd // n][cnd % m] = 9
    for i in range(n):
        for j in range(m):
            sumb = 0
            if Map[i][j] == 9:
                continue
            for x in range(8):
                nx = i + dx[x]
                ny = j + dy[x]
                if not available(nx, ny):
                    continue
                if Map[nx][ny] == 9:
                    sumb += 1
            Map[i][j] = sumb
    for i in range(n * m):
        init_drw(i)
    return


def pprint():
    for i in range(n):
        for j in range(m):
            print(Map[i][j], end=" ")
        print()
    return


def result(res):
    t = Text(Point(50, N + 25), "You " + res + "!!!")
    t.draw(win)
    return


def init_drw(num):
    st = Rectangle(Point(M * (num % m) / m, N * (num // n) / n), Point(M * (num % m + 1) / m, N * (num // n + 1) / n))
    st.setFill("white")
    st.setWidth(1)
    st.setOutline("grey")
    st.draw(win)
    return


def drw(num, color, word):
    if word == 0:
        word = ""
    st = Rectangle(Point(M * (num % m) / m, N * (num // n) / n), Point(M * (num % m + 1) / m, N * (num // n + 1) / n))
    st.setFill(color)
    st.setWidth(0.5)
    st.draw(win)

    if word == 9:
        c = Circle(Point(M * (num % m + 0.5) / m, N * (num // n + 0.5) / n), min(N, M) / min(n, m) / 2.5)
        c.setFill("black")
        c.draw(win)
        return

    t = Text(Point(M * (num % m + 0.5) / m, N * (num // n + 0.5) / n), str(word))
    t.draw(win)
    return


def available(x, y):
    return 0 <= x < n and 0 <= y < n


def dfs(x, y):
    #    print(x, y)
    uncovered[x][y] = 1
    drw(x * m + y, "grey", Map[x][y])
    global remain
    remain -= 1
    for dirt in range(8):
        nx = x + dx[dirt]
        ny = y + dy[dirt]
        if not available(nx, ny) or uncovered[nx][ny] == 1 or Map[nx][ny] == 9:
            continue
        if Map[nx][ny] == 0:
            dfs(nx, ny)
        else:
            uncovered[nx][ny] = 1
            drw(nx * m + ny, "grey", Map[nx][ny])
            remain -= 1
    return


def main():
    global remain
    init()
    #    pprint()
    #   print(uncovered)
    while True:
        pos = win.getMouse()
        pj, pi = int(pos.getX() // (M / m)), int(pos.getY() // (N / n))
        if not available(pi, pj) or uncovered[pi][pj] == 1:
            continue
        # print(pi, pj)
        if Map[pi][pj] == 9:
            result("lose")
            for i in range(n):
                for j in range(m):
                    if uncovered[i][j] == -1:
                        uncovered[i][j] = 1
                        if Map[i][j] == 9:
                            drw(i * m + j, "red", Map[i][j])
                        else:
                            drw(i * m + j, "grey", Map[i][j])
            win.getMouse()
            break
        if Map[pi][pj] == 0:
            dfs(pi, pj)
        else:
            drw(pi * m + pj, "grey", Map[pi][pj])
            uncovered[pi][pj] = 1
            remain -= 1

        if remain == 0:
            result("win")
            for i in range(n):
                for j in range(m):
                    if uncovered[i][j] == -1:
                        uncovered[i][j] = 1
                        drw(i * m + j, "grey", Map[i][j])
            win.getMouse()
            break
    return


main()
