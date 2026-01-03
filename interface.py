import devices as dev
import functions as fn
import history
import irsdk
import os
import sound_fx as sfx
import sys
import variables as var
import vjoy
from car_settings_list import car_settings
from controls import step
from PyQt6.QtCore import (pyqtSlot, QSize, Qt, QThreadPool, QTimer)
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QGridLayout, QLabel, QLCDNumber, QLineEdit,
    QMainWindow, QProgressBar, QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget)
from time import sleep

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        if getattr(sys, 'frozen', False):
            applicationPath = sys._MEIPASS
        elif __file__:
            applicationPath = os.path.dirname(__file__)

        self.store = {
            "width": 626,
            "height": 250,
            "running": False,
            "settings_busy": False,
            "content": {},
            "index": {},
            "timer": QTimer(),
            "thread_pool": QThreadPool(),
        }

        self.layout = QVBoxLayout()
        self.setFixedSize(QSize(self.store['width'], self.store['height']))
        self.setWindowIcon(QIcon(os.path.join(applicationPath, "icon.ico")))
        self.setWindowTitle(var.lang['title'] + " " + var.lang['version'])

        self.store['content'] = {}
        self.tabs = {
            "obj": QTabWidget(),
            "types": {
                "adjustment": ("weight_jacker", "front_roll_bar", "rear_roll_bar", "fuel_map"),
                "input": ("throttle", "clutch"),
                "other": ("axes_display", "hybrid", "settings")
            }
        }
        for type in self.tabs['types']:
            for function in self.tabs['types'][type]:
                self.tabs[function] = QWidget()
                self.tabs['obj'].addTab(self.tabs[function], var.lang[function])
                self.store['content'][function] = {}
                if type == "adjustment" or type == "input":
                    self.tool_tabs(type, function)
                elif type == "other":
                    self.other_tabs(function)

        self.layout.addWidget(self.tabs['obj'])
        self.setCentralWidget(self.tabs['obj'])

        self.apply_settings('settings.ini')
        self.refresh_settings_list()

        self.store['index']['car_id'] = self.store['content']['axes_display']['car_id']

        self.ir = irsdk.IRSDK()
        self.ir.startup()
        fn.check_uid(self.ir)
        self.store['content']['axes_display']['car_id'] = "None"
        self.update_limits()

        self.lastval = {
            'soc': None,
            'deploy_lim': None,
        }

        self.store['timer'].timeout.connect(self.updater)
        self.store['timer'].start(int((var.settings['frequency'] * 1000) / 10))

    def tool_tabs(self, type, function):
        local_store = {
            "binds": ["up", "down", "switch"],
            "decimals": 0,
            "range": {
                "increment": [1, int((1 / step[function]) + 1)],
                "switch": [1, int((1 / step[function]) + 1)],
            },
            "step": 1,
        }

        if type == "input":
            local_store['binds'].append("pedal")
            local_store['decimals'] = 1
            local_store['range']['increment'] = [0.1, ((1 / step[function]) / 2)]
            local_store['range']['switch'] = [0.0, ((1 / step[function]) / 2)]
            local_store['step'] = 0.1

        if function == "weight_jacker":
            local_store['range']['increment'] = [1, int(1 / step[function])]
            local_store['range']['switch'] = [-20, 20]

        self.tabs[function].layout = QGridLayout()

        self.store['content'][function]['lcd'] = QLCDNumber()

        self.store['content'][function]['axis'] = QProgressBar()
        self.store['content'][function]['axis'].setTextVisible(False)

        self.store['content'][function]['calibrate'] = QPushButton()
        self.store['content'][function]['calibrate'].setFixedSize(100, 25)
        self.store['content'][function]['calibrate'].setText(var.lang['calibrate'])
        self.store['content'][function]['calibrate'].clicked.connect(lambda: self.calibrate_start(function))

        self.store['content'][function]['increment_label'] = QLabel()
        self.store['content'][function]['increment_label'].setText(var.lang['increment'])

        self.store['content'][function]['switch_value_label'] = QLabel()
        self.store['content'][function]['switch_value_label'].setText(var.lang['switch_value'])
        self.store['content'][function]['switch_value_label'].setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.store['content'][function]['increment'] = QDoubleSpinBox()
        self.store['content'][function]['increment'].setFixedSize(70, 25)
        self.store['content'][function]['increment'].setRange(local_store['range']['increment'][0], local_store['range']['increment'][1])
        self.store['content'][function]['increment'].setDecimals(local_store['decimals'])
        self.store['content'][function]['increment'].setSingleStep(local_store['step'])
        self.store['content'][function]['increment'].valueChanged.connect(lambda: self.increment(function))

        self.store['content'][function]['switch'] = QDoubleSpinBox()
        self.store['content'][function]['switch'].setFixedSize(70, 25)
        self.store['content'][function]['switch'].setRange(local_store['range']['switch'][0], local_store['range']['switch'][1])
        self.store['content'][function]['switch'].setDecimals(local_store['decimals'])
        self.store['content'][function]['switch'].setSingleStep(local_store['step'])
        self.store['content'][function]['switch'].valueChanged.connect(lambda: self.switch(function))

        self.store['content'][function]['increment_mode_label'] = QLabel()
        self.store['content'][function]['increment_mode_label'].setText(var.lang['increment_mode'])

        self.store['content'][function]['switch_mode_label'] = QLabel()
        self.store['content'][function]['switch_mode_label'].setText(var.lang['switch_mode'])
        self.store['content'][function]['switch_mode_label'].setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.store['content'][function]['increment_mode'] = QComboBox()
        self.store['content'][function]['increment_mode'].setFixedSize(100, 25)
        self.store['content'][function]['increment_mode'].addItems((var.lang['continuous'], var.lang['single']))
        self.store['content'][function]['increment_mode'].currentIndexChanged.connect(lambda: self.increment_mode(function))

        self.store['content'][function]['switch_mode'] = QComboBox()
        self.store['content'][function]['switch_mode'].setFixedSize(70, 25)
        self.store['content'][function]['switch_mode'].addItems((var.lang['hold'], var.lang['toggle']))
        self.store['content'][function]['switch_mode'].currentIndexChanged.connect(lambda: self.switch_mode(function))
        
        if type == "input":
            self.store['content'][function]['pedal_label'] = QLabel()
            self.store['content'][function]['pedal_label'].setText(var.lang['pedal'])

            self.store['content'][function]['pedal_device'] = QLineEdit()
            self.store['content'][function]['pedal_device'].setFixedHeight(25)
            self.store['content'][function]['pedal_device'].setReadOnly(True)
            self.store['content'][function]['pedal_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.store['content'][function]['pedal_bind'] = QPushButton()
            self.store['content'][function]['pedal_bind'].setFixedSize(100, 25)
            self.store['content'][function]['pedal_bind'].setText(var.lang['bind'])
            self.store['content'][function]['pedal_bind'].clicked.connect(lambda: self.bind_start(function, "pedal"))

        self.store['content'][function]['up_label'] = QLabel()
        self.store['content'][function]['up_label'].setText(var.lang['up'])

        self.store['content'][function]['up_device'] = QLineEdit()
        self.store['content'][function]['up_device'].setFixedHeight(25)
        self.store['content'][function]['up_device'].setReadOnly(True)
        self.store['content'][function]['up_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.store['content'][function]['up_bind'] = QPushButton()
        self.store['content'][function]['up_bind'].setFixedSize(100, 25)
        self.store['content'][function]['up_bind'].setText(var.lang['bind'])
        self.store['content'][function]['up_bind'].clicked.connect(lambda: self.bind_start(function, "up"))

        self.store['content'][function]['down_label'] = QLabel()
        self.store['content'][function]['down_label'].setText(var.lang['down'])

        self.store['content'][function]['down_device'] = QLineEdit()
        self.store['content'][function]['down_device'].setFixedHeight(25)
        self.store['content'][function]['down_device'].setReadOnly(True)
        self.store['content'][function]['down_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.store['content'][function]['down_bind'] = QPushButton()
        self.store['content'][function]['down_bind'].setFixedSize(100, 25)
        self.store['content'][function]['down_bind'].setText(var.lang['bind'])
        self.store['content'][function]['down_bind'].clicked.connect(lambda: self.bind_start(function, "down"))

        self.store['content'][function]['switch_label'] = QLabel()
        self.store['content'][function]['switch_label'].setText(var.lang['switch'])

        self.store['content'][function]['switch_device'] = QLineEdit()
        self.store['content'][function]['switch_device'].setFixedHeight(25)
        self.store['content'][function]['switch_device'].setReadOnly(True)
        self.store['content'][function]['switch_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.store['content'][function]['switch_bind'] = QPushButton()
        self.store['content'][function]['switch_bind'].setFixedSize(100, 25)
        self.store['content'][function]['switch_bind'].setText(var.lang['bind'])
        self.store['content'][function]['switch_bind'].clicked.connect(lambda: self.bind_start(function, "switch"))

        row, column = 0, 0
        for element in self.store['content'][function]:
            self.tabs[function].layout.addWidget(self.store['content'][function][element], row, column)
            if element != "switch_value_label" and element != "switch_mode_label":
                column += 1
                if column > 2:
                    column = 0
                    row += 1
        del row, column
        self.tabs[function].setLayout(self.tabs[function].layout)

        self.store['index'][function] = {}
        for control in local_store['binds']:
            self.store['index'][function][control] = {
                "bind": self.store['content'][function][control + '_bind'],
                "device": self.store['content'][function][control + '_device'],
                "label": self.store['content'][function][control + '_label'],
            }

    def other_tabs(self, function):
        self.tabs[function].layout = QGridLayout()

        if function == "axes_display":
            self.store['content'][function]['car_id_label'] = QLabel()
            self.store['content'][function]['car_id_label'].setText(var.lang['car_id'])

            self.store['content'][function]['car_id'] = QLabel()
            self.store['content'][function]['car_id'].setText("None")

            self.store['content'][function]['car_id_limits'] = QLabel()
            self.store['content'][function]['car_id_limits'].setText("Placeholder")
            self.store['content'][function]['car_id_limits'].setWordWrap(True)

            self.store['content'][function]['weight_jacker_label'] = QLabel()
            self.store['content'][function]['weight_jacker_label'].setText(var.lang['weight_jacker'])

            self.store['content'][function]['weight_jacker_lcd'] = QLCDNumber()
            self.store['content'][function]['weight_jacker_lcd'].display(0)
            self.store['content'][function]['weight_jacker_lcd'].setSegmentStyle(self.store['content']['weight_jacker']['lcd'].segmentStyle())

            self.store['content'][function]['weight_jacker_axis'] = QProgressBar()
            self.store['content'][function]['weight_jacker_axis'].setTextVisible(False)
            self.store['content'][function]['weight_jacker_axis'].setMinimum(0)
            self.store['content'][function]['weight_jacker_axis'].setMaximum(100)

            self.store['content'][function]['front_roll_bar_label'] = QLabel()
            self.store['content'][function]['front_roll_bar_label'].setText(var.lang['front_roll_bar'])

            self.store['content'][function]['front_roll_bar_lcd'] = QLCDNumber()
            self.store['content'][function]['front_roll_bar_lcd'].display(0)

            self.store['content'][function]['front_roll_bar_axis'] = QProgressBar()
            self.store['content'][function]['front_roll_bar_axis'].setTextVisible(False)
            self.store['content'][function]['front_roll_bar_axis'].setMinimum(0)
            self.store['content'][function]['front_roll_bar_axis'].setMaximum(100)

            self.store['content'][function]['rear_roll_bar_label'] = QLabel()
            self.store['content'][function]['rear_roll_bar_label'].setText(var.lang['rear_roll_bar'])

            self.store['content'][function]['rear_roll_bar_lcd'] = QLCDNumber()
            self.store['content'][function]['rear_roll_bar_lcd'].display(0)

            self.store['content'][function]['rear_roll_bar_axis'] = QProgressBar()
            self.store['content'][function]['rear_roll_bar_axis'].setTextVisible(False)
            self.store['content'][function]['rear_roll_bar_axis'].setMinimum(0)
            self.store['content'][function]['rear_roll_bar_axis'].setMaximum(100)

            self.store['content'][function]['fuel_map_label'] = QLabel()
            self.store['content'][function]['fuel_map_label'].setText(var.lang['fuel_map'])

            self.store['content'][function]['fuel_map_lcd'] = QLCDNumber()
            self.store['content'][function]['fuel_map_lcd'].display(0)

            self.store['content'][function]['fuel_map_axis'] = QProgressBar()
            self.store['content'][function]['fuel_map_axis'].setTextVisible(False)
            self.store['content'][function]['fuel_map_axis'].setMinimum(0)
            self.store['content'][function]['fuel_map_axis'].setMaximum(100)

            self.store['content'][function]['clutch_label'] = QLabel()
            self.store['content'][function]['clutch_label'].setText(var.lang['clutch'])

            self.store['content'][function]['clutch_lcd'] = QLCDNumber()
            self.store['content'][function]['clutch_lcd'].display(0)

            self.store['content'][function]['clutch_axis'] = QProgressBar()
            self.store['content'][function]['clutch_axis'].setTextVisible(False)
            self.store['content'][function]['clutch_axis'].setMinimum(0)
            self.store['content'][function]['clutch_axis'].setMaximum(100)

            self.store['content'][function]['throttle_label'] = QLabel()
            self.store['content'][function]['throttle_label'].setText(var.lang['throttle'])

            self.store['content'][function]['throttle_lcd'] = QLCDNumber()
            self.store['content'][function]['throttle_lcd'].display(0)

            self.store['content'][function]['throttle_axis'] = QProgressBar()
            self.store['content'][function]['throttle_axis'].setTextVisible(False)
            self.store['content'][function]['throttle_axis'].setMinimum(0)
            self.store['content'][function]['throttle_axis'].setMaximum(100)
        elif function == "hybrid":
            self.store['content'][function]['soc_label'] = QLabel()
            self.store['content'][function]['soc_label'].setText(var.lang['soc'])
            self.store['content'][function]['soc_label'].setStyleSheet("color: red;")

            self.store['content'][function]['soc_lcd'] = QLCDNumber()
            self.store['content'][function]['soc_lcd'].display(str(0.00))

            self.store['content'][function]['soc_axis'] = QProgressBar()
            self.store['content'][function]['soc_axis'].setTextVisible(False)
            self.store['content'][function]['soc_axis'].setMinimum(0)
            self.store['content'][function]['soc_axis'].setMaximum(100)

            self.store['content'][function]['deploy_lim_label'] = QLabel()
            self.store['content'][function]['deploy_lim_label'].setText(var.lang['deploy_lim'])
            self.store['content'][function]['deploy_lim_label'].setStyleSheet("color: red;")

            self.store['content'][function]['deploy_lim_lcd'] = QLCDNumber()
            self.store['content'][function]['deploy_lim_lcd'].display(str(0.00))

            self.store['content'][function]['deploy_lim_axis'] = QProgressBar()
            self.store['content'][function]['deploy_lim_axis'].setTextVisible(False)
            self.store['content'][function]['deploy_lim_axis'].setMinimum(0)
            self.store['content'][function]['deploy_lim_axis'].setMaximum(100)
        elif function == "settings":
            self.store['content'][function]['high_threshold_label'] = QLabel()
            self.store['content'][function]['high_threshold_label'].setText(var.lang['high_threshold'])

            self.store['content'][function]['high_threshold'] = QSpinBox()
            self.store['content'][function]['high_threshold'].setFixedSize(60, 20)
            self.store['content'][function]['high_threshold'].setRange(min(int(var.settings['low_threshold']*100)+1,51), 99)
            self.store['content'][function]['high_threshold'].setValue(int(var.settings['high_threshold'] * 100))
            self.store['content'][function]['high_threshold'].valueChanged.connect(lambda: self.settings_set('high_threshold'))

            self.store['content'][function]['low_threshold_label'] = QLabel()
            self.store['content'][function]['low_threshold_label'].setText(var.lang['low_threshold'])

            self.store['content'][function]['low_threshold'] = QSpinBox()
            self.store['content'][function]['low_threshold'].setFixedSize(60, 20)
            self.store['content'][function]['low_threshold'].setRange(1, max(int(var.settings['high_threshold']*100)-1,49))
            self.store['content'][function]['low_threshold'].setValue(int(var.settings['low_threshold'] * 100))
            self.store['content'][function]['low_threshold'].valueChanged.connect(lambda: self.settings_set('low_threshold'))

            self.store['content'][function]['axis_samples_label'] = QLabel()
            self.store['content'][function]['axis_samples_label'].setText(var.lang['axis_samples'])

            self.store['content'][function]['axis_samples'] = QSpinBox()
            self.store['content'][function]['axis_samples'].setFixedSize(60, 20)
            self.store['content'][function]['axis_samples'].setRange(2, 10)
            self.store['content'][function]['axis_samples'].valueChanged.connect(lambda: self.settings_set('axis_samples'))

            self.store['content'][function]['scale_label'] = QLabel()
            self.store['content'][function]['scale_label'].setText(var.lang['scale'])

            self.store['content'][function]['scale'] = QComboBox()
            self.store['content'][function]['scale'].setFixedSize(70, 22)
            self.store['content'][function]['scale'].addItem("0.50" + "x")
            self.store['content'][function]['scale'].addItem("0.75" + "x")
            self.store['content'][function]['scale'].addItem("1.00" + "x")
            self.store['content'][function]['scale'].addItem("1.25" + "x")
            self.store['content'][function]['scale'].addItem("1.50" + "x")
            self.store['content'][function]['scale'].currentTextChanged.connect(self.scale)

            self.store['content'][function]['timer_first_label'] = QLabel()
            self.store['content'][function]['timer_first_label'].setText(var.lang['timer_first'])

            self.store['content'][function]['timer_first'] = QSpinBox()
            self.store['content'][function]['timer_first'].setFixedSize(70, 20)
            self.store['content'][function]['timer_first'].setRange(1, 1000)
            self.store['content'][function]['timer_first'].valueChanged.connect(lambda: self.settings_set('timer_first'))

            self.store['content'][function]['timer_loop_label'] = QLabel()
            self.store['content'][function]['timer_loop_label'].setText(var.lang['timer_loop'])

            self.store['content'][function]['timer_loop'] = QSpinBox()
            self.store['content'][function]['timer_loop'].setFixedSize(70, 20)
            self.store['content'][function]['timer_loop'].setRange(1, 1000)
            self.store['content'][function]['timer_loop'].valueChanged.connect(lambda: self.settings_set('timer_loop'))

            self.store['content'][function]['settings_filename_label'] = QLabel()
            self.store['content'][function]['settings_filename_label'].setText(var.lang['settings_filename'])

            self.store['content'][function]['settings_filename'] = QComboBox()
            self.store['content'][function]['settings_filename'].setFixedSize(200, 25)
            if var.settings_active:
                self.store['content'][function]['settings_filename'].setCurrentText(var.settings_active)
                self.store['content'][function]['settings_filename'].addItem(var.settings_active)
            else:
                self.store['content'][function]['settings_filename'].setCurrentText('None')
                self.store['content'][function]['settings_filename'].addItem("settings.ini")
            self.store['content'][function]['settings_filename'].activated.connect(lambda: self.refresh_settings_list())
            self.store['content'][function]['settings_filename'].currentTextChanged.connect(lambda: self.apply_settings(self.store['content'][function]['settings_filename'].currentText()))

            self.store['content'][function]['sound_label'] = QLabel()
            self.store['content'][function]['sound_label'].setText(var.lang['sound_label'])

            self.store['content'][function]['sound'] = QComboBox()
            self.store['content'][function]['sound'].setFixedSize(200, 25)
            self.store['content'][function]['sound'].addItem("Yes")
            self.store['content'][function]['sound'].addItem("No")
            self.store['content'][function]['sound'].setCurrentText("No")
            self.store['content'][function]['sound'].currentIndexChanged.connect(lambda: self.settings_set('sound'))

            self.store['content'][function]['volume_label'] = QLabel()
            self.store['content'][function]['volume_label'].setText(var.lang['volume_label'])

            self.store['content'][function]['volume'] = QSpinBox()
            self.store['content'][function]['volume'].setFixedSize(70, 25)
            self.store['content'][function]['volume'].setRange(0, 100)
            self.store['content'][function]['volume'].valueChanged.connect(lambda: self.settings_set('volume'))

        row, column = 0, 0
        for element in self.store['content'][function]:
            self.tabs[function].layout.addWidget(self.store['content'][function][element], row, column)
            column += 1
            if function == "settings":
                if column > 1:
                    column = 0
                    row += 1
            else:
                if column > 2:
                    column = 0
                    row += 1
        del row, column
        self.tabs[function].setLayout(self.tabs[function].layout)

    def updater(self):
        for function in var.status:
            if function in self.store['content']:
                value = var.status[function]['secondary']
                if function == "weight_jacker":
                    # var.status[function]['secondary'] = (value * step[function]) + 0.5
                    value = int(round((value - 0.5)/step[function]))
                elif function == "clutch" or function == "throttle":
                    # var.status[function]['secondary'] = value/100
                    value = float(value*100)
                #elif function == "settings":
                    #self.refresh_settings_list()
                elif function == "regen" or function == "deploy":
                    value = value * (self.store['content'][function]['switch'].maximum() - self.store['content'][function]['switch'].minimum()) + self.store['content'][function]['switch'].minimum()
                else:
                    # var.status[function]['secondary'] = (value * step[function]) - step[function]
                    value = int(round((value / step[function]) + 1))

                self.store['content'][function]['switch'].setValue(value)

        self.display()

        if not self.ir.is_initialized:
            self.ir.startup()
            fn.check_uid(self.ir)
        if self.ir.is_initialized and self.ir.is_connected:
            length = len(self.ir['DriverInfo']['Drivers'])
            index = length-1
            check = True
            while index >= 0 and check:
                if self.ir['DriverInfo']['Drivers'][index]['CarIdx'] == self.ir['PlayerCarIdx']:
                    check = False
                else:
                    index -= 1
            if self.store['content']['axes_display']['car_id'] != int(self.ir['DriverInfo']['Drivers'][index]['CarID']):
                self.store['content']['axes_display']['car_id'] = int(self.ir['DriverInfo']['Drivers'][index]['CarID'])
                self.update_limits()
        elif self.ir.is_initialized and not self.ir.is_connected and self.store['content']['axes_display']['car_id']['car_id'] != "None":
            self.ir.shutdown()
            self.store['content']['axes_display']['car_id']['car_id'] = "None"
            for entry in self.store['content']['hybrid']:
                self.store['content']['hybrid'][entry]['axis'].setValue(0)
                self.store['content']['hybrid'][entry]['axis'].update()
                self.store['content']['hybrid'][entry]['lcd'].display(str(0.00))
                self.store['content']['hybrid'][entry]['lcd'].update()
                self.store['content']['hybrid'][entry]['label'].setStyleSheet("color: red;")
            self.update_limits()

    def display(self):
        for func in vjoy.axis_values:
            if func in self.store['content']: #only because not every tab has been developed yet...
                pct = vjoy.axis_values[func]
                #print("display check1: ", func, pct)
                self.store['content'][func]['axis'].setValue(int(pct * 100))
                self.store['content'][func]['axis'].update()
                self.store['content']['axes_display'][func + '_axis'].setValue(int(pct * 100))
                self.store['content']['axes_display'][func + '_axis'].update()

                if func == 'clutch' or func == "throttle":
                    if (pct*100)%1 == 0:
                        self.store['content'][func]['lcd'].display(str(round(pct*100)) + ".0") # bad hack to get the lcd to always display one decimal place
                        self.store['content']['axes_display'][func + '_lcd'].display(str(round(pct*100)) + ".0")
                    else:
                        self.store['content'][func]['lcd'].display(round(pct*100, 1))
                        self.store['content']['axes_display'][func + '_lcd'].display(round(pct*100, 1))
                elif func == 'regen' or func == "deploy":
                    value = round(pct * (self.store['content'][func]['switch'].maximum() - self.store['content'][func]['switch'].minimum()) + self.store['content'][func]['switch'].minimum(), 1)
                    if value%1 == 0:
                        self.store['content'][func]['lcd'].display(str(round(value)) + ".0") # bad hack to get the lcd to always display one decimal place
                        self.store['content']['axes_display'][func + '_lcd'].display(str(round(value)) + ".0")
                    else:
                        self.store['content'][func]['lcd'].display(round(value, 1))
                        self.store['content']['axes_display'][func + '_lcd'].display(round(value, 1))
                else:
                    value = round(pct * (self.store['content'][func]['switch'].maximum() - self.store['content'][func]['switch'].minimum()) + self.store['content'][func]['switch'].minimum(), 1)
                    self.store['content'][func]['lcd'].display(round(value))
                    self.store['content']['axes_display'][func + '_lcd'].display(round(value))
                self.store['content'][func]['lcd'].update()
                self.store['content']['axes_display'][func + '_lcd'].update()
        if (self.store['content']['axes_display']['car_id'] in car_settings) and 'hybrid' in car_settings[self.store['content']['axes_display']['car_id']]:
            self.store['content']['hybrid']['soc_label'].setStyleSheet(QLabel.styleSheet(self.store['index']['car_id']))
            self.store['content']['hybrid']['deploy_lim_label'].setStyleSheet(QLabel.styleSheet(self.store['index']['car_id']))
            if self.ir['IsOnTrackCar'] and (car_settings[self.store['content']['axes_display']['car_id']]['hybrid'] == True): # and hybrid in car_settings
                soc_pct = self.ir['EnergyERSBatteryPct']
                self.store['content']['hybrid']['soc_axis'].setValue(int(soc_pct*100))
                self.store['content']['hybrid']['soc_axis'].update()
                self.store['content']['hybrid']['soc_lcd'].display(str(round(soc_pct*100,1)))
                self.store['content']['hybrid']['soc_lcd'].update()
                deploy_lim_pct = self.ir['EnergyMGU_KLapDeployPct']
                self.store['content']['hybrid']['deploy_lim_axis'].setValue(int(deploy_lim_pct*100))
                self.store['content']['hybrid']['deploy_lim_axis'].update()
                self.store['content']['hybrid']['deploy_lim_lcd'].display(str(round(deploy_lim_pct*100,1)))
                self.store['content']['hybrid']['deploy_lim_lcd'].update()
            else:
                self.store['content']['hybrid']['soc_axis'].setValue(0)
                self.store['content']['hybrid']['soc_axis'].update()
                self.store['content']['hybrid']['soc_lcd'].display(str(0.00))
                self.store['content']['hybrid']['soc_lcd'].update()
                self.store['content']['hybrid']['soc_label'].setStyleSheet("color: red;")
                self.lastval['soc'] = None
                self.store['content']['hybrid']['deploy_lim_axis'].setValue(0)
                self.store['content']['hybrid']['deploy_lim_axis'].update()
                self.store['content']['hybrid']['deploy_lim_lcd'].display(str(0.00))
                self.store['content']['hybrid']['deploy_lim_lcd'].update()
                self.store['content']['hybrid']['deploy_lim_label'].setStyleSheet("color: red;")
                self.lastval['deploy_lim'] = None
            if self.store['content']['settings']['sound'].currentText() == "Yes":
                if self.lastval['soc'] != None: # 'soc' and 'deploy_lim' will always either both be a number or both be None at the same time
                    if self.store['content']['hybrid']['soc_axis'].value() <= 0.10*100 and self.lastval['soc'] > 0.10*100: # make this adjustable later
                        print("call play low")
                        fn.start_thread(sfx.play('low'))
                    if self.store['content']['hybrid']['soc_axis'].value() >= 0.90*100 and self.lastval['soc'] < 0.90*100: # make this adjustable later
                        print("call play high")
                        fn.start_thread(sfx.play('high'))
                    if self.store['content']['hybrid']['deploy_lim_axis'].value() >= 1.0*100 and self.lastval['deploy_lim'] < 1.0*100: # make this adjustable later maybe?
                        print("call play deploy limit")
                        fn.start_thread(sfx.play('limit'))
                self.lastval['soc'] = self.store['content']['hybrid']['soc_axis'].value()
                self.lastval['deploy_lim'] = self.store['content']['hybrid']['deploy_lim_axis'].value()

    @pyqtSlot()
    def calibrate(self):
        if self.axis in self.store['content']:
            self.store['content'][self.axis]['calibrate'].setText(var.lang['calibrating'])
        else:
            print("Warning: calibrate()")

        vjoy.calibrate(self.axis)
        while self.store['running'] == True:
            sleep(0.1)
        self.store['content'][self.axis]['calibrate'].setText(var.lang['calibrate'])
        vjoy.set(self.axis,self.pct)
        var.status['calibration'] = False

    @pyqtSlot()
    def calibrate_start(self, func):
        self.axis = func
        if not self.store['running']:
            self.store['running'] = True
            var.status['calibration'] = True
            sleep(0.1) #wait for loops to stop
            if not var.status[func]['switched']:
                self.pct = var.status[func]['primary']
            elif var.status[func]['switched']:
                self.pct = var.status[func]['secondary']
            self.store['thread_pool'].start(self.calibrate)
        else:
            self.store['running'] = False

    @pyqtSlot()
    def increment(self, func):
        var.settings[func]['increment'] = self.store['content'][func]['increment'].value()
        fn.write_config()

    @pyqtSlot()
    def switch(self, func):
        value = self.store['content'][func]['switch'].value()
        var.settings[func]['switch_value'] = value
        if func == "weight_jacker":
            var.status[func]['secondary'] = (value * step[func]) + 0.5
        elif func == "clutch" or func == "throttle":
            var.status[func]['secondary'] = value/100
        else:
            var.status[func]['secondary'] = (value * step[func]) - step[func]
        if var.status[func]['switched'] == True:
            vjoy.set(func, var.status[func]['secondary'])
        fn.write_config()

    @pyqtSlot()
    def increment_mode(self, func):
        if self.store['content'][func]['increment_mode'].currentText() == "Continuous":
            var.settings[func]['continuous'] = True
        elif self.store['content'][func]['increment_mode'].currentText() == "Single":
            var.settings[func]['continuous'] = False
        fn.write_config()

    @pyqtSlot()
    def switch_mode(self, func):
        if self.store['content'][func]['switch_mode'].currentText() == "Toggle":
            var.settings[func]['toggle'] = True
        elif self.store['content'][func]['switch_mode'].currentText() == "Hold":
            var.status[func]['switched'] = False
            vjoy.set(func, var.status[func]['primary'])
            var.settings[func]['toggle'] = False
        fn.write_config()

    @pyqtSlot()
    def settings_set(self, func):
        if func == 'sound':
            value = self.store['content']['settings'][func].currentText()
        else:
            value = self.store['content']['settings'][func].value()
        if func == 'high_threshold':
            if value/100 > var.settings['low_threshold']:
                self.store['content']['settings']['low_threshold'].setRange(1, value-1)
                fn.reset_bind_thresh(func, value/100)
                var.settings[func] = value/100
                fn.write_config()
        elif func == 'low_threshold':
            if value/100 < var.settings['high_threshold']:
                self.store['content']['settings']['high_threshold'].setRange(value+1, 99)
                fn.reset_bind_thresh(func, value/100)
                var.settings[func] = value/100
                fn.write_config()
        elif func == 'sound':
            var.settings['audio']['on'] = (value == "Yes")
            fn.write_config()
        elif func == 'volume':
            var.settings['audio']['volume'] = value/100
            fn.write_config()
        else:
            var.settings[func] = value
            fn.write_config()

    @pyqtSlot()
    def scale(self):
        scale = self.store['content']['settings']['scale'].currentText()
        scale = scale.replace("x", "")
        var.settings['scale'] = scale
        fn.write_config()

    @pyqtSlot()
    def bind(self):
        self.store['running'] = True
        var.bindings['status']['active'] = True
        function = var.bindings['status']['function']
        control = var.bindings['status']['control']
        history.clear()

        print(self.store['index']['throttle']['pedal'])
        self.store['index'][function][control]['bind'].setText(var.lang['binding'])

        var.event = {
            "guid": 0,
            "type": "",
            "num": 0,
            "value": None,
        }
        var.bindings[function][control] = None
        while not var.bindings[function][control]:
            if self.store['running'] == False:
                var.bindings[function][control] = {"guid": 0, "type": "none", "num": 0}

            if var.event['guid'] != 0:
                if var.event['type'] == "button":
                    if var.event['value'] != False:
                        var.bindings[function][control] = {
                            "guid": var.event['guid'],
                            "type": var.event['type'],
                            "num": var.event['num'],
                        }
                elif var.event['type'] == "axis":
                    if (function == 'clutch' or function == 'throttle') and control == 'pedal':
                        var.bindings[function][control] = {
                            "guid": var.event['guid'],
                            "type": var.event['type'],
                            "num": var.event['num'],
                        }
                    else:
                        if var.event['value'] >= var.settings['high_threshold'] and history.check_valid(var.event['guid'], var.event['num'], var.event['value'], True):
                            var.bindings[function][control] = {
                                "guid": var.event['guid'],
                                "type": var.event['type'],
                                "num": var.event['num'],
                                "value": var.settings['high_threshold']
                            }
                        if var.event['value'] <= var.settings['low_threshold'] and history.check_valid(var.event['guid'], var.event['num'], var.event['value'], False):
                            var.bindings[function][control] = {
                                "guid": var.event['guid'],
                                "type": var.event['type'],
                                "num": var.event['num'],
                                "value": var.settings['low_threshold']
                            }
                elif var.event['type'] == "hat":
                    if var.event['value'] != "none":
                        var.bindings[function][control] = {
                            "guid": var.event['guid'],
                            "type": var.event['type'],
                            "num": var.event['num'],
                            "dir": var.event['value'],
                        }
            sleep(0.001)

        self.store['index'][function][control]['bind'].setText(var.lang['bind'])

        self.store['index'][function][control]['device'].setText(dev.format(function, control))

        var.bindings['status'] = {
            "active": False,
            "function": None,
            "control": None,
        }
        fn.write_config()
        self.store['running'] = False

    @pyqtSlot()
    def bind_start(self, func, ctrl):
        var.bindings['status'] = {
            "function": func,
            "control": ctrl,
        }
        if not self.store['running']:
            self.store['thread_pool'].start(self.bind)
        else:
            self.store['running'] = False

    @pyqtSlot()
    def refresh_settings_list(self):
        self.store['settings_busy'] = True
        file = self.store['content']['settings']['settings_filename'].currentText()
        self.store['content']['settings']['settings_filename'].clear()
        for name in fn.get_settings_files():
            self.store['content']['settings']['settings_filename'].addItem(name)
        self.store['content']['settings']['settings_filename'].setCurrentText(file)
        self.store['settings_busy'] = False

    @pyqtSlot()
    def update_limits(self):
        if self.store['content']['axes_display']['car_id'] == "None":
            self.store['index']['car_id'].setText("None")
            print("Updating car_id to None")
            self.store['content']['axes_display']['weight_jacker_label'].setStyleSheet("color: red;")
            self.store['content']['axes_display']['front_roll_bar_label'].setStyleSheet("color: red;")
            self.store['content']['axes_display']['rear_roll_bar_label'].setStyleSheet("color: red;")
            self.store['content']['axes_display']['fuel_map_label'].setStyleSheet("color: red;")
        elif self.store['content']['axes_display']['car_id'] in car_settings:
            car_id = self.store['content']['axes_display']['car_id']
            self.store['index']['car_id'].setText(car_settings[car_id]['name'])
            print("Updating for car_id: " + str(car_id) + " " + car_settings[car_id]['name'])
            if 'weight_jacker' in car_settings[car_id]:
                min = car_settings[car_id]['weight_jacker'][0]
                max = car_settings[car_id]['weight_jacker'][1]
                step['weight_jacker'] = 1 / (max - min)
                self.store['content']['weight_jacker']['switch'].setRange(min, max)
                self.store['content']['axes_display']['weight_jacker_label'].setStyleSheet(QLabel.styleSheet(self.store['index']['car_id']))
            else:
                self.store['content']['axes_display']['weight_jacker_label'].setStyleSheet("color: red;")
            if 'front_roll_bar' in car_settings[car_id]:
                min = car_settings[car_id]['front_roll_bar'][0]
                max = car_settings[car_id]['front_roll_bar'][1]
                step['front_roll_bar'] = 1 / (max - min)
                self.store['content']['front_roll_bar']['switch'].setRange(min, max)
                self.store['content']['axes_display']['front_roll_bar_label'].setStyleSheet(QLabel.styleSheet(self.store['index']['car_id']))
            else:
                self.store['content']['axes_display']['front_roll_bar_label'].setStyleSheet("color: red;")
            if 'rear_roll_bar' in car_settings[car_id]:
                min = car_settings[car_id]['rear_roll_bar'][0]
                max = car_settings[car_id]['rear_roll_bar'][1]
                step['rear_roll_bar'] = 1 / (max - min)
                self.store['content']['rear_roll_bar']['switch'].setRange(min, max)
                self.store['content']['axes_display']['rear_roll_bar_label'].setStyleSheet(QLabel.styleSheet(self.store['index']['car_id']))
            else:
                self.store['content']['axes_display']['rear_roll_bar_label'].setStyleSheet("color: red;")
            if 'fuel_map' in car_settings[car_id]:
                min = car_settings[car_id]['fuel_map'][0]
                max = car_settings[car_id]['fuel_map'][1]
                step['fuel_map'] = 1 / (max - min)
                self.store['content']['fuel_map']['switch'].setRange(min, max)
                self.store['content']['axes_display']['fuel_map_label'].setStyleSheet(QLabel.styleSheet(self.store['index']['car_id']))
            else:
                self.store['content']['axes_display']['fuel_map_label'].setStyleSheet("color: red;")
        else:
            car_id = self.store['content']['axes_display']['car_id']['car_id']
            self.store['index']['car_id'].setText(str(car_id) + " (not in car_settings list yet)")
            print("current_car " + str(car_id) + " not in car_settings!")
            self.store['content']['axes_display']['weight_jacker']['label'].setStyleSheet("color: red;")
            self.store['content']['axes_display']['front_roll_bar_label'].setStyleSheet("color: red;")
            self.store['content']['axes_display']['rear_roll_bar_label'].setStyleSheet("color: red;")
            self.store['content']['axes_display']['fuel_map_label'].setStyleSheet("color: red;")
        text = "WJ: " + str(int(self.store['content']['weight_jacker']['switch'].minimum())) + " to " + str(int(self.store['content']['weight_jacker']['switch'].maximum()))
        text += ", FARB: " + str(int(self.store['content']['front_roll_bar']['switch'].minimum())) + " to " + str(int(self.store['content']['front_roll_bar']['switch'].maximum()))
        text += ", RARB: " + str(int(self.store['content']['rear_roll_bar']['switch'].minimum())) + " to " + str(int(self.store['content']['rear_roll_bar']['switch'].maximum()))
        text += ", Fuel Map: " + str(int(self.store['content']['fuel_map']['switch'].minimum())) + " to " + str(int(self.store['content']['fuel_map']['switch'].maximum()))
        self.store['content']['axes_display']['car_id_limits'].setText(text)

    @pyqtSlot()
    def apply_settings(self, file):
        if self.store['settings_busy']: #if list is getting cleared or current text is being reset during list refresh, skip this function
            return

        fn.re_read_config(file)

        self.store['content']['weight_jacker']['increment'].setValue(var.settings['weight_jacker']['increment'])
        self.store['content']['weight_jacker']['switch'].setValue(var.settings['weight_jacker']['switch_value'])
        if var.settings['weight_jacker']['continuous']:
            self.store['content']['weight_jacker']['increment_mode'].setCurrentText(var.lang['continuous'])
        else:
            self.store['content']['weight_jacker']['increment_mode'].setCurrentText(var.lang['single'])
        if var.settings['weight_jacker']['toggle']:
            self.store['content']['weight_jacker']['switch_mode'].setCurrentText(var.lang['toggle'])
        else:
            self.store['content']['weight_jacker']['switch_mode'].setCurrentText(var.lang['hold'])
        self.store['content']['weight_jacker']['up_device'].setText(dev.format("weight_jacker", "up"))
        self.store['content']['weight_jacker']['down_device'].setText(dev.format("weight_jacker", "down"))
        self.store['content']['weight_jacker']['switch_device'].setText(dev.format("weight_jacker", "switch"))

        self.store['content']['front_roll_bar']['increment'].setValue(var.settings['front_roll_bar']['increment'])
        self.store['content']['front_roll_bar']['switch'].setValue(var.settings['front_roll_bar']['switch_value'])
        if var.settings['front_roll_bar']['continuous']:
            self.store['content']['front_roll_bar']['increment_mode'].setCurrentText(var.lang['continuous'])
        else:
            self.store['content']['front_roll_bar']['increment_mode'].setCurrentText(var.lang['single'])
        if var.settings['front_roll_bar']['toggle']:
            self.store['content']['front_roll_bar']['switch_mode'].setCurrentText(var.lang['toggle'])
        else:
            self.store['content']['front_roll_bar']['switch_mode'].setCurrentText(var.lang['hold'])
        self.store['content']['front_roll_bar']['up_device'].setText(dev.format("front_roll_bar", "up"))
        self.store['content']['front_roll_bar']['down_device'].setText(dev.format("front_roll_bar", "down"))
        self.store['content']['front_roll_bar']['switch_device'].setText(dev.format("front_roll_bar", "switch"))


        self.store['content']['rear_roll_bar']['increment'].setValue(var.settings['rear_roll_bar']['increment'])
        self.store['content']['rear_roll_bar']['switch'].setValue(var.settings['rear_roll_bar']['switch_value'])
        if var.settings['rear_roll_bar']['continuous']:
            self.store['content']['rear_roll_bar']['increment_mode'].setCurrentText(var.lang['continuous'])
        else:
            self.store['content']['rear_roll_bar']['increment_mode'].setCurrentText(var.lang['single'])
        if var.settings['rear_roll_bar']['toggle']:
            self.store['content']['rear_roll_bar']['switch_mode'].setCurrentText(var.lang['toggle'])
        else:
            self.store['content']['rear_roll_bar']['switch_mode'].setCurrentText(var.lang['hold'])
        self.store['content']['rear_roll_bar']['up_device'].setText(dev.format("rear_roll_bar", "up"))
        self.store['content']['rear_roll_bar']['down_device'].setText(dev.format("rear_roll_bar", "down"))
        self.store['content']['rear_roll_bar']['switch_device'].setText(dev.format("rear_roll_bar", "switch"))


        self.store['content']['fuel_map']['increment'].setValue(var.settings['fuel_map']['increment'])
        self.store['content']['fuel_map']['switch'].setValue(var.settings['fuel_map']['switch_value'])
        if var.settings['fuel_map']['continuous']:
            self.store['content']['fuel_map']['increment_mode'].setCurrentText(var.lang['continuous'])
        else:
            self.store['content']['fuel_map']['increment_mode'].setCurrentText(var.lang['single'])
        if var.settings['fuel_map']['toggle']:
            self.store['content']['fuel_map']['switch_mode'].setCurrentText(var.lang['toggle'])
        else:
            self.store['content']['fuel_map']['switch_mode'].setCurrentText(var.lang['hold'])
        self.store['content']['fuel_map']['up_device'].setText(dev.format("fuel_map", "up"))
        self.store['content']['fuel_map']['down_device'].setText(dev.format("fuel_map", "down"))
        self.store['content']['fuel_map']['switch_device'].setText(dev.format("fuel_map", "switch"))


        self.store['content']['clutch']['increment'].setValue(var.settings['clutch']['increment'])
        self.store['content']['clutch']['switch'].setValue(var.settings['clutch']['switch_value'])
        if var.settings['clutch']['continuous']:
            self.store['content']['clutch']['increment_mode'].setCurrentText(var.lang['continuous'])
        else:
            self.store['content']['clutch']['increment_mode'].setCurrentText(var.lang['single'])
        if var.settings['clutch']['toggle']:
            self.store['content']['clutch']['switch_mode'].setCurrentText(var.lang['toggle'])
        else:
            self.store['content']['clutch']['switch_mode'].setCurrentText(var.lang['hold'])
        self.store['content']['clutch']['pedal_device'].setText(dev.format("clutch", "pedal"))
        self.store['content']['clutch']['up_device'].setText(dev.format("clutch", "up"))
        self.store['content']['clutch']['down_device'].setText(dev.format("clutch", "down"))
        self.store['content']['clutch']['switch_device'].setText(dev.format("clutch", "switch"))


        self.store['content']['throttle']['increment'].setValue(var.settings['throttle']['increment'])
        self.store['content']['throttle']['switch'].setValue(var.settings['throttle']['switch_value'])
        if var.settings['throttle']['continuous']:
            self.store['content']['throttle']['increment_mode'].setCurrentText(var.lang['continuous'])
        else:
            self.store['content']['throttle']['increment_mode'].setCurrentText(var.lang['single'])
        if var.settings['throttle']['toggle']:
            self.store['content']['throttle']['switch_mode'].setCurrentText(var.lang['toggle'])
        else:
            self.store['content']['throttle']['switch_mode'].setCurrentText(var.lang['hold'])
        self.store['content']['throttle']['pedal_device'].setText(dev.format("throttle", "pedal"))
        self.store['content']['throttle']['up_device'].setText(dev.format("throttle", "up"))
        self.store['content']['throttle']['down_device'].setText(dev.format("throttle", "down"))
        self.store['content']['throttle']['switch_device'].setText(dev.format("throttle", "switch"))

        self.store['content']['settings']['high_threshold'].setRange(min(int(var.settings['low_threshold']*100)+1,51), 99)
        self.store['content']['settings']['high_threshold'].setValue(int(var.settings['high_threshold'] * 100))
        self.store['content']['settings']['low_threshold'].setRange(1, max(int(var.settings['high_threshold']*100)-1,49))
        self.store['content']['settings']['low_threshold'].setValue(int(var.settings['low_threshold'] * 100))
        self.store['content']['settings']['axis_samples'].setValue(int(var.settings['axis_samples']))
        self.store['content']['settings']['scale'].setCurrentText(str(var.settings['scale']) + "x")
        self.store['content']['settings']['timer_first'].setValue(int(var.settings['timer_first']))
        self.store['content']['settings']['timer_loop'].setValue(int(var.settings['timer_loop']))
        self.store['content']['settings']['settings_filename'].setCurrentText(var.settings_active)
        if var.settings['audio']['on']:
            self.store['content']['settings']['sound'].setCurrentText('Yes')
        else:
            self.store['content']['settings']['sound'].setCurrentText('No')
        self.store['content']['settings']['volume'].setValue(int(var.settings['audio']['volume']*100))

def main():
    os.environ["QT_SCALE_FACTOR"] = str(var.settings['scale'])

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    window.update()
    app.exec()