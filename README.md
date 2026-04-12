# ISMU

Information system master unit
todo: write short description of project

## How to Run the Project on Raspberry Pi Pico W Using VSCode

### Prerequisites

1. **Hardware:**

- Raspberry Pi Pico W.
- USB cable with data transfer capability.

2. **Software:**

- [Visual Studio Code (VSCode)](https://code.visualstudio.com/) installed.
- VSCode Extension: MicroPico.
- Python 3.x (preferably version 3.11 or newer).
- MicroPython firmware(.uf2 file) installed on the Raspberry Pi Pico W.

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

#### 3. Open the Project in VSCode

- Launch Visual Studio Code and open the project directory:

```bash
  code .
```

#### 4. Initialize virtual environment in project directory

```
python -m venv .venv
source .venv/bin/activate
```

#### 4a. (Optional) Install dependencies and set up the git hook scripts

> [!TIP]
> Skip this step if you only want to run the project on the Pico. Install dependencies and set up git hooks if you want to develop the project.

```
pip install -r requirements-dev.txt
```

```
pre-commit install
```

#### 5. Initialize MicroPico project

- **Right-click** on area in folder/project view.
- In the context menu that appears, select **Initialize MicroPico project**

> After that step the extension will treat the folder as a MicroPico project and enables the right-click commands ("Upload File to Pico", "Run current file on Pico", etc.). Without it, those menu options won't appear.

#### 6. Toggle virtual MicroPico workspace

- At the bottom of vs studio you will see a button with the same name and you should click it

#### 7. Prepare project for work

todo: say about files what should be generated or changed, and config options what should be added

#### 8. Upload Code to Pico

- To upload your code:
  - **Right-click** on the file you want to upload in the side panel (or folder/project view).
  - In the context menu that appears, select **Upload File to Pico**

> You don't need all files on board. You only need: app, config, lib, utils directories and main.py

> [!IMPORTANT]
> Your lib directory must contain two specific files: `lang.py` and `font.py`. An English `lang.py` is included by default, though you can easily replace it with your preferred language. For the `font.py` file, please see the chapter on generating font files using the `write` library.

#### 11. Run the Program

- **Right-click** on the `main.py` in Mpy Remote Workspace.
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

> [!IMPORTANT]
> Your lib directory must contain two specific files: `lang.py` and `font.py`. An English `lang.py` is included by default, though you can easily replace it with your preferred language. For the `font.py` file, please see the chapter on generating font files using the `write` library.

#### 4. Deploying firmware to the device

Firmware can be deployed to the device by putting it into bootloader mode
(hold down BOOTSEL while powering on or resetting) and then either copying
`firmware.uf2` to the USB mass storage device that appears.

> You can find `firmware.uf2` inside build-RPI_PICO_W directory. (schematic path : micropython/ports/rp2/build-RPI_PICO_W)

#### 5. Cleaning unnecessary files from Mpy Remote Workplace

After loading compiled code to firmware, you don't need anymore `app`, `lib`, `utils` directories and `main.py`(if you used `manifest_release.py`), so you can remove it from there. In config directory you need to have: `char_map.json`, `font.py`, `lang.json`(language file).

### How to make font.py for project

todo
