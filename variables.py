import copy
import os

lang = {
    "title": "I5G Tools",
    "version": "v0.5.1b",
    "pedal": "Pedal Axis:",
    "up": "Increase:",
    "down": "Decrease:",
    "switch": "Switch:",
    "increment": "Increment:",
    "switch_value": "Switch Value:",
    "switch_mode": "Switch Mode:",
    "hold": "Hold",
    "toggle": "Toggle",
    "increment_mode": "Increment Mode:",
    "continuous": "Continuous",
    "single": "Single",
    "bind": "Bind",
    "binding": "<-Binding->",
    "calibrate": "Calibrate",
    "calibrating": "<-Calibrating->",
    "high_threshold": "High Axis Threshold:",
    "low_threshold": "Low Axis Threshold:",
    # "axis_samples": "Number of Axis Samples:",
    "scale": "Scale Factor:",
    "timer_loop": "Continuous Mode Loop Timer (in ms):",
    "timer_first": "Continuous Mode Initial Loop Timer (in ms)",
    "none": "None",
    "weight_jacker": "Weight Jacker",
    "front_roll_bar": "Front Bar",
    "rear_roll_bar": "Rear Bar",
    "fuel_map": "Fuel Map",
    "clutch": "Clutch",
    "throttle": "Throttle",
    "regen": "Regen",
    "deploy": "Deploy",
    "deploy_lim": "Deploy Limit:",
    "settings": "Settings",
    "create": "Create",
    "delete": "Delete",
    "profile_create": "Create Profile:",
    "profile_select": "Select Profile:",
    "axes_display": "Display",
    "car_id": "Car ID:",
    "soc": "SoC",
    "hybrid": "Hybrid",
    "sound_label": "Sound:",
    "volume_label": "Volume:",
    "section_errors": {
        "config": {
            "title": "I5G Tools  -  Unknown sections in global config file!",
            "intro": "There are sections in the global config file that are not recognized by this version of the program. The unknown sections have the following names:\n\n",
            "outro": "\nIf this settings file is used, any settings related to the unrecognized sections listed above will be deleted.\n\n"
                    "Pressing OK will open the app and delete all settings related to the unrecognized sections.\n"
                    "Pressing Cancel will close the app now if you want to manually backup the global config file before opening this app again.\nProceed?",
        },
        "profile": {
            "title": "I5G Tools  -  Unknown sections in profile config file!",
            "intro": "There are sections in the profile config file that are not recognized by this version of the program. The unknown sections have the following names:\n\n",
            "outro": "\nIf this settings file is used, any settings related to the unrecognized sections listed above will be deleted.\n\n"
                    "Pressing OK will open the app and delete all settings related to the unrecognized sections.\n"
                    "Pressing Cancel will close the app now if you want to manually backup the profile config file before opening this app again.\nProceed?",
        },
    },
    "not_found":{
        "config": {
            "title": "I5G Tools  -  Global settings file not found!",
            "body": "The global settings file does not exist.\n"
                    "Pressing OK will create a default global settings file if you are okay with loading in with a default global settings file.\n"
                    "Pressing Cancel will close the app now if you want to add the global settings file back into the I5G Tools folder before opening this app again.\n"
                    "Proceed?",
        },
        "profile": {
            "title": "I5G Tools  -  Config file listed in global settings file not found!",
            "intro": "The config file that was last open does not exist anymore. The config file that was last open was named:\n\n",
            "outro": "\n\n"
                    "Pressing OK will open the app and switch back to the Default config file (or create a new blank Default config file if Default.ini doesn't exist).\n"
                    "Pressing Cancel will close the app now if you want to add this config file back into the profiles folder before opening this app again.\n"
                    "Proceed?",
        },
    },
    "settings_version": "v0.5.0b" # the version written down in the settings/global file, not necessarily equal to the program current version (to avoid breaking profile/global backwards compatibility unnecessarily)
}

step = {
    "weight_jacker": 1 / (41 - 1),
    "front_roll_bar": 1 / (6 - 1),
    "rear_roll_bar": 1 / (6 - 1),
    "fuel_map": 1 / (8 - 1),
    "clutch": 1 / (201 - 1),
    "throttle": 1 / (201 - 1),
    "regen": 1 / (1.0 - 0.5),
    "deploy": 1 / (1.0 - 0.1),
}

bindings = {
    "status": {
        "active": False,
        "function": None,
        "control": None,
    },
    "weight_jacker": {
        "up": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "down": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "switch": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
    },
    "front_roll_bar": {
        "up": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "down": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "switch": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
    },
    "rear_roll_bar": {
        "up": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "down": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "switch": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
    },
    "fuel_map": {
        "up": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "down": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "switch": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
    },
    "clutch": {
        "pedal": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "up": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "down": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "switch": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
    },
    "throttle": {
        "pedal": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "up": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "down": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "switch": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
    },
}

bindings_cache = copy.deepcopy(bindings)

settings = {
    "frequency": 0.1,
    "scale": 1.25,
    "axis_samples": 2, # constant, not really a setting anymore
    "timer_loop": 150,
    "timer_first": 300,
    "config": "global.ini",
    "path": os.path.expanduser("~") + "\\AppData\\Local\\I5G Tools",

    "sound": {
        "path": "sfx",
        "hybrid_high": "high.mp3",
        "hybrid_low": "low.mp3",
        "hybrid_limit": "limit.mp3",
    },

    "profile": {
        "current": "Default",
        "path": "profiles",
    },

    "local": {
        "high_threshold": 0.90,
        "low_threshold": 0.10,
        "audio": False,
        "volume": 0.5,
    },

    "weight_jacker": {
        "continuous": True,
        "toggle": False,
        "increment": 1,
        "switch_value": -20,
    },
    "front_roll_bar": {
        "continuous": False,
        "toggle": False,
        "increment": 1,
        "switch_value": 1,
    },
    "rear_roll_bar": {
        "continuous": False,
        "toggle": False,
        "increment": 1,
        "switch_value": 6,
    },
    "fuel_map": {
        "continuous": False,
        "toggle": True,
        "increment": 1,
        "switch_value": 8,
    },
    "clutch": {
        "continuous": False,
        "toggle": False,
        "increment": 0.1,
        "switch_value": 50,
    },
    "throttle": {
        "continuous": False,
        "toggle": False,
        "increment": 0.1,
        "switch_value": 50,
    },
}

status = {
    "calibration": False,
    "devices_loaded": False,
    "key_prev": None,
    "profile_prev": "None",
    "profile_list": [],
    "first": False,
    "rewrite":{
        "config": False,
        "profile": False,
    },
    "weight_jacker": {
        "primary": 0.5,
        "secondary": 0.0,
        "switched": False,
        "thread": {
            "running": {
                "up": False,
                "down": False
            },
            "waiting": False,
        },
    },
    "front_roll_bar": {
        "primary": 1.0,
        "secondary": 0.0,
        "switched": False,
        "thread": {
            "current": 0,
            "running": {
                "up": False,
                "down": False
            },
            "waiting": False,
        },
    },
    "rear_roll_bar": {
        "primary": 0.0,
        "secondary": 1.0,
        "switched": False,
        "thread": {
            "current": 0,
            "running": {
                "up": False,
                "down": False
            },
            "waiting": False,
        },
    },
    "fuel_map": {
        "primary": 0.0,
        "secondary": 1.0,
        "switched": False,
        "thread": {
            "current": 0,
            "running": {
                "up": False,
                "down": False
            },
            "waiting": False,
        },
    },
    "clutch": {
        "primary": 0.0,
        "secondary": 0.5,
        "switched": False,
        "thread": {
            "current": 0,
            "running": {
                "up": False,
                "down": False,
                "pedal": False
            },
            "waiting": False,
        },
    },
    "throttle": {
        "primary": 0.0,
        "secondary": 0.2,
        "switched": False,
        "thread": {
            "current": 0,
            "running": {
                "up": False,
                "down": False,
                "pedal": False
            },
            "waiting": False,
        },
    },
    "brake": {
        "primary": 0.0,
        "secondary": 0.2,
        "switched": False,
        "thread": {
            "current": 0,
            "running": {
                "up": False,
                "down": False
            },
            "waiting": False,
        },
    },
}

event = {
    "guid": 0,
    "type": "",
    "num": 0,
    "value": None,
}

backend = {
    "whitelist": (38722, 41368, 64400, 90193, 93858, 114220, 153763, 167574, 288105, 509505),
}

profile_list = []