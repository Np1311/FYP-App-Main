# Import your Python scripts
import tkinter
import sys
from PyQt5 import QtWidgets
from login import Ui_MainWindow
import os
import pymysql
from pydicom.encoders import gdcm
from pydicom.encoders import pylibjpeg
import django
# import sqlite3
# import socket
# from datetime import datetime
from SQLSetting import SQLSettings

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import settings


            
def main():
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
    
    django.setup()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(MainWindow)
    ui.setupUi(MainWindow)
    MainWindow.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

