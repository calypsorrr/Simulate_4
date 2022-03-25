#!/bin/bash

sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install python3-pip
sudo apt -y install git
sudo apt-get -y install nodejs npm node-semver
pip3 install flask
sudo pip3 install facebook-sdk
pip3 install pigpio
pip3 install RPI.GPIO
sudo pip3 install adafruit-blinka
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo apt-get -y install python-smbus
sudo apt-get -y install i2c-tools
sudo pip3 install pillow
sudo pip3 install image
sudo apt-get -y install libopenjp2-7 libtiff5 libatlas-base-dev
sudo pip3 install Adafruit_BBIO
sudo pip3 install Adafruit-SSD1306
sudo apt-get install hostapd
sudo apt-get install udhcpd
sudo systemctl unmask hostapd
sudo systemctl disable hostapd
sudo systemctl disable udhcpd

