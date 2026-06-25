from time import sleep

import pyvjoy as vjoy

import devices as dev
import variables as var
import functions as fn

axis_ref = {
    "weight_jacker": vjoy.HID_USAGE_X,
    "front_roll_bar": vjoy.HID_USAGE_Y,
    "rear_roll_bar": vjoy.HID_USAGE_Z,
    "fuel_map": vjoy.HID_USAGE_RX,
    "clutch": vjoy.HID_USAGE_RY,
    "throttle": vjoy.HID_USAGE_RZ,
    "regen_rate": vjoy.HID_USAGE_SL0,
    "deploy_rate": vjoy.HID_USAGE_SL1,
}

axis_values = {
    "weight_jacker": 0.5,
    "front_roll_bar": 1.0,
    "rear_roll_bar": 0.0,
    "fuel_map": 0.0,
    "clutch": 0.0,
    "throttle": 0.0,
    "regen_rate": 1.0,
    "deploy_rate": 1.0,
}

axis_busy = {
    "weight_jacker": False,
    "front_roll_bar": False,
    "rear_roll_bar": False,
    "fuel_map": False,
    "clutch": False,
    "throttle": False,
    "regen_rate": False,
    "deploy_rate": False,
}

button_ref = {
    "regen": 1,
    "deploy": 2,
}

try:
    j = vjoy.VJoyDevice(1)
except:
    raise TypeError("\n\n**vjoy set up failed**\n- Check to make sure vjoy is running\n- Check if an instance of this app is already running\n")

queue = []
number = 0

def set_axis(axis, pct):
    try:
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
        if var.settings[axis]['rollover_mode']:
            if pct < -0.004:
                pct = 1.0
            elif pct > 1.004:
                pct = 0.0
        if pct > 1.0:
            pct = 1.0
        elif pct < 0.0:
            pct = 0.0
        else:
            pct = round(pct, 5)
        raw = round(pct * 32768)
        if raw <= 0:
            raw = 1
            pct = 0.0
        elif raw > 32768:
            raw = 32768
            pct = 1.0
        print("try set using: ", axis, raw, pct)
        j.set_axis(axis_ref[axis], raw)
        axis_values[axis] = pct
        if switched:
            var.status[axis]['secondary'] = axis_values[axis]
            print("new secondary: ", var.status[axis]['secondary'])
        else:
            var.status[axis]['primary'] = axis_values[axis]
            print("new primary: ", var.status[axis]['primary'])
        axis_busy[axis] = False
    except Exception as e:
        fn.error_handling(e, "vjoy.set_axis()")

def set_button(button, state):
    try:
        print("try set using: ", button, button_ref[button], state)
        j.set_button(button_ref[button], state)
    except Exception as e:
        fn.error_handling(e, "vjoy.set_button()")

def calibrate_axis(axis):
    try:
        #var.status['calibration'] = True
        while var.status[axis]['thread']['waiting']: #wait for any hold loops to finish
            sleep(0.05)
        step = 0.01
        pct = 0.0
        while pct < 1.0:
            set_axis(axis, pct)
            pct = pct + step
            sleep(0.005)
        set_axis(axis, pct)
        sleep(0.05) # make sure iRacing reads the max value
        set_axis(axis, pct)
        sleep(0.125)
        while pct > 0:
            set_axis(axis, pct)
            pct = pct - step
            sleep(0.005)
        set_axis(axis, 0.0)
        sleep(0.25)

        #var.status['calibration'] = False
    except Exception as e:
        fn.error_handling(e, "vjoy.calibrate()_axis")

def calibrate_button(button):
    try:
        set_button(button, True)
        sleep(0.25)
        set_button(button, False)
    except Exception as e:
        fn.error_handling(e, "vjoy.calibrate()_axis")

def intialize():
    try:
        j.update()
        set_axis("weight_jacker", 0.5)
        set_axis("front_roll_bar", 1.0)
        set_axis("rear_roll_bar", 0.0)
        set_axis("fuel_map", 0.0)
        set_axis("clutch", 0.0)
        set_axis("throttle", 0.0)
        # set("regen_rate", 1.0)
        # set("deploy_rate", 1.0)
        set_button("regen", False)
        set_button("deploy", False)
    except Exception as e:
        fn.error_handling(e, "vjoy.initialize()")

def find_instance():
    try:
        for device in dev.device_info:
            if "vJoy" in dev.device_info[device]['name']:
                var.status['vjoy_instance'] = dev.device_info[device]['instance']
    except Exception as e:
        fn.error_handling(e, "vjoy.find_instance()")