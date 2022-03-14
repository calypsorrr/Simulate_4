#!/bin/bash

sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install python3-pip
sudo apt -y install git
sudo apt-get -y install nodejs npm node-semver
pip3 install flask
sudo pip3 install facebook-sdk
sudo pip3 install pigpio
pip3 install RPI.GPIO
sudo pip3 install adafruit-blinka
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo apt-get install hostapd
sudo apt-get install udhcpd
sudo systemctl disable hostapd
sudo systemctl disable udhcpd
