import variables as var
import os

def run():
    if not os.path.exists(var.settings['path']):
        os.mkdir(var.settings['path'])
        var.status['first'] = True
    else:
        var.status['first'] = False

    for sub_setting in var.settings:
        if isinstance(var.settings[sub_setting], dict) and 'path' in var.settings[sub_setting]:
            if not os.path.exists(var.settings['path'] + "\\" + var.settings[sub_setting]['path']):
                os.mkdir(var.settings['path'] + "\\" + var.settings[sub_setting]['path'])