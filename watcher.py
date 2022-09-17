from time import sleep
from os import listdir, system
TIMEOUT: int = 60
while True:
    #start cmd.exe @cmd /k "Command"
    system('start cmd.exe @cmd /c "D:\\Programming\\Python\\_AIT\\CanonClicker\\runner.cmd"')
    print("Starting Scraper!")
    print(60*" ")
    for i in range(TIMEOUT):
        print(f"Seconds to restart: {TIMEOUT-i}", end='\r')
        sleep(1)