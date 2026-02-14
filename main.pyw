import check_dir
check_dir.run() # checks to make sure all the folders are already set up and creates them if they don't exist before doing anything else

import devices as dev
import functions as fn
import interface as ui
import threading
import vjoy

if __name__ == '__main__':
    detect = threading.Thread(target=dev.device_detection, daemon=True)
    detect.start()

    vjoy.intialize()
    fn.read_config()
    ui.main()