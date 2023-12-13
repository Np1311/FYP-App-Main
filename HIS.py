from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit
from datetime import datetime
import uuid
import os
import sys
import atexit
from django.db import connection
import django
import mysql.connector
import pymysql
import home

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
pymysql.install_as_MySQLdb()

class Ui_MainWindow(object):
    def __init__(self, main_window, username):
        self.main_window = main_window 
        self.username = username

    def setupUi(self, MainWindow):
        bgImage = os.path.join(os.path.dirname(__file__), 'background.png').replace("\\", "/")
        lgImage = os.path.join(os.path.dirname(__file__), 'logo.png').replace("\\", "/")
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1246, 721)

        #Creating of Design
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.Banner = QtWidgets.QFrame(self.centralwidget)
        self.Banner.setGeometry(QtCore.QRect(0, 0, 1251, 80))
        self.Banner.setStyleSheet("background-color: rgb(227, 236, 250);")
        self.Banner.setObjectName("Banner")
        self.Logo = QtWidgets.QLabel(self.Banner)
        self.Logo.setGeometry(QtCore.QRect(0, 10, 110, 61))
        self.Logo.setStyleSheet(f"image: url({lgImage});")
        self.Logo.setText("")
        self.Logo.setObjectName("Logo")
        self.IntelligentHealthInc = QtWidgets.QLabel(self.Banner)
        self.IntelligentHealthInc.setGeometry(QtCore.QRect(90, 5, 161, 71))
        self.IntelligentHealthInc.setStyleSheet("font: 18pt \"MS Shell Dlg 2\"; color: #0000FF")
        self.IntelligentHealthInc.setObjectName("IntelligentHealthInc")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(-20, 80, 1261, 491))
        self.label.setStyleSheet(f"background-image: url({bgImage});")
        self.label.setText("")
        self.label.setObjectName("label")
        
        # Creating of button
        self.Back = QtWidgets.QPushButton(self.Banner)
        self.Back.setGeometry(QtCore.QRect(950, 20, 151, 41))
        self.Back.setStyleSheet("color: navy; font-family: Arial; font-size: 1pt; border: none;")
        self.Back.setObjectName("Back")
        self.Back.setText("Back")
        self.Back.setCursor(Qt.PointingHandCursor)
        self.Back.clicked.connect(self.To_Home)  # Connect the button to your function
        self.addInfoButton = QtWidgets.QPushButton(self.centralwidget)
        self.addInfoButton.setGeometry(QtCore.QRect(980, 110, 93, 28))
        self.addInfoButton.setObjectName("addInfoButton")
        self.addInfoButton.setText("Add Info")
        self.addInfoButton.clicked.connect(self.add_info_to_database)
        self.addInfoButton.clicked.connect(self.switch_for_addinfo)  # Connect the button to your function

        self.searchBar = QLineEdit(self.centralwidget)
        self.searchBar.setGeometry(QtCore.QRect(20, 100, 200, 25))
        self.searchBar.setPlaceholderText("Search...")
        self.searchBar.textChanged.connect(self.filter_table)

        # Add a QTableWidget to the central widget
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(20, 140, 1050, 411))
        self.tableWidget.setObjectName("tableWidget")

        # Connect to the database and fetch data when the application starts
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1246, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.Fetch_HIS()  # Call the method to fetch and display data

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("HIS", "HIS"))
        self.Back.setText(_translate("MainWindow", "Back"))
        self.Back.setStyleSheet("font-family: Arial; font-size: 22px; color: navy; border: none; font-weight: bold")
        self.IntelligentHealthInc.setWhatsThis(_translate("MainWindow", "<html><head/><body><p>Intelligent<br/>Health Inc.</p></body></html>"))
        self.IntelligentHealthInc.setText(_translate("MainWindow", "<html><head/><body><p>INTELLIGENT<br/>HEALTH INC.</p></body></html>"))
        self.IntelligentHealthInc.setStyleSheet("font-weight: bold; padding-top: 5px; color: navy; font-family: Arial; font-size: 22px")
        self.addInfoButton.setText(_translate("MainWindow", "Add Info"))    
        self.addInfoButton.setStyleSheet("font-family: Arial; font-size: 10pt; color: navy;")

    def Fetch_HIS(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM his")
                data = cursor.fetchall()

                # Set the number of rows and columns in the table
                self.tableWidget.setRowCount(len(data))
                self.tableWidget.setColumnCount(len(cursor.description) + 1)  # +1 for the checkbox column

                # Set column headers, including an empty header for the checkbox column
                self.tableWidget.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem(""))
                for i, column_info in enumerate(cursor.description):
                    self.tableWidget.setHorizontalHeaderItem(i + 1, QtWidgets.QTableWidgetItem(column_info[0]))

                # Populate the table with a checkbox and the data
                for row_num, row_data in enumerate(data):
                    checkbox_item = QtWidgets.QTableWidgetItem()
                    checkbox_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    checkbox_item.setCheckState(QtCore.Qt.Unchecked)
                    self.tableWidget.setItem(row_num, 0, checkbox_item)

                    for col_num, cell_value in enumerate(row_data):
                        col_index = col_num + 1
                        item = QtWidgets.QTableWidgetItem(str(cell_value))
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)

                        self.tableWidget.setItem(row_num, col_index, item)


        except Exception as err:
            print(f"Error executing query: {err}")

    def filter_table(self):
        # Get the search query from the search bar and iterate through the rows and show/hide based on the search query
        search_query = self.searchBar.text()
        for row_num in range(self.tableWidget.rowCount()):
            row_hidden = True
            for col_num in range(1, self.tableWidget.columnCount()):
                item = self.tableWidget.item(row_num, col_num)
                if item and search_query.lower() in item.text().lower():
                    row_hidden = False
                    break

            # Set the row visibility based on whether it matches the search query
            self.tableWidget.setRowHidden(row_num, row_hidden)

    def calculate_age(self, date_of_birth):
        # Convert the date_of_birth string to a datetime.date object
        date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        today = datetime.today().date()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        return age
    
    def get_random_doctor_name(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT DoctorName FROM Doctors ORDER BY RAND() LIMIT 1")
            random_doctor_name = cursor.fetchone()
        return random_doctor_name[0] if random_doctor_name else None
    
    def add_info_to_database(self):
        # Get selected rows and their data
        selected_rows = []
        for row_num in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row_num, 0)
            if item and item.checkState() == QtCore.Qt.Checked:
                selected_row_data = [self.tableWidget.item(row_num, col_num).text() for col_num in range(1, self.tableWidget.columnCount())]
                selected_rows.append(selected_row_data)

        if not selected_rows:
            QtWidgets.QMessageBox.information(self.centralwidget, "Information", "No rows selected.")
            return

        try:
            with connection.cursor() as cursor:
                for row_data in selected_rows:
                    unique_record_id = f"CXR{uuid.uuid4().int % 100000:05d}"
                    patient_ID, patient_name, date_of_birth, gender, nationality, area = row_data[0], row_data[1], row_data[2], row_data[3], row_data[10], row_data[7]
                    age = self.calculate_age(date_of_birth)
                    modality, request_time, status = 'CXR', None, 'Registered'
                    docName = self.get_random_doctor_name()
                    indications = 'fever, cough, nausea, shortness of breath, and diarrhea'

                    # Use the unique_record_id in your INSERT statement
                    sql_query = ("INSERT INTO medicaltech_radiologyrecord "
                        "(record_id, patient_name, patient_ID, age, date_of_birth, modality, request_time, status, nationality, area, gender,indications, senderDoctor) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                    cursor.execute(sql_query, (unique_record_id, patient_name, patient_ID, age, date_of_birth, modality, request_time, status, nationality, area, gender, indications, docName))
                connection.commit()
        except mysql.connector.Error as err:
            print(f"Error adding data to the database: {err}")

        QtWidgets.QMessageBox.information(self.centralwidget, "Information", "Selected rows added to the database.")
    
    # Navigate to the Home Page
    def To_Home(self):
        self.main_window.close()
        self.window = QtWidgets.QMainWindow()
        self.ui = home.Ui_MainWindow(self.window,self.username)
        self.ui.setupUi(self.window)
        self.window.show()    
    
    def switch_for_addinfo(self):
        # Check if any rows are selected
        for row_num in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row_num, 0)  # Checkbox is in the first column
            if item and item.checkState() == QtCore.Qt.Checked:
                self.To_Home()
                return  # Exit the function if rows are selected

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    django.setup()

    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    
    atexit.register(lambda: connection.close()) 
    sys.exit(app.exec_())