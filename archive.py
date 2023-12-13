from PyQt5 import QtCore, QtGui, QtWidgets
import os
from PyQt5.QtCore import Qt
import home
import sys
from django.db import connection
import pymysql
from PyQt5.QtWidgets import QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import zipfile

class Ui_MainWindow(object):
    def __init__(self, main_window, username):
            self.main_window = main_window 
            self.username = username
            self.update_successful = False  # Initialize the update_successful flag
    
    def setupUi(self, MainWindow):
        self.main_window = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        bgImage = os.path.join(os.path.dirname(__file__), 'background.png').replace("\\", "/")
        lgImage = os.path.join(os.path.dirname(__file__), 'logo.png').replace("\\", "/")
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1243, 961)
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Creating of Design
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 0, 1241, 851))
        self.label.setStyleSheet(f"background-image: url({bgImage});")
        self.label.setText("")
        self.label.setObjectName("label")
        self.Banner = QtWidgets.QFrame(self.centralwidget)
        self.Banner.setGeometry(QtCore.QRect(0, 0, 1241, 80))
        self.Banner.setStyleSheet("background-color: rgb(227, 236, 250);")
        self.Banner.setObjectName("Banner")
        self.Logo = QtWidgets.QLabel(self.Banner)
        self.Logo.setGeometry(QtCore.QRect(0, 10, 110, 61))
        self.Logo.setStyleSheet(f"image: url({lgImage});")
        self.Logo.setText("")
        self.Logo.setObjectName("Logo")
        self.IntelligentHealthInc = QtWidgets.QLabel(self.Banner)
        self.IntelligentHealthInc.setGeometry(QtCore.QRect(90, 5, 161, 71))
        self.IntelligentHealthInc.setStyleSheet("font-weight: bold; padding-top: 5px; color: navy; font-family: Arial; font-size: 22px")
        self.IntelligentHealthInc.setObjectName("IntelligentHealthInc")
        self.archive = QtWidgets.QLabel(self.centralwidget)
        self.archive.setGeometry(QtCore.QRect(20, 150, 100, 40))  
        self.archive.setStyleSheet("font-weight: bold; color: navy; font-family: Arial; font-size: 18px")  
        self.archive.setText("Archive")

        self.searchBar = QtWidgets.QLineEdit(self.centralwidget)
        self.searchBar.setGeometry(QtCore.QRect(20, 200, 300, 30))  
        self.searchBar.setObjectName("searchBar")
        self.searchBar.textChanged.connect(self.search_table)

        # Creating of Button
        self.backButton = QtWidgets.QPushButton(self.Banner)
        self.backButton.setGeometry(QtCore.QRect(1020, 20, 151, 41))
        self.backButton.setStyleSheet("color: navy; font-family: Arial; font-size: 1pt; border: none;")
        self.backButton.setText("Back")
        self.backButton.setCursor(Qt.PointingHandCursor)
        self.backButton.clicked.connect(self.To_Home)  
        self.selectall = QtWidgets.QPushButton(self.centralwidget)
        self.selectall.setGeometry(QtCore.QRect(20, 250, 161, 28))
        self.selectall.setText("Select all")
        self.selectall.clicked.connect(self.Select_All)  # Connect the button click event
        self.download = QtWidgets.QPushButton(self.centralwidget)
        self.download.setGeometry(QtCore.QRect(10, 700, 161, 28))
        self.download.setText("Download Selected")
        self.download.clicked.connect(self.download_selected_images_as_dicom)  # Connect the button click event
        self.delete = QtWidgets.QPushButton(self.centralwidget)
        self.delete.setGeometry(QtCore.QRect(220, 700, 141, 28))
        self.delete.setText("Delete Selected")
        self.delete.clicked.connect(self.Delete_Selected_Image)
        self.delete.clicked.connect(self.update_to_home)

        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(20, 300, 1200, 380))
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["", "Record ID", "Patient Name", "Patient ID", "Upload Time", "Filename"])
        header = self.tableWidget.horizontalHeader()
        for i in range(self.tableWidget.columnCount()):
            if i == 0:
                header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
                self.tableWidget.setColumnWidth(i, 200)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        MainWindow.setMenuBar(self.menubar)
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.Fetch_Recorded_Image()  # Call the method to fetch and display data

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("Archive", "Archive"))
        self.backButton.setText(_translate("MainWindow", "Back"))
        self.backButton.setStyleSheet("font-family: Arial; font-size: 22px; color: navy; border: none; font-weight: bold")
        self.IntelligentHealthInc.setWhatsThis(_translate("MainWindow", "<html><head/><body><p>Intelligent<br/>Health Inc.</p></body></html>"))
        self.IntelligentHealthInc.setText(_translate("MainWindow", "<html><head/><body><p>INTELLIGENT<br/>HEALTH INC.</p></body></html>"))
        self.IntelligentHealthInc.setStyleSheet("font-weight: bold; padding-top: 5px; color: navy; font-family: Arial; font-size: 22px")
        self.archive.setStyleSheet("font-weight: bold; padding-top: 5px; color: navy; font-family: Arial; font-size: 22px")
    
    def Fetch_Recorded_Image(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT RR.record_id, RR.patient_name, RR.patient_ID, IR.upload_date, IR.image_filename FROM medicaltech_radiologyrecord RR JOIN medicaltech_image_record IR on RR.record_id = IR.record_id_id where IR.image is not null")
                result = cursor.fetchall()
                self.tableWidget.setRowCount(len(result))
                for row_num, row_data in enumerate(result):
                    checkbox_item = QtWidgets.QTableWidgetItem()
                    checkbox_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    checkbox_item.setCheckState(QtCore.Qt.Unchecked)
                    self.tableWidget.setItem(row_num, 0, checkbox_item)

                    for col_num, cell_value in enumerate(row_data):
                        col_index = col_num + 1
                        item = QtWidgets.QTableWidgetItem(str(cell_value))
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                        self.tableWidget.setItem(row_num, col_index, item)

        except pymysql.Error as err:
            print(f"Error: {err}")

    def Select_All(self):
        first_checkbox_item = self.tableWidget.item(0, 0)  # Get the checkbox in the first row

        if first_checkbox_item and first_checkbox_item.checkState() == QtCore.Qt.Checked:
            # If the first checkbox is checked, uncheck all rows
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 0)
                if item:
                    item.setCheckState(QtCore.Qt.Unchecked)
        else:
            # If the first checkbox is unchecked, check all rows
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 0)
                if item:
                    item.setCheckState(QtCore.Qt.Checked)
  
    
    def Delete_Selected_Image(self):
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
                    record_id = row_data[0]
                    image = None

                    # Update the patient record to Null 
                    sql_query = ("Update medicaltech_image_record SET image = %s WHERE record_id_id = %s")
                    cursor.execute(sql_query, (image, record_id))
                connection.commit()
                self.update_successful = True

        except pymysql.Error as err:
            print(f"Error: {err}")

        QtWidgets.QMessageBox.information(self.centralwidget, "Information", "Selected rows image deleted from the database.")

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
    
    def download_selected_images_as_dicom(self):
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
            # Prompt the user to select a save location for the zip file
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            save_path, _ = QFileDialog.getSaveFileName(self.centralwidget, "Save Zip File", "", "Zip Files (*.zip);;All Files (*)", options=options)

            if save_path:
                # Ensure the file has a .zip extension
                if not save_path.endswith(".zip"):
                    save_path += ".zip"

                # Create a zip file at the user-selected location
                with zipfile.ZipFile(save_path, 'w') as zipf:
                    for row_data in selected_rows:
                        record_id = row_data[0]

                        with connection.cursor() as cursor:
                            sql_query = "SELECT image FROM medicaltech_image_record WHERE record_id_id = %s"
                            cursor.execute(sql_query, (record_id,))
                            dicom_data = cursor.fetchone()

                            # Save the DICOM data to a file
                            output_file_path = f"{record_id}.dcm"  # Customize the file name as needed
                            with open(output_file_path, "wb") as file:
                                file.write(dicom_data[0])

                            # Add the file to the zip archive
                            zipf.write(output_file_path, os.path.basename(output_file_path))

                            # Remove the individual DICOM file if you no longer need it
                            os.remove(output_file_path)

                QtWidgets.QMessageBox.information(self.centralwidget, "Information", f"DICOM files saved in {save_path}")
            else:
                QtWidgets.QMessageBox.warning(self.centralwidget, "Information", "No save location selected.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self.centralwidget, "Error", f"An error occurred: {str(e)}")

    def To_Home(self):
        self.main_window.close()
        self.window = QtWidgets.QMainWindow()
        self.ui = home.Ui_MainWindow(self.window,self.username)
        self.ui.setupUi(self.window)
        self.window.show() 

    def update_to_home(self):
            if not self.update_successful:  # Check if the update was successful
                    return
            self.To_Home()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())