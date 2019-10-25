#!/bin/bash

LUSER=`whoami`
SCRIPTNAME="CrazyRadio Setup"
groupadd plugdev
echo "$SCRIPTNAME: User group created."
usermod -a -G plugdev $LUSER
echo "$SCRIPTNAME: User added to group."

#Creates a  rules file for the CrazyRadio and updates it with correct permissions
FILE="/etc/udev/rules.d/99-crazyradio.rules"
touch $FILE
echo "$SCRIPTNAME: CrazyRadio udev rules created."

VAL='SUBSYSTEM=="usb", ATTRS{idVendor}=="1915", ATTRS{idProduct}=="7777", MODE="0664", GROUP="plugdev"'
echo $VAL >> $FILE
VAL='SUBSYSTEM=="usb", ATTRS{idVendor}=="1915", ATTRS{idProduct}=="0101", MODE="0664", GROUP="plugdev"'
echo $VAL >> $FILE
echo "$SCRIPTNAME: CrazyRadio udev rules inserted."


#Creates a rules file for the CrazyFlie drone and updates it with correct permissions
FILE="/etc/udev/rules.d/99-crazyflie.rules"
touch $FILE
echo "$SCRIPTNAME: CrazyFlie udev rules created."
VAL='SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE="0664", GROUP="plugdev"'
echo $VAL >> $FILE
echo "$SCRIPTNAME: CrazyFlie udev rules inserted."


