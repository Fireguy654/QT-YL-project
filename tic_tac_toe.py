import sys
from PyQt5.QtWidgets import QLineEdit, QPushButton, QWidget, QHBoxLayout, QApplication, \
    QVBoxLayout, QLabel, QLCDNumber, QCheckBox, QSizePolicy, QRadioButton, QDialog


# "QtTTT" это окно, которое одновременно является интерфейсом крестиков-ноликов и реализует их
class QtTTT(QDialog):
    def __init__(self, pl_x, pl_o, data_con):
        super().__init__()

        self.data_con = data_con

        self.initUI(pl_x, pl_o)

    def initUI(self, pl_x, pl_o):
        self.setModal(True)

        self.pls = {
            'O': pl_o,
            'X': pl_x
        }

        self.setWindowTitle('tic-tac-toe')

        self.cnt = 0
        self.main_layout = QVBoxLayout(self)
        self.rad_btn_layout = QHBoxLayout(self)
        self.btn_layouts = [QHBoxLayout(self) for _ in range(3)]

        self.setWindowTitle('tic-tac-toe')

        self.x_RB = QRadioButton('X', self)
        self.x_RB.setChecked(True)
        self.x_RB.setEnabled(False)
        self.rad_btn_layout.addWidget(self.x_RB)

        self.o_RB = QRadioButton('O', self)
        self.o_RB.setEnabled(False)
        self.rad_btn_layout.addWidget(self.o_RB)

        self.field = [[QPushButton(self) for _ in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                self.field[i][j].clicked.connect(self.place)
                self.field[i][j].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.field[i][j].setMinimumSize(60, 60)
                self.btn_layouts[i].addWidget(self.field[i][j])

        self.won_line = QLabel(self)

        self.main_layout.addLayout(self.rad_btn_layout)
        for i in range(3):
            self.main_layout.addLayout(self.btn_layouts[i])
        self.main_layout.addWidget(self.won_line)

    def place(self):
        self.sender().setEnabled(False)
        if self.x_RB.isChecked():
            self.sender().setText('X')
            self.o_RB.setChecked(True)
        else:
            self.sender().setText('O')
            self.x_RB.setChecked(True)
        self.cnt += 1
        if self.field[0][0].text() == self.field[0][1].text() == self.field[0][2].text() != '':
            self.won(self.pls[self.field[0][0].text()])
        elif self.field[1][0].text() == self.field[1][1].text() == self.field[1][2].text() != '':
            self.won(self.pls[self.field[1][0].text()])
        elif self.field[2][0].text() == self.field[2][1].text() == self.field[2][2].text() != '':
            self.won(self.pls[self.field[2][0].text()])
        elif self.field[0][0].text() == self.field[1][0].text() == self.field[2][0].text() != '':
            self.won(self.pls[self.field[0][0].text()])
        elif self.field[0][1].text() == self.field[1][1].text() == self.field[2][1].text() != '':
            self.won(self.pls[self.field[0][1].text()])
        elif self.field[0][2].text() == self.field[1][2].text() == self.field[2][2].text() != '':
            self.won(self.pls[self.field[0][2].text()])
        elif self.field[0][0].text() == self.field[1][1].text() == self.field[2][2].text() != '':
            self.won(self.pls[self.field[0][0].text()])
        elif self.field[2][0].text() == self.field[1][1].text() == self.field[0][2].text() != '':
            self.won(self.pls[self.field[2][0].text()])
        elif self.cnt == 9:
            self.won('Ничья!')

    def won(self, who_won):
        for i in range(3):
            for j in range(3):
                self.field[i][j].setEnabled(False)
        if who_won == 'Ничья!':
            self.won_line.setText(who_won)
        else:
            self.won_line.setText(f'Выиграл {who_won}!')
            self.data_con.execute("""
                                  UPDATE accounts
                                  SET ttt = ttt + 1
                                  WHERE name = ?
                                  """, (who_won,))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = QtTTT('pl1', 'pl2')
    wnd.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
