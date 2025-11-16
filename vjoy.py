from time import sleep

import pyvjoy as vjoy

import devices as dev
import variables as var

axis_ref = {
    "weight_jacker": vjoy.HID_USAGE_X,
    "front_roll_bar": vjoy.HID_USAGE_Y,
    "rear_roll_bar": vjoy.HID_USAGE_Z,
    "fuel_map": vjoy.HID_USAGE_RX,
    "bite_point": vjoy.HID_USAGE_RY,
    "engine_warming": vjoy.HID_USAGE_RZ,
    "brake": vjoy.HID_USAGE_SL0,
    "other": vjoy.HID_USAGE_SL1,
}

axis_values = {
    "weight_jacker": 0.5,
    "front_roll_bar": 1.0,
    "rear_roll_bar": 0.0,
    "fuel_map": 0.0,
    "bite_point": 0.0,
    "engine_warming": 0.0,
    "brake": 0.0,
    "other": 0.0,
}

status = {
    "busy": False,
}

j = vjoy.VJoyDevice(1)

def set(axis, pct):
    #print("vjoy set check1")
    while status['busy']: # no queue, just whoever happens to check at the right time first if there are multiple instances of vjoy.set() in this loop
        sleep(0.01)
    status['busy'] = True
    switched = var.status[axis]['switched']
    raw = round(pct * 32768)
    if raw <= 0:
        raw = 1
    elif raw > 32768:
        raw = 32768

    j.set_axis(axis_ref[axis], raw)
    axis_values[axis] = round(raw / 32768, 3)
    if switched:
        var.status[axis]['secondary'] = axis_values[axis]
        #print("new secondary: ", var.status[axis]['secondary'])
    else:
        var.status[axis]['primary'] = axis_values[axis]
        #print("new primary: ", var.status[axis]['primary'])
    status['busy'] = False

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
    sleep(1.0)
    j.update()
    set("weight_jacker", 0.5)
    set("front_roll_bar", 1.0)
    set("rear_roll_bar", 0.0)
    set("fuel_map", 0.0)
    set("bite_point", 0.0)
    set("engine_warming", 0.0)
    set("brake", 0.0)
    set("other", 0.0)

def find_instance():
    for device in dev.device_info:
        if "vJoy" in dev.device_info[device]['name']:
            var.status['vjoy_instance'] = dev.device_info[device]['instance']