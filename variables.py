import copy
import os

lang = {
    "title": "I5G Tools",
    "version": "v0.7.0b",
    "settings_version": "v0.7.0b", # identical to version now, compatibility list stored elsewhere
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
    "scale": "Scale Factor (Requires Restart):",
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
    "hybrid_low_audio_label": "Hybrid Low Audio (if Sound is Yes):",
    "hybrid_high_audio_label": "Hybrid High Audio (if Sound is Yes):",
    "hybrid_limit_audio_label": "Hybrid Limit Audio (if Sound is Yes):",
    "hybrid_low_label": "SoC Low Trigger:",
    "hybrid_high_label": "SoC High Trigger:",
    "hybrid_limit_label": "Deploy Limit Trigger:",
    "upshift_beep_label": "Upshift Beep (if Sound is Yes):",
    "downshift_beep_label": "Downshift Beep (if Sound is Yes):",
    "beep_mode_label": "Beep Trigger Mode (Dynamic is experimental):",
    "dynamic_mode_offset_label": "Dynamic Mode Offset (in ms):",
    "upshift_offset_label": "Upshift Trigger Offset from redline (in RPM):",
    "downshift_offset_label": "Downshift Trigger Offset from redline (in RPM):",
    "p2p_behind_audio_label": "Car Behind P2P Single Warning (if Sound is Yes):",
    "p2p_behind_audio_cont_label": "Car Behind P2P Continuous Warning (if Sound is Yes):",
    "p2p_behind_nobrake_label": "Stop P2P Warning Under Braking:",
    "p2p_behind_thresh_label": "P2P Single Warning Threshold (in ms, -1 is any distance):",
    "p2p_behind_thresh_cont_label": "P2P Continuous Warning Threshold (in ms, -1 is any distance):",
    "p2p_behind_closest_car_label": "P2P Warning For Closest Car Behind Only:",
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
    "donate": "Support this app on Ko-Fi",
    "donate_link": "https://ko-fi.com/cmdracer",
    "I5GYT": "Team I5G YouTube",
    "I5GYT_link": "https://www.youtube.com/@TeamI5G",
    "discord": "App Discord (TODO)",
    "discord_link": "https://www.discord.com",
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
        "upshift_beep": "upshift_beep.mp3",
        "downshift_beep": "downshift_beep.mp3",
        "p2p_active": "p2p_behind.mp3",
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
        "hybrid_low_audio": True,
        "hybrid_high_audio": True,
        "hybrid_limit_audio": True,
        "hybrid_low_val": 10,
        "hybrid_high_val": 90,
        "hybrid_limit_val": 100,
        "upshift_beep": False,
        "downshift_beep": False,
        "beep_mode": True,
        "dynamic_mode_offset": 500,
        "upshift_offset": 300,
        "downshift_offset": 450,
        "p2p_behind_audio": False,
        "p2p_behind_audio_cont": False,
        "p2p_behind_nobrake": True,
        "p2p_behind_thresh": int(3000),
        "p2p_behind_thresh_cont": int(1000),
        "p2p_behind_closest_car": True,
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
    "calibration": "None",
    "devices_loaded": False,
    "key_prev": None,
    "profile_prev": "None",
    "profile_list": [],
    "first": False,
    "refresh_labels": False,
    "rewrite":{
        "config": False,
        "profile": False,
    },
    "flash_tab": [],
    "set_list_count": 1,
    "upshift_val": -1,
    "downshift_val": -1,
    "p2p_sound_active": {
        "single": False,
        "loop": False,
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
    "whitelist": (38722, 41368, 64400, 90193, 93858, 114220, 153763, 167574, 288105, 509505, 668169, 821985,
                  693475, 778565, 292374, 909283),
}

compatible_settings = ['v0.6.0b', 'v0.6.1b', 'v0.6.1.1b', 'v0.6.1.2b', 'v0.6.2b', 'v0.6.3b', 'v0.6.4b', 'v0.7.0b']


profile_list = []

potential_bind = {}

gearing = [[]] # the first index is the gear-1 and the second index gives the number of sample points, the current average, and the current variance (std dev squared)
