import os
import sys
import threading
import time
from threading import Thread

import cv2
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QMessageBox
from PyQt5.uic import loadUi

import DecodeImage
import EncodeImage
from GenerateSignature import generateSignature


class MainMenu(QDialog):
    def __init__(self):
        super(MainMenu, self).__init__()
        loadUi("UI Files/MainMenu.ui", self)
        self.setFixedHeight(532)
        self.setFixedWidth(833)
        self.btnEncode.clicked.connect(self.GoToEncodePage)
        self.btnDecode.clicked.connect(self.GoToDecodePage)
        self.btnGenerateSignature.clicked.connect(self.GoToGenerateSignaturePage)

    def GoToEncodePage(self):
        # encodeFilePage = EncodeFile()
        # widget.addWidget(encodeFilePage)
        widget.setFixedWidth(1137)
        widget.setCurrentIndex(1)

    def GoToDecodePage(self):
        widget.setFixedWidth(1137)
        widget.setCurrentIndex(2)
    def GoToGenerateSignaturePage(self):
        widget.setFixedWidth(1137)
        widget.setCurrentIndex(3)


class EncodeFile(QDialog):
    def __init__(self):
        super(EncodeFile, self).__init__()
        loadUi("UI Files/EncodeFilePage.ui", self)

        self.btnCoverImage.clicked.connect(self.loadCoverImage)
        self.btnMessageFile.clicked.connect(self.loadMessageFile)
        self.btnOutputDestination.clicked.connect(self.loadOutputDestination)
        self.btnEncode.clicked.connect(self.thread)
        self.btnBack.clicked.connect(self.backToMainMenu)
        self.progressBar.setMaximum(100)

    def loadCoverImage(self):
        filter = "Images (*.png *.bmp *.jpg)"
        coverImageName = QFileDialog.getOpenFileNames(self, 'Get Cover Image', './', filter=filter)

        if len(coverImageName[0]) != 0:
            self.lnedtCoverImage.setText(coverImageName[0][0])

            image = cv2.imread(self.lnedtCoverImage.text())
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            imageSize = len(image) * len(image[0]) * len(image[0][0])

            maxMessageSize = int(imageSize / 8) -50

            self.labelMaxSize.setText("Maximum Size This Photo Can Carry (bytes): "+str(maxMessageSize))
        else:
            self.labelMaxSize.setText("")

    def loadMessageFile(self):
        filter = "Text files (*.txt)"
        messageFileName = QFileDialog.getOpenFileNames(self, 'Get Message File', './', filter=filter)

        if len(messageFileName[0]) != 0:
            self.lnedtMessageFile.setText(messageFileName[0][0])

    def loadOutputDestination(self):

        # filter = "Images (*.png *.bmp )"
        # outputDestination = QFileDialog.getOpenFileNames(self, 'Set Output Destination', '', filter=filter)
        filter = "Images (*.png *.bmp)"
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Set Output Destination", './', filter=filter)
        if len(filename) != 0:
            self.lnedtOutputDestination.setText(filename)

    # if len(outputDestination[0]) != 0:
    #      self.lnedtOutputDestination.setText(outputDestination[0][0])

    def thread(self):
        self.progressBar.setValue(0)
        self.labelStatus.setText("Not Working")
        if len(self.lnedtCoverImage.text()) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setText("Make sure to select a cover image!")

            msg.setWindowTitle("No Cover Image")

            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            retval = msg.exec_()

        else:
            if len(self.lnedtMessageFile.text()) == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)

                msg.setText("Make sure to select a message File!")

                msg.setWindowTitle("No Message File")

                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

                retval = msg.exec_()
            else:
                if len(self.lnedtOutputDestination.text()) == 0:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)

                    msg.setText("Make sure to select an Output Destination!")

                    msg.setWindowTitle("No Output Destination")

                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

                    retval = msg.exec_()
                else:

                    #Check to see if the text fits in the image
                    image = cv2.imread(self.lnedtCoverImage.text())
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                    imageSize = len(image) * len(image[0]) * len(image[0][0])

                    maxMessageSize = int(imageSize / 8) -50

                    with open(self.lnedtMessageFile.text()) as f:
                        messageContent = f.read()

                    messageContent = messageContent.replace('|', '')


                    messageContentSize = len(messageContent)

                    messageFileName = os.path.basename(f.name)
                    messageSignature = generateSignature(messageContent)

                    messageToHide = messageFileName + "|" + str(
                        messageContentSize) + "|" + messageSignature + "|" + messageContent

                    if len(messageToHide) > maxMessageSize -1 :

                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)

                        msg.setText("The message is too big to hide in this photo.")

                        msg.setWindowTitle("Message Too Big!")

                        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

                        retval = msg.exec_()

                    else:
                        encodeImage = EncodeImage.EncodeImageClass()

                        t1 = Thread(target=self.EncodeThread, daemon=True, kwargs={'encodeImage': encodeImage})
                        t1.start()

                        self.startTheThread(encodeImage)




    def startTheThread(self, encodeImage):
        t = threading.Thread(daemon=True, name='StatusThread', target=myThreadEncoder,
                             args=[self.UpdateStatus, encodeImage])
        t.start()

    def UpdateStatus(self, progress):
        self.progressBar.setValue(progress)
        if progress == 10:
            self.labelStatus.setText("Opened Image")
        else:
            if progress == 15:
                self.labelStatus.setText("Opening Message")
            else:
                if progress == 40:
                    self.labelStatus.setText("Converting image to Binary")
                else:
                    if progress == 60:
                        self.labelStatus.setText("Encoding Message")
                    else:
                        if progress == 80:
                            self.labelStatus.setText("Saving new Image")
                        else:
                            if progress == 100:
                                self.labelStatus.setText("Done")

    def EncodeThread(self, encodeImage):
        encodeImage.EncodeImageMethod(self.lnedtCoverImage.text()
                                      , self.lnedtMessageFile.text()
                                      , self.lnedtOutputDestination.text()
                                      )

    def backToMainMenu(self):
        widget.setFixedWidth(833)
        widget.setCurrentIndex(0)


class Communicate(QObject):
    myGUI_signal = pyqtSignal(int)


def myThreadEncoder(callbackFunc, encodeImage):
    mySrc = Communicate()
    mySrc.myGUI_signal.connect(callbackFunc)

    progress = 0
    while not encodeImage.finished:
        time.sleep(1)
        if progress != encodeImage.progress:
            progress = encodeImage.progress
            mySrc.myGUI_signal.emit(progress)


# https://stackoverflow.com/questions/37252756/simplest-way-for-pyqt-threading
# Source for threading in pyqt5

class DecodeFile(QDialog):
    def __init__(self):
        super(DecodeFile, self).__init__()
        loadUi("UI Files/DecodeFilePage.ui", self)
        self.btnCoverImage.clicked.connect(self.loadCoverImage)
        self.btnOutputDestination.clicked.connect(self.loadOutputDestination)
        self.btnDecode.clicked.connect(self.thread)
        self.btnBack.clicked.connect(self.backToMainMenu)

        self.progressBar.setMaximum(100)

    def loadCoverImage(self):
        filter = "Images (*.png *.bmp *.jpg)"
        coverImageName = QFileDialog.getOpenFileNames(self, 'Get Cover Image', './', filter=filter)

        if len(coverImageName[0]) != 0:
            self.lnedtCoverImage.setText(coverImageName[0][0])

    def loadOutputDestination(self):

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Set Output Destination", './', "Text File (*.txt")
        if len(filename) != 0:
            self.lnedtOutputDestination.setText(filename)

    def thread(self):
        if len(self.lnedtCoverImage.text()) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setText("Make sure to select a cover image!")

            msg.setWindowTitle("No Cover Image")

            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            retval = msg.exec_()

        else:

            if len(self.lnedtOutputDestination.text()) == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)

                msg.setText("Make sure to select an Output Destination!")

                msg.setWindowTitle("No Output Destination")

                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

                retval = msg.exec_()

            else:
                decodeImage = DecodeImage.DecodeImageClass()
                t1 = Thread(target=self.DecodeThread,kwargs={'decodeImage': decodeImage}, daemon=True)
                t1.start()

                self.startTheThread(decodeImage)



    def startTheThread(self, decodeImage):
        t = threading.Thread(daemon=True, name='StatusThread', target=myThreadDecoder,
                             args=[self.UpdateStatus, decodeImage])
        t.start()

    def UpdateStatus(self, decodeImage):
        progress = decodeImage.progress
        self.progressBar.setValue(progress)
        if progress == 10:
            self.labelStatus.setText("Opened Image")
        else:
            if progress == 25:
                self.labelStatus.setText("Located File Information")
            else:
                if progress == 30:
                    self.labelStatus.setText("Converting Information to Binary")
                else:
                    if progress == 50:
                        self.labelStatus.setText("Extracting Message")
                    else:
                        if progress == 60:
                            self.labelStatus.setText("Converting to ASCII")
                        else:
                            if progress == 80:
                                self.labelStatus.setText("Converting to Character")
                            else:
                                if progress == 100:
                                    self.labelStatus.setText("Done")

                                    if decodeImage.success:
                                        msg = QMessageBox()
                                        msg.setIcon(QMessageBox.Information)
                                        msg.setText("Text Extracted Succssfully")
                                        msg.setWindowTitle("Success")

                                        msg.setStandardButtons(QMessageBox.Ok)
                                        retval = msg.exec_()

                                    else:

                                        msg = QMessageBox()
                                        msg.setIcon(QMessageBox.Warning)
                                        msg.setText(decodeImage.reason)
                                        msg.setWindowTitle("Failure :(")

                                        msg.setStandardButtons(QMessageBox.Ok)
                                        retval = msg.exec_()










    def DecodeThread(self, decodeImage):
        decodeImage.DecodeImageMethod(self.lnedtCoverImage.text()
                                      , self.lnedtOutputDestination.text()
                                      )


    def backToMainMenu(self):
        widget.setFixedWidth(833)
        widget.setCurrentIndex(0)


class CommunicateDecoder(QObject):
    myGUI_signal = pyqtSignal(DecodeImage.DecodeImageClass)

def myThreadDecoder(callbackFunc, decodeImage):
    mySrc = CommunicateDecoder()
    mySrc.myGUI_signal.connect(callbackFunc)

    progress = 0
    while not decodeImage.finished:
        time.sleep(1)
        if progress != decodeImage.progress:
            progress = decodeImage.progress
            mySrc.myGUI_signal.emit(decodeImage)



class GenerateSignature(QDialog):
    def __init__(self):
        super(GenerateSignature, self).__init__()
        loadUi("UI Files/GenerateFileSignaturePage.ui", self)
        self.btnFile.clicked.connect(self.loadFile)
        self.btnOutputDestination.clicked.connect(self.loadOutputDestination)
        self.btnGenerate.clicked.connect(self.generate)
        self.btnBack.clicked.connect(self.backToMainMenu)

    def loadFile(self):
        filter = "Text files (*.txt)"
        messageFileName = QFileDialog.getOpenFileNames(self, 'Get Message File', './', filter=filter)

        if len(messageFileName[0]) != 0:
            self.lnedtFile.setText(messageFileName[0][0])

    def loadOutputDestination(self):

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Set Output Destination", './', "Text File (*.txt")
        if len(filename) != 0:
            self.lnedtOutputDestination.setText(filename)

    def generate(self):
        if len(self.lnedtFile.text()) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setText("Make sure to select a text File!")

            msg.setWindowTitle("No Text File")

            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            retval = msg.exec_()

        else:

            with open(self.lnedtFile.text()) as f:
                messageContent = f.read()
            signature = generateSignature(messageContent)

            self.labelSignature.setText("Generates Signature: " + signature)

            if len(self.lnedtOutputDestination.text()) != 0:

                with open(self.lnedtOutputDestination.text(), 'w') as f:
                    f.write(signature)



    def backToMainMenu(self):
        widget.setFixedWidth(833)
        widget.setCurrentIndex(0)




app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()  # Create an instance of QStackedWidget

mainMenuPage = MainMenu()
widget.addWidget(mainMenuPage)  # Add the MainMenu page to the stack
widget.setWindowTitle("Izzat's LSB Steganography")
widget.setWindowIcon(QtGui.QIcon('favicon.png'))

encodePage = EncodeFile()
widget.addWidget(encodePage)

decodePage = DecodeFile()
widget.addWidget(decodePage)

generateSignaturePage = GenerateSignature()
widget.addWidget(generateSignaturePage)

widget.show()
sys.exit(app.exec_())

# If the gui is closed while the encoding proccess is ongoing, the program will throw an exception
# This is intentional. Its purpose is to prevent the threads from continously running once the gui is shut down.
