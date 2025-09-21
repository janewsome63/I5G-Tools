import pyvjoy as vjoy
import devices as dev
import variables as var
from time import sleep

axis_ref = {
    "wj": vjoy.HID_USAGE_X,
    "farb": vjoy.HID_USAGE_Y,
    "rarb": vjoy.HID_USAGE_Z,
    "fuel": vjoy.HID_USAGE_RX,
    "throttle": vjoy.HID_USAGE_RY,
    "clutch": vjoy.HID_USAGE_RZ,
    "brake": vjoy.HID_USAGE_SL0,
    "other": vjoy.HID_USAGE_SL1,
}

axis_values = {
    "wj": 0.5,
    "farb": 1.0,
    "rarb": 0.0,
    "fuel": 0.0,
    "throttle": 0.0,
    "clutch": 0.0,
    "brake": 0.0,
    "other": 0.0,
}

def set(axis, pct):
    raw = round(pct * 32768)
    if raw <= 0:
        raw = 1
    elif raw > 32768:
        raw = 32768
    vjoy.VJoyDevice(var.settings['vjoy_device']).set_axis(axis_ref[axis], raw)
    axis_values[axis] = raw / 32768

def calibrate(axis, pct_end):
    step = 0.05
    pct = 0.0
    while pct <= 1.0:
        set(axis, pct)
        pct = pct + step
    while pct >= 0.0:
        set(axis, pct)
        pct = pct - step
    while pct <= pct_end:
        set(axis, pct)
        pct = pct + step

def intialize():
    sleep(1.0)
    vjoy.VJoyDevice(var.settings['vjoy_device']).update()
    set("wj", 0.5)
    set("farb", 1.0)
    set("rarb", 0.0)
    set("fuel", 0.0)
    set("throttle", 0.0)
    set("clutch", 0.0)
    set("brake", 0.0)
    set("other", 0.0)

def find_instance():
    for device in dev.device_info:
        if "vJoy" in dev.device_info[device]['name']:
            var.status['vjoy_instance'] = dev.device_info[device]['instance']