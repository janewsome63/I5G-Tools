import check_dir
check_dir.run() # checks to make sure all the folders are already set up and creates them if they don't exist before doing anything else

import devices as dev
import functions as fn
import interface as ui
import sdk
import vjoy

if __name__ == '__main__':
    fn.start_thread(dev.device_detection)
    fn.start_thread(sdk.main)

    vjoy.intialize()
    fn.read_config()
    ui.main()