#!/bin/bash

sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install python3-pip
sudo apt -y install git
sudo apt-get -y install nodejs npm node-semver
pip3 install flask
pip3 install facebook-sdk
pip3 install pigpio
pip3 install RPI.GPIO
pip3 install adafruit-blinka
pip3 install rpi_ws281x adafruit-circuitpython-neopixel
git clone git@github.com:davidflanagan/wifi-setup.git
cd wifi-setup
npm install
sudo apt-get install hostapd
sudo apt-get install udhcpd
sudo systemctl disable hostapd
sudo systemctl disable udhcpd
