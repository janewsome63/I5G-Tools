import devices as dev
import functions as fn
import interface as ui
import variables as var
import threading
from time import sleep

if __name__ == '__main__':
    fn.init_vars()
    detect = threading.Thread(target=dev.device_detection, daemon=True)
    detect.start()

    ui.ui()