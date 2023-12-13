from PyQt5 import QtWidgets, QtCore

class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(QtCore.QRect(100, 300, 400, 100))

        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setGeometry(QtCore.QRect(110, 350, 271, 35))
        self.pushButton.clicked.connect(self.authenticate_user)  # Connect to the authenticate_user method
        self.pushButton.setObjectName("pushButton")

        layout.addWidget(self.frame)
        self.setLayout(layout)

    def authenticate_user(self):
        print("Button clicked!")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.authenticate_user()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()