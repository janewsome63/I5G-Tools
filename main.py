import devices as dev
import functions as fn
import interface as ui
import variables as var
import threading

if __name__ == '__main__':
    fn.init_vars()
    threading.Thread(target=ui.ui(), daemon=True).start()