import functions as fn
import variables as var

from pyglet import input, app
from warnings import catch_warnings, filterwarnings

with catch_warnings():
    filterwarnings("ignore", category=UserWarning)
    controllers = input.get_controllers()
    joysticks = input.get_joysticks()

for controller in controllers:
    controller.open()
    var.devices[controller.device.name] = {
        "guid": controller.device.get_guid(),
        "manufacturer": controller.device.manufacturer,
        "connected": controller.device.connected,
        "intialized": controller.device.is_open,
        "display": controller.device.display,
    }

    @controller.event
    def on_button_press(controller, button_name):
        var.devices[controller.device.name][button_name] = {
            "type": "Button",
            "pressed": True,
        }

        print(controller.device.name, button_name + " " + str(var.devices[controller.device.name][button_name]['pressed']))

    @controller.event
    def on_button_release(controller, button_name):
        var.devices[controller.device.name][button_name] = {
            "type": "Button",
            "pressed": False,
        }

        print(controller.device.name, button_name + " " + str(var.devices[controller.device.name][button_name]['pressed']))

    @controller.event
    def on_stick_motion(controller, axis_name, vector):
        position = fn.separate_vector(vector)

        var.devices[controller.device.name][axis_name] = {
            "type": "Stick",
            "x": position['x'],
            "y": position['y'],
        }

        print(controller.device.name, axis_name + " " + str(var.devices[controller.device.name][axis_name]['x']) + " " + str(var.devices[controller.device.name][axis_name]['y']))

    @controller.event
    def on_trigger_motion(controller, axis_name, vector):
        var.devices[controller.device.name][axis_name] = {
            "type": "Stick",
            "x": vector,
        }

        print(controller.device.name, axis_name + " " + str(var.devices[controller.device.name][axis_name]['x']))

    @controller.event
    def on_dpad_motion(controller, vector):
        position = fn.separate_vector(vector)

        var.devices[controller.device.name]['dpad'] = {
            "type": "D-pad",
            "x": position['x'],
            "y": position['y'],
        }

        print(controller.device.name, 'dpad' + " " + str(var.devices[controller.device.name]['dpad']['x']) + " " + str(var.devices[controller.device.name]['dpad']['y']))

for joystick in joysticks:
    joystick.open()
    @joystick.event
    def on_joybutton_press(joy, button):
        print(joy.device.name, button + " pressed")

    @joystick.event
    def on_joybutton_release(joy, button):
        print(joy.device.name, button + " released")

    @joystick.event
    def on_joyaxis_motion(joy, axis, value):
        print(joy.device.name, axis, value)

    @joystick.event
    def on_joyhat_motion(joy, hat_x, hat_y):
        print(joy.device.name, hat_x, hat_y)

app.run()