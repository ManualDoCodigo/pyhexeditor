# 2021 - Douglas Diniz - www.manualdocodigo.com.br

import sys

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import QFile, QTextStream


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.filename = ""

        # Load the UI Page
        uic.loadUi("mainwindow.ui", self)

        self.actionopen.triggered.connect(self.open)
        self.actionsave.triggered.connect(self.save)
        self.actionsave_as.triggered.connect(self.saveAs)
        self.lineEditAddress.textChanged.connect(self.serCursorPosition)

    def open(self):
        fName, filter = QtWidgets.QFileDialog.getOpenFileName(self, "OpenFile")
        f = QtCore.QFile(fName)
        f.open(QtCore.QFile.ReadOnly)
        data = f.readAll()

        self.hexwidget.setData(data)
        self.filename = fName

    def save(self):
        if self.filename:
            data = self.hexwidget.getData()
            f = open(self.filename, "wb")
            f.write(data)
            f.close()

            print("Saved successfully...")
        else:
            print("No file to save")

    def saveAs(self):
        fName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File")

        if fName:
            self.filename = fName
            self.save()
        else:
            print("Invalid File")

    def serCursorPosition(self):
        try:
            address = int(self.lineEditAddress.text(), 16)
            self.hexwidget.setCursorPosition(address)
        except:
            print("Invalid hexadecimal number")


def main():
    app = QtWidgets.QApplication(sys.argv)

    # Theme test from:
    # https://github.com/Alexhuszagh/BreezeStyleSheets
    if False:
        file = QFile("./dark.qss")
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())

    main = MainWindow()

    main.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
