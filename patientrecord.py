import sys
import os
import pydicom
import numpy as np
from keras.models import load_model
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtWidgets import QFileDialog, QApplication, QMessageBox
import mysql.connector
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import atexit
from django.db import connection
import django
import home
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QDesktopWidget, QWidget
from PyQt5.QtWidgets import QScrollArea
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

class Ui_MainWindow(object):
        dicom_binary = None
        def __init__(self, main_window, record_id,patient_name, patient_id, age, dob, modality, request_time, sender_doc, indication, username):
                # Store the passed patient information
                self.record_id = record_id
                self.patient_name = patient_name
                self.patient_id = patient_id
                self.age = age
                self.dob = dob
                self.modality = modality
                self.request_time = request_time
                self.sender_doc = sender_doc
                self.indications = indication
                self.update_successful = False  # Initialize the update_successful flag
                self.main_window = main_window 
                self.username = username

        def setupUi(self, MainWindow):
                backgroundImage = os.path.join(os.path.dirname(__file__), 'background.png').replace("\\", "/")
                logoImage = os.path.join(os.path.dirname(__file__), 'logo.png').replace("\\", "/")
                iconImage = os.path.join(os.path.dirname(__file__), 'file_upload_icon.png').replace("\\", "/")
                # Obtain the screen dimensions
                desktop = QApplication.desktop()
                screen_rect = desktop.screenGeometry()
                screen_height = screen_rect.height()
                screen_width = screen_rect.width()

                 # Calculate scaling factors for different elements based on the screen resolution
                button_width = int(screen_width * 0.12)  # 12% of screen width
                button_height = int(screen_height * 0.04)  # 4% of screen height
                banner_height = int(screen_height * 0.1)  # 10% of screen height
                label_font_size = int(screen_width * 0.014)


                MainWindow.setObjectName("MainWindow")
                MainWindow.resize(1243, 961)
                self.centralwidget = QtWidgets.QWidget(MainWindow)
                self.centralwidget.setObjectName("centralwidget")
                palette = QtGui.QPalette()
                background_image = QtGui.QPixmap(backgroundImage)
                background_image = background_image.scaled(screen_width, screen_height)
                palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(background_image))
                MainWindow.setPalette(palette)

                self.label = QtWidgets.QLabel(self.centralwidget)
                self.label.setGeometry(QtCore.QRect(0, 0, screen_width, screen_height))
                self.label.setStyleSheet(f"background-image: url({backgroundImage}); background-repeat: no-repeat; background-position: center;")
                self.label.setText("")
                self.label.setObjectName("label")
                self.Banner = QtWidgets.QFrame(self.centralwidget)
                self.Banner.setGeometry(QtCore.QRect(0, 0, screen_width, banner_height))
                self.Banner.setStyleSheet("background-color: rgb(227, 236, 250);")
                self.Banner.setObjectName("Banner")
                # Add these lines to the `setupUi` method in `patientrecord.py`
                self.backButton = QtWidgets.QPushButton(self.Banner)
                self.backButton.setGeometry(QtCore.QRect(screen_width - 20 - button_width, 20, button_width, button_height))
                self.backButton.setStyleSheet(f"color: navy; font-family: Arial; font-size: {label_font_size}; border: none;")
                self.backButton.setText("Back")
                self.backButton.setCursor(Qt.PointingHandCursor)
                self.backButton.clicked.connect(self.To_Home)  # Connect the button click event to go_back method
                self.backButton.show()
                MainWindow.setWindowState(Qt.WindowMaximized)

                self.Logo = QtWidgets.QLabel(self.Banner)
                self.Logo.setGeometry(QtCore.QRect(0, 10, 110, 61))
                self.Logo.setStyleSheet(f"image: url({logoImage});")      
                self.Logo.setText("")
                self.Logo.setObjectName("Logo")
                self.IntelligentHealthInc = QtWidgets.QLabel(self.Banner)
                self.IntelligentHealthInc.setGeometry(QtCore.QRect(90, 5, 161, 71))
                self.IntelligentHealthInc.setStyleSheet("font-weight: bold; padding-top: 5px; color: navy; font-family: Arial; font-size: 22px")
                self.IntelligentHealthInc.setObjectName("IntelligentHealthInc")

                #Patient Info
                self.patientInfoContainer = QtWidgets.QGroupBox(self.centralwidget)
                self.patientInfoContainer.setGeometry(QtCore.QRect(140, 120, 500, 260))
                self.patientInfoContainer.setStyleSheet("background-color: rgb(227, 236, 250);")
                self.patientInfoContainer.setObjectName("patientInfoContainer")
                self.patinetInfo = QtWidgets.QGridLayout(self.patientInfoContainer)
                self.patinetInfo.setObjectName("patinetInfo")
                self.RecordID = QtWidgets.QLabel(self.patientInfoContainer)
                self.RecordID.setObjectName("RecordID")
                self.patinetInfo.addWidget(self.RecordID, 0, 0, 1, 1)

                self.PatientID = QtWidgets.QLabel(self.patientInfoContainer)
                self.PatientID.setObjectName("PatientID")
                self.patinetInfo.addWidget(self.PatientID, 1, 0, 1, 1)

                self.DateofBirth = QtWidgets.QLabel(self.patientInfoContainer)
                self.DateofBirth.setObjectName("DateofBirth")
                self.patinetInfo.addWidget(self.DateofBirth, 2, 0, 1, 1)
        
                self.Gender = QtWidgets.QLabel(self.patientInfoContainer)
                self.Gender.setObjectName("Gender")
                self.patinetInfo.addWidget(self.Gender, 3, 0, 1, 1)

                self.PatientName = QtWidgets.QLabel(self.patientInfoContainer)
                self.PatientName.setObjectName("Name")
                self.patinetInfo.addWidget(self.PatientName, 0, 1, 1, 1)
                
                self.Age = QtWidgets.QLabel(self.patientInfoContainer)
                self.Age.setObjectName("Age")
                self.patinetInfo.addWidget(self.Age, 1, 1, 1, 1)

                self.Modality = QtWidgets.QLabel(self.patientInfoContainer)
                self.Modality.setObjectName("Modality")
                self.patinetInfo.addWidget(self.Modality, 2, 1, 1, 1)

                self.SenderDoctor = QtWidgets.QLabel(self.patientInfoContainer)
                self.SenderDoctor.setObjectName("Sender Doctor:")
                self.patinetInfo.addWidget(self.SenderDoctor, 3, 1, 1, 1)

                #image contatiner
                self.imageContainer = QtWidgets.QGroupBox(self.centralwidget)
                self.imageContainer.setGeometry(QtCore.QRect(40, 435, 700, 400))
                self.imageContainer.setStyleSheet("background-color: rgb(227, 236, 250);")
                self.imageContainer.setObjectName("imageContainer")
                # self.gridLayout_2 = QtWidgets.QGridLayout(self.imageContainer)
                # self.gridLayout_2.setObjectName("gridLayout_2")
                 
                self.uploadedLabel = QtWidgets.QLabel(self.imageContainer)
                self.uploadedLabel.setGeometry(QtCore.QRect(40, 50, 325, 325))
                self.uploadedLabel.setObjectName("uploadedLabel")
                self.uploadedLabel.setScaledContents(True)
                self.predictionLabel = QtWidgets.QLabel(self.imageContainer)
                self.predictionLabel.setGeometry(QtCore.QRect(500, 160, 300, 40))
                self.predictionLabel.setObjectName("predictionLabel")
                

                # Create filenameContainer to display the filename
                self.filenameContainer = QtWidgets.QGroupBox(self.centralwidget)
                self.filenameContainer.setGeometry(QtCore.QRect(40, 400, 700, 60))
                self.filenameContainer.setStyleSheet("background-color: rgb(227, 236, 250);")
                self.filenameContainer.setObjectName("filenameContainer")
                self.FilenameLabel = QtWidgets.QLabel(self.filenameContainer)
                self.FilenameLabel.setObjectName("FilenameLabel")
                self.FilenameLabel.setText("Filename: ") 
                self.FilenameLabel.setStyleSheet("padding-left: 5px;") # Set the initial text or leave it empty
                self.gridLayout_4 = QtWidgets.QGridLayout(self.filenameContainer)
                self.gridLayout_4.setObjectName("gridLayout_4")
                self.gridLayout_4.addWidget(self.FilenameLabel, 0, 0, 1, 1)
                self.uploadButton = QtWidgets.QPushButton(self.filenameContainer)
                self.uploadButton.setIconSize(QtCore.QSize(25, 35)) 
                self.uploadButton.setGeometry(QtCore.QRect(620, 20, 20, 20))
                self.uploadButton.setObjectName("uploadButton")
                self.uploadButton.setIcon(QIcon(iconImage))
                self.uploadButton.setStyleSheet("border: none;")
                self.uploadButton.clicked.connect(self.uploadDICOM) # Connect the button click event to the uploadDICOM method
                
                #upcomingAppointmentContainer
                self.upcomingAppointmentContainer = QtWidgets.QTableView(self.centralwidget)
                self.upcomingAppointmentContainer.setGeometry(QtCore.QRect(800, 120, 530, 260))
                self.upcomingAppointmentContainer.setStyleSheet("background-color: rgb(227, 236, 250);")
                self.upcomingAppointmentContainer.setObjectName("upcomingAppointmentContainer")
                self.UpcomingAppointment = QtWidgets.QLabel(self.centralwidget)
                self.UpcomingAppointment.setGeometry(QtCore.QRect(810, 130, 180, 16))
                self.UpcomingAppointment.setObjectName("UpcomingAppointment")
                self.RequestTime = QtWidgets.QLabel(self.centralwidget)
                self.RequestTime.setGeometry(QtCore.QRect(810, 190, 110, 16))
                self.RequestTime.setObjectName("RequestTime")
                self.RequestTime.setFixedWidth(400)
                self.Indications = QtWidgets.QLabel(self.centralwidget)
                self.Indications.setGeometry(QtCore.QRect(810, 270, 300, 16))
                self.Indications.setObjectName("Indications")
                self.Indications.setFixedWidth(400)

                #notesContainer
                self.notesContainer = QtWidgets.QTableWidget(self.centralwidget)
                self.notesContainer.setGeometry(QtCore.QRect(800, 400, 530, 370))
                self.notesContainer.setStyleSheet("background-color: rgb(227, 236, 250);")
                self.notesContainer.setObjectName("notesContainer")
                self.notesContainer.setColumnCount(0)
                self.notesContainer.setRowCount(0)
                self.Notes = QtWidgets.QLabel(self.centralwidget)
                self.Notes.setGeometry(QtCore.QRect(820, 395, 55, 50))
                self.Notes.setObjectName("Notes")
                self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
                self.plainTextEdit.setGeometry(QtCore.QRect(825, 440, 480, 300))
                self.plainTextEdit.setObjectName("plainTextEdit")
                MainWindow.setCentralWidget(self.centralwidget)
                
                self.menubar = QtWidgets.QMenuBar(MainWindow)
                self.menubar.setGeometry(QtCore.QRect(0, 0, 1243, 26))
                self.menubar.setObjectName("menubar")
                MainWindow.setMenuBar(self.menubar)
                self.statusbar = QtWidgets.QStatusBar(MainWindow)
                self.statusbar.setObjectName("statusbar")
                MainWindow.setStatusBar(self.statusbar)

               #update button
                self.updateButtonContainer = QtWidgets.QWidget(self.centralwidget)
                self.updateButtonContainer.setGeometry(QtCore.QRect(800, 775, 150, 50))
                self.updateButtonContainer.setObjectName("updateButtonContainer")
                self.updateButtonContainer.setStyleSheet(
                "border-radius: 10px;"
                "background-color: #44AEE7;"
                )
                                
                self.updateButton = QtWidgets.QPushButton(self.updateButtonContainer)
                self.updateButton.setGeometry(QtCore.QRect(0, 0, 150, 45))
                self.updateButton.setObjectName("updateButton")
                self.Display_Image_Info()
                self.updateButton.clicked.connect(self.on_click_Update)  # Connect the button click event to on_click_Update method
                self.updateButton.clicked.connect(self.update_to_home)
               
                scroll_area = QScrollArea(MainWindow)
                scroll_area.setWidgetResizable(True)

                # Set your central widget inside the scroll area
                scroll_area.setWidget(self.centralwidget)

                # Set the scroll area as the central widget for the main window
                MainWindow.setCentralWidget(scroll_area)

                self.retranslateUi(MainWindow)
                QtCore.QMetaObject.connectSlotsByName(MainWindow)
                self.updatePatientInfo()

        def retranslateUi(self, MainWindow):
                _translate = QtCore.QCoreApplication.translate
                MainWindow.setWindowTitle(_translate("Patient Record", "Patient Record"))
                self.backButton.setText(_translate("MainWindow", "Back"))
                self.backButton.setStyleSheet("font-family: Arial; font-size: 22px; color: navy; border: none; font-weight: bold")
                self.IntelligentHealthInc.setWhatsThis(_translate("MainWindow", "<html><head/><body><p>Intelligent<br/>Health Inc.</p></body></html>"))
                self.IntelligentHealthInc.setText(_translate("MainWindow", "<html><head/><body><p>INTELLIGENT<br/>HEALTH INC.</p></body></html>"))
                self.Gender.setText(_translate("MainWindow", "Gender:"))
                self.DateofBirth.setText(_translate("MainWindow", "Date of Birth: "))
                self.RecordID.setText(_translate("MainWindow", "Record ID: "))
                self.PatientName.setText(_translate("MainWindow", "Name:"))
                self.PatientID.setText(_translate("MainWindow", "Patient ID: "))
                self.Age.setText(_translate("MainWindow", "Age:"))
                self.Modality.setText(_translate("MainWindow", "Modality"))
                self.SenderDoctor.setText(_translate("MainWindow", "Sender Doctor:" ))

                self.Gender.setStyleSheet("padding-left:5px;")
                self.DateofBirth.setStyleSheet("padding-left:5px;")
                self.RecordID.setStyleSheet("padding-left:5px;")
                self.PatientName.setStyleSheet("padding-left:5px;")
                self.PatientID.setStyleSheet("padding-left:5px;")
                self.Age.setStyleSheet("padding-left:5px;")
                self.Modality.setStyleSheet("padding-left:5px;")
                self.SenderDoctor.setStyleSheet("padding-left:5px;")

                self.UpcomingAppointment.setText(_translate("MainWindow", "Upcoming Appointment"))
                self.RequestTime.setText(_translate("MainWindow", "Request Time:"))
                self.Indications.setText(_translate("MainWindow", "Indications:" ))
                self.Notes.setText(_translate("MainWindow", "Notes"))
                self.updateButton.setText(_translate("MainWindow", "Update"))
                self.updateButton.setStyleSheet("font-family: Arial; font-size: 17px; color: white;")

        def changeEvent(self, event):
                if event.type() == QtCore.QEvent.WindowStateChange:
                        if MainWindow.windowState() & Qt.WindowMinimized:
                                self.backButton.move(MainWindow.width() - 200, 20)
                        elif MainWindow.windowState() & Qt.WindowMaximized:
                                self.backButton.move(MainWindow.width() - 400, 20)
                        event.accept()
                else:
                        event.ignore()

        def on_click_Update(self):
                cursor = connection.cursor()
                record_id = self.record_id
                
                cursor.execute("SELECT COUNT(*) FROM medicaltech_image_record WHERE record_id_id = %s", (record_id,))
                count = cursor.fetchone()[0]
                
                image = Ui_MainWindow.dicom_binary
                predicted = self.predictionLabel.text()
                prediction_words = predicted.split(' ')
                username = self.username
                if Ui_MainWindow.dicom_binary is None or len(prediction_words) <= 1:
                        message_box = QMessageBox()
                        message_box.critical(None, "Error", "No new image recorded. Cannot update the patient record.")
                        return
                else:
                        result = prediction_words[1]
                        notes = "Image taken, No Notes" if self.plainTextEdit.toPlainText() == "" else self.plainTextEdit.toPlainText()
                        upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Include microseconds

                        image_record = self.FilenameLabel.text()
                        filename = os.path.basename(image_record)
                        fName = filename.split(' ')
                        image_name = fName[1]

                        if count > 0:
                                update_sql = """UPDATE medicaltech_image_record
                                        SET image = %s, prediction = %s, notes = %s, upload_date = %s, image_filename = %s, medTech = %s
                                        WHERE record_id_id = %s """
                                data_to_update = (image, result, notes, upload_date, image_name, username, record_id)
                                cursor.execute(update_sql, data_to_update)
                        else:
                                # The record does not exist, so insert a new record
                                insert_sql = """INSERT INTO medicaltech_image_record
                                        (record_id_id, image, prediction, notes, upload_date, image_filename, medTech)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s) """
                                data_to_insert = (record_id, image, result, notes, upload_date, image_name,username)
                                cursor.execute(insert_sql, data_to_insert)

                        # Define and update the new status
                        new_status = "In Progress"
                        update_sql = """UPDATE medicaltech_radiologyrecord SET status = %s WHERE record_id = %s"""
                        data_to_update = (new_status, record_id)
                        cursor.execute(update_sql, data_to_update)

                        connection.commit()
                        cursor.close()
                        self.update_successful = True

        def Display_Image_Info(self):
                # Connect to the database and retrieve prediction, image filename, and image data from the database for the given record_id
                cursor = connection.cursor()
                record_id = self.record_id
                select_sql = "SELECT prediction, image_filename, image FROM medicaltech_image_record WHERE record_id_id = %s"
                cursor.execute(select_sql, (record_id,))
                result = cursor.fetchone()

                if result:
                        prediction, image_filename, image_data = result
                        Ui_MainWindow.dicom_binary = image_data

                        # Display the prediction and image filename in respective QLabel widgets
                        self.predictionLabel.setText(f"Prediction: {prediction}")
                        self.FilenameLabel.setText(f"Filename: {image_filename}")
                        if image_data is not None: dicom_dataset = pydicom.dcmread(BytesIO(image_data)); self.Display_Image(dicom_dataset)
                else:
                        print("Record not found in the database for record_id:", record_id)

                cursor.close()

        # Create a method to display the DICOM image
        def Display_Image(self, dicom_dataset):
                if dicom_dataset:
                        # Extract the pixel data from the DICOM dataset before Creating Matplotlib figure and Axis
                        image_data = dicom_dataset.pixel_array
                        image_data = cv2.resize(image_data, (224, 224), interpolation=cv2.INTER_LINEAR)
                        image_data = cv2.cvtColor(image_data, cv2.COLOR_GRAY2RGB)  # Convert to RGB format
                        image_data = cv2.resize(image_data, (224, 224))  # Resize to (224, 224)

                        # Normalize pixel values to 0-255 range
                        image_data = ((image_data - image_data.min()) / (image_data.max() - image_data.min()) * 255).astype(np.uint8)

                        # Convert image_data to QImage
                        height, width, channel = image_data.shape
                        bytes_per_line = 3 * width
                        image_qt = QtGui.QImage(image_data.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)

                        # Create a QPixmap directly from the QImage and set pixmap to the self.dicomImageLabel
                        pixmap = QPixmap.fromImage(image_qt)

                        if not pixmap.isNull():
                                self.uploadedLabel.setPixmap(pixmap)
                                self.uploadedLabel.setScaledContents(True)
                                self.uploadedLabel.setAlignment(QtCore.Qt.AlignCenter)
                        else:
                                print("Failed to load the image from data")

        def updatePatientInfo(self):
                # Update the labels in gridGroupBox1 with the stored patient information
                self.RecordID.setText(f"Record ID: {self.record_id}")
                self.PatientName.setText(f"Name: {self.patient_name}")
                self.PatientID.setText(f"Patient ID: {self.patient_id}")
                self.Age.setText(f"Age: {self.age}")
                self.DateofBirth.setText(f"Date of Birth: {self.dob}")
                self.Modality.setText(f"Modality: {self.modality}")
                self.RequestTime.setText(f"Request Time: {self.request_time}")
                self.SenderDoctor.setText(f"Sender Doc: {self.sender_doc}")
                self.Indications.setText((f"Indications: {self.indications}"))
                
                cursor = connection.cursor()
                # Retrieve the prediction, image filename, and image data from the database for the given record_id
                cursor.execute("select RR.record_id, RR.gender, IR.notes from medicaltech_radiologyrecord RR left join medicaltech_image_record IR on RR.record_id = IR.record_id_id where RR.record_id = %s", (self.record_id,))
                result = cursor.fetchone()
                if result:
                        gender, notes = result[1], result[2]
                        self.Gender.setText((f"Gender: {gender}"))
                        self.plainTextEdit.setPlainText(notes)

        def uploadDICOM(self):
                options = QFileDialog.Options()
                options |= QFileDialog.ReadOnly
                file_name, _ = QFileDialog.getOpenFileName(None, "Open DICOM File", "", "DICOM Files (*.dcm);;All Files (*)", options=options)

                if file_name:                        
                        # Open the DICOM file in binary read mode and read its contents
                        with open(file_name, 'rb') as dicom_file:
                                binary_data = dicom_file.read()
                                
                        # Store the binary data for future use
                        Ui_MainWindow.dicom_binary = binary_data

                        # Load the selected file (you can determine the file type based on its extension)
                        file_extension = os.path.splitext(file_name)[1].lower()
                        if file_extension in {'.dcm', '.dicom'}:
                                # Handle DICOM file and Convert the DICOM pixel data to a QImage
                                dicom_data = pydicom.dcmread(file_name)
                                image_data = dicom_data.pixel_array
                                image_data = cv2.resize(image_data, (224, 224), interpolation=cv2.INTER_LINEAR)
                                image_data = cv2.cvtColor(image_data, cv2.COLOR_GRAY2RGB)  # Convert to RGB format
                                image_data = cv2.resize(image_data, (224, 224))  # Resize to (224, 224)

                                # Normalize pixel values to 0-255 range
                                image_data = ((image_data - image_data.min()) / (image_data.max() - image_data.min()) * 255).astype(np.uint8)

                                # Convert image_data to QImage
                                height, width, channel = image_data.shape
                                bytes_per_line = 3 * width
                                image_qt = QtGui.QImage(image_data.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)

                                # Create a QPixmap directly from the QImage and set pixmap to the self.dicomImageLabel
                                pixmap = QPixmap.fromImage(image_qt)
                                self.uploadedLabel.setPixmap(pixmap)
                                self.uploadedLabel.setAlignment(QtCore.Qt.AlignCenter)

                                model_path = os.path.join(os.path.dirname(__file__), 'Model2_VGG16.h5')
                                model = load_model(model_path)

                                # Preprocess the image for prediction
                                image_data = image_data / 255.0  # Normalize the image data
                                image_data = np.expand_dims(image_data, axis=0)  # Add batch dimension

                                # Make a prediction using the model
                                prediction = model.predict(image_data)
                                predicted_value = prediction[0][0]  # Assuming prediction is a single value
                                predicted_class = 'Positive' if predicted_value > 0.5 else 'Negative'
                                self.predictionLabel.setText(f"Prediction: {predicted_class}")

                                # Set the image name as the text of the FilenameLabel
                                self.FilenameLabel.setText(f"Filename: {os.path.basename(file_name)}")
        
        # Navigate back to the Home Page
        def To_Home(self):
                self.main_window.close()
                self.window = QtWidgets.QMainWindow()
                self.ui = home.Ui_MainWindow(self.window, self.username)
                self.ui.setupUi(self.window)
                self.window.show()    

        def update_to_home(self):
                if not self.update_successful:  # Check if the update was successful
                        return
                self.To_Home()

if __name__ == "__main__":
    django.setup()
    if len(sys.argv) == 10:
        record_id, patient_name, patient_id, age, dob, modality, request_time, sender, indication = sys.argv[1:]

        app = QtWidgets.QApplication(sys.argv)
        MainWindow = QtWidgets.QMainWindow()
        ui = Ui_MainWindow(record_id, patient_name, patient_id, age, dob, modality, request_time, sender, indication)
        ui.setupUi(MainWindow)
        MainWindow.show()
        
        atexit.register(connection.close)
        sys.exit(app.exec_())