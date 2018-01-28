#!/usr/bin/python
# -*- coding: utf-8 -*-

# First import the library
import pyzed.sl as sl
import time
from dashing import *
import serial
import os
from datetime import datetime
import Jetson.GPIO as GPIO

user_button_pressed = False
def cb(channel):
    global user_button_pressed
    user_button_pressed = True
    GPIO.output(high_pin, GPIO.HIGH)

pin = 'MCLK05' #'UART1_RTS' #'SOC_GPIO54'
high_pin = 'UART1_RTS'
GPIO.setmode(GPIO.CVM)#TEGRA_SOC)
GPIO.setup(pin, GPIO.IN)
GPIO.setup(high_pin, GPIO.OUT, initial = GPIO.LOW)
GPIO.add_event_detect(pin, GPIO.RISING, callback = cb, bouncetime = 200)
print("GPIO setup finished")

## TODO setup zed camera
init = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD720,
                             coordinate_units=sl.UNIT.METER,
                             coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP)
zed = sl.Camera()
status = zed.open(init)
if status != sl.ERROR_CODE.SUCCESS:
    print(repr(status))
    exit()

tracking_params = sl.PositionalTrackingParameters(_enable_pose_smoothing=False, 
                                                  _set_floor_as_origin = False,
                                                  _enable_imu_fusion = False)
tracking_params.area_file_path = "nsh_chair.area" #"smith.area"
zed.enable_positional_tracking(tracking_params)

runtime = sl.RuntimeParameters()
camera_pose = sl.Pose()

camera_info = zed.get_camera_information()

py_translation = sl.Translation()
py_orientation = sl.Orientation()
pose_data = sl.Transform()
sensors_data = sl.SensorsData()

text_translation = ""

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
#with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser:
ui.items[0].items[0].append("system started")
ui.items[0].items[1].append("not using OLA")
#    update_display()
    ## pull out the init info from the OLA
#    for idx in range(16):
#        ui.items[0].items[1].append(str(ser.readline()))
update_display()

curDT = datetime.now()
file_str = curDT.strftime("%Y-%m-%d-%H:%M:%S")
with open("/home/dennis/t265_data_collector/zed_data/{}.txt".format(file_str), 'w') as f:
    f.write("timestamp,posX,posY,posZ,quatW,quatX,quatY,quatZ,tracking_confidence,mapping_confidence,zed_aX,zed_aY,zed_aZ,zed_gX,zed_gY,zed_gZ,button\n")
    try:
        while True:

            ## TODO get pose & IMU data 
            if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
                tracking_state = zed.get_position(camera_pose)
                zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.CURRENT)
                tracking_confidence = 0
                mapping_confidence = 0
                button = 0

                if user_button_pressed:
                    button = 1
                    user_button_pressed = False
                    GPIO.output(high_pin, GPIO.LOW)
                if tracking_state == sl.POSITIONAL_TRACKING_STATE.OK:
                    rotation = camera_pose.get_orientation().get()
                    translation = camera_pose.get_translation(py_translation).get()
                    acc = sensors_data.get_imu_data().get_linear_acceleration()
                    gyro = sensors_data.get_imu_data().get_angular_velocity()
                    tracking_confidence = camera_pose.pose_confidence
                    mapping_confidence = 1
#                    pose_data = camera_pose.pose_data(sl.Transform())

                    f.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(camera_pose.timestamp.data_ns,
                                                                                translation[0],
                                                                                translation[1],
                                                                                translation[2],
                                                                                rotation[3],
                                                                                rotation[0],
                                                                                rotation[1],
                                                                                rotation[2],
                                                                                tracking_confidence,
                                                                                mapping_confidence,
                                                                                acc[0],
                                                                                acc[1],
                                                                                acc[2],
                                                                                gyro[0],
                                                                                gyro[1],
                                                                                gyro[2],
                                                                                button,
                                                                                ))

                update_dx += 1
                if update_dx % 60 == 0 and run_dashing_display:
                    ui.items[1].items[0].value = (tracking_confidence+1)
                    ui.items[1].items[1].value = (mapping_confidence+1)*50
                    ui.items[0].items[0].append(str((time.time() - start_time)/60))
        #            ui.items[0].items[1].append(str(ser.readline()))
                    update_display()
                    update_dx = 0

    finally:
        ui.items[0].items[0].append("shutting down")
        update_display()

#            ## send close commands to OLA ( newline, q, then y)
#            ser.write(b'\n')
#            time.sleep(2)
#            ser.write(b'q')
#            time.sleep(2)
#            ser.write(b'y')

        ## TODO shutdown zed
        zed.close()

        GPIO.cleanup()

        os.system("clear")
        print("done")
