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
    # "bite_point": {
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
    # "engine_warming": {
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
    "weight_jacker": {
        "primary": 0.5,
        "secondary": 0.0,
        "switched": False,
        "thread": {
            "running": None,
            "waiting": False,
        },
    },
    "front_roll_bar": {
        "primary": 1.0,
        "secondary": 0.0,
        "switched": False,
        "thread": {
            "current": 0,
            "running": 0,
            "waiting": False,
        },
    },
    "rear_roll_bar": {
        "primary": 0.0,
        "secondary": 1.0,
        "switched": False,
        "thread": {
            "current": 0,
            "running": 0,
            "waiting": False,
        },
    },
    "fuel_map": {
        "primary": 0.0,
        "secondary": 1.0,
        "switched": False,
        "thread": {
            "current": 0,
            "running": 0,
            "waiting": False,
        },
    },
    "bite_point": {
        "primary": 0.0,
        "secondary": 0.5,
        "switched": False,
        "thread": {
            "current": 0,
            "running": 0,
            "waiting": False,
        },
    },
    "engine_warming": {
        "primary": 0.0,
        "secondary": 0.2,
        "switched": False,
        "thread": {
            "current": 0,
            "running": 0,
            "waiting": False,
        },
    },
    "brake": {
        "primary": 0.0,
        "secondary": 0.2,
        "switched": False,
        "thread": {
            "current": 0,
            "running": 0,
            "waiting": False,
        },
    },
    "other": {
        "primary": 0.0,
        "secondary": 0.2,
        "switched": False,
        "thread": {
            "current": 0,
            "running": 0,
            "waiting": False,
        },
    }
}

event = {
    "guid": 0,
    "type": "",
    "num": 0,
    "value": None,
}

backend = {
    "config": os.path.expanduser("~") + "\\AppData\\Local\\I5G Tools" + "\\" + "settings.ini",
}