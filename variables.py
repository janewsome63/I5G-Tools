import os

lang = {
    "title": "I5G Tools",
    "version": "v0.4.5b",
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
    "axis_samples": "Number of Axis Samples:",
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
    "settings_filename": "Current Settings File:",
    "axes_display": "Display",
    "car_id": "Car ID:",
    "soc": "SoC",
    "hybrid": "Hybrid",
    "sound_label": "Sound:",
    "volume_label": "Volume:",
}

bindings = {
    "status": {
        "active": False,
        "function": None,
        "control": None,
    },
    "weight_jacker": {
        "up": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "down": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "switch": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
    },
    "front_roll_bar": {
        "up": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "down": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "switch": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
    },
    "rear_roll_bar": {
        "up": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "down": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "switch": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
    },
    "fuel_map": {
        "up": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "down": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "switch": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
    },
    "clutch": {
        "pedal": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "up": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "down": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "switch": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
    },
    "throttle": {
        "pedal":{
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "up": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "down": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "switch": {
            "guid": 0,
            "type": "none",
            "num": 0,
        },
    },
}

settings = {
    "high_threshold": 0.90,
    "low_threshold": 0.10,
    "frequency": 0.1,
    "scale": 1.25,
    "axis_samples": 2,
    "timer_loop": 150,
    "timer_first": 300,

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
    "audio": {
        "on": False,
        "volume": 0.5,
    }
}

status = {
    "calibration": False,
    "devices_loaded": False,
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
    # "regen": {
    #     "primary": 0.25,
    #     "secondary": 0.9,
    #     "switched": False,
    #     "thread": {
    #         "current": 0,
    #         "running": {
    #             "up": False,
    #             "down": False
    #         },
    #         "waiting": False,
    #     },
    # },
    # "deploy": {
    #     "primary": 0.25,
    #     "secondary": 0.9,
    #     "switched": False,
    #     "thread": {
    #         "current": 0,
    #         "running": {
    #             "up": False,
    #             "down": False
    #         },
    #         "waiting": False,
    #     },
    # },
}

event = {
    "guid": 0,
    "type": "",
    "num": 0,
    "value": None,
}

settings_active = "settings.ini" #default

settings_old = ""

backend = {
    "config": os.path.expanduser("~") + "\\AppData\\Local\\I5G Tools" + "\\" + settings_active,
    "whitelist": (38722, 41368, 64400, 90193, 93858, 114220, 153763, 167574, 288105, 509505),
}

sound_folder = {
    "config": os.path.expanduser("~") + "\\AppData\\Local\\I5G Tools\\Sound FX\\"
}

settings_list = []