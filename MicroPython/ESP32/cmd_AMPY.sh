#!/bin/bash

# https://www.baeldung.com/linux/use-command-line-arguments-in-bash-script

# cmd_AMPY.sh put main.py
# cmd_AMPY.sh get main.py
# cmd_AMPY.sh rm  main.py
# cmd_AMPY.sh ls  folder
# cmd_AMPY.sh run -n main.py # -n option indicates to not waiting for output

ampy --port /dev/ttyUSB0 $1 $2 $3