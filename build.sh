rm -rf dist

# Remove build folder
rm -rf build

# Remove spec file
rm -f IntelligentHealthInc.spec

echo "Cleanup complete."

pyinstaller --add-data "logo.png:." --add-data "background.png:." --add-data "fyp.db:." --add-data "file_upload_icon.png:." --add-data "Model2_VGG16.h5:." --add-data "logo.ico:." --windowed --name IntelligentHealthInc --icon logo.ico --hidden-import=pymysql --hidden-import=tensorflow --hidden-import=sqlite3 main.py