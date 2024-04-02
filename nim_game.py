import random
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication


# "QtNIM" это окно, которое одновременно является интерфейсом игры НИМ и реализует её
class QtNIM(QDialog):
    def __init__(self, fpl, spl, data_con):
        super().__init__()

        self.data_con = data_con

        self.initUI(fpl, spl)

    def initUI(self, fpl, spl):
        self.setModal(True)

        uic.loadUi('nim_interface.ui', self)

        self.setWindowTitle('NIM')

        self.players = [fpl, spl]
        self.cur_move = 0
        self.mes_label.setText(f"{self.players[self.cur_move]}, It's time to make your move...")

        self.heap_1.setChecked(True)
        self.cnt_1.display(random.randint(10, 100))
        self.amount.setMaximum(self.cnt_1.value())
        self.amount.setMinimum(1)
        self.heap_1.clicked.connect(self.change_max_amount)

        self.cnt_2.display(random.randint(10, 100))
        self.heap_2.clicked.connect(self.change_max_amount)

        self.cnt_3.display(random.randint(10, 100))
        self.heap_3.clicked.connect(self.change_max_amount)

        self.pick.clicked.connect(self.make_a_move)

    def change_max_amount(self):
        if self.heap_1.isChecked():
            self.amount.setMaximum(self.cnt_1.value())
        if self.heap_2.isChecked():
            self.amount.setMaximum(self.cnt_2.value())
        if self.heap_3.isChecked():
            self.amount.setMaximum(self.cnt_3.value())

    def make_a_move(self):
        if self.heap_1.isChecked():
            self.cnt_1.display(self.cnt_1.value() - self.amount.value())
            if self.cnt_1.value() == 0:
                self.heap_1.setEnabled(False)
                if self.cnt_2.value() == 0:
                    self.heap_3.click()
                else:
                    self.heap_2.click()
            else:
                self.amount.setMaximum(self.cnt_1.value())
        elif self.heap_2.isChecked():
            self.cnt_2.display(self.cnt_2.value() - self.amount.value())
            if self.cnt_2.value() == 0:
                self.heap_2.setEnabled(False)
                if self.cnt_3.value() == 0:
                    self.heap_1.click()
                else:
                    self.heap_3.click()
            else:
                self.amount.setMaximum(self.cnt_2.value())
        elif self.heap_3.isChecked():
            self.cnt_3.display(self.cnt_3.value() - self.amount.value())
            if self.cnt_3.value() == 0:
                self.heap_3.setEnabled(False)
                if self.cnt_2.value() == 0:
                    self.heap_1.click()
                else:
                    self.heap_2.click()
            else:
                self.amount.setMaximum(self.cnt_3.value())
        if self.cnt_1.value() == 0 and self.cnt_2.value() == 0 and self.cnt_3.value() == 0:
            self.mes_label.setText(f'{self.players[self.cur_move]} won!')
            self.setEnabled(False)
            self.data_con.execute("""
                                  UPDATE accounts
                                  SET nim = nim + 1
                                  WHERE name == ?
                                  """, (self.players[self.cur_move],))
            return
        self.cur_move = (self.cur_move + 1) % 2
        self.mes_label.setText(f"{self.players[self.cur_move]}, It's time to make your move...")


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = QtNIM('pl1', 'pl2')
    wnd.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
