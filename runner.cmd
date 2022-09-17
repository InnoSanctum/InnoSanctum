tasklist /fi "ImageName eq python3.10.exe" /fo csv 2>NUL | find /I "python3.10.exe">NUL
if NOT "%ERRORLEVEL%"=="0" python3.10.exe "D:\Programming\Python\_AIT\CanonClicker\main.py"