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