# pyGui.pyGui

import sys
import time
import datetime
import socket
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import QSize
from client import socketSend    
from cache import values

class HelloWindow(QMainWindow):
    def __init__(self, host, port):
        QMainWindow.__init__(self)

        self.host = host
        self.port = port
        self.setMinimumSize(QSize(640, 480))    
        self.setWindowTitle("Rover Gui")

        # Grid Layout that widgets are placed on
        gridLayout = QGridLayout(self)     

        # Run Message Thread
        self.msg_thread = receiveMsgThreadClass()
        self.msg_thread.start()

        # Game Table
        self.table 	= QTableWidget(self)
    
        self.table.setWindowTitle("Game Table")
        self.table.resize(400, 175)
        self.table.move(120, 50)
        self.table.setRowCount(3)
        self.table.setColumnCount(2)
        self.table.setColumnWidth(0, 199)
        self.table.setColumnWidth(1, 199)
        self.table.setHorizontalHeaderLabels(['Description', 'Data'])
        self.table.verticalHeader().hide()

        # set items for table
        self.table.setItem(0,0, QTableWidgetItem("Score"))
        self.table.setItem(1,0, QTableWidgetItem("Time Since Start"))
        self.table.setItem(2,0, QTableWidgetItem("Time Since Last Tag"))

        # initial data values
        self.table.setItem(0,1, QTableWidgetItem(str(0)))
        self.table.setItem(1,1, QTableWidgetItem("0:00:00"))
        self.table.setItem(2,1, QTableWidgetItem("0:00:00"))

        gridLayout.addWidget(self.table)

        # Declare threads 
        self.start_thread = startThreadClass()
        self.tag_thread = tagThreadClass()
        self.send_start = sendMsgStartThreadClass(self.host, self.port)
        self.send_pause = sendMsgPauseThreadClass(self.host, self.port)
        self.send_reset = sendMsgResetThreadClass(self.host, self.port)

        # Start Button
        firstButtonPos = 120
        
        self.startButton = QPushButton('Start', self)
        self.startButton.resize(100,32)
        self.startButton.move(firstButtonPos, 320)
        self.startButton.clicked.connect(self.handleStartButton) 
        self.start_thread.signal.connect(self.startFinished)
        self.tag_thread.signal.connect(self.tagFinished)
        gridLayout.addWidget(self.startButton)

        # Reset Button
        self.resetButton = QPushButton('Reset', self)
        self.resetButton.resize(100,32)
        self.resetButton.move(firstButtonPos + 150, 320)
        self.resetButton.clicked.connect(self.handleResetButton)
        self.resetButton.setEnabled(False)
        gridLayout.addWidget(self.resetButton)

        # Pause Button
        self.pauseButton = QPushButton('Pause', self)
        self.pauseButton.resize(100,32)
        self.pauseButton.move(firstButtonPos + 300, 320)
        self.pauseButton.clicked.connect(self.handlePauseButton)
        self.pauseButton.setEnabled(False)
        gridLayout.addWidget(self.pauseButton)

    def handleStartButton(self):
        # start the thread
        self.start_thread.start()
        self.tag_thread.start()
        self.send_start.start()
        values["paused"] = False

        # disable start button and enable pause button
        self.startButton.setEnabled(False)
        self.resetButton.setEnabled(True)
        self.pauseButton.setEnabled(True)


    def handleResetButton(self):
        # First terminate the start thread
        self.start_thread.terminate()
        self.tag_thread.terminate()
        self.send_reset.start()
        values["paused"] = True

        # return to initial data values
        self.table.setItem(0,1, QTableWidgetItem(str(0)))
        self.table.setItem(1,1, QTableWidgetItem("0:00:00"))
        self.table.setItem(2,1, QTableWidgetItem("0:00:00"))
        values["startTime"] = 0
        values["tagTime"] = 0
        values["score"] = 0

        # disable pause button and enable start button
        self.startButton.setEnabled(True)
        self.resetButton.setEnabled(False)
        self.pauseButton.setEnabled(False)

    def handlePauseButton(self):
        # pause the thread
        self.start_thread.terminate()
        self.tag_thread.terminate()
        self.send_pause.start()
        values["paused"] = True

        # disable pause button and enable start button
        self.startButton.setEnabled(True)
        self.pauseButton.setEnabled(False)

    def startFinished(self, result):
        result = str(datetime.timedelta(seconds=result))
        self.table.setItem(1,1, QTableWidgetItem(str(result)))

    def tagFinished(self, result):
        tagTime = str(datetime.timedelta(seconds=result["tagTime"]))
        self.table.setItem(2,1, QTableWidgetItem(str(tagTime)))

        score = str(result["score"])
        self.table.setItem(0, 1, QTableWidgetItem(str(score)))

        # update score
 

class startThreadClass(QtCore.QThread):
    signal = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        while not values["paused"]:
            time.sleep(1)
            values["startTime"] = values["startTime"] + 1
            self.signal.emit(values["startTime"])
 

class tagThreadClass(QtCore.QThread):
    signal = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        while not values["paused"]:
            if values["tagged"]:
                values["tagTime"] = 0
                values["score"] = values["score"] + 1
                values["tagged"] = False
            else:
                time.sleep(1)
                values["tagTime"] = values["tagTime"] + 1
            self.signal.emit({"tagTime": values["tagTime"], "score": values["score"]})

class sendMsgStartThreadClass(QtCore.QThread):
    signal = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self, host, port):
        QtCore.QThread.__init__(self)
        self.host = host
        self.port = port

    def run(self):
        # create dictionary and send through socket
        msg = {
            "type": "SRP",
            "text": "Start Rovers",
            "code": 'S',
        }
        socketSend(msg, self.host, self.port)

class sendMsgPauseThreadClass(QtCore.QThread):
    signal = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self, host, port):
        QtCore.QThread.__init__(self)
        self.host = host
        self.port = port

    def run(self):
        # create dictionary and send through socket
        msg = {
            "type": "SRP",
            "text": "Pause Rovers",
            "code": 'P',
        }
        socketSend(msg, self.host, self.port)

class sendMsgResetThreadClass(QtCore.QThread):
    signal = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self, host, port):
        QtCore.QThread.__init__(self)
        self.host = host
        self.port = port

    def run(self):
        # create dictionary and send through socket
        msg = {
            "type": "SRP",
            "text": "Reset Rovers",
            "code": 'R',
        }
        socketSend(msg, self.host, self.port)

class receiveMsgThreadClass(QtCore.QThread):
    signal = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self):
        QtCore.QThread.__init__(self)
        host = sys.argv[2]
        port = int(sys.argv[4])

    def run(self):
        while 1:
            msg = {
                "type": "Wait",
                "text": "Waiting for rover signal",
                "code": 'W',
            }
            isTagged = socketSend(msg, host, port)
            if isTagged:
                # increment score counter and reset tag time
                values["tagged"] = True


if __name__ == "__main__":
    host = sys.argv[2]
    port = int(sys.argv[4])
    app = QtWidgets.QApplication(sys.argv)
    mainWin = HelloWindow(host, port)
    mainWin.show()
    sys.exit( app.exec_() )