# METR4810_TEAM5_MiniBot

This is the code used in Team5's mini matchbox robot, 2023 METR4810 project.

The python files in the ESP code folder are to be uploaded to the ESP32C3, with micropython installed.

Now the ESP is advertising bluetooth, use the MAC_scan.py file to scan for the ESP's Mac address.
Paste this mac address into the Mac_address variable in the main.py file.
Now when the main.py file is run, it will connect to the esp32 via bluetooth and transmit inputs from the controller

Team members:
Jack McDonald 
Lucas Stephens
James Moran