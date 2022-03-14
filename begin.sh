#!/bin/bash

iwgetid
if [ $? -eq 255 ]; then
  cd wifi-setup
  sudo node index.js
  python3 /home/pi/python_flask/web.py
  echo reboot
else
  sudo python3 /home/pi/button_notion.py
fi
