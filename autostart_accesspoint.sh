#!/bin/bash

iwgetid
if [ $? -eq 255 ]; then
  sudo service wifi-setup start
  sleep 60
  python3 /home/pi/project_sim/web.py
  echo reboot
else
  sudo python3 /home/pi/project_sim/finale_code.py
fi
