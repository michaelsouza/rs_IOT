# Getting started with MicroPython on the ESP32

## 1 Installing
[https://docs.micropython.org/en/latest/esp32/tutorial/intro.html](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)

1. Create a new virtual environment
    ```bash
    venv venv
    ```

1. Activate the virtual environment
    ```bash
    souce venv/bin/activate
    ```

1. Install epstool
    ```bash
    pip -m install esptool
    ```

1. Get latest version from 

    [https://micropython.org/download/esp32/](https://micropython.org/download/esp32/)

    ```bash
    wget https://micropython.org/resources/firmware/esp32-20220618-v1.19.1.bin
    ```

1. Erase flash

    ```bash
    esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
    ```

1. Install the new firmware

    ```bash
    esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-20190125-v1.10.bin
    ```

## 2 Check installation
1. Install picocom

    ```bash
    sudo apt install picocom
    ```

1. Access the serial port
    ```bash
    picocom /dev/ttyUSB0 -b115200
    ```

1. Blink
    On MicroPython accessed with picocom, type
    
    ```Python
    import machine    
    import time
    
    ledR = machine.Pin(13, machine.Pin.OUT)
    ledR.value(1)
    time.sleep(1)
    ledR.value(0)
    ```

## 3 Config VSCode Pylint

[https://micropython-stubs.readthedocs.io/en/main/22_vscode.html](https://micropython-stubs.readthedocs.io/en/main/22_vscode.html)

1. Get system and platform from MicroPython


        On MicroPython accessed with picocom, type
        
    ```python
    import sys        
    
    print('platform:', sys.platform, 'version:', sys.version)    
    ```

1. Install stubs

    ```bash
    pip install -U micropython-esp32-stubs==1.19.*
    ```
    
1. Create the file "*.vscode/settings.json*"

    ```json
    {
        "python.languageServer": "Pylance",
        "python.analysis.typeCheckingMode": "basic",
        "python.analysis.diagnosticSeverityOverrides": {
            "reportMissingModuleSource": "none"
        },
        "python.analysis.typeshedPaths": [
            ".venv/Lib/site-packages"
        ],
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": true,
    } 
    ```


## Uploading files to the file system

[https://techtutorialsx.com/2017/06/04/esp32-esp8266-micropython-uploading-files-to-the-file-system/](https://techtutorialsx.com/2017/06/04/esp32-esp8266-micropython-uploading-files-to-the-file-system/)