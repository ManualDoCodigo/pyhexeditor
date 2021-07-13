#2021 - Douglas Diniz - www.manualdocodigo.com.br

from PyQt5 import QtCore, QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt
from hexeditor import HexEditor
import hexeditor as he
import sys
import os

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #scrollArea.setWidget(self.hexwidget)

        #Load the UI Page
        uic.loadUi('mainwindow.ui', self)

        self.actionopen.triggered.connect(self.open)

    def open(self):
        fileName, filter = QtWidgets.QFileDialog.getOpenFileName(self, 'OpenFile')
        f = QtCore.QFile(fileName)
        f.open(QtCore.QFile.ReadOnly)
        data = f.readAll()
        
        self.hexwidget.setData(data)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()

    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':         
    main()