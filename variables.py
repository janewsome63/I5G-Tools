import copy
import os

compatible_settings = ['v0.6.0b', 'v0.6.1b', 'v0.6.1.1b', 'v0.6.1.2b', 'v0.6.2b', 'v0.6.3b', 'v0.6.4b', 'v0.7.0b',
                       'v0.7.1b', 'v0.7.1.1b', 'v0.8.0b', 'v0.8.1b', 'v0.8.2b', 'v0.8.3b',
                       
                       'v0.8.3.1b', 'v0.8.3.2b', 'v0.8.3.3b', 'v0.8.3.4b', 'v0.8.3.5b']

lang = {
    "title": "I5G Tools",
    "version": "v0.8.3.5b",
    "pedal": "Pedal Axis",
    "up": "Increase",
    "down": "Decrease",
    "switch": "Switch",
    "increment": "Increment",
    "switch_value": "Switch Value",
    "switch_mode": "Switch Mode",
    "switch_status": "Switch Status",
    "primary": "Primary",
    "secondary": "Secondary",
    "hold": "Hold",
    "toggle": "Toggle",
    "increment_mode": "Increment Mode",
    "continuous": "Continuous",
    "single": "Single",
    "axis_threshold": "Axis Threshold Setting for Device",
    "rollover_mode": "Rollover Mode",
    "locked": "Locked",
    "unlocked": "Unlocked",
    "bind": "Bind",
    "binding": "<-Binding->",
    "calibrate": "Calibrate",
    "calibrating": "<-Calibrating->",
    "high_threshold": "High Axis Threshold",
    "low_threshold": "Low Axis Threshold",
    "axis_rollover": "Axis Rollover",
    # "axis_samples": "Number of Axis Samples:",
    "scale": "Scale Factor (Requires Restart)",
    "timer_loop": "Continuous Mode Loop Timer (in ms)",
    "timer_first": "Continuous Mode Initial Loop Timer (in ms)",
    "none": "None",
    "weight_jacker": "WJ",
    "front_roll_bar": "FARB",
    "rear_roll_bar": "RARB",
    "fuel_map": "Map",
    "clutch": "Clutch",
    "throttle": "Throttle",
    "regen": "Regen",
    "deploy": "Deploy",
    "deploy_limit": "Deploy Limit",
    "fuel": "Fuel",
    "sounds": "Sounds",
    "settings": "Settings",
    "about": "About",
    "create": "Create",
    "delete": "Delete",
    "profile_create": "Create Profile",
    "profile_select": "Select Profile",
    "display": "Display",
    "car_id": "Car ID",
    "soc": "Battery",
    "hybrid": "Hybrid",
    "play_sound": "Play Sound",
    "playing_sound": "Playing",
    "sound_label": "Sound",
    "volume_label": "Volume",
    "hybrid_low_audio_label": "Hybrid Low Audio (if Sound is Yes)",
    "hybrid_high_audio_label": "Hybrid High Audio (if Sound is Yes)",
    "hybrid_limit_audio_label": "Hybrid Limit Audio (if Sound is Yes)",
    "hybrid_low_label": "SoC Low Trigger",
    "hybrid_high_label": "SoC High Trigger",
    "hybrid_limit_label": "Deploy Limit Trigger",
    "upshift_beep_label": "Upshift Beep (if Sound is Yes)",
    "downshift_beep_label": "Downshift Beep (if Sound is Yes)",
    "beep_mode_label": "Beep Trigger Mode (Dynamic is experimental)",
    "dynamic_mode_offset_label": "Dynamic Mode Offset (in ms)",
    "upshift_offset_label": "Upshift Trigger Offset from redline (in RPM)",
    "downshift_offset_label": "Downshift Trigger Offset from redline (in RPM)",
    "p2p_behind_audio_label": "Car Behind P2P Single Warning (if Sound is Yes)",
    "p2p_behind_audio_cont_label": "Car Behind P2P Continuous Warning (if Sound is Yes)",
    "p2p_behind_nobrake_label": "Stop P2P Warning Under Braking",
    "p2p_behind_thresh_label": "P2P Single Warning Threshold (in ms, -1 is any distance)",
    "p2p_behind_thresh_cont_label": "P2P Continuous Warning Threshold (in ms, -1 is any distance)",
    "p2p_behind_closest_car_label": "P2P Warning For Closest Car Behind Only",
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
    "open_folder": "Open Settings Folder",
    "donate": "Support on Ko-Fi",
    "donate_link": "https://ko-fi.com/cmdracer",
    "I5GYT": "Team I5G YouTube",
    "I5GYT_link": "https://www.youtube.com/@TeamI5G",
    "discord": "Discord",
    "discord_link": "https://discord.gg/hm7ywUygNy",
    "github": "Github",
    "github_link": "https://github.com/janewsome63/I5G-Tools",
}
lang['settings_version'] = lang['version']

step = {
    "weight_jacker": 1 / (41 - 1),
    "front_roll_bar": 1 / (6 - 1),
    "rear_roll_bar": 1 / (6 - 1),
    "fuel_map": 1 / (8 - 1),
    "clutch": 1 / (201 - 1),
    "throttle": 1 / (201 - 1),
    "brake": 1 / (201 - 1),
    "regen_rate": 1 / (1.0 - 0.5),
    "deploy_rate": 1 / (1.0 - 0.1),
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
    "hybrid": {
        "regen": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
        "deploy": {
            "label": "None",
            "guid": 0,
            "type": "none",
            "num": 0,
        },
    },
}

bindings_cache = copy.deepcopy(bindings)

bindings_info = {
    "types": ("up", "down", "switch", "pedal", "label", "regen", "deploy")
}

settings = {
    "frequency": 0.1,
    "scale": 1.25,
    "axis_samples": 2, # constant, not really a setting anymore
    "timer_loop": 150,
    "timer_first": 300,
    "config": "global.ini",
    "path": os.path.expanduser("~") + "\\AppData\\Local\\I5G Tools",
    "car_settings": "car_settings.csv",
    "vjoy_rid": 1,

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
        # "high_threshold": 0.90,
        # "low_threshold": 0.10,
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
        "rollover_mode": False,
    },
    "front_roll_bar": {
        "continuous": False,
        "toggle": False,
        "increment": 1,
        "switch_value": 1,
        "rollover_mode": False,
    },
    "rear_roll_bar": {
        "continuous": False,
        "toggle": False,
        "increment": 1,
        "switch_value": 6,
        "rollover_mode": False,
    },
    "fuel_map": {
        "continuous": False,
        "toggle": True,
        "increment": 1,
        "switch_value": 8,
        "rollover_mode": False,
    },
    "clutch": {
        "continuous": False,
        "toggle": False,
        "increment": 0.1,
        "switch_value": 50,
        "rollover_mode": False,
    },
    "throttle": {
        "continuous": False,
        "toggle": False,
        "increment": 0.1,
        "switch_value": 50,
        "rollover_mode": False,
    },
    "hybrid": {
        "regen_toggle": False,
        "deploy_toggle": False,
    },
    "fuel": {
        "": None,
    },
    "device_axis_thresh": {
        "-2": {
            "name": "None",
            "high_threshold": 0.90,
            "low_threshold": 0.10,
        },
                           },
}

id_table = [[-2,-2]] # index is the instance id, first value is the joystick index, second value is the guid; -1 is keyboard, so using -2 to avoid confusion

status = {
    "calibration": "None",
    "devices_loaded": False,
    "key_prev": None,
    "profile_prev": "None",
    "profile_list": [],
    "first": False,
    "refresh_labels": False,
    "refresh_guid_list": False,
    "rewrite_profile": False,
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
    "ir": {
        "connected": False,
        "pitting": False,
        "spectator": False,
        "spotter": False,
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
    "hybrid": {
        "regen": {
            "state": False,
            "thread": {
                "waiting": False,
            },
        },
        "deploy": {
            "state": False,
            "thread": {
                "waiting": False,
            },
        },
    },
}

telemetry = {
    "units": "imperial",
    "car": {
        "garage": False,
        "name": "",
        "pitting": False,
        "position": 0.0,
        "surface": -1,
    },
    "driver": {
        "driving": False,
        "idx": -1,
        "incidents": 0,
        "lap": {
            "completed": 0,
            "dist": 0.0,
            "next": 0,
            "pct": 0.0,
        },
        # "reset": "",
    },
    "engine": {
        "hex": 0x0,
        "list": [],
        "oil": 0.0,
        "water": 0.0,
    },
    "flags": {
        "hex": 0x0,
        "list": [],
    },
    "fuel": {
        "full": 999.0,
        "level": 0.0,
        "limit": 1.0,
        "pct": 1.0,
    },
    "session": {
        "lap": {
            "remaining": 0,
            "time": 0.0,
            "total": 0,
        },
        "state": 0x0,
        "time": {
            "current": 0.0,
            "remaining": 0.0,
            "total": 0.0,
        },
        "type": "None",
    },
    "tires": {
        "lf": {
            "temp": {
                "l": 0.0,
                "m": 0.0,
                "r": 0.0,
            },
            "wear": {
                "l": 0.0,
                "m": 0.0,
                "r": 0.0,
            },
        },
        "lr": {
            "temp": {
                "l": 0.0,
                "m": 0.0,
                "r": 0.0,
            },
            "wear": {
                "l": 0.0,
                "m": 0.0,
                "r": 0.0,
            },
        },
        "rf": {
            "temp": {
                "l": 0.0,
                "m": 0.0,
                "r": 0.0,
            },
            "wear": {
                "l": 0.0,
                "m": 0.0,
                "r": 0.0,
            },
        },
        "rr": {
            "temp": {
                "l": 0.0,
                "m": 0.0,
                "r": 0.0,
            },
            "wear": {
                "l": 0.0,
                "m": 0.0,
                "r": 0.0,
            },
        },
        "temp_total": 0.0,
        "wear_total": 0.0,
    },
    "track": {
        "name": "",
        "length": 0.0,
        "rubber": "",
        "temperature": 0.0,
        "wetness": "",
    },
    "weather": {
        "clouds": "N/A",
        "date": "2000-01-01",
        "density": 0.0,
        "fog": 0.0,
        "humidity": 0.0,
        "precipitation": 0.0,
        "pressure": 0.0,
        "temperature": 0.0,
        "time": "12:00am",
        "wind": {
            "direction": "N/A",
            "velocity": 0.0,
        }
    },
}

cache = {
    "distances": [0],
    "driving": False,
    "engine": {
        "oil": 77.0,
        "water": 77.0,
        "temp_total": 154.0,
    },
    "fuel": {
        "pct_prev": 0.0,
        "level_prev": 0.0,
        "level_prev_lap": 0.0,
    },
    "tires": {
        "temp_total": 0.0,
    },
    "lap": {
        "pct": 0.0,
        "pct_diff": 0.0,
    },
    "pitted": False,
    "session_type": "None",
}

triggers = {
    "active_reset": {
        "generic": False,
    },
    "driving": {
        "generic": False,
    },
    "lap": {
        "active_reset": False,
    },
    "reset": {
        "active_reset": False,
    },
}

codes = {
    "flags": {
        "checkered": 0x00000001,
        "white": 0x00000002,
        "green": 0x00000004,
        "yellow": 0x00000008,
        "red": 0x00000010,
        "blue": 0x00000020,
        "debris": 0x00000040,
        "crossed": 0x00000080,
        "yellow_waving": 0x00000100,
        "one_lap_to_green": 0x00000200,
        "green_held": 0x00000400,
        "ten_to_go": 0x00000800,
        "five_to_go": 0x00001000,
        "random_waving": 0x00002000,
        "caution": 0x00004000,
        "caution_waving": 0x00008000,
        "black": 0x00010000,
        "disqualify": 0x00020000,
        "serviceable": 0x00040000,
        "furled": 0x00080000,
        "repair": 0x00100000,
        "start_hidden": 0x10000000,
        "start_ready": 0x20000000,
        "start_set": 0x40000000,
        "start_go": 0x80000000,
    },
}

event = {
    "guid": 0,
    "type": "",
    "num": 0,
    "value": None,
}

backend = {
    "startup_time": None,
}

potential_bind = {}

gearing = [[]] # the first index is the gear-1 and the second index gives the number of sample points, the current average, and the current variance (std dev squared)

obsolete = ('high_threshold', 'low_threshold', 'axis_rollover')