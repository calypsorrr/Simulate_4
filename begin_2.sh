#!/bin/bash

if [ -f "escape.txt" ]; then
  sudo python3 /home/pi/project_sim/button_notion.py
else
  python3 /home/pi/project_sim/web.py
  sudo python3 /home/pi/project_sim/button_notion.py
fi
