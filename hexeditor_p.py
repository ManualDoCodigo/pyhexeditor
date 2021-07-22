#2021 - Douglas Diniz - www.manualdocodigo.com.br

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from hexdata import HexData
from selections import Selections

import os

class HexEditor_p(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(HexEditor_p, self).__init__(parent)

        self._scroll = parent

        self.BYTES_PER_LINE = 16

        self._cursorTimer = QtCore.QTimer()

        self.data = HexData()
        self.data.setData(bytearray(os.urandom(1024*20)))

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

        #For the selection we have the place we clicked and the start and end of the selection
        #We can drag up or down related to the clicked position, so we need to save the
        #clicked position.
        self.currentSelection = {
            'click': 0,
            'start': 0,
            'end': 0
        }

        self.selections = Selections()

        self.setMinimumHeight((len(self.data)//16)*self._charHeight+self._charHeight)
        self.setCursorVariables(0) #TODO

        self._cursorTimer.timeout.connect(self.updateCursor)
        self._cursorTimer.setInterval(500)
        self._cursorTimer.start()

    def setData(self, data):
        if isinstance(data, (bytearray, bytes, QtCore.QByteArray)):
            self.data.setData(data)
            self.setCursorVariables(0)
            self.update()
        else:
            print("The Data should be a bytearray or bytes")

    def updateCursor(self):
        self._cursorBlink = not self._cursorBlink
        self.update(self._cursorXPositionInCanvas, self._cursorYPositionInCanvas, self._charWidth, self._charHeight)

    def clickedInAddressArea(self, point):
        if point.x() > self.addr_xpos and point.x() < self.addr_xpos + self.addr_width:
            return True
        return False

    def clickedInHexArea(self, point):
        if point.x() > self.hex_xpos and point.x() < self.hex_xpos + self.hex_width:
            return True
        return False
    
    def clickedInAsciiArea(self, point):
        if point.x() > self.ascii_xpos and point.x() < self.ascii_xpos + self.ascii_width:
            return True
        return False
    
    def mousePressEvent(self, e):
        '''The mouse click event starts a new selection and update the cursor variables'''
        self.update()
        if self.clickedInHexArea(e.pos()):
            self.setCursorVariables(self.mapPointToHexIndex(e.pos()))
            self.currentSelection['click'] = self._cursorIndexInData
            self.currentSelection['start'] = self._cursorIndexInData
            self.currentSelection['end'] = self._cursorIndexInData
        elif self.clickedInAddressArea(e.pos()):
            lineStartAddr = self.mapPointToLineStartPos(e.pos())
            self.setCursorVariables(lineStartAddr*2)
            self.currentSelection['click'] = lineStartAddr
            self.currentSelection['start'] = lineStartAddr
            self.currentSelection['end'] = lineStartAddr+self.BYTES_PER_LINE-1
        elif self.clickedInAsciiArea(e.pos()):
            self.setCursorVariables(self.mapPointToDataIndex(e.pos())*2)
            self.currentSelection['click'] = self._cursorIndexInData
            self.currentSelection['start'] = self._cursorIndexInData
            self.currentSelection['end'] = self._cursorIndexInData
    
    def mouseMoveEvent(self, e):
        '''This method is called when we drag the mouse over the widget canvas.
        This way the user can select a block of bytes.
        So we use the mouse location the calculate the start and end points of the selection.'''

        self.update()
        

        if self.mapPointToDataIndex(e.pos())>=0:
            cursorPos = self.mapPointToDataIndex(e.pos())

            if cursorPos >= self.currentSelection['click']:
                self.currentSelection['start'] = self.currentSelection['click']
                self.currentSelection['end'] = cursorPos
            else:
                self.currentSelection['start'] = cursorPos
                self.currentSelection['end'] = self.currentSelection['click']

            self.setCursorVariables(self.currentSelection['start']*2)
        elif self.mapPointToLineStartPos(e.pos())>=0:
            lineAddrSelected = self.mapPointToLineStartPos(e.pos())
            
            if lineAddrSelected >= self.currentSelection['click']:
                self.currentSelection['start'] = self.currentSelection['click']
                self.currentSelection['end'] = lineAddrSelected+self.BYTES_PER_LINE-1
            else:
                self.currentSelection['start'] = lineAddrSelected
                self.currentSelection['end'] = self.currentSelection['click']

            self.setCursorVariables(self.currentSelection['start']*2)

    def setCursorVariables(self, hexIndex):
        self._cursorIndexInData = hexIndex//2
        self._cursorHexPosition = hexIndex
        
        self._cursorYPositionInCanvas = (self._cursorHexPosition // (2*self.BYTES_PER_LINE)) * self._charHeight +self._charHeight + 2
        #print(f"charHeight: {self._charHeight}")

        x = self._cursorHexPosition % (2*self.BYTES_PER_LINE)
        self._cursorXPositionInCanvas = (((x//2)*3) + (x%2)) * self._charWidth + self.hex_xpos + self._charWidth

        #print(f"_cursorIndexInData: {self._cursorIndexInData} - self._cursorHexPosition: {self._cursorHexPosition} - \
        #self._cursorXPositionInCanvas: {self._cursorXPositionInCanvas} - self._cursorYPositionInCanvas: {self._cursorYPositionInCanvas}")


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

    def resetCurrentSelection(self, pos):
        '''Reset the current selection, point all the variabels to a single position'''
        if pos<0:
            pos=0

        self.currentSelection['click'] = pos
        self.currentSelection['start'] = pos
        self.currentSelection['end'] = pos


    def mapPointToDataIndex(self,point):
        if point.x() > self.hex_xpos and point.x() < self.hex_xpos + self.hex_width - self._charWidth:
            x = ((point.x() - self.hex_xpos) // self._charWidth) // 3
            y = (point.y() // self._charHeight) * self.BYTES_PER_LINE
        elif point.x() > self.ascii_xpos and point.x() < self.ascii_xpos + self.ascii_width - self._charWidth:
            x = ((point.x() - self.ascii_xpos) // self._charWidth)-1
            y = (point.y() // self._charHeight) * self.BYTES_PER_LINE
        else: 
            return -1
      
        return x+y

    def mapPointToLineStartPos(self,point):
        if point.x() > self.addr_xpos and point.x() < self.hex_xpos:
            x = ((point.x() - self.hex_xpos) // self._charWidth)
            y = (point.y() // self._charHeight) * self.BYTES_PER_LINE
        else:
            return -1
      
        return y

    def keyPressEvent(self, e):
        key = e.text()

        if (key >= "0" and key <= "9") or (key >= "a" and key <= "f"):
            if len(self.data) > 0:
                #If there is a block selection active, we need to start the changes
                #from the beginning of the block.
                if self.currentSelection['start'] != self.currentSelection['end']:
                    selectionSize = self.currentSelection['end']-self.currentSelection['start']+1

                    self.selections.add(self.currentSelection['start'], self.currentSelection['end'])
                    self.setCursorVariables(self.currentSelection['start']*2)
                    self.data.replaceWithValue(self.currentSelection['start'], selectionSize, 0x0)
                    self.resetCurrentSelection(self.currentSelection['start'])

                byte = self.data[self._cursorIndexInData]
                #print(f"{byte:02x}")

                if self._cursorHexPosition % 2 == 1:
                    byte = (byte&0xf0) | (int(key,16) & 0xf)
                else:
                    byte = (byte&0xf) | ((int(key,16) & 0xf)<<4)

                #print(f"{byte:02x}")
                self.replaceByte(self._cursorIndexInData, byte)
                self.setCursorVariables(self._cursorHexPosition+1)      

        if e.matches(QtGui.QKeySequence.Delete):
            self.selections.add(self.currentSelection['start'], self.currentSelection['end'])
            if self.currentSelection['start'] != self.currentSelection['end']:                
                selectionSize = self.currentSelection['end']-self.currentSelection['start']+1
                self.data.remove(self.currentSelection['start'], selectionSize)
            else:
                self.data.remove(self.currentSelection['start'], 1)
        
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

            #print(f"line: {lineNum}, cursor: {self._cursorIndexInData}")

            if (
                (self.currentSelection['start']>=address and self.currentSelection['start']<address+self.BYTES_PER_LINE) or
                (self.currentSelection['end']>=address and self.currentSelection['end']<address+self.BYTES_PER_LINE) or
                (address>=self.currentSelection['start'] and address<self.currentSelection['end'])
            ):
                painter.setBackground(QtGui.QBrush(QtGui.QColor(0xff, 0x00, 0x00, 0x80)))
                painter.setBackgroundMode(Qt.OpaqueMode)
            else:
                painter.setBackgroundMode(Qt.TransparentMode)
            
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

                #Painting the current selection with a different color
                if i>=self.currentSelection['start'] and i<=self.currentSelection['end'] and self.currentSelection['start'] != self.currentSelection['end']:
                        painter.setBackground(QtGui.QBrush(QtGui.QColor(0x00, 0xff, 0x00, 0x30)))
                        painter.setBackgroundMode(Qt.OpaqueMode)
                elif self.selections.isSelected(i):
                    painter.setBackground(QtGui.QBrush(QtGui.QColor(0xff, 0x00, 0x00, 0x30)))
                    painter.setBackgroundMode(Qt.OpaqueMode)
                else:
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
        painter.setBackgroundMode(Qt.TransparentMode)
        painter.fillRect(QtCore.QRect(self.ascii_xpos, e.rect().top(), self.ascii_width, self.height()), QtGui.QColor(0xff, 0xfb, 0xd0, 0xff))

        ypos = ((self.firstIndexToPaint) / self.BYTES_PER_LINE) * self._charHeight + self._charHeight
        lineNum = self.firstIndexToPaint

        while lineNum<self.lastIndexToPaint:
            xpos = self.ascii_xpos + self._charWidth

            for i in range(lineNum,lineNum+16):
                ch = self.data[i]

                if ch < 0x20 or (ch > 0x7e and ch < 0xa0) or ch == 0xad:
                    ch = '.'
                else:
                    ch = chr(ch)

                if self.currentSelection['start']<=i and self.currentSelection['end']>=i:
                    painter.setBackground(QtGui.QBrush(QtGui.QColor(0xff, 0x00, 0xff, 0x80)))
                    painter.setBackgroundMode(Qt.OpaqueMode)
                else:
                    painter.setBackgroundMode(Qt.TransparentMode)

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
