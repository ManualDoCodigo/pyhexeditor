#2021 - Douglas Diniz - www.manualdocodigo.com.br

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from hexeditor_p import HexEditor_p

import os

class HexEditor(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super(HexEditor, self).__init__(parent)

        self.hex_p = HexEditor_p(self)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        #self.ensureWidgetVisible(self.hex_p)
        self.setWidget(self.hex_p)
        
    def setData(self, data):
        self.hex_p.setData(data)

    def getData(self):
        return self.hex_p.getData()

    def setNumberOfBytesPerLine(self, num):
        self.hex_p.setNumberOfBytesPerLine(num)
    
    def setNumberOfLines(self, num):
        self.hex_p.setNumberOfLines(num)
    
    def setFontSize(self, size):
        self.hex_p.setFontSize(size)
    
    def setCursorPosition(self, address):
        self.hex_p.setCursorPosition(address)