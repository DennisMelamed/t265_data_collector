#!/usr/bin/python
# -*- coding: utf-8 -*-
## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2019 Intel Corporation. All Rights Reserved.

#####################################################
##           librealsense T265 example             ##
#####################################################

# First import the library
import pyzed.sl as sl
import time
from dashing import *
import serial
import os


## TODO setup zed camera

ui = HSplit(
        VSplit(
            Log("Timestamp", color= 3, border_color = 5),
            Log("OLA Data", color= 3, border_color = 5),
        ),
        VSplit(
            HGauge(val=0, title="tracker accuracy", border_color=5),
            HGauge(val=0, title="mapper accuracy", border_color=5),
        )
    )


run_dashing_display = True
def update_display():
    if run_dashing_display:
        ui.display()

update_display()


update_dx = -1
start_time = time.time()

## open a serial terminal here, should lead to a logging start on the OLA if its in deep sleep mode
with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser:
    ui.items[0].items[0].append("system started")
    update_display()
    ## pull out the init info from the OLA
    for idx in range(16):
        ui.items[0].items[1].append(str(ser.readline()))
    update_display()

    with open(f"zed_data/{time.time()}.txt", 'w') as f:
        f.write("timestamp,posX,posY,posZ,quatW,quatX,quatY,quatZ,tracking_confidence,mapping_confidence,zed_aX,zed_aY,zed_aZ,zed_gX,zed_gY,zed_gZ\n")
        try:
            while True:

                ## TODO get pose & IMU data 

                    f.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(pose.timestamp,
                                                                                    data.translation.x,
                                                                                    data.translation.y,
                                                                                    data.translation.z,
                                                                                    data.rotation.w,
                                                                                    data.rotation.x,
                                                                                    data.rotation.y,
                                                                                    data.rotation.z,
                                                                                    data.tracker_confidence,
                                                                                    data.mapper_confidence,
                                                                                    accel.x,
                                                                                    accel.y,
                                                                                    accel.z,
                                                                                    gyro.x,
                                                                                    gyro.y,
                                                                                    gyro.z,
                                                                                    ))

                    update_dx += 1
                    if update_dx % 60 == 0 and run_dashing_display:
                        ui.items[1].items[0].value = (data.tracker_confidence+1)*25
                        ui.items[1].items[1].value = (data.mapper_confidence+1)*25
                        ui.items[0].items[0].append(str((time.time() - start_time)/60))
                        ui.items[0].items[1].append(str(ser.readline()))
                        update_display()
                        update_dx = 0

        finally:
            ui.items[0].items[0].append("shutting down")
            update_display()

            ## send close commands to OLA ( newline, q, then y)
            ser.write(b'\n')
            time.sleep(2)
            ser.write(b'q')
            time.sleep(2)
            ser.write(b'y')

            ## TODO shutdown zed

            os.system("clear")
            print("done")
