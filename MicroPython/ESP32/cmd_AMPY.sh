#!/bin/bash

# https://www.baeldung.com/linux/use-command-line-arguments-in-bash-script

# cmd_AMPY.sh put main.py
# cmd_AMPY.sh get main.py
# cmd_AMPY.sh rm  main.py
# cmd_AMPY.sh ls  folder

ampy --port /dev/ttyUSB0 $1 $2