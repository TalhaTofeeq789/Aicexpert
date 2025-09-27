@echo off
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Starting Flask backend server...
echo Backend will be available at: http://localhost:5000
echo.
python app.py