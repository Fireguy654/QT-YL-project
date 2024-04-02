import random
import sys

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QLabel, QLineEdit, \
    QApplication, QCheckBox, QRadioButton

lost_flag = False


# "Cage" это класс, который реализует механики текущей клетки
class Cage:
    def __init__(self, board, x, y):
        self.flag = False
        self.quest = False
        self.opened = False
        self.armed = 0
        if random.randint(1, 100) % 10 in [1, 3, 7]:
            self.armed = 1
        self.x = x
        self.y = y
        self.board = board
        self.bcnt = 0
        if self.armed:
            self.board.add_bomb()

    def set_flag(self):
        if self.quest:
            self.quest = False
        self.flag = True

    def set_quest(self):
        if self.flag:
            self.flag = False
        self.quest = True

    def open(self, recursion):
        if (self.flag or self.quest) and not recursion:
            return False
        if self.opened:
            return
        cnt = 0
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if self.board.check(i, j):
                    cnt += 1
        self.bcnt = cnt
        self.opened = True
        self.board.add_opened()
        if self.bcnt == 0:
            for i in range(self.x - 1, self.x + 2):
                for j in range(self.y - 1, self.y + 2):
                    self.board.open(i, j, True)

    def check_arming(self):
        return self.armed

    def get_text(self):
        if self.opened:
            return str(self.bcnt)
        if self.flag:
            return '!'
        if self.quest:
            return'?'
        return ''

    def dismark(self):
        self.quest = False
        self.flag = False


# "Board" это класс, реализующий механики доски, на которой происходит игра
class Board:
    def __init__(self, x_size, y_size):
        self.cntb = 0
        self.board = [[Cage(self, i, j) for i in range(x_size)]
                      for j in range(y_size)]
        self.x_size = x_size
        self.y_size = y_size
        self.opened = 0

    def add_bomb(self):
        self.cntb += 1

    def add_opened(self):
        self.opened += 1

    def open(self, x, y, recursion):
        if x >= self.x_size or x < 0 or y >= self.y_size or y < 0 or self.board[y][x].check_arming():
            return False
        self.board[y][x].open(recursion)

    def check(self, x, y):
        if x < 0 or x >= self.x_size or y < 0 or y >= self.y_size:
            return False
        return self.board[y][x].check_arming()

    def mark(self, x, y, command):
        if command == '?':
            self.board[y][x].set_quest()
        if command == '!':
            self.board[y][x].set_flag()

    def get_cnt_bombs(self):
        return self.cntb

    def get_cnt_opened(self):
        return self.opened

    def dismark(self, x, y):
        self.board[y][x].dismark()


# "do_query" это функция, реализующая взаимодействие между интерфейсом сапёра и классами, реализующими его
def do_query(query, board, interface):
    x, y, com = query.split()
    x = int(x)
    y = int(y)
    if com == 'dismark':
        board.dismark(x, y)
        interface.field[y][x].setText('')
        return
    if com == 'armed':
        board.mark(x, y, '!')
        interface.field[y][x].setText(board.board[y][x].get_text())
        return
    if com == 'quest':
        board.mark(x, y, '?')
        interface.field[y][x].setText(board.board[y][x].get_text())
        return
    if board.board[y][x].check_arming() and board.board[y][x].get_text() == '':
        for i in range(board.x_size):
            for j in range(board.y_size):
                if interface.field[j][i].text() not in ['', '!', '?']:
                    interface.cnt -= 1
        global lost_flag
        lost_flag = True
        interface.mes_label.setText("YOU LOST")
        interface.setEnabled(False)
        for i in range(board.x_size):
            for j in range(board.y_size):
                board.dismark(i, j)
                board.open(i, j, True)
                interface.field[j][i].setText(board.board[j][i].get_text())
                if interface.field[j][i].text() == '':
                    interface.field[j][i].setText('*')
        interface.data_con.execute("""
                                   UPDATE accounts
                                   SET sapper = sapper + ?
                                   WHERE name == ?
                                   """, (interface.cnt, interface.pl))
        return
    board.open(x, y, False)
    for i in range(board.x_size):
        for j in range(board.y_size):
            interface.field[j][i].setText(board.board[j][i].get_text())
            if board.board[j][i].opened:
                interface.field[j][i].setEnabled(False)
    if board.get_cnt_bombs() + board.get_cnt_opened() == board.x_size * board.y_size:
        interface.mes_label.setText("YOU WON")
        interface.setEnabled(False)
        interface.cnt = board.x_size * board.y_size
        interface.data_con.execute("""
                                   UPDATE accounts
                                   SET sapper = sapper + ?
                                   WHERE name == ?
                                   """, (interface.cnt, interface.pl))
        return

# "CoordButton" это кнопка, которая хранит своё расположение
class CoordButton(QPushButton):
    def __init__(self, parent, y, x):
        super().__init__(parent)

        self.x = x
        self.y = y


# "QtSapper" это окно, реализующее интерфейс сапёра
class QtSapper(QDialog):
    def __init__(self, x_size, y_size, pl, data_con):
        super().__init__()

        self.data_con = data_con

        self.initUI(x_size, y_size, pl)

    def initUI(self, x_size, y_size, pl):
        self.setModal(True)

        self.pl = pl
        self.cnt = 0

        self.board = Board(x_size, y_size)

        self.setWindowTitle('Sapper')
        self.main_layout = QVBoxLayout(self)
        self.command_layout = QHBoxLayout(self)
        self.main_layout.addLayout(self.command_layout)
        self.h_layouts = [QHBoxLayout(self) for _ in range(y_size)]
        for i in self.h_layouts:
            self.main_layout.addLayout(i)

        self.arm_cb = QRadioButton(self)
        self.arm_cb.setText("mark as armed")
        self.command_layout.addWidget(self.arm_cb)

        self.op_cb = QRadioButton(self)
        self.op_cb.setText('open')
        self.op_cb.setChecked(True)
        self.command_layout.addWidget(self.op_cb)

        self.q_cb = QRadioButton(self)
        self.q_cb.setText('mark as strange')
        self.command_layout.addWidget(self.q_cb)

        self.d_cb = QRadioButton(self)
        self.d_cb.setText('dismark')
        self.command_layout.addWidget(self.d_cb)

        self.field = [[CoordButton(self, i, j) for j in range(x_size)] for i in range(y_size)]
        for i in range(y_size):
            for j in range(x_size):
                self.field[i][j].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                if y_size < 6 and x_size < 6:
                    self.field[i][j].setMinimumSize(80, 80)
                else:
                    self.field[i][j].setMinimumSize(60, 60)
                self.h_layouts[i].addWidget(self.field[i][j])
                self.field[i][j].clicked.connect(self.makeMove)

        self.messages_layout = QHBoxLayout(self)
        self.main_layout.addLayout(self.messages_layout)

        self.mes_label = QLabel(self)
        self.messages_layout.addWidget(self.mes_label)

        self.amount = QLabel(f'Amount of bombs: {self.board.get_cnt_bombs()}', self)
        self.messages_layout.addWidget(self.amount)

    def makeMove(self):
        self.mes_label.setText('')
        cur = self.sender()
        cur_com = ''
        if self.d_cb.isChecked():
            cur_com = 'dismark'
        if self.op_cb.isChecked():
            cur_com = 'open'
        if self.arm_cb.isChecked():
            cur_com = 'armed'
        if self.q_cb.isChecked():
            cur_com = 'quest'
        do_query(f'{cur.x} {cur.y} {cur_com}', self.board, self)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = QtSapper(4, 4, 'pl')
    wnd.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
