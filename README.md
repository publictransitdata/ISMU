# ISMU
Information system master unit

## How to Run the Project on Raspberry Pi Pico Using VSCode
### Prerequisites
1. **Hardware:**
    - Raspberry Pi Pico W.
    - USB cable with data transfer capability.

2. **Software:**
    - [Visual Studio Code (VSCode)](https://code.visualstudio.com/) installed.
    - VSCode Extension: MicroPico.
    - Python 3.x (preferably version 3.11 or newer).
    - MicroPython UF2 file installed on the Raspberry Pi Pico W. 
> Follow the [official MicroPython setup guide](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) for installing it on your Pico.

### Steps to Configure and Run the Project
#### 1. Install and Configure **MicroPico** Extension
- Open Visual Studio Code.
- Go to the **Extensions** panel and install the **MicroPico** extension.
- After installing, ensure your Raspberry Pi Pico is connected to your computer via USB.

#### 2. Clone the Project Repository
- Copy the repository to your local machine:
``` bash
  git clone https://github.com/publictransitdata/ISMU.git
  cd ISMU
```
#### 3. Make Sure Required Files Are in Place
- Ensure Python files for your project are located in a directory that will be synced to the Pico. Typically, this is the project’s root directory.

#### 4. Open the Project in VSCode
- Launch Visual Studio Code and open the project directory:
``` bash
  code .
```
#### 5. Upload Code to Pico
- To upload your code:
  - **Right-click** on the file you want to upload in the side panel (or folder/project view).
  - In the context menu that appears, select **Upload File to Pico**

#### 6. Run the Script
  - **Right-click** on the file you want to run in the side panel (In Mpy Remote Workspace).
  - In the context menu that appears, select **run current file on Pico**