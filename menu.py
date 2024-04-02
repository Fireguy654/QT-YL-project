import sys
import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QDialog, QApplication

from nim_game import QtNIM
from sapper import QtSapper
from tic_tac_toe import QtTTT


# Класс "myDialog" является предком нескольких последующих классов и реализует их общие функции
# А именно "cancel", реализующая выход из диалога и проверка на правильность введённого аккаунта
class myDialog(QDialog):
    def __init__(self, filename, data_con):
        super().__init__()

        self.initUI(filename, data_con)

    def initUI(self, filename, data_con):
        self.setModal(True)

        self.data_con = data_con

        uic.loadUi(filename, self)

        self.cancel_btn.clicked.connect(self.cancel)

    def cancel(self):
        self.close()
        return

    def match(self, name, passw):
        good_password = self.data_con.execute("""
                                          SELECT password
                                          FROM accounts
                                          WHERE name == ?
                                          """, (name,)).fetchone()
        if good_password is None or good_password[0] != passw:
            return False
        return True


# "CreateWidget" это диаолговое окно, реализующее создание нового аккаунта в базе данных
class createWidget(myDialog):
    def __init__(self, data_con):
        super().__init__('create_interface.ui', data_con)

        self.initSpecUI()

    def initSpecUI(self):
        self.setWindowTitle('Create')

        self.ok_btn.clicked.connect(self.createAccount)

    def createAccount(self):
        try:
            if self.password.text() == '':
                raise ValueError("Password can't be empty")

            if len(self.name.text()) >= 25:
                raise ValueError("Name is too long")

            self.data_con.execute("""
                                  INSERT INTO accounts(name, password, nim, sapper, ttt)
                                  VALUES(?, ?, 0, 0, 0)
                                  """, (self.name.text(), self.password.text()))

            self.mes_label.setText('Account created')
            self.setEnabled(False)
            return
        except Exception as error:
            if error.__class__.__name__ == 'IntegrityError':
                self.mes_label.setText('Account with this name already exists')
            else:
                self.mes_label.setText(str(error))
            return


# "nimStarting" это диалоговое окно, реализующее подготовку к запуску НИМа
# А именно вход в акаунты игроков
class nimStarting(myDialog):
    def __init__(self, data_con):
        super().__init__('preparing_for_nim.ui', data_con)

        self.initSpecUI()

    def initSpecUI(self):
        self.setWindowTitle('NIM preparing')

        self.ok_btn.clicked.connect(self.startGame)

        self.passw1.setEchoMode(2)

        self.passw2.setEchoMode(2)

    def startGame(self):
        try:
            if (not self.match(self.name1.text(), self.passw1.text())) and \
                    (not self.match(self.name2.text(), self.passw2.text())):
                raise ValueError('Wrong password or nickname(1st and 2nd players)')

            if not self.match(self.name1.text(), self.passw1.text()):
                raise ValueError('Wrong password or nickname(1st player)')

            if not self.match(self.name2.text(), self.passw2.text()):
                raise ValueError('Wrong password or nickname(2nd player)')

            self.cur = QtNIM(self.name1.text(), self.name2.text(), self.data_con)
            self.cur.exec()
            self.close()
            return
        except Exception as error:
            self.mes_label.setText(str(error))
            return


# "tttStarting" это диалоговое окно, реализующее подготовку к запуску крестиков-ноликов
# А именно вход в акаунты игроков
class tttStarting(myDialog):
    def __init__(self, data_con):
        super().__init__('preparing_for_ttt.ui', data_con)

        self.initSpecUI()

    def initSpecUI(self):
        self.setWindowTitle('tic-tac-toe preparing')

        self.ok_btn.clicked.connect(self.startGame)

        self.passw1.setEchoMode(2)

        self.passw2.setEchoMode(2)

    def startGame(self):
        try:
            if (not self.match(self.name1.text(), self.passw1.text())) and \
                    (not self.match(self.name2.text(), self.passw2.text())):
                raise ValueError('Wrong password or nickname(1st and 2nd players)')

            if not self.match(self.name1.text(), self.passw1.text()):
                raise ValueError('Wrong password or nickname(1st player)')

            if not self.match(self.name2.text(), self.passw2.text()):
                raise ValueError('Wrong password or nickname(2nd player)')

            self.cur = QtTTT(self.name1.text(), self.name2.text(), self.data_con)
            self.cur.exec()
            self.close()
            return
        except Exception as error:
            self.mes_label.setText(str(error))
            return


# "startingSapper" это диалоговое окно, реализующее подготовку к запуску сапёра
# А именно выбор размера поля и вход в аккаунт игрока
class startingSapper(myDialog):
    def __init__(self, data_con):
        super().__init__('preparing_for_sapper.ui', data_con)

        self.initSpecUI()

    def initSpecUI(self):
        self.setWindowTitle('Sapper preparing')

        self.ok_btn.clicked.connect(self.startGame)

        self.passw.setEchoMode(2)

    def startGame(self):
        try:
            if not self.match(self.name.text(), self.passw.text()):
                raise ValueError('Wrong password or nickname')

            self.cur = QtSapper(self.x_size.value(), self.y_size.value(), self.name.text(), self.data_con)
            self.cur.exec()
            self.close()
            return
        except Exception as error:
            self.mes_label.setText(str(error))
            return


# "menuWidget" это диалоговое окно, которое является главным меню. Показывает рейтинги игроков.
# А также позволяет начать какую-либо игру или создать аккаунт.
class menuWidget(QWidget):
    def __init__(self, data_con):
        super().__init__()

        self.initUI(data_con)

    def initUI(self, data_con):
        self.data_con = data_con

        uic.loadUi('menu_interface.ui', self)

        self.setWindowTitle("Menu")

        self.nim_lb.setEnabled(False)

        self.ttt_lb.setEnabled(False)

        self.sap_lb.setEnabled(False)

        self.create_btn.clicked.connect(self.openNewWindow)

        self.nim_btn.clicked.connect(self.openNewWindow)

        self.ttt_btn.clicked.connect(self.openNewWindow)

        self.sap_btn.clicked.connect(self.openNewWindow)

        self.updateLeaderBoards()

    def openNewWindow(self):
        cur = self.sender()
        if cur.text() == 'Create new account':
            self.cur = createWidget(self.data_con)
        if cur.text() == 'Play NIM':
            self.cur = nimStarting(self.data_con)
        if cur.text() == 'Play tic-tac-toe':
            self.cur = tttStarting(self.data_con)
        if cur.text() == 'Play sapper':
            self.cur = startingSapper(self.data_con)
        self.cur.exec()
        self.updateLeaderBoards()

    def updateLeaderBoards(self):
        cur_data = self.data_con.execute("""
                                    SELECT nim, name
                                    FROM accounts
                                    ORDER BY nim * -1
                                    """).fetchmany(10)
        cur_ld = ''
        for i in range(10):
            if i < len(cur_data):
                cur_ld += f'{i + 1}. {cur_data[i][1]} ({cur_data[i][0]})\n\n'
            else:
                cur_ld += f'{i + 1}. -\n\n'
        self.nim_lb.setPlainText(cur_ld)

        cur_data = self.data_con.execute("""
                                            SELECT ttt, name
                                            FROM accounts
                                            ORDER BY ttt * -1
                                            """).fetchmany(10)
        cur_ld = ''
        for i in range(10):
            if i < len(cur_data):
                cur_ld += f'{i + 1}. {cur_data[i][1]} ({cur_data[i][0]})\n\n'
            else:
                cur_ld += f'{i + 1}. -\n\n'
        self.ttt_lb.setPlainText(cur_ld)

        cur_data = self.data_con.execute("""
                                            SELECT sapper, name
                                            FROM accounts
                                            ORDER BY sapper * -1
                                            """).fetchmany(10)
        cur_ld = ''
        for i in range(10):
            if i < len(cur_data):
                cur_ld += f'{i + 1}. {cur_data[i][1]} ({cur_data[i][0]})\n\n'
            else:
                cur_ld += f'{i + 1}. -\n\n'
        self.sap_lb.setPlainText(cur_ld)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    con = sqlite3.connect('players.db')
    data_con = con.cursor()
    wnd = menuWidget(data_con)
    wnd.show()
    sys.excepthook = except_hook
    status = app.exec()
    con.commit()
    data_con.close()
    sys.exit(status)
