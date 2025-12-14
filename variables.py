import os

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
    "bite_point": {
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
    "engine_warming": {
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
    # "regen": {
    #     "up": {
    #         "guid": 0,
    #         "type": "none",
    #         "num": 0,
    #     },
    #     "down": {
    #         "guid": 0,
    #         "type": "none",
    #         "num": 0,
    #     },
    #     "switch": {
    #         "guid": 0,
    #         "type": "none",
    #         "num": 0,
    #     },
    # },
    # "deploy": {
    #     "up": {
    #         "guid": 0,
    #         "type": "none",
    #         "num": 0,
    #     },
    #     "down": {
    #         "guid": 0,
    #         "type": "none",
    #         "num": 0,
    #     },
    #     "switch": {
    #         "guid": 0,
    #         "type": "none",
    #         "num": 0,
    #     },
    # },
}
settings = {}
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
    "bite_point": {
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
    "engine_warming": {
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
}

sound_folder = {
    "config": os.path.expanduser("~") + "\\AppData\\Local\\I5G Tools\\Sound FX\\"
}

settings_list = []