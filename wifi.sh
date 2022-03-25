#!/bin/bash

cd wifi-setup
npm install
sudo nano /etc/default/hostapd
sudo cp config/hostapd.conf /etc/hostapd/hostapd.conf
sudo nano /etc/default/udhcpd
sudo cp config/udhcpd.conf /etc/udhcp.conf
sudo cp config/wifi-setup.service /lib/systemd/system
sudo cp index.js /usr/bin/
sudo nano /lib/systemd/system/wifi-setup.service