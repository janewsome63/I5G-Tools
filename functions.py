import variables as var

def init_vars():
    var.bindings['wj_up_device'] = "Placeholder Device"
    var.bindings['wj_up_button'] = "1"
    var.bindings['wj_down_device'] = "Placeholder Device"
    var.bindings['wj_down_button'] = "2"
    var.bindings['wj_switch_device'] = "Placeholder Device"
    var.bindings['wj_switch_button'] = "3"

    var.wj_values['percent'] = 50
    var.wj_values['raw'] = 12345
    var.wj_values['value'] = -20
    var.wj_values['increment'] = 1
    var.wj_values['switch_value'] = -20
    var.wj_values['switch_mode'] = 1
    var.wj_values['increment_mode'] = 1

def format_vector(vector):
    string = str(vector).replace("(", " ")
    string = string.replace(")", "")
    string = string.replace("=", " ")
    string = string.replace(",", "")
    string = string.split()

    pos = {
        "x": string[2],
        "y": string[4],
    }

    return pos