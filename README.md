# ISMU

Information system master unit

## How to Run the Project on Raspberry Pi Pico W Using VSCode

### Prerequisites

1. **Hardware:**
   - Raspberry Pi Pico W.
   - USB cable with data transfer capability.

2. **Software:** - [Visual Studio Code (VSCode)](https://code.visualstudio.com/) installed. - VSCode Extension: MicroPico. - Python 3.x (preferably version 3.11 or newer). - MicroPython UF2 file installed on the Raspberry Pi Pico W.
   > Follow the [official MicroPython setup guide](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) for installing it on your Pico.

### Steps to Configure and Run the Project

#### 1. Install and Configure **MicroPico** Extension

- Open Visual Studio Code.
- Go to the **Extensions** panel and install the **MicroPico** extension.
- After installing, ensure your Raspberry Pi Pico is connected to your computer via USB.

#### 2. Clone the Project Repository

- Copy the repository to your local machine:

```bash
  git clone https://github.com/publictransitdata/ISMU.git
  cd ISMU
```

#### 3. Make Sure Required Files Are in Place

- Ensure Python files for your project are located in a directory that will be synced to the Pico. Typically, this is the project’s root directory.

#### 4. Open the Project in VSCode

- Launch Visual Studio Code and open the project directory:

```bash
  code .
```

#### 5. Initialize virtual environment in project directory

```
python -m venv .venv
source .venv/bin/activate
```

#### 6. Install all required dependencies(if you want to develop project install also dev dependencies)

```
pip install -r requirements.txt
opptionally:
pip install -r requirements-dev.txt
```

#### 7. Set up the git hook scripts

```
pre-commit install
```

#### 8. Initialize MicroPico project

- **Right-click** on area in folder/project view.
- In the context menu that appears, select **Initialize MicroPico project**

#### 9. Toggle virtual MicroPico workspace

- At the bottom of vs studio you will see a button with the same name and you have to click it

#### 10. Upload Code to Pico

- To upload your code:
  - **Right-click** on the file you want to upload in the side panel (or folder/project view).
  - In the context menu that appears, select **Upload File to Pico**

> You don't need all files on board. You only need: app, config, lib, utils directories and main.py

#### 11. Run the Program

- **Right-click** on the main.py in Mpy Remote Workspace.
- In the context menu that appears, select **run current file on Pico**

> Alternatively, right-click main.py in the MicroPython Remote Workspace, then click the Run button at the bottom.

### How to freeze code and make firmware for raspberry pi pico W board

#### 1. Git clone micropython repo

```
git clone https://github.com/micropython/micropython.git
```

#### 2. Go inside cloned directory and build the MicroPython cross-compiler

```
cd micropython
make -C mpy-cross
```

#### 3. Build the firmware

```
make BOARD=RPI_PICO_W submodules
make BOARD=RPI_PICO_W clean
make -j $(nproc) BOARD=RPI_PICO_W FROZEN_MANIFEST=/path/to/manifest.py/file/inside/ISMU/directory
```

> The ISMU directory contains two manifest files. One includes main.py (manifest_release.py) to auto-start the program on power-up, while the other excludes it so you can run the code manually from an IDE.

#### 4. Deploying firmware to the device

Firmware can be deployed to the device by putting it into bootloader mode
(hold down BOOTSEL while powering on or resetting) and then either copying
`firmware.uf2` to the USB mass storage device that appears.

> You can find firmware.uf2 inside build-RPI_PICO_W directory. (schematic path : micropython/ports/rp2/build-RPI_PICO_W)

#### 5. Cleaning unnecessary files from Mpy Remote Workplace

After loading compiled code to firmware, you don't need anymore app, lib, utils directories and main.py(if you used manifest_release.py), so you can remove it from there. In config directory you need to have: char_map.json, font.py, lang.json(language file).

### How to make font.py for project

todo
