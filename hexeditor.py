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

    def setHexLineWidth(self, width):
        self.hex_p.setHexLineWidth(width)