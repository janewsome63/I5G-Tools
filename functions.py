import configparser
import threading

import variables as var


def write_config():
    config = configparser.ConfigParser()
    config['General'] = {
        "threshold": var.settings['threshold'],
        "frequency": var.settings['frequency'],
        "scale": var.settings['scale'],
        "device": var.settings['device'],
    }

    config['Weight Jacker'] = {

    }

def is_bind():
    if var.event['type'] == "hat":
        event = {
            "guid": var.event['guid'],
            "type": var.event['type'],
            "num": var.event['num'],
            "dir": var.event['value']
        }
    else:
        event = {
            "guid": var.event['guid'],
            "type": var.event['type'],
            "num": var.event['num'],
        }
    result = None

    for function in var.bindings:
        if function != "status":
            for control in var.bindings[function]:
                if event == var.bindings[function][control]:
                    result = {
                        "function": function,
                        "control": control,
                    }
                    break

    return result

def start_thread(target):
    thread = threading.Thread(target=target, daemon=True)
    thread.start()