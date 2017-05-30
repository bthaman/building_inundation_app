@echo OFF
color 0d
if exist "c:\Python27\ArcGIS10.1\python.exe" (SET thepath=10.1)
if exist "c:\Python27\ArcGIS10.2\python.exe" (SET thepath=10.2)
if exist "c:\Python27\ArcGIS10.3\python.exe" (SET thepath=10.3)
if exist "c:\Python27\ArcGIS10.4\python.exe" (SET thepath=10.4)
if defined thepath (c:\Python27\ArcGIS%thepath%\python.exe "bldg_wse_app_v2.py") else (echo python exe could ^not be found)
REM pause