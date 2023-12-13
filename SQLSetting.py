import sqlite3
import socket
import sys
import os
import pymysql
from datetime import datetime

class SQLSettings:
    def __init__(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(os.path.dirname(__file__))

        db_file_path = os.path.join(base_path, 'fyp.db')
        self.date_format = "%Y-%m-%d %H:%M:%S"
        # Connect to the SQLite database
        try:
            self.conn = sqlite3.connect(db_file_path)
            self.cursor_sqlite = self.conn.cursor()
        except sqlite3.Error as e:
            print("SQLite Error:", e)
            return None
    def checkIntenetStatus(self):
        try:
            socket.create_connection(("www.google.com", 80))
            self.conn_mysql = pymysql.connect(
                host = "fyp-database.mysql.database.azure.com",
                port= 3306,
                user= "master",
                password= "hdforsure100%",
                database= "fyp"
            )
            self.cursor_mysql = self.conn_mysql.cursor()
            return True
        except OSError:
            return False

    def checkRadiologyRecordNotInDB(self,recordID,targetDB):
        if targetDB == 'sqlite':
            cursor = self.conn.cursor()
            
        else:
            cursor = self.conn_mysql.cursor()
            
        cursor.execute("SELECT record_id FROM medicalTech_radiologyrecord")
        recordIDs = [item[0] for item in cursor.fetchall()]

        if recordID not in recordIDs:
            print("Record not found")
            return True
        else:
            return False
        
    def checkUpdateTime(self, recordID, targetDB):
        try:
            if targetDB == 'sqlite':
                cursor = self.conn.cursor()
                placeholder = '?'
            else:
                cursor = self.conn_mysql.cursor()
                placeholder = '%s'

            cursor.execute(f"SELECT update_time FROM medicalTech_radiologyrecord WHERE record_id = {placeholder}", (recordID,))
            result = cursor.fetchone()

            if result:
                updateTimeinDB = result[0]
                
                if updateTimeinDB is not None:
                    if isinstance(updateTimeinDB, str):
                        updateTimeinDB = datetime.strptime(updateTimeinDB, self.date_format)

                return updateTimeinDB
            else:
                return None
        except Exception as e:
            print(f"An error occurred while checking update time: {str(e)}")
            return None


    def checkImageRecordNotInDB(self, recordID, targetDB):
        if targetDB == 'sqlite':
            cursor = self.conn.cursor()
            
        else:
            cursor = self.conn_mysql.cursor()
            
        cursor.execute("SELECT record_id_id FROM medicalTech_image_record")
        recordIDs = [item[0] for item in cursor.fetchall()]

        if recordID not in recordIDs:
            print("Record not found")
            return True
        else:
            return False
        

    def checkImageUploadTime(self, recordID, targetDB):
        try:
            if targetDB == 'sqlite':
                cursor = self.conn.cursor()
                placeholder = '?'
            else:
                cursor = self.conn_mysql.cursor()
                placeholder = '%s'

            cursor.execute(f"SELECT upload_date FROM medicalTech_image_record WHERE record_id_id = {placeholder}", (recordID,))
            result = cursor.fetchone()

            if result:
                uploadTimeInDb = result[0]

                if uploadTimeInDb is not None:
                    if isinstance(uploadTimeInDb, str):
                        uploadTimeInDb = datetime.strptime(uploadTimeInDb, self.date_format)

                return uploadTimeInDb
            else:
                return None
        except Exception as e:
            print(f"An error occurred while checking upload time: {str(e)}")
            return None

    def checkImageDeletionTime(self, recordID, targetDB):
        try:
            if targetDB == 'sqlite':
                cursor = self.conn.cursor()
                placeholder = '?'
            else:
                cursor = self.conn_mysql.cursor()
                placeholder = '%s'

            cursor.execute(f"SELECT deletion_time FROM medicalTech_image_record WHERE record_id_id = {placeholder}", (recordID,))
            result = cursor.fetchone()

            if result:
                deletionTimeinDB = result[0]
                print("deletionTime: " + str(deletionTimeinDB))

                if deletionTimeinDB is not None:
                    if isinstance(deletionTimeinDB, str):
                        deletionTimeinDB = datetime.strptime(deletionTimeinDB, self.date_format)
                return deletionTimeinDB
            else:
                return None
        except Exception as e:
            print(f"An error occurred while checking deletion time: {str(e)}")
            return None
    
    def migrateRadiologyRecord(self, initialDB):
        
        if initialDB == 'MYSQL':
            self.cursor_sqlite.execute("SELECT COUNT(*) FROM medicalTech_radiologyrecord")
            count = self.cursor_sqlite.fetchone()[0]
            self.cursor_mysql.execute("SELECT * FROM medicalTech_radiologyrecord")
            radiology_data = self.cursor_mysql.fetchall()
            connection = self.conn
            

            placeholders = ', '.join(['?'] * 14)
            updatePlaceholder = '?'
            targetDB = 'sqlite'

        else:
            self.cursor_mysql.execute("SELECT COUNT(*) FROM medicalTech_radiologyrecord")
            count = self.cursor_mysql.fetchone()[0]
            self.cursor_sqlite.execute("SELECT * FROM medicalTech_radiologyrecord")
            radiology_data = self.cursor_sqlite.fetchall()

            connection = self.conn_mysql
            
            placeholders = ', '.join(['%s'] * 14)
            updatePlaceholder = '%s'
            targetDB = 'MYSQL'

        print('running migration from '+initialDB+' to '+targetDB)
        columns = (
            'record_id', 'patient_name', 'patient_id', 'age', 'date_of_birth', 'modality',
            'request_time', 'status', 'nationality', 'area', 'gender', 'indications', 'senderDoctor', 'update_time'
        )
        sql = f"INSERT INTO medicalTech_radiologyrecord ({', '.join(columns)}) VALUES ({placeholders})"
        cursor = connection.cursor()
        print(str(count) + ' records in '+ targetDB)

        if count == 0:
           
            for row in radiology_data:
                record_id = row[0]
                patient_name = row[1]
                patient_id = row[2]
                age = row[3]
                date_of_birth = row[4]
                modality = row[5]
                request_time = row[6]
                status = row[7]
                nationality = row[8]
                area = row[9]
                gender = row[10]
                indications = row[11]
                senderDoctor = row[12]
                updateTime = row[13]

                try:
                    cursor.execute(sql, (
                        record_id, patient_name, patient_id, age, date_of_birth, modality, request_time,
                        status, nationality, area, gender, indications, senderDoctor, updateTime
                    ))
                    print('transferred record to mysql ' + str(record_id))
                except Exception as e:
                    print(f"An error occurred during insertion: {str(e)}")
        else:

            for row in radiology_data:
                record_id = row[0]
                patient_name = row[1]
                patient_id = row[2]
                age = row[3]
                date_of_birth = row[4]
                modality = row[5]
                request_time = row[6]
                status = row[7]
                nationality = row[8]
                area = row[9]
                gender = row[10]
                indications = row[11]
                senderDoctor = row[12]
                updateTime = row[13]

                print("Start migrations for "+str(record_id))

                if self.checkRadiologyRecordNotInDB(record_id,targetDB):
                    print("migrate additional data")
                    try:
                        cursor.execute(sql, (
                            record_id, patient_name, patient_id, age, date_of_birth, modality, request_time,
                            status, nationality, area, gender, indications, senderDoctor, updateTime
                        ))
                        print('transferred record to '+ targetDB + ' ' + str(record_id))
                    except Exception as e:
                        print(f"An error occurred during insertion: {str(e)}")
                else:
                    print("running update")
                    updateTimeinDb = self.checkUpdateTime(record_id, targetDB)
                    if updateTime is None and updateTimeinDb is None:
                        print("skipping update")
                        continue
                    else:
                        
                        if updateTime is not None:
                            if isinstance(updateTime, str):
                                updateTime = datetime.strptime(updateTime, self.date_format)
                        print(type(updateTime))
                        print(type(updateTimeinDb))
                        # if updateTimeinDb is not None:
                        #     updateTimeinDb = datetime.strptime(updateTimeinDb, date_format)
                        updateSQL = f"UPDATE medicalTech_radiologyrecord SET request_time = {updatePlaceholder}, update_time = {updatePlaceholder}, status = {updatePlaceholder} WHERE record_id = {updatePlaceholder}"

                        if updateTime is not None and updateTimeinDb is None:
                            try:
                                cursor.execute(updateSQL, (request_time, updateTime, status, record_id))
                                print('update record to '+ targetDB + ' ' + str(record_id))
                            except Exception as e:
                                print(f"An error occurred during insertion: {str(e)}")
                        elif updateTimeinDb is not None and updateTime is None:
                            continue
                        elif updateTime > updateTimeinDb:
                            try:
                                cursor.execute(updateSQL, (request_time, updateTime, status, record_id))
                                print('update record to '+ targetDB + ' ' + str(record_id))
                            except Exception as e:
                                print(f"An error occurred during insertion: {str(e)}")
                        else:
                            continue
        
        connection.commit()

    def migrateImageRecord(self, initialDB):
        
        if initialDB == 'MYSQL':
            self.cursor_sqlite.execute("SELECT COUNT(*) FROM medicalTech_image_record")
            count = self.cursor_sqlite.fetchone()[0]
            self.cursor_mysql.execute("SELECT * FROM medicalTech_image_record")
            image_data = self.cursor_mysql.fetchall()
            connection = self.conn
            

            placeholders = ', '.join(['?'] * 12)
            updatePlaceholder = '?'
            targetDB = 'sqlite'

        else:
            self.cursor_mysql.execute("SELECT COUNT(*) FROM medicalTech_image_record")
            count = self.cursor_mysql.fetchone()[0]
            self.cursor_sqlite.execute("SELECT * FROM medicalTech_image_record")
            image_data = self.cursor_sqlite.fetchall()

            connection = self.conn_mysql
            
            placeholders = ', '.join(['%s'] * 12)
            updatePlaceholder = '%s'
            targetDB = 'MYSQL'

        print('running migration of image_record from '+initialDB+' to '+targetDB)
        columns = ('record_id_id', 'image', 'prediction', 'notes', 'upload_date', 'image_filename', 'examination', 'findings', 'impressions', 'medTech', 'radiologyDoctor', 'deletion_time')
        sql = f"INSERT INTO medicalTech_image_record ({', '.join(columns)}) VALUES ({placeholders})"
        cursor = connection.cursor()
        print(str(count) + ' image records in '+ targetDB)

        if count == 0:
           
            for row in image_data:
                record_id = row[0]
                image = row[1]
                prediction = row[2]
                notes = row[3]
                upload_date = row[4]
                image_filename = row[5]
                examination = row[6]
                findings = row[7]
                impressions = row[8]
                medTech = row[9]
                radiologyDoctor = row[10]
                deletion_time = row[11]
                
                try:
                    cursor.execute(sql, (record_id, image, prediction, notes, upload_date, image_filename, examination, findings, impressions, medTech, radiologyDoctor, deletion_time))
                    print('transferred image record to '+targetDB+" " + str(record_id))
                except Exception as e:
                    print(f"An error occurred during insertion: {str(e)}")
        else:

            for row in image_data:
                record_id = row[0]
                image = row[1]
                prediction = row[2]
                notes = row[3]
                upload_date = row[4]
                image_filename = row[5]
                examination = row[6]
                findings = row[7]
                impressions = row[8]
                medTech = row[9]
                radiologyDoctor = row[10]
                deletion_time = row[11]

                if upload_date is not None:
                    if isinstance(upload_date, str):
                        upload_date = datetime.strptime(upload_date, self.date_format)
                    
                uploadDateInDB = self.checkImageUploadTime(record_id, targetDB)
                deletionTimeInDB = self.checkImageDeletionTime(record_id, targetDB)

                if self.checkImageRecordNotInDB(record_id, targetDB):
                    print("migrate additional data")
                    try:
                        cursor.execute(sql, (record_id, image, prediction, notes, upload_date, image_filename, examination, findings, impressions, medTech, radiologyDoctor, deletion_time))
                        print('transferred image record to '+ targetDB + ' ' + str(record_id))
                    except Exception as e:
                        print(f"An error occurred during insertion: {str(e)}")

                else :
                    updateSQL = f"UPDATE medicalTech_image_record SET image = {updatePlaceholder}, prediction = {updatePlaceholder}, notes = {updatePlaceholder}, upload_date = {updatePlaceholder}, image_filename = {updatePlaceholder}, medTech = {updatePlaceholder} WHERE record_id_id = {updatePlaceholder}"
                    deletSQL = f"UPDATE medicalTech_image_record SET image = {updatePlaceholder}, deletion_time = {updatePlaceholder} WHERE record_id_id = {updatePlaceholder}"

                    if upload_date is not None and uploadDateInDB is None:
                        try:
                            cursor.execute(updateSQL, (image, prediction, notes, upload_date, image_filename, medTech, record_id))
                            print('update image record of '+ targetDB + ' ' + str(record_id))
                        except Exception as e:
                            print(f"An error occurred during updation: {str(e)}")

                    elif upload_date is None and uploadDateInDB is None:
                        continue

                    elif upload_date > uploadDateInDB:
                        try:
                            cursor.execute(updateSQL, (image, prediction, notes, upload_date, image_filename, medTech, record_id))
                            print('update image record of '+ targetDB + ' ' + str(record_id))
                        except Exception as e:
                            print(f"An error occurred during updation: {str(e)}")

                    elif deletion_time is not None and deletionTimeInDB is None:
                        try:
                            cursor.execute(deletSQL, (image, deletion_time, record_id))
                            print('update image record of '+ targetDB + ' ' + str(record_id))
                        except Exception as e:
                            print(f"An error occurred during updation: {str(e)}")

                    else:
                        continue
        connection.commit()

    def migrateAuth_user(self, initialDB):
        
        connection = self.conn
        connection.cursor().execute("DELETE FROM auth_user")
        connection.commit()
        self.cursor_mysql.execute("SELECT * FROM auth_user")
        account_data = self.cursor_mysql.fetchall()
        
        

        placeholders = ', '.join(['?'] * 11)
        targetDB = 'sqlite'

        print('running migration of auth_user from '+initialDB+' to '+targetDB)
        columns = ('id', 'password', 'last_login', 'is_superuser', 'username','first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined')
        sql = f"INSERT INTO auth_user ({', '.join(columns)}) VALUES ({placeholders})"
        cursor = connection.cursor()

        for row in account_data:
            id = row[0]
            password = row[1]
            last_login = row[2]
            is_superuser = row[3]
            username = row[4]
            first_name = row[5]
            last_name = row[6]
            email = row[7]
            is_staff = row[8]
            is_active = row[9]
            date_joined = row[10]
    
            
            try:
                cursor.execute(sql, (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined))
                print('transferred account to '+targetDB+" " + str(id))
            except Exception as e:
                print(f"An error occurred during insertion: {str(e)}")
        connection.commit()

    def migrateProfile(self, initialDB):
        
        connection = self.conn
        connection.cursor().execute("DELETE FROM systemAdmin_profile")
        connection.commit()
        self.cursor_mysql.execute("SELECT * FROM systemAdmin_profile WHERE role = 'medicalTech'")
        account_data = self.cursor_mysql.fetchall()
        
        

        placeholders = ', '.join(['?'] * 10)
        targetDB = 'sqlite'

        print('running migration of profile from '+initialDB+' to '+targetDB)
        columns = ('id', 'created_at', 'first_name', 'last_name', 'email', 'dob', 'phone', 'account_id', 'role', 'status')
        sql = f"INSERT INTO systemAdmin_profile ({', '.join(columns)}) VALUES ({placeholders})"
        cursor = connection.cursor()

        for row in account_data:
            id = row[0]
            created_at = row[1]
            first_name = row[2]
            last_name = row[3]
            email = row[4]
            dob = row[5]
            phone = row[6]
            account_id = row[7]
            role = row[8]
            status = row[9]
    
            
            try:
                cursor.execute(sql, (id, created_at, first_name, last_name, email, dob, phone, account_id, role, status))
                print('transferred profile to '+targetDB+" " + str(id))
            except Exception as e:
                print(f"An error occurred during insertion: {str(e)}")

        connection.commit()
