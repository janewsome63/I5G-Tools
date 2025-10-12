import configparser
import threading

import variables as var


def write_config():
    config = configparser.ConfigParser()
    config['General'] = {
        "high_threshold": var.settings['high_threshold'],
        "low_threshold": var.settings['low_threshold'],
        "axis_samples": var.settings['axis_samples'],
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
    elif var.event['type'] == "axis":
        event = {
            "guid": var.event['guid'],
            "type": var.event['type'],
            "num": var.event['num'],
            "value": var.event['value']
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
                if event['type'] == "axis" and var.bindings[function][control] != None:
                    if event['guid'] == var.bindings[function][control]['guid'] and event['num'] == var.bindings[function][control]['num'] and (event['value'] >= var.settings['high_threshold'] or event['value'] <= var.settings['low_threshold']):
                        result = [{
                            "function": function,
                            "control": control,
                        }]
                        break
                elif event['type'] == "hat":
                    if var.bindings[function][control]['type'] == "hat" and var.bindings[function][control]['dir'] in event['dir']:
                        if result == None:
                            result = [{
                                "function": function,
                                "control": control,
                            }]
                        else:
                            result.append({
                                "function": function,
                                "control": control,
                            })
                elif event == var.bindings[function][control]:
                    result = [{
                        "function": function,
                        "control": control,
                    }]
                    break

    return result

def start_thread(target):
    thread = threading.Thread(target=target, daemon=True)
    thread.start()