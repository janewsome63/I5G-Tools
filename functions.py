import variables as var
import configparser

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