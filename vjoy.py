from time import sleep

import pyvjoy as vjoy

import devices as dev
import variables as var

axis_ref = {
    "weight_jacker": vjoy.HID_USAGE_X,
    "front_roll_bar": vjoy.HID_USAGE_Y,
    "rear_roll_bar": vjoy.HID_USAGE_Z,
    "fuel_map": vjoy.HID_USAGE_RX,
    "clutch": vjoy.HID_USAGE_RY,
    "throttle": vjoy.HID_USAGE_RZ,
    "regen": vjoy.HID_USAGE_SL0,
    "deploy": vjoy.HID_USAGE_SL1,
    "brake": vjoy.HID_USAGE_WHL,
}

axis_values = {
    "weight_jacker": 0.5,
    "front_roll_bar": 1.0,
    "rear_roll_bar": 0.0,
    "fuel_map": 0.0,
    "clutch": 0.0,
    "throttle": 0.0,
    "regen": 0.0,
    "deploy": 0.0,
    "brake": 0.0,
}

axis_busy = {
    "weight_jacker": False,
    "front_roll_bar": False,
    "rear_roll_bar": False,
    "fuel_map": False,
    "clutch": False,
    "throttle": False,
    "regen": False,
    "deploy": False,
    "brake": False,
}

try:
    j = vjoy.VJoyDevice(1)
except:
    raise TypeError("\n\n**vjoy set up failed**\n- Check to make sure vjoy is running\n- Check if an instance of this app is already running\n")

queue = []
number = 0

def set(axis, pct):
    global number
    print("vjoy set check1")
    if axis_busy[axis]:
        local_number = number
        queue.append(local_number)
        # print("queue number ", local_number)
        number += 1
        while queue[0] != local_number: # queue
            sleep(0.01)
        check = queue.pop()
        if check != local_number: # only for debugging
            print("queue order error in vjoy.py!!!")
    axis_busy[axis] = True
    switched = var.status[axis]['switched']
    raw = round(pct * 32768)
    if raw <= 0:
        raw = 1
        pct = 0.0
    elif raw > 32768:
        raw = 32768
        pct = 1.0
    print("try set using: ", axis, pct)
    j.set_axis(axis_ref[axis], raw)
    axis_values[axis] = pct
    if switched:
        var.status[axis]['secondary'] = axis_values[axis]
        print("new secondary: ", var.status[axis]['secondary'])
    else:
        var.status[axis]['primary'] = axis_values[axis]
        print("new primary: ", var.status[axis]['primary'])
    axis_busy[axis] = False

def calibrate(axis):
    #var.status['calibration'] = True
    while var.status[axis]['thread']['waiting']: #wait for any hold loops to finish
        sleep(0.05)
    step = 0.01
    pct = 0.0
    while pct < 1.0:
        set(axis, pct)
        pct = pct + step
        sleep(0.005)
    while pct > 0:
        set(axis, pct)
        pct = pct - step
        sleep(0.005)
    set(axis,0.0)
    sleep(0.25)

    #var.status['calibration'] = False

def intialize():
    j.update()
    set("weight_jacker", 0.5)
    set("front_roll_bar", 1.0)
    set("rear_roll_bar", 0.0)
    set("fuel_map", 0.0)
    set("clutch", 0.0)
    set("throttle", 0.0)
    # set("regen", 4/9) # 0.5 in sim
    # set("deploy", 4/9) # 0.5 in sim
    set("brake", 0.0)

def find_instance():
    for device in dev.device_info:
        if "vJoy" in dev.device_info[device]['name']:
            var.status['vjoy_instance'] = dev.device_info[device]['instance']