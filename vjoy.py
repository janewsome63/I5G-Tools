import pyvjoy as vjoy
import devices as dev
from time import sleep

v = vjoy.VJoyDevice(1)

axis_ref = {
    "x": vjoy.HID_USAGE_X,
    "y": vjoy.HID_USAGE_Y,
    "z": vjoy.HID_USAGE_Z,
    "rx": vjoy.HID_USAGE_RX,
    "ry": vjoy.HID_USAGE_RY,
    "rz": vjoy.HID_USAGE_RZ,
    "sl0": vjoy.HID_USAGE_SL0,
    "sl1": vjoy.HID_USAGE_SL1,
}

def calibrate_axis(axis):
    v.set_axis(axis_ref[axis], 0x8000)
    sleep(0.5)
    v.set_axis(axis_ref[axis], 0x1)
    sleep(0.5)
    v.set_axis(axis_ref[axis], 0x4000)

def set_wj(pct):
    value = int(pct * 32768)
    if value <= 0:
        value = 1
    elif value > 32768:
        value = 32768
    v.set_axis(vjoy.HID_USAGE_X, 0x1 * value)

def find_vjoy():
    for device in dev.device_info:
        if "vJoy" in dev.device_info[device]['name']:
            instance = dev.device_info[device]['instance']
        else:
            instance = 99
    return instance