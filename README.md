# Automated Drone Delivery System

![GitHub repo size](https://img.shields.io/github/repo-size/i-akb25/AUTOMATED_DRONE_DELIVERY?color=ff69b4&style=flat-square) ![GitHub stars](https://img.shields.io/github/stars/i-akb25/AUTOMATED_DRONE_DELIVERY?style=social) ![GitHub last commit](https://img.shields.io/github/last-commit/i-akb25/AUTOMATED_DRONE_DELIVERY?color=ff69b4&style=flat-square) 

## Project Overview

The Automated Drone Delivery System is designed to autonomously deliver parcels to a target location and return to the launch point. The drone employs facial recognition to identify the target person, ensuring secure and efficient delivery. Once the target person's face is detected within the camera's field of view, the drone automatically drops the parcel using a servo motor and then returns to the launch point.

## Features

- Autonomous navigation to specified locations.
- Facial recognition for target identification.
- Automatic parcel drop-off using a servo motor.
- Safe return to the launch point after delivery.

## Components

1. **Pixhawk Flight Controller Kit**
2. **Quadcopter Frame S500**
3. **DYS BLDC Motor 1000KV**
4. **ESC 30A**
5. **Propeller (Glass Fiber)**
6. **Radio Telemetry Kit**
7. **GPS Module**
8. **3S 4200mAh 11.1V Battery**
9. **Raspberry Pi Camera**
10. **Raspberry Pi Model 4 B**
11. **Transmitter and Receiver**

## Tools and Technologies

- **Raspberry Pi**
- **Pixhawk Drone**
- **Dronekit Python**
- **Mavlink**
- **Facial Recognition Algorithm**
- **Servo Motor (Micro Servo 9G-SG90)**

---

## Setup and Installation

### Prerequisites

- Download Raspbian OS: [Raspbian Buster](https://downloads.raspberrypi.org/raspios_armhf/images/raspios_armhf-2021-05-28)
- Download IP Scanner: [Advanced IP Scanner](https://www.advanced-ip-scanner.com/)

### Update Raspberry Pi

```bash
sudo apt-get update
sudo apt-get upgrade
sudo reboot
```

### Install Facial Recognition Library

1. Clone the repository and install dependencies:

   ```bash
   sudo apt-get install -y \
   build-essential \
   cmake \
   gfortran \
   git \
   wget \
   curl \
   graphicsmagick \
   libgraphicsmagick1-dev \
   libatlas-base-dev \
   libavcodec-dev \
   libavformat-dev \
   libgtk2.0-dev \
   libjpeg-dev \
   liblapack-dev \
   libswscale-dev \
   pkg-config \
   python3-dev \
   python3-numpy \
   software-properties-common \
   zip
   ```

2. Install **Dlib**:

   ```bash
   git clone https://github.com/davisking/dlib.git
   cd dlib
   mkdir build
   cd build
   cmake ..
   cmake --build .
   cd ..
   sudo python3 setup.py install
   ```

3. Install **face\_recognition**:

   ```bash
   pip3 install face_recognition
   ```

### Configure Raspberry Pi for Pixhawk Communication

1. Install required libraries:

   ```bash
   sudo pip3 install future pyserial dronekit geopy MAVProxy
   sudo apt-get install screen python-wxgtk4.0 libxml2-dev libxslt1-dev
   ```

2. Update Raspberry Pi configuration:

   - Disable login shell and enable serial port hardware.
   - Enable the camera.
   - Enable VNC server (optional).
   - Set the display resolution to the highest setting.

3. Edit the boot configuration:

   ```bash
   sudo nano /boot/config.txt
   ```

   Add the following lines if not already present:

   ```
   enable_uart=1
   ```

dtoverlay=disable-bt \`\`\`

4. Connect the Raspberry Pi to the Pixhawk using wires.
5. Test the connection:
   ```bash
   mavproxy.py --master=/dev/ttyAMA0
   ```

---

## Running the Drone

1. Write and execute the Python script for drone automation:
   ```bash
   python3 drone_automation.py --connect /dev/ttyAMA0
   ```

---

## Python Script Overview

The **drone_automation.py** script manages the following:

- Establishes communication between Raspberry Pi and Pixhawk.
- Integrates facial recognition to detect the target.
- Controls the servo motor to release the parcel.
- Automates the return-to-home functionality.

---

## Commands Summary

- **Update Raspberry Pi:**
  ```bash
  sudo apt-get update && sudo apt-get upgrade
  ```
- **Install Libraries:**
  ```bash
  pip3 install dronekit face_recognition
  ```
- **Test Pixhawk Connection:**
  ```bash
  mavproxy.py --master=/dev/ttyAMA0
  ```
- **Run Drone Script:**
  ```bash
  python3 delivery_drone_yt.py
  ```

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Acknowledgments

- [**Dlib Library**](https://github.com/davisking/dlib) for facial recognition.
- [**Dronekit**](https://github.com/dronekit) for drone control.
- The open-source community for providing excellent resources and tools.

---

Feel free to reach out with questions or feedback!

