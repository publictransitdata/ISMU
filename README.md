# ISMU

Information system master unit

## Overview

ISMU is an open source project that is used to control passenger information systems over IBIS (VDV300) protocol. This solution is specifically designed and developed for public transit applications.

This repository provides all the necessary code, documentation and resources to run it on Raspberry Pi Pico W

### Target Audience

- **Public transit agencies**: small and large operators who need an affordable, fully customizable control unit for passenger information systems.

- **System integrators**: teams deploying or maintaining IBIS-compatible display systems who need a ready-made, configurable solution.

- **Embedded developers and makers**: developers and enthusiasts working on transit-related projects.

## Documentation

Extended documentation is available in the [project Wiki](https://github.com/publictransitdata/ISMU/wiki)

> [!NOTE]
> The wiki is coming soon.


## How to Run the Project on Raspberry Pi Pico W Using VSCode

### Prerequisites

1. **Hardware:**

- Raspberry Pi Pico W.
- OLED SH1106 I2C screen.
- 4 normally opened push buttons or 4 button matrix keypad.
- IBIS (VDV300) module with UART connection.
- USB cable with data transfer capability.

1.1. **Connections**

| Pi Pico W    | Devices             |
|--------------|---------------------|
| GPIO 0 (TX)  | IBIS module RX      |
| GPIO 1 (RX)  | IBIS module TX      |
| GPIO 2       | Button Down         |
| GPIO 3       | Button Select       |
| GPIO 4       | Button Menu         |
| GPIO 5       | Button Up           |
| GPIO 10 (SDA)| SH1106 SDA          |
| GPIO 11 (SCL)| SH1106 SCL          |


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

Copy the repository to your local machine:

```bash
  git clone https://github.com/publictransitdata/ISMU.git
  cd ISMU
```

#### 3. Open the Project in VSCode

Launch Visual Studio Code and open the project directory:

```bash
  code .
```

#### 4. Initialize virtual environment in project directory

```bash
python -m venv .venv
source .venv/bin/activate
```

#### 4a. (Optional) Install dependencies and set up the git hook scripts

> [!NOTE]
> Skip this step if you only want to run the project on the Pico. Install dependencies and set up git hooks if you want to develop the project.

```bash
pip install -r requirements-dev.txt
```

```bash
pre-commit install
```

#### 5. Initialize MicroPico project

**Right-click** on area in folder/project view.
In the context menu that appears, select **Initialize MicroPico project**

> [!NOTE]
> After that step the extension will treat the folder as a MicroPico project and enables the right-click commands ("Upload File to Pico", "Run current file on Pico", etc.). Without it, those menu options won't appear.

#### 6. Toggle virtual MicroPico workspace

Click the "Toggle MicroPico Virtual Workspace" button in the VS Code status bar at the bottom.

#### 7. Prepare project for work

To run the project you will need to create or configure the following files:

- **`font.py`** (**lib** directory)
  See the chapter on font generation for details.

- **`lang.py`** (**lib** directory)
  By default the interface is in English. You can modify `lang.py` to use your preferred language — just replace the key values with your translations and make sure your font file includes any language-specific symbols.

  > [!IMPORTANT]
  > You must add language-specific symbols to the font file for correct text rendering on screen. See the chapter on font generation.

- **`char_map.json`** (**config** directory) _(optional)_
  Only needed if your monitors use non-standard ASCII symbols.

  See the [char_map.json format](todo: add wiki link) wiki page for details.

  > [!IMPORTANT]
  > To enable `char_map.json`, set `"use_char_map": true` in `config.json`. Without this setting, the file will be ignored even if it is present in the correct directory.

- **`routes.ndjson`** (**config** directory)
  You can add this file before starting the project, or upload it later via theweb server in update mode. See the [routes.ndjson format](https://github.compublictransitdata/ISMU/wiki/routes.ndjson-format) wiki page for details.

  todo: fix link when wiki will be created

  > [!TIP]
  > Coming soon: a dedicated service to generate `routes.ndjson` automatically.

- **`config.json`** (**config** directory)
  You can add this file before starting the project, or upload it later via theweb server in update mode. See the [config.json format](https://github.compublictransitdata/ISMU/wiki/config.json-format) wiki page for details.

  todo: fix link when wiki will be created

  > [!TIP]
  > Coming soon: a dedicated service to generate `config.json` automatically.

#### 8. Upload Code to Pico

To upload your code:

- **Right-click** on the file you want to upload in the side panel (or folder/project view).
- In the context menu that appears, select **Upload File to Pico**

> [!TIP]
> You don't need all files on board. You only need: **app**, **config**, **lib**, **utils** directories and main.py

> [!IMPORTANT]
> Your lib directory must contain two specific files: `lang.py` and `font.py`. An English `lang.py` is included by default, though you can easily replace it with your preferred language. For the `font.py` file, please see [How to generate `font.py`](#how-to-generate-fontpy) chapter.

> [!IMPORTANT]
> If `"use_char_map": true` is set in `config.json`, you must provide `char_map.json` in the **config** directory. See the [char_map.json format](todo: add wiki link)

#### 9. Run the Program

**Right-click** on the `main.py` in Mpy Remote Workspace.
In the context menu that appears, select **run current file on Pico**

> [!TIP]
> Alternatively, right-click main.py in the MicroPython Remote Workspace, then click the Run button at the bottom.

## How to generate `font.py`

This project uses the [**micropython-font-to-py**](https://github.com/peterhinch/micropython-font-to-py) library to convert TTF/OTF fonts into MicroPython-compatible Python files for use with display drivers. The key tool is [`font_to_py.py`](https://github.com/peterhinch/micropython-font-to-py/blob/master/FONT_TO_PY.md) — a command-line utility that takes a font file and a pixel height as input and outputs a `.py` file ready to use on the Pico.

> [!NOTE]
> The steps below cover the most common use case. For full usage options, refer to the [official documentation](https://github.com/peterhinch/micropython-font-to-py/blob/master/FONT_TO_PY.md#3-usage).

#### 1. Clone the library repository

```bash
git clone https://github.com/peterhinch/micropython-font-to-py
cd micropython-font-to-py
```

#### 2. Set up a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

#### 3. Install the `font_to_py` package

```bash
pip install font_to_py
```

#### 4. Generate the font file

font_to_py.py is a command line utility written in Python 3. It is run on a PC. It takes as input a font file with a ttf or otf extension and a required height in pixels and outputs a Python 3 source file. The pixel layout is determined by command arguments. By default fonts are stored in variable pitch form. This may be overidden by a command line argument.

> [!NOTE]
> It is recommended to read original documentation about usage of [font_to_py.py](https://github.com/peterhinch/micropython-font-to-py/blob/master/FONT_TO_PY.md#3-usage).

Examples of usage to produce Python fonts with a height of 14 pixels:

```bash
./font_to_py.py Monotype.ttf 14 lang.py
```

Mandatory positional arguments:

- Font file path. Must be a ttf or otf file.
- Height in pixels. In the case of bdf or pcf files a height of 0 should be specified as the height is retrieved from the file.
- Output file path. Filename must have a .py extension (unless writing a binary font). A warning is output if the output filename does not have a .py extension as the creation of a binary font file may not be intended.

> [!NOTE]
> If you want to use custom alternative character sets for example Cyrillic, Arabic etc. Read [Appendix 4](https://github.com/peterhinch/micropython-font-to-py/blob/master/FONT_TO_PY.md#appendix-4-custom-character-sets)

#### 5. Place the generated file

Copy the generated `font.py` into the **`lib`** directory of the ISMU project.

## How to freeze code and make firmware for Raspberry Pi Pico W board

#### 1. Git clone micropython repo

```bash
git clone https://github.com/micropython/micropython.git
```

#### 2. Go inside cloned directory and build the MicroPython cross-compiler

```bash
cd micropython
make -C mpy-cross
```

#### 3. Build the firmware

```bash
make BOARD=RPI_PICO_W submodules
make BOARD=RPI_PICO_W clean
make -j $(nproc) BOARD=RPI_PICO_W FROZEN_MANIFEST=/path/to/manifest.py/file/inside/ISMU/directory
```

The ISMU directory contains two manifest files. One includes main.py (manifest_release.py) to auto-start the program on power-up, while the other excludes it so you can run the code manually from an IDE.

> [!IMPORTANT]
> Your lib directory must contain two specific files: `lang.py` and `font.py`. An English `lang.py` is included by default, though you can easily replace it with your preferred language. For the `font.py` file, please see the chapter on generating font files using the `write` library.

#### 4. Deploying firmware to the device

Firmware can be deployed to the device by putting it into bootloader mode
(hold down BOOTSEL while powering on or resetting) and then either copying
`firmware.uf2` to the USB mass storage device that appears.

You can find `firmware.uf2` inside build-RPI_PICO_W directory. (schematic path : micropython/ports/rp2/build-RPI_PICO_W)

#### 5. Cleaning unnecessary files from Mpy Remote Workplace

After loading compiled code to firmware, you don't need anymore **app**, **lib**, **utils** directories and `main.py`(if you used `manifest_release.py`), so you can remove it from there. In config directory you need to have: `char_map.json`. In lib directory you need to have: `font.py`, `lang.py`.

## Third‑party licenses

This project includes documentation snippets derived from the **micropython-font-to-py** library.

© 2016 Peter Hinch  
Licensed under the MIT License.

See `THIRD_PARTY_LICENSES/micropython-font-to-py-mit.txt` for the full license text.
