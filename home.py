from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QCalendarWidget, QTimeEdit, QComboBox, QPushButton
import os
import sys
import atexit
import pymysql
from datetime import datetime
import sqlite3
import socket
import django
from django.db import connection
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
pymysql.install_as_MySQLdb()

from SQLSetting import SQLSettings 
import login
from HIS import Ui_MainWindow as HISWindow 
from patientrecord import Ui_MainWindow as PRWindow
from archive import Ui_MainWindow as ArchiveWindow 

class Ui_MainWindow(object):
    def __init__(self, main_window, username):
        self.main_window = main_window 
        self.username = username

    def setupUi(self, MainWindow):
        bgImage = os.path.join(os.path.dirname(__file__), 'background.png').replace("\\", "/")
        lgImage = os.path.join(os.path.dirname(__file__), 'logo.png').replace("\\", "/")
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1246, 716)
        
        # Creating of Designs
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
        self.IntelligentHealthInc.setGeometry(QtCore.QRect(90, 10, 161, 71))
        self.IntelligentHealthInc.setStyleSheet("font: 18pt \"MS Shell Dlg 2\"; color: #0000FF")
        self.IntelligentHealthInc.setObjectName("IntelligentHealthInc")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(-10, 80, 1261, 491))
        self.label.setStyleSheet(f"background-image: url(\"{bgImage}\");")
        self.label.setText("")
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Create the respective buttons
        self.logoutButton = QtWidgets.QPushButton(self.Banner)
        self.logoutButton.setGeometry(QtCore.QRect(1070, 20, 151, 41))
        self.logoutButton.setStyleSheet("color: navy; font-family: Arial; font-size: 1pt; border: none;")
        self.logoutButton.setText("Logout")
        self.logoutButton.setCursor(Qt.PointingHandCursor)
        self.logoutButton.clicked.connect(self.logout)        
        self.fetchDataButton = QtWidgets.QPushButton(self.centralwidget)
        self.fetchDataButton.setGeometry(QtCore.QRect(10, 590, 131, 41))
        self.fetchDataButton.setText("Fetch Data")
        self.fetchDataButton.setStyleSheet("font-family: Arial; font-size: 14pt; color: navy;")
        self.fetchDataButton.clicked.connect(self.Fetch_RadiologyRecord)
        self.HISbutton = QtWidgets.QPushButton(self.centralwidget)
        self.HISbutton.setGeometry(QtCore.QRect(1100, 95, 93, 36))
        self.HISbutton.setObjectName("pushButton")
        self.HISbutton.clicked.connect(self.To_HIS)
        self.archiveButton = QtWidgets.QPushButton(self.centralwidget)
        self.archiveButton.setGeometry(QtCore.QRect(1000, 95, 93, 36))
        self.archiveButton.setObjectName("archiveButton")
        self.archiveButton.setText("Archive")
        self.archiveButton.clicked.connect(self.To_Archive)

        # Create a search bar (QLineEdit)
        self.searchBar = QtWidgets.QLineEdit(self.centralwidget)
        self.searchBar.setGeometry(QtCore.QRect(10, 100, 250, 30))
        self.searchBar.setPlaceholderText("Search...")
        self.searchBar.textChanged.connect(self.search_table)

        # Create a QTableWidget to display the database data
        self.tableWidget = QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(10, 150, 1226, 400))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(11)
        self.tableWidget.setHorizontalHeaderLabels(["Record ID", "Patient Name", "Patient ID", "Age", "Date of Birth", "Modality", "Request Time", "Sender", "Indications", "Status", "Emergency"])
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.cellClicked.connect(self.on_cell_click)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1246, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("Home", "Home"))
        self.IntelligentHealthInc.setWhatsThis(_translate("MainWindow", "<html><head/><body><p>Intelligent<br/>Health Inc.</p></body></html>"))
        self.IntelligentHealthInc.setText(_translate("MainWindow", "<html><head/><body><p>INTELLIGENT<br/>HEALTH INC.</p></body></html>"))
        self.IntelligentHealthInc.setStyleSheet("font-weight: bold; padding-top: 5px; color: navy; font-family: Arial; font-size: 22px")
        self.logoutButton.setText(_translate("MainWindow", "Logout"))
        self.logoutButton.setStyleSheet("font-family: Arial; font-size: 22px; color: navy; border: none; font-weight: bold")
        self.HISbutton.setText(_translate("MainWindow", "To HIS"))
        self.HISbutton.setStyleSheet("font-family: Arial; font-size: 14pt; color: navy;")
        self.archiveButton.setText(_translate("MainWindow", "Archive"))
        self.archiveButton.setStyleSheet("font-family: Arial; font-size: 14pt; color: navy;")

    # Fetching and displaying the table from the database
    def getUpdateTime(self):
        currentDatetime = datetime.now()
        updateTime = currentDatetime.strftime("%Y-%m-%d %H:%M:%S")
        return updateTime
    
    def Fetch_RadiologyRecord(self):
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT RR.record_id, RR.patient_name, RR.patient_ID, RR.age, RR.date_of_birth, RR.modality, RR.request_time, RR.senderDoctor, RR.indications, RR.status FROM medicaltech_radiologyrecord RR")
                    result = cursor.fetchall()

                    status_order = {"EMERGENCY": 0, "Registered": 2, "Queueing": 1, "In Progress": 3, "Completed": 4}
                    result = sorted(result, key=lambda row_data: status_order.get(row_data[9], 5))
                    self.tableWidget.setRowCount(len(result))
                    unique_statuses = ["Registered", "Queueing", "In Progress", "Completed", "EMERGENCY"]

                    for row_index, row_data in enumerate(result):
                        for col_index, cell_data in enumerate(row_data):
                            cell_data = "" if cell_data is None else str(cell_data)
                            item = QTableWidgetItem(str(cell_data))
                            self.tableWidget.setItem(row_index, col_index, item)

                        status_item = self.tableWidget.item(row_index, 9)
                        if status_item:
                            current_status = status_item.text()
                            if current_status in unique_statuses:
                                self.Status_DropdownList(row_index, current_status)

            except pymysql.Error as err:
                print(f"Error: {err}")  

    def Status_DropdownList(self, row_index, current_status):
        # Create the status combobox
        unique_statuses = ["Registered", "Queueing", "In Progress", "Completed", "EMERGENCY"]
        status_combobox = QComboBox()
        status_combobox.addItems(unique_statuses)
        status_combobox.model().item(unique_statuses.index("EMERGENCY")).setEnabled(False)

        index = status_combobox.findText(current_status)
        if index >= 0:
            status_combobox.setCurrentIndex(index)
            self.tableWidget.setCellWidget(row_index, 9, status_combobox)

            # Hide the button when the status is "Completed" or "In Progress"
            button = QPushButton()
            if current_status in ["Completed", "In Progress"]:
                button.setEnabled(False)
            else:
                button_label = "Cancel Emergency" if current_status == "EMERGENCY" else "EMERGENCY"
                button.setText(button_label)

            self.tableWidget.setCellWidget(row_index, 10, button)
            status_combobox.currentIndexChanged.connect(lambda _, row=row_index, button=button: self.update_dropdown_status(row, button))
            button.clicked.connect(lambda _, row=row_index: self.on_emergency_button_click(row))

    def update_dropdown_status(self, row, button):
        record_id = self.tableWidget.item(row, 0).text()
        combobox = self.tableWidget.cellWidget(row, 9)
        if combobox.currentText() == "EMERGENCY":
            button.setVisible(True)
            button.setEnabled(True)
            button.setText("Cancel Emergency")
        elif combobox.currentText() in ("Registered", "Queueing"):
            button.setVisible(True)
            button.setEnabled(True)
            button.setText("EMERGENCY")
        else:
            button.setVisible(False)
        try:
            updateTime = self.getUpdateTime()
            with connection.cursor() as cursor:
                sql_query = "UPDATE medicaltech_radiologyrecord SET status = %s , update_time = %s WHERE record_id = %s"
                cursor.execute(sql_query, (combobox.currentText(), updateTime, record_id))
            connection.commit()
        except pymysql.Error as err:
            print(f"Error: {err}")

    def on_emergency_button_click(self, row):
        record_id = self.tableWidget.item(row, 0).text()
        current_status = self.tableWidget.cellWidget(row, 9).currentText()
        try:
            updateTime = self.getUpdateTime()
            with connection.cursor() as cursor:
                if current_status == "EMERGENCY":
                    sql_query = "UPDATE medicaltech_radiologyrecord SET status='Registered' , update_time=%s WHERE record_id=%s"
                    new_status = "Registered"
                else:
                    sql_query = "UPDATE medicaltech_radiologyrecord SET status='EMERGENCY' , update_time=%s WHERE record_id=%s"
                    new_status = "EMERGENCY"
                cursor.execute(sql_query, (updateTime,record_id))
                connection.commit()
                
                # Update the status in the dropdown
                combobox = self.tableWidget.cellWidget(row, 9)
                index = combobox.findText(new_status)
                if index >= 0:
                    combobox.setCurrentIndex(index)

                # Update the button text
                button = self.tableWidget.cellWidget(row, 10)
                if button and isinstance(button, QtWidgets.QPushButton):
                    button.setText("Cancel Emergency" if new_status == "EMERGENCY" else "EMERGENCY")
        except pymysql.Error as err:
            print(f"Error: {err}")

    def search_table(self):
        search_query = self.searchBar.text().strip().lower()
        for row in range(self.tableWidget.rowCount()):
            match = False
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item and search_query in item.text().strip().lower():
                    match = True
                    break
            self.tableWidget.setRowHidden(row, not match)

    def on_cell_click(self, row, column):
        item = self.tableWidget.item(row, column)
        if item and column == 6:
            selected_date = QDateTime.fromString(item.text(), "yyyy-MM-dd hh:mm:ss")
            
            dialog = QtWidgets.QDialog(self.centralwidget)
            dialog.setWindowTitle("Select Request Time")
            dialog.setLayout(QtWidgets.QVBoxLayout())
            
            calendar_widget = QCalendarWidget()
            calendar_widget.setSelectedDate(selected_date.date())
            
            time_widget = QTimeEdit()
            time_widget.setDisplayFormat("hh:mm:ss")
            time_widget.setTime(selected_date.time())
            
            dialog.layout().addWidget(calendar_widget)
            dialog.layout().addWidget(time_widget)
            
            ok_button = QtWidgets.QPushButton("OK")
            ok_button.clicked.connect(lambda: item.setText(QDateTime(calendar_widget.selectedDate(), time_widget.time()).toString("yyyy-MM-dd hh:mm:ss")))
            ok_button.clicked.connect(dialog.accept)
            dialog.layout().addWidget(ok_button)
            
            if dialog.exec_():
                selected_date = QDateTime(calendar_widget.selectedDate(), time_widget.time())
                self.update_request_time(row, item, selected_date)
        else:
            record_id, patient_name, patient_id, age, dob, modality, request_time, sender_doc, indication = [self.tableWidget.item(row, i).text() for i in range(9)]
            self.To_PatientRecord(record_id, patient_name, patient_id, age, dob, modality, request_time, sender_doc, indication, self.username)

    def update_request_time(self, row, item, selected_date):
        # Format the selected date as a string and update QTableWidgetItem in the table widget
        formatted_date = selected_date.toString("yyyy-MM-dd hh:mm:ss")
        item.setText(formatted_date)

        # Get the record ID from the clicked row to update the correct row
        record_id = self.tableWidget.item(row, 0).text()
        try:
            updateTime = self.getUpdateTime()
            with connection.cursor() as cursor:
                sql_query = "UPDATE medicaltech_radiologyrecord SET request_time = %s, update_time = %s WHERE record_id = %s"
                cursor.execute(sql_query, (formatted_date, updateTime, record_id))
            connection.commit()
        except pymysql.Error as err:
            print(f"Error: {err}")
    
    # Navigate to the other page
    def To_HIS(self):
        self.main_window.close()
        self.window = QtWidgets.QMainWindow()
        self.his_page = HISWindow(self.window,self.username)
        self.his_page.setupUi(self.window)
        self.window.show()  # Show the HIS page

    def To_PatientRecord(self, record_id, patient_name, patient_id, age, dob, modality, request_time, sender_doc, indication, username):
        self.main_window.close()
        self.window = QtWidgets.QMainWindow()
        self.PR_page = PRWindow(self.window, record_id, patient_name, patient_id, age, dob, modality, request_time, sender_doc, indication, username)  # Create an instance of the HIS page class
        self.PR_page.setupUi(self.window)
        self.window.show()  # Show the Patient Record page

    def To_Archive(self):
        self.main_window.close()
        self.window = QtWidgets.QMainWindow()
        self.archive_page = ArchiveWindow(self.window, self.username)
        self.archive_page.setupUi(self.window)
        self.window.show()  # Show the Archive page

    def logout(self):
        self.main_window.close()
        self.window = QtWidgets.QMainWindow()
        self.ui = login.Ui_MainWindow(self.window)
        self.ui.setupUi(self.window)
        self.window.show() # Show the Logout Page
        # Set the DJANGO_SETTINGS_MODULE and load Django
        migrationData = SQLSettings()

        if migrationData.checkIntenetStatus():
            print(migrationData.checkIntenetStatus())
            
            try: 
                
                migrationData.migrateRadiologyRecord('MYSQL')
                migrationData.migrateRadiologyRecord('sqlite')
                migrationData.migrateImageRecord('MYSQL')
                migrationData.migrateImageRecord('sqlite')
                migrationData.migrateAuth_user('MYSQL')
                migrationData.migrateProfile('MYSQL')
            
                # migrationData.migrateImageRecord()
                
            except Exception as e:
                print(e)
                
        
        else:
            print("intenet not found")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    django.setup()

    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(MainWindow)
    ui.setupUi(MainWindow)
    MainWindow.show()

    atexit.register(lambda: connection.close())
    sys.exit(app.exec_())
