# Instructions

# Required hardware:

  A linux PC

  Raspberry pi model 3B+ (might work on others, probably not on the 4)
  
  SD card >16GB
  
  Crazyradio PA
  
  OpenMV H7 (might work on others)
  
  M12 lens with 940nm bandpass filter, and no infrared cut filter! (ours says xenocam on the side)
  
  power supply for the RasPi
  
  ARAV power switch board
  
  crazyflie 2.0 or 2.1 quadcopter
  
  crazyflie flow deck
  
  crazyflie Qi charger deck
  
  ARAV deck extension PCB
  
  Ethernet cable
 
# Required Software:

apibackup3.img.gz (not included in this repo because it is 6GB)

[OpenMV IDE](https://openmv.io/pages/download)

[ir_track2.py](https://github.com/mcginnisa/UAV-Land-Recharge/blob/master/camera/ir_track2.py)

# Recipe

Flash ir_track2.py onto the OpenMV.

burn the raspi image onto the SD card with a command similar to (if your SD card is mounted at sdc)

```bash
gunzip --stdout -v /media/main/Windows/Users/main/Desktop/apibackup3.img.gz | sudo dd bs=4M of=/dev/sdc
```

Insert SD card into RasPi and connect it to power

Connect RasPi to your linux PC with the ethernet cable, [establish a network between the two](https://askubuntu.com/questions/996963/connecting-pc-and-raspberrypi-using-lan-cable)
 and SSH into it with a command similar to this. The password is uav123

```bash
ssh -X -C uav@192.168.1.104
```

Place the camera pointing up and close to where you want the UAV to land

Connect a RasPi USB port to the input USB port of the ARAV power switch board

Connect the output USB port of the ARAV power switch board to the OpenMV camera

Connect [GPIO physical pin 7](https://pinout.xyz/pinout/pin7_gpio4) to one of the EN pins on the ARAV power switch board

Connect crazyradio PA to RasPi

Insure IR BPF lens is installed in OpenMV cam
 
install the ARAV deck extension PCB, flow deck, and crazyflie Qi charger deck, and battery into the quadcopter

Place the quadcopter close to the camera if the ceiling is not very high (only do this indoors with soft floors)

Run this command on the Pi to launch and land the UAV

```bash
python3 ~/Repositories/UAV-Land-Recharge/main.py
```

