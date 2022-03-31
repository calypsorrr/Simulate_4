#!/bin/bash

iwgetid
if [ $? -eq 255 ]; then
  cd project_sim
  sudo service wifi-setup start
  sleep 60
  python3 /home/pi/python_flask/web.py
  echo reboot
else
  sudo python3 /home/pi/project_sim/button_notion.py
fi
