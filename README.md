# Bluetooth GATT server for Raspberry Pi

Toothd.py enables you to control various parts of your Raspberry's system without having to be connected over Lan, wireless or directly via console. It runs 5 example Bluetooth services each with a number of Characteristics that show cases various type of controls such as GPIO, System Restart, Wifi Configuration, Ip Address display etc.

The system commands are very basic and a mix of grep and cut to demonstrate functionality.

Download the piNet app from the AppStore to control the Raspberry. Ofcourse, you can easily extend on the above functionality and services with your own. The App have expects certain Characteristics and UUID's from toothd.py to function properly. Just copy existing examples and modify for your needs.

## Install pre-requisites
Start with installing the required dependencies by following http://headstation.com/archives/controlling-raspberry-over-bluetooth/

