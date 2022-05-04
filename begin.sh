#!/bin/bash

iwgetid
if [ $? -eq 255 ]; then
  cd project_sim
  sudo python3 /home/pi/project_sim/create.py
  sudo service wifi-setup start
  sleep 60
  python3 /home/pi/project_sim/web.py
  echo reboot
else
  cd project_sim
  sudo python3 /home/pi/project_sim/button_notion.py
fi
