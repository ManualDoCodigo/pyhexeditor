#2021 - Douglas Diniz - www.manualdocodigo.com.br

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal

import os

class HexEditor_p(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(HexEditor_p, self).__init__(parent)

        self._scroll = parent

        self.BYTES_PER_LINE = 16

        self._cursorTimer = QtCore.QTimer()

        self.data = bytearray(os.urandom(1024*20))

        self.setFont(QtGui.QFont("Courier", 8))
        self.setFocusPolicy(Qt.StrongFocus)

        self.penStandard = QtGui.QPen(self.palette().color(QtGui.QPalette.WindowText))

        self._charWidth = self.fontMetrics().width('9')
        self._charHeight = self.fontMetrics().height()

        self.addr_xpos = 0
        self.addr_width = self.numHexChars(len(self.data)) * self._charWidth + self._charWidth

        self.hex_xpos = self.addr_width
        self.hex_width = 49*self._charWidth

        self.ascii_xpos = self.addr_width + self.hex_width
        self.ascii_width = 18*self._charWidth

        self.widget_width = self.ascii_xpos + self.ascii_width

        self.firstIndexToPaint = 0
        self.lastIndexToPaint = 0

        self._cursorIndexInData = 0
        self._cursorHexPosition = 0
        self._cursorXPositionInCanvas = 0
        self._cursorYPositionInCanvas = 0
        self._cursorBlink = False

        self.currentSelection = {
            'start': 0,
            'end': 0
        }

        self.setMinimumHeight((len(self.data)//16)*self._charHeight+self._charHeight)
        self.setCursorVariables(0) #TODO

        self._cursorTimer.timeout.connect(self.updateCursor)
        self._cursorTimer.setInterval(500)
        self._cursorTimer.start()

    def setData(self, data):
        if isinstance(data, (bytearray, bytes, QtCore.QByteArray)):
            self.data = data
            self.setCursorVariables(0)
            self.update()
        else:
            print("The Data should be a bytearray or bytes")

    def updateCursor(self):
        self._cursorBlink = not self._cursorBlink
        self.update(self._cursorXPositionInCanvas, self._cursorYPositionInCanvas, self._charWidth, self._charHeight)

    def mousePressEvent(self, e):
        self.update()
        self.setCursorVariables(self.mapPointToHexIndex(e.pos()))
        self.currentSelection['start'] = self._cursorIndexInData
        self.currentSelection['end'] = self._cursorIndexInData
        #print(self.currentSelection)

    def setCursorVariables(self, hexIndex):
        self._cursorIndexInData = hexIndex//2
        self._cursorHexPosition = hexIndex
        
        self._cursorYPositionInCanvas = (self._cursorHexPosition // (2*self.BYTES_PER_LINE)) * self._charHeight +self._charHeight + 2
        #print(f"charHeight: {self._charHeight}")

        x = self._cursorHexPosition % (2*self.BYTES_PER_LINE)
        self._cursorXPositionInCanvas = (((x//2)*3) + (x%2)) * self._charWidth + self.hex_xpos + self._charWidth

        print(f"_cursorIndexInData: {self._cursorIndexInData} - self._cursorHexPosition: {self._cursorHexPosition} - \
        self._cursorXPositionInCanvas: {self._cursorXPositionInCanvas} - self._cursorYPositionInCanvas: {self._cursorYPositionInCanvas}")


    def mapPointToHexIndex(self,point):
        if point.x() > self.hex_xpos and point.x() < self.hex_xpos + self.hex_width - self._charWidth:
            x = ((point.x() - self.hex_xpos) // self._charWidth)

            if x%3 == 2:                
                x = (x//3)*2 + 1
            else:
                x = (x//3)*2

            y = (point.y() // self._charHeight) * self.BYTES_PER_LINE * 2        
        else:
            return -1
        
        return x+y

    # def mapPointToDataIndex(self,point):
    #     if point.x() > self.hex_xpos and point.x() < self.hex_xpos + self.hex_width - self._charWidth:
    #         x = ((point.x() - self.hex_xpos) // self._charWidth) // 3
    #         y = (point.y() // self._charHeight) * self.BYTES_PER_LINE
        
    #     else:
    #         return -1
        
    #     return x+y

    def keyPressEvent(self, e):
        key = e.text()

        if (key >= "0" and key <= "9") or (key >= "a" and key <= "f"):
            if len(self.data) > 0:
                byte = self.data[self._cursorIndexInData]
                #print(f"{byte:02x}")

                if self._cursorHexPosition % 2 == 1:
                    byte = (byte&0xf0) | (int(key,16) & 0xf)
                else:
                    byte = (byte&0xf) | ((int(key,16) & 0xf)<<4)

                #print(f"{byte:02x}")
                self.replaceByte(self._cursorIndexInData, byte)
                self.setCursorVariables(self._cursorHexPosition+1)                
        
        self.update()

    def replaceByte(self, index, byte):
        self.data[index] = byte

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)

        painter.setPen(Qt.gray)
        painter.drawLine(self.ascii_xpos, e.rect().top(), self.ascii_xpos, self.height())
        painter.drawLine(self.hex_xpos, e.rect().top(), self.hex_xpos, self.height())

        painter.setPen(self.penStandard)

        self.firstIndexToPaint = ((e.rect().top() // self._charHeight) - self._charHeight) * self.BYTES_PER_LINE
        self.lastIndexToPaint = ((e.rect().bottom() // self._charHeight) + self._charHeight) * self.BYTES_PER_LINE

        if self.firstIndexToPaint < 0:
            self.firstIndexToPaint = 0

        if self.lastIndexToPaint > len(self.data):
            self.lastIndexToPaint = len(self.data)

        #Address part
        self.paintAddressArea(painter, e)

        #Hex part
        self.paintHexArea(painter, e)

        #Latin1 part
        self.paintLatin1Area(painter, e)

        #Paint Cursor Line
        self.paintCursor(painter, e)
        
    def paintAddressArea(self, painter, e):
        painter.fillRect(QtCore.QRect(0, e.rect().top(), self.addr_width, self.height()), QtGui.QColor(0xd4, 0xd4, 0xd4, 0xff))        

        
        ypos = ((self.firstIndexToPaint) / self.BYTES_PER_LINE) * self._charHeight + self._charHeight
        xpos = self._charWidth/2
        lineNum = self.firstIndexToPaint

        while lineNum<self.lastIndexToPaint:
            address = lineNum
            painter.drawText(xpos, ypos, f'{address:0{self.numHexChars(len(self.data))}x}')

            ypos += self._charHeight
            lineNum += self.BYTES_PER_LINE

    def paintHexArea(self, painter, e):
        painter.fillRect(QtCore.QRect(self.hex_xpos, e.rect().top(), self.hex_width, self.height()), self.palette().color(QtGui.QPalette.Base))
        
        ypos = ((self.firstIndexToPaint) / self.BYTES_PER_LINE) * self._charHeight + self._charHeight
        lineNum = self.firstIndexToPaint

        while lineNum<self.lastIndexToPaint:

            xpos = self.hex_xpos

            for i in range(lineNum,lineNum+16):
                hex = self.data[i]

                #print(type(hex))
                
                painter.setBackgroundMode(Qt.TransparentMode)
                painter.drawText(xpos, ypos, ' ')
                xpos += self._charWidth

                if i == self._cursorIndexInData:
                    painter.setBackground(QtGui.QBrush(QtGui.QColor(0x6d, 0x9e, 0xff, 0xff)))
                    painter.setBackgroundMode(Qt.OpaqueMode)
                    #print(f"i: {i} - hex: {hex}")

                painter.drawText(xpos, ypos, f'{hex:02x}')
                xpos += self._charWidth*2

            
            ypos += self._charHeight
            lineNum += self.BYTES_PER_LINE

    def paintLatin1Area(self, painter, e):
        painter.fillRect(QtCore.QRect(self.ascii_xpos, e.rect().top(), self.ascii_width, self.height()), QtGui.QColor(0xff, 0xfb, 0xd0, 0xff))

        ypos = ((self.firstIndexToPaint) / self.BYTES_PER_LINE) * self._charHeight + self._charHeight
        lineNum = self.firstIndexToPaint

        while lineNum<self.lastIndexToPaint:
            xpos = self.ascii_xpos + self._charWidth

            for i in range(lineNum,lineNum+16):
                ch = self.data[i]

                if ch <0x20 or (ch > 0x7e and ch < 0xa0):
                    ch = '.'
                else:
                    ch = chr(ch)


                painter.drawText(xpos, ypos,ch)
                xpos += self._charWidth

            ypos += self._charHeight
            lineNum += self.BYTES_PER_LINE

    def paintCursor(self, painter, e):
        if self._cursorBlink:
            painter.fillRect(self._cursorXPositionInCanvas, self._cursorYPositionInCanvas, self._charWidth, 2, self.palette().color(QtGui.QPalette.WindowText))


    def numHexChars(self, num):
        numHexs = 0

        while num:
            num >>= 4
            numHexs += 1

        return numHexs
