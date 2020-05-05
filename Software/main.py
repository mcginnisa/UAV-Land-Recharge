"""                                                    

      .o.       ooooooooo.         .o.       oooooo     oooo 
     .888.      `888   `Y88.      .888.       `888.     .8'  
    .8"888.      888   .d88'     .8"888.       `888.   .8'   
   .8' `888.     888ooo88P'     .8' `888.       `888. .8'    
  .88ooo8888.    888`88b.      .88ooo8888.       `888.8'     
 .8'     `888.   888  `88b.   .8'     `888.       `888'      
o88o     o8888o o888o  o888o o88o     o8888o       `8'       
                                                             
                                                             
File:      main
Purpose:   This file is a sample main file which makes use of
           the LandingPlatformController and UAVController classes
           implemented by the ARAV team at Sonoma State University
           for the 2020 Senior Design Course.
Author: Joseph Haun, Alexander McGinnis, Anthony Aboumrad
Created: 12-1-2019
Modified: 5-5-2020

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
  MA  02110-1301, USA.

"""

from UAVController import UAVController
from LandingPlatformController import LandingPlatformController

import signal
import sys
import time

LPC = None

def signalHandler(sig, frame):
    global LPC
    if(LPC != None):
        LPC.done()
    
    sys.exit(0)

def main():
    global LPC
    UAV = None
    signal.signal(signal.SIGINT, signalHandler)
    print("MAIN: Attempting to connect to UAV")
    while(UAV == None):
        UAV = UAVController()
    print("MAIN: UAV Connected, Initializing Landing Platform Controller")        
    LPC = None
    settingsArray = dict()
    settingsArray['uav'] = UAV
    while(LPC == None):
        LPC = LandingPlatformController(settings=settingsArray, debug=False)
    print("MAIN: Landing Platform Controller Initialized")
    LPC.engageFlightRoutine()
    LPC.done()

if __name__ == "__main__":
    main()
