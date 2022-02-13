# MidiPi
This is an early stage development project which hopes to createa a simple midi synth on a raspberry pi

I have a midi controller and keyboard with no audio output. I'd like to be able to plug it into a raspberry pi to make a portable instrument with very simple controls.

Hardware:
AKAI MPK mini MKII

Raspberry Pi with Raspbian GNU/Linux 11 (bullseye)
Pi Model 4 

Waveshare 1.44" LCD Hat available from: https://www.amazon.co.uk/Waveshare-1-44inch-interface-Direct-pluggable-Raspberry/dp/B077Z7DWW1

## Setup
1) Start with a fresh SD card with Raspberry Pi OS Lite: e.g. https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-11-08/2021-10-30-raspios-bullseye-armhf-lite.zip

2) Enable MIDI settings on boot. Open /boot/config.txt and add the following lines:
    `CONFIG_USB_F_MIDI=m
    CONFIG_USB_CONFIGFS_F_MIDI=y
    CONFIG_USB_MIDI_GADGET=m`

3) Enable SPI for the LCD screen
    `>>> sudo raspi-config`
Choose Interfacing Options -> SPI -> Yes

Install the following libraries:
    `>>> sudo apt install git fluidsynth python3-mido python3-numpy python3-pil python3-rtmidi`

If you want the synth to start when the pi boots you will need to edit the file /etc/rc.local
    `>>> sudo nano /etc/rc.local`
    add the following lines above the line at the end that says exit 0
    
    cd /home/pi/midipi
    ./startsynth.sh
    
