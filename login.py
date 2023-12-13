from PyQt5 import QtCore, QtGui, QtWidgets
import mysql.connector
import sys
from django.contrib.auth import authenticate, login
import os
import django
from django.conf import settings
from django.contrib import messages
from mysql.connector.locales.eng import client_error
import atexit
import pymysql

# Set the DJANGO_SETTINGS_MODULE
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.db import connection
from home import Ui_MainWindow as HomeWindow

class Ui_MainWindow(object):
    def __init__(self, main_window):
        self.main_window = main_window  # Store a reference to the MainWindow

    def setupUi(self, MainWindow):
        bgImage = os.path.join(os.path.dirname(__file__), 'background.png').replace("\\", "/")
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(492, 576)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.IntelligentHealthInc = QtWidgets.QLabel()
        self.IntelligentHealthInc.setGeometry(QtCore.QRect(90, 5, 161, 71))
        self.IntelligentHealthInc.setStyleSheet("font: 18pt \"MS Shell Dlg 2\"; color: #0000FF")
        self.IntelligentHealthInc.setObjectName("IntelligentHealthInc")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(0, 0, 491, 541))
        self.frame.setStyleSheet(f"background-image: url({bgImage});")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        
        # Creating of the login page and button
        self.Login = QtWidgets.QLabel(self.frame)
        self.Login.setGeometry(QtCore.QRect(220, 60, 141, 71))
        self.Login.setObjectName("Login")
        self.label_username = QtWidgets.QLabel(self.frame)
        self.label_username.setGeometry(QtCore.QRect(142, 190, 211, 16))
        self.label_username.setObjectName("label_username")
        self.label_username.setText("Username")
        self.Username = QtWidgets.QLineEdit(self.frame)
        self.Username.setGeometry(QtCore.QRect(142, 215, 211, 22))
        self.Username.setObjectName("Username")
        self.label_password = QtWidgets.QLabel(self.frame)
        self.label_password.setGeometry(QtCore.QRect(142, 255, 211, 16))
        self.label_password.setObjectName("label_password")
        self.label_password.setText("Password")
        self.Password = QtWidgets.QLineEdit(self.frame)
        self.Password.setGeometry(QtCore.QRect(142, 280, 211, 22))
        self.Password.setObjectName("Password")
        self.Password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.submitButton = QtWidgets.QPushButton(self.frame)
        self.submitButton.setGeometry(QtCore.QRect(110, 350, 271, 35))
        self.submitButton.clicked.connect(self.authenticate_user)  # Connect to the authenticate_user method
        self.submitButton.setObjectName("submitButton")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 492, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("Login", "Login"))
        self.IntelligentHealthInc.setWhatsThis(_translate("MainWindow", "<html><head/><body><p>Intelligent<br/>Health Inc.</p></body></html>"))
        self.IntelligentHealthInc.setText(_translate("MainWindow", "<html><head/><body><p>INTELLIGENT<br/>HEALTH INC.</p></body></html>"))
        self.IntelligentHealthInc.setStyleSheet("font-weight: bold; padding-top: 5px; color: navy; font-family: Arial; font-size: 22px")
        self.Login.setText(_translate("MainWindow", "Login "))
        self.Login.setStyleSheet("font-family: Arial; font-size: 22px; color: navy; border: none; font-weight: bold")
        self.label_username.setStyleSheet("font-family: Arial; font-size: 14pt; color: navy;")
        self.label_password.setStyleSheet("font-family: Arial; font-size: 14pt; color: navy;")
        self.submitButton.setText(_translate("MainWindow", "Login"))
        self.submitButton.setStyleSheet("font-family: Arial; font-size: 14pt; color: navy; background-color: #44AEE7;")

    def authenticate_user(self):
        try:
            # Get the entered username and password from the QLineEdit widgets
            username = self.Username.text()
            password = self.Password.text()

            # Use Django's authenticate function to verify the credentials
            user = authenticate(username=username, password=password)
            if user is not None:
                cursor = connection.cursor()
                cursor.execute("SELECT auth_user.id, auth_user.username, auth_user.password, systemadmin_profile.role FROM auth_user join systemadmin_profile on auth_user.id = systemadmin_profile.account_id WHERE auth_user.username = %s;", (username,))
                data = cursor.fetchone()

                user_role = data[3]
                if user_role == 'medicalTech':
                    # Close the current window (MainWindow) and launch Home.py
                    self.main_window.close()
                    self.window = QtWidgets.QMainWindow()
                    self.ui = HomeWindow(self.window, username)
                    self.ui.setupUi(self.window)
                    self.window.show()    
                else:
                    self.show_warning("You don't have the required role.")
            else:
                self.show_warning("Invalid Credential.")

        except mysql.connector.Error as err:
            print(f"Database Error: {err}")
        except Exception as e:
            print(f"Error: {e}")
    
    def show_warning(self, message):
        QtWidgets.QMessageBox.warning(self.centralwidget, "Authentication Error", message)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    django.setup()

    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(MainWindow)
    ui.setupUi(MainWindow)
    MainWindow.show()

    atexit.register(lambda: connection.close())
    sys.exit(app.exec_())