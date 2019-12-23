#!/bin/bash
#
# This script installs Crazyflie libraries from Bitcraze AB's GitHub repo and ensures 
#    that udev rules & permissions are configured for complete workstation setup. 
#
# Author: Joseph Haun, Sonoma State University


if [ $EUID -ne 0 ]; then
    echo "This script requires root permissions. Use sudo -H"
    exit 1
fi

LUSER=`whoami`
SCRIPTNAME=$0
INSTALLLOC="/usr/UAVLIBRARIES"

echo "$SCRIPTNAME: Creating $INSTALLLOC"
mkdir $INSTALLLOC
echo "$SCRIPTNAME: Entering $INSTALLLOC"
cd $INSTALLLOC

echo "$SCRIPTNAME: Cloning crazyflie-lib-python.git"
git clone https://github.com/bitcraze/crazyflie-lib-python.git

echo "$SCRIPTNAME: Installing cflib"
pip3 install -e crazyflie-lib-python/

echo "$SCRIPTNAME: Installing cflib dependencies."
pip3 install -r crazyflie-lib-python/requirements.txt

echo "$SCRIPTNAME: Creating User group."
groupadd plugdev
echo "$SCRIPTNAME: Adding User to group."
usermod -a -G plugdev $LUSER

#Creates a  rules file for the CrazyRadio and updates it with correct permissions
echo "$SCRIPTNAME: Creating CrazyRadio udev rules."
FILE="/etc/udev/rules.d/99-crazyradio.rules"
touch $FILE

echo "$SCRIPTNAME: Inserting CrazyRadio udev rules."
if [ -f $FILE ]; then
    echo "$SCRIPTNAME: CrazyRadio udev rules already present."
else
    VAL='SUBSYSTEM=="usb", ATTRS{idVendor}=="1915", ATTRS{idProduct}=="7777", MODE="0664", GROUP="plugdev"'
    echo $VAL >> $FILE
    VAL='SUBSYSTEM=="usb", ATTRS{idVendor}=="1915", ATTRS{idProduct}=="0101", MODE="0664", GROUP="plugdev"'
    echo $VAL >> $FILE
fi


#Creates a rules file for the CrazyFlie drone and updates it with correct permissions
echo "$SCRIPTNAME: Creating CrazyFlie udev rules."
FILE="/etc/udev/rules.d/99-crazyflie.rules"
touch $FILE
if [ -f $FILE ]; then
    echo "$SCRIPTNAME: Crazyflie udev rules already present."
else
    echo "$SCRIPTNAME: Inserting CrazyFlie udev rules."
    VAL='SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE="0664", GROUP="plugdev"'
    echo $VAL >> $FILE
fi

echo "$SCRIPTNAME: Setup complete. A system reset/user logout will be needed to update udev permissions."
