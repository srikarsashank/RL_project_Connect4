from tkinter import *
import tkinter.font as tkFont
import random
import math
import copy

dx = [1, 1, 1, 0]
dy = [1, 0, -1, 1]


class Board(object):

    def __init__(self, board, last_move=[None, None]):
        self.board = board
        self.last_move = last_move

    def tryMove(self, move):

        if (move < 0 or move > 7 or self.board[0][move] != 0):
            return -1;

        for i in range(len(self.board)):
            if (self.board[i][move] != 0):
                return i - 1
        return len(self.board) - 1

    def terminal(self):
        for i in range(len(self.board[0])):
            if (self.board[0][i] == 0):
                return False
        return True

    def legal_moves(self):
        legal = []
        for i in range(len(self.board[0])):
            if (self.board[0][i] == 0):
                legal.append(i)

        return legal

    def next_state(self, turn):
        # Retuns next state
        aux = copy.deepcopy(self)
        moves = aux.legal_moves()
        if len(moves) > 0:
            ind = random.randint(0, len(moves) - 1)
            row = aux.tryMove(moves[ind])
            aux.board[row][moves[ind]] = turn
            aux.last_move = [row, moves[ind]]
        return aux

    def winner(self):
        x = self.last_move[0]
        y = self.last_move[1]

        if x == None:
            return 0

        for d in range(4):

            h_counter = 0
            c_counter = 0

            for k in range(-3, 4):

                u = x + k * dx[d]
                v = y + k * dy[d]

                if u < 0 or u >= 6:
                    continue

                if v < 0 or v >= 7:
                    continue

                if self.board[u][v] == -1:
                    c_counter = 0
                    h_counter += 1
                elif self.board[u][v] == 1:
                    h_counter = 0
                    c_counter += 1
                else:
                    h_counter = 0
                    c_counter = 0

                if h_counter == 4:
                    return -1

                if c_counter == 4:
                    return 1

        return 0



class Node():

    def __init__(self, state, parent=None):
        self.visits = 1
        self.reward = 0.0
        self.state = state
        self.children = []
        self.children_move = []
        self.parent = parent

    def addChild(self, child_state, move):
        child = Node(child_state, self)
        self.children.append(child)
        self.children_move.append(move)

    def update(self, reward):
        self.reward += reward
        self.visits += 1

    def fully_explored(self):
        if len(self.children) == len(self.state.legal_moves()):
            return True
        return False


def MTCS(maxIter, root, factor):
    for inter in range(maxIter):
        front, turn = treePolicy(root, 1, factor)
        reward = defaultPolicy(front.state, turn)
        backup(front, reward, turn)

    ans = bestChild(root, 0)
    for c in ans.parent.children:
        print(c.reward / c.visits)

    return ans


def treePolicy(node, turn, factor):
    while node.state.terminal() == False and node.state.winner() == 0:
        if (node.fully_explored() == False):
            return expand(node, turn), -turn
        else:
            node = bestChild(node, factor)
            turn *= -1
    return node, turn


def expand(node, turn):
    tried_children_move = [m for m in node.children_move]
    possible_moves = node.state.legal_moves()

    for move in possible_moves:
        if move not in tried_children_move:
            row = node.state.tryMove(move)
            new_state = copy.deepcopy(node.state)
            new_state.board[row][move] = turn
            new_state.last_move = [row, move]
            break

    node.addChild(new_state, move)
    return node.children[-1]


def bestChild(node, factor):
    bestscore = -10000000.0
    bestChildren = []
    for c in node.children:
        exploit = c.reward / c.visits
        explore = math.sqrt(math.log(2.0 * node.visits) / float(c.visits))
        score = exploit + factor * explore
        if score == bestscore:
            bestChildren.append(c)
        if score > bestscore:
            bestChildren = [c]
            bestscore = score
    return random.choice(bestChildren)


def defaultPolicy(state, turn):
    while state.terminal() == False and state.winner() == 0:
        state = state.next_state(turn)
        turn *= -1
    return state.winner()


def backup(node, reward, turn):
    while node != None:
        node.visits += 1
        node.reward -= turn * reward
        node = node.parent
        turn *= -1
    return



class Info(Frame):

    def __init__(self, master=None):
        Frame.__init__(self)
        self.configure(width=500, height=100, bg="white")
        police = tkFont.Font(family="comicsans", size=35, weight="bold")
        self.t = Label(self, text="CONNECT 4 ", font=police, bg="white")
        self.t.grid(sticky=NSEW, pady=20)


class Point(object):

    def __init__(self, x, y, canvas, color="white"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.color = color
        self.turn = 1
        self.r = 30
        self.point = self.canvas.create_oval(self.x + 10, self.y + 10, self.x + 61, self.y + 61, fill=color,
                                             outline="blue")

    def setColor(self, color):
        self.canvas.itemconfigure(self.point, fill=color)
        self.color = color


class Terrain(Canvas):

    def __init__(self, master=None):

        Canvas.__init__(self)
        self.configure(width=500, height=400, bg="blue")

        self.p = []
        self.winner = False

        board = []
        for i in range(6):
            row = []
            for j in range(7):
                row.append(0)
            board.append(row)

        self.b = Board(board)
        self.last_bstate = self.b

        for i in range(0, 340, int(400 / 6)):
            spots = []
            for j in range(0, 440, int(500 / 7)):
                spots.append(Point(j, i, self))

            self.p.append(spots)

        self.bind("<Button-1>", self.action)

    def reloadBoard(self, i=None, j=None, val=None, bstate=None):

        if i == None:
            if bstate != None:
                self.b = copy.deepcopy(bstate)
            for i in range(6):
                for j in range(7):
                    self.reloadBoard(i, j, val=None, bstate=None)
        elif val == None:
            if self.b.board[i][j] == -1:
                self.p[i][j].setColor("yellow")
            elif self.b.board[i][j] == 1:
                self.p[i][j].setColor("red")
            elif self.b.board[i][j] == 0:
                self.p[i][j].setColor("white")
        else:
            self.b.board[i][j] = val
            self.reloadBoard(i, j)

    def findBestMove(self, factor):
        o = Node(self.b)
        bestMove = MTCS(3000, o, factor)
        self.b = copy.deepcopy(bestMove.state)

        self.reloadBoard()

    def action(self, event):

        self.last_bstate = copy.deepcopy(self.b)


        if not self.winner:
            col = int(event.x / 71)
            ok = False
            row = self.b.tryMove(col)

            if row == -1:
                return
            else:
                self.reloadBoard(row, col, -1)
                self.b.last_move = [row, col]
                ok = True

            if ok:
                info.t.config(text="Computer's Turn")

            result = self.b.winner()

            if result == 1:
                info.t.config(text="YOU LOST!")
                self.winner = True
            elif result == -1:
                info.t.config(text="YOU WON!")
                self.winner = True
            elif self.b.terminal():
                info.t.config(text="DRAW")
                self.winner = True

        self.update()

        if not self.winner:

            self.findBestMove(2.0)
            ok = True

            if ok:
                info.t.config(text="YOUR TURN")

            result = self.b.winner()

            if result == 1:
                info.t.config(text="YOU LOST!")
                self.winner = True
            elif result == -1:
                info.t.config(text="YOU WON!")
                self.winner = True
            elif self.b.terminal():
                info.t.config(text="DRAW")
                self.winner = True

        self.update()

    def step_back(self):

        self.winner = False
        info.t.config(text="YOUR TURN")
        self.reloadBoard(bstate=self.last_bstate)
        self.update()


if __name__ == "__main__":
    root = Tk()
    root.geometry("500x550")
    root.title("CONNECT 4 MCL")
    root.configure(bg="white")
    root.minsize(500, 600)
    root.maxsize(500, 600)

    info = Info(root)
    info.grid(row=0, column=0)

    t = Terrain(root)
    t.grid(row=1, column=0)


    def restart():
        global info
        info.t.config(text="")

        info = Info(root)
        info.grid(row=0, column=0)

        t = Terrain(root)
        t.grid(row=1, column=0)


    def step_back():
        global t
        t.step_back()


    def close():
        root.destroy()


    Button(root, text="TRY AGAIN", command=restart).grid(row=3, column=0, pady=5)
    Button(root, text="STEP BACK", command=step_back).grid(row=2, column=0, pady=2)
    Button(root, text="EXIT", command=close).grid(row=4, column=0, pady=2)

    root.mainloop()
