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
from PyQt6.QtCore import (pyqtSlot, QSize, Qt, QThreadPool, QTimer)
from PyQt6.QtGui import (QIcon, QColor, QWheelEvent)
from PyQt6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QGridLayout, QLabel, QLCDNumber, QLineEdit,
    QMainWindow, QProgressBar, QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget, QScrollArea)
from time import sleep
import math

# noinspection PyUnresolvedReferences,PyProtectedMember
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        if getattr(sys, 'frozen', False):
            applicationPath = sys._MEIPASS
        elif __file__:
            applicationPath = os.path.dirname(__file__)
        else:
            applicationPath = "C:\\"

        self.store = {
            "width": 640,
            "height": 250,
            "running": False,
            "profile_busy": False,
            "content": {},
            "index": {},
            "timer": QTimer(),
            "thread_pool": QThreadPool(),
            "axis": None,
            "pct": None,
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
                if function == "settings":
                    self.settings_scroll = QScrollArea()
                    self.settings_scroll.setWidgetResizable(True)
                    self.settings_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                    self.settings_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                    self.settings_scroll.setWidget(self.tabs[function])
                    self.tabs['obj'].addTab(self.settings_scroll, var.lang[function])
                else:
                    self.tabs['obj'].addTab(self.tabs[function], var.lang[function])
                self.store['content'][function] = {}
                if type == "adjustment" or type == "input":
                    self.tool_tabs(type, function)
                elif type == "other":
                    self.other_tabs(function)        

        self.layout.addWidget(self.tabs['obj'])
        self.setCentralWidget(self.tabs['obj'])

        self.apply_settings(var.settings['profile']['current'])
        self.refresh_profile_list()

        self.store['index']['car_id'] = self.store['content']['axes_display']['car_id']

        self.ir = irsdk.IRSDK()
        self.ir.startup()
        fn.check_uid(self.ir)
        self.store['content']['axes_display']['car_id'] = "None"
        self.update_limits()

        self.lastval = {
            'soc': 999.0,
            'deploy_lim': 999.0,
            'IsOnTrack': False,
            'OnPitLane': False,
            'CarIdx': -1,
            'SessionTick': -1,
            'Throttle': -1,
            'Gear': -1,
            'Brake': -1,
            'Clutch': -1,
            'RPM': -1,
            'Speed': 0,
            'IsOnTrack_beep': False,
            'p2p': False,
            'CarIdxp2p': [],
            'CarIdxEstTime': [],
            'CarIdx_Within_p2p_Range': [],
            'CarIdx_Within_Cont_p2p_Range': [],
        }

        self.store['timer'].timeout.connect(self.updater)
        self.store['timer'].start(int((var.settings['frequency'] * 1000) / 10))

        self.flashtimer = {}
        self.default_tab_color = {}

        for type in self.tabs['types']:
            for function in self.tabs['types'][type]:
                if type == "adjustment" or type == "input":
                    if type == "input":
                        controls = ("pedal", "up", "down", "switch")
                    else:
                        controls = ("up", "down", "switch")
                    for control in controls:
                        self.update_label(function, control)

        # for function in var.bindings:
        #     if function != "status":
        #         for control in var.bindings[function]:
        #             if var.bindings[function][control]['label'] == "Unknown device" and var.bindings[function][control]['guid'] in dev.device_info:
        #                 var.status['rewrite']['profile'] = True
        #                 self.store['index'][function][control]['device'].setText(dev.format_device(function, control))
        # if var.status['rewrite']['profile']:
        #     fn.write_profile()
        #     var.status['rewrite']['profile'] = False

    def tool_tabs(self, type, function):
        local_store = {
            "binds": ["up", "down", "switch"],
            "decimals": 0,
            "range": {
                "increment": [1, int((1 / var.step[function]) + 1)],
                "switch": [1, int((1 / var.step[function]) + 1)],
            },
            "step": 1,
        }

        if type == "input":
            local_store['binds'].append("pedal")
            local_store['decimals'] = 1
            local_store['range']['increment'] = [0.1, ((1 / var.step[function]) / 2)]
            local_store['range']['switch'] = [0.0, ((1 / var.step[function]) / 2)]
            local_store['step'] = 0.1

        if function == "weight_jacker":
            local_store['range']['increment'] = [1, int(1 / var.step[function])]
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

        self.store['content'][function]['increment'] = CustomDoubleSpinBox()
        self.store['content'][function]['increment'].setFixedSize(70, 25)
        self.store['content'][function]['increment'].setRange(local_store['range']['increment'][0], local_store['range']['increment'][1])
        self.store['content'][function]['increment'].setDecimals(local_store['decimals'])
        self.store['content'][function]['increment'].setSingleStep(local_store['step'])
        self.store['content'][function]['increment'].valueChanged.connect(lambda: self.increment(function))

        self.store['content'][function]['switch'] = CustomDoubleSpinBox()
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

        self.store['content'][function]['increment_mode'] = CustomComboBox()
        self.store['content'][function]['increment_mode'].setFixedSize(100, 25)
        self.store['content'][function]['increment_mode'].addItems((var.lang['continuous'], var.lang['single']))
        self.store['content'][function]['increment_mode'].currentIndexChanged.connect(lambda: self.increment_mode(function))

        self.store['content'][function]['switch_mode'] = CustomComboBox()
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
            self.store['content'][function]['pedal_bind'].clicked.connect(lambda: self.bind_start(function, "pedal", True))

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

            self.store['content'][function]['high_threshold'] = CustomSpinBox()
            self.store['content'][function]['high_threshold'].setFixedSize(60, 20)
            self.store['content'][function]['high_threshold'].setRange(min(int(var.settings['local']['low_threshold']*100)+1,51), 99)
            self.store['content'][function]['high_threshold'].setValue(int(var.settings['local']['high_threshold'] * 100))
            self.store['content'][function]['high_threshold'].valueChanged.connect(lambda: self.settings_set('high_threshold'))

            self.store['content'][function]['low_threshold_label'] = QLabel()
            self.store['content'][function]['low_threshold_label'].setText(var.lang['low_threshold'])

            self.store['content'][function]['low_threshold'] = CustomSpinBox()
            self.store['content'][function]['low_threshold'].setFixedSize(60, 20)
            self.store['content'][function]['low_threshold'].setRange(1, max(int(var.settings['local']['high_threshold']*100)-1,49))
            self.store['content'][function]['low_threshold'].setValue(int(var.settings['local']['low_threshold'] * 100))
            self.store['content'][function]['low_threshold'].valueChanged.connect(lambda: self.settings_set('low_threshold'))

            # self.store['content'][function]['axis_samples_label'] = QLabel()
            # self.store['content'][function]['axis_samples_label'].setText(var.lang['axis_samples'])

            # self.store['content'][function]['axis_samples'] = QSpinBox()
            # self.store['content'][function]['axis_samples'].setFixedSize(60, 20)
            # self.store['content'][function]['axis_samples'].setRange(2, 10)
            # self.store['content'][function]['axis_samples'].valueChanged.connect(lambda: self.settings_set('axis_samples'))

            self.store['content'][function]['scale_label'] = QLabel()
            self.store['content'][function]['scale_label'].setText(var.lang['scale'])

            self.store['content'][function]['scale'] = CustomComboBox()
            self.store['content'][function]['scale'].setFixedSize(70, 22)
            self.store['content'][function]['scale'].addItem("0.5" + "x")
            self.store['content'][function]['scale'].addItem("0.75" + "x")
            self.store['content'][function]['scale'].addItem("1.0" + "x")
            self.store['content'][function]['scale'].addItem("1.25" + "x")
            self.store['content'][function]['scale'].addItem("1.5" + "x")
            self.store['content'][function]['scale'].currentTextChanged.connect(self.scale)

            self.store['content'][function]['timer_first_label'] = QLabel()
            self.store['content'][function]['timer_first_label'].setText(var.lang['timer_first'])

            self.store['content'][function]['timer_first'] = CustomSpinBox()
            self.store['content'][function]['timer_first'].setFixedSize(70, 20)
            self.store['content'][function]['timer_first'].setRange(1, 1000)
            self.store['content'][function]['timer_first'].valueChanged.connect(lambda: self.settings_set('timer_first'))

            self.store['content'][function]['timer_loop_label'] = QLabel()
            self.store['content'][function]['timer_loop_label'].setText(var.lang['timer_loop'])

            self.store['content'][function]['timer_loop'] = CustomSpinBox()
            self.store['content'][function]['timer_loop'].setFixedSize(70, 20)
            self.store['content'][function]['timer_loop'].setRange(1, 1000)
            self.store['content'][function]['timer_loop'].valueChanged.connect(lambda: self.settings_set('timer_loop'))

            self.store['content'][function]['profile_create_label'] = QLabel()
            self.store['content'][function]['profile_create_label'].setText(var.lang['profile_create'])

            self.store['content'][function]['profile_create_name'] = QLineEdit()
            self.store['content'][function]['profile_create_name'].setFixedSize(100, 25)
            self.store['content'][function]['profile_create_name'].setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.store['content'][function]['profile_create'] = QPushButton()
            self.store['content'][function]['profile_create'].setFixedSize(100, 25)
            self.store['content'][function]['profile_create'].setText(var.lang['create'])
            self.store['content'][function]['profile_create'].clicked.connect(lambda: self.create_profile(self.store['content'][function]['profile_create_name'].text()))

            self.store['content'][function]['profile_select_label'] = QLabel()
            self.store['content'][function]['profile_select_label'].setText(var.lang['profile_select'])

            self.store['content'][function]['profile_select'] = CustomComboBox()
            self.store['content'][function]['profile_select'].setFixedSize(100, 25)
            self.store['content'][function]['profile_select'].addItem(var.settings['profile']['current'])
            self.store['content'][function]['profile_select'].setCurrentText(var.settings['profile']['current'])
            self.store['content'][function]['profile_select'].activated.connect(lambda: self.refresh_profile_list())
            self.store['content'][function]['profile_select'].currentTextChanged.connect(lambda: self.apply_settings(self.store['content'][function]['profile_select'].currentText()))
            # self.store['content'][function]['profile_select'].highlighted.connect(lambda: self.refresh_profile_list()) # This causes a recusion error in v0.5.4b?? Is this an Apollo Error 62 situation?

            self.store['content'][function]['profile_delete'] = QPushButton()
            self.store['content'][function]['profile_delete'].setFixedSize(100, 25)
            self.store['content'][function]['profile_delete'].setText(var.lang['delete'])
            self.store['content'][function]['profile_delete'].clicked.connect(lambda: self.delete_profile(self.store['content'][function]['profile_select'].currentText()))

            self.store['content'][function]['sound_label'] = QLabel()
            self.store['content'][function]['sound_label'].setText(var.lang['sound_label'])

            self.store['content'][function]['sound'] = CustomComboBox()
            self.store['content'][function]['sound'].setFixedSize(200, 25)
            self.store['content'][function]['sound'].addItem("Yes")
            self.store['content'][function]['sound'].addItem("No")
            self.store['content'][function]['sound'].setCurrentText("No")
            self.store['content'][function]['sound'].currentIndexChanged.connect(lambda: self.settings_set('sound'))

            self.store['content'][function]['volume_label'] = QLabel()
            self.store['content'][function]['volume_label'].setText(var.lang['volume_label'])

            self.store['content'][function]['volume'] = CustomSpinBox()
            self.store['content'][function]['volume'].setFixedSize(70, 25)
            self.store['content'][function]['volume'].setRange(0, 100)
            self.store['content'][function]['volume'].valueChanged.connect(lambda: self.settings_set('volume'))

            self.store['content'][function]['hybrid_low_audio_label'] = QLabel()
            self.store['content'][function]['hybrid_low_audio_label'].setText(var.lang['hybrid_low_audio_label'])

            self.store['content'][function]['hybrid_low_audio'] = CustomComboBox()
            self.store['content'][function]['hybrid_low_audio'].setFixedSize(200, 25)
            self.store['content'][function]['hybrid_low_audio'].addItem("Yes")
            self.store['content'][function]['hybrid_low_audio'].addItem("No")
            self.store['content'][function]['hybrid_low_audio'].setCurrentText(str(var.settings['local']['hybrid_low_audio']))
            self.store['content'][function]['hybrid_low_audio'].currentIndexChanged.connect(lambda: self.settings_set('hybrid_low_audio'))

            self.store['content'][function]['hybrid_high_audio_label'] = QLabel()
            self.store['content'][function]['hybrid_high_audio_label'].setText(var.lang['hybrid_high_audio_label'])

            self.store['content'][function]['hybrid_high_audio'] = CustomComboBox()
            self.store['content'][function]['hybrid_high_audio'].setFixedSize(200, 25)
            self.store['content'][function]['hybrid_high_audio'].addItem("Yes")
            self.store['content'][function]['hybrid_high_audio'].addItem("No")
            self.store['content'][function]['hybrid_high_audio'].setCurrentText(str(var.settings['local']['hybrid_high_audio']))
            self.store['content'][function]['hybrid_high_audio'].currentIndexChanged.connect(lambda: self.settings_set('hybrid_high_audio'))

            self.store['content'][function]['hybrid_limit_audio_label'] = QLabel()
            self.store['content'][function]['hybrid_limit_audio_label'].setText(var.lang['hybrid_limit_audio_label'])

            self.store['content'][function]['hybrid_limit_audio'] = CustomComboBox()
            self.store['content'][function]['hybrid_limit_audio'].setFixedSize(200, 25)
            self.store['content'][function]['hybrid_limit_audio'].addItem("Yes")
            self.store['content'][function]['hybrid_limit_audio'].addItem("No")
            self.store['content'][function]['hybrid_limit_audio'].setCurrentText(str(var.settings['local']['hybrid_limit_audio']))
            self.store['content'][function]['hybrid_limit_audio'].currentIndexChanged.connect(lambda: self.settings_set('hybrid_limit_audio'))

            self.store['content'][function]['hybrid_low_label'] = QLabel()
            self.store['content'][function]['hybrid_low_label'].setText(var.lang['hybrid_low_label'])

            self.store['content'][function]['hybrid_low_val'] = CustomSpinBox()
            self.store['content'][function]['hybrid_low_val'].setFixedSize(70, 20)
            self.store['content'][function]['hybrid_low_val'].setRange(0, 99)
            self.store['content'][function]['hybrid_low_val'].setValue(int(var.settings['local']['hybrid_low_val']))
            self.store['content'][function]['hybrid_low_val'].valueChanged.connect(lambda: self.settings_set('hybrid_low_val'))

            self.store['content'][function]['hybrid_high_label'] = QLabel()
            self.store['content'][function]['hybrid_high_label'].setText(var.lang['hybrid_high_label'])

            self.store['content'][function]['hybrid_high_val'] = CustomSpinBox()
            self.store['content'][function]['hybrid_high_val'].setFixedSize(70, 20)
            self.store['content'][function]['hybrid_high_val'].setRange(1, 99)
            self.store['content'][function]['hybrid_high_val'].setValue(int(var.settings['local']['hybrid_high_val']))
            self.store['content'][function]['hybrid_high_val'].valueChanged.connect(lambda: self.settings_set('hybrid_high_val'))

            self.store['content'][function]['hybrid_limit_label'] = QLabel()
            self.store['content'][function]['hybrid_limit_label'].setText(var.lang['hybrid_limit_label'])

            self.store['content'][function]['hybrid_limit_val'] = CustomSpinBox()
            self.store['content'][function]['hybrid_limit_val'].setFixedSize(70, 20)
            self.store['content'][function]['hybrid_limit_val'].setRange(1, 100)
            self.store['content'][function]['hybrid_limit_val'].setValue(int(var.settings['local']['hybrid_limit_val']))
            self.store['content'][function]['hybrid_limit_val'].valueChanged.connect(lambda: self.settings_set('hybrid_limit_val'))

            self.store['content'][function]['upshift_beep_label'] = QLabel()
            self.store['content'][function]['upshift_beep_label'].setText(var.lang['upshift_beep_label'])

            self.store['content'][function]['upshift_beep'] = CustomComboBox()
            self.store['content'][function]['upshift_beep'].setFixedSize(200, 25)
            self.store['content'][function]['upshift_beep'].addItem("Yes")
            self.store['content'][function]['upshift_beep'].addItem("No")
            self.store['content'][function]['upshift_beep'].setCurrentText(str(var.settings['local']['upshift_beep']))
            self.store['content'][function]['upshift_beep'].currentIndexChanged.connect(lambda: self.settings_set('upshift_beep'))

            self.store['content'][function]['downshift_beep_label'] = QLabel()
            self.store['content'][function]['downshift_beep_label'].setText(var.lang['downshift_beep_label'])

            self.store['content'][function]['downshift_beep'] = CustomComboBox()
            self.store['content'][function]['downshift_beep'].setFixedSize(200, 25)
            self.store['content'][function]['downshift_beep'].addItem("Yes")
            self.store['content'][function]['downshift_beep'].addItem("No")
            self.store['content'][function]['downshift_beep'].setCurrentText(str(var.settings['local']['downshift_beep']))
            self.store['content'][function]['downshift_beep'].currentIndexChanged.connect(lambda: self.settings_set('downshift_beep'))

            self.store['content'][function]['beep_mode_label'] = QLabel()
            self.store['content'][function]['beep_mode_label'].setText(var.lang['beep_mode_label'])

            self.store['content'][function]['beep_mode'] = CustomComboBox()
            self.store['content'][function]['beep_mode'].setFixedSize(200, 25)
            self.store['content'][function]['beep_mode'].addItem("Fixed")
            # self.store['content'][function]['beep_mode'].addItem("Dynamic")
            self.store['content'][function]['beep_mode'].setCurrentText(str(var.settings['local']['beep_mode']))
            self.store['content'][function]['beep_mode'].currentIndexChanged.connect(lambda: self.settings_set('beep_mode'))

            #dynamic mode offset
            self.store['content'][function]['dynamic_mode_offset_label'] = QLabel()
            self.store['content'][function]['dynamic_mode_offset_label'].setText(var.lang['dynamic_mode_offset_label'])

            self.store['content'][function]['dynamic_mode_offset'] = CustomSpinBox()
            self.store['content'][function]['dynamic_mode_offset'].setFixedSize(70, 20)
            self.store['content'][function]['dynamic_mode_offset'].setRange(-10000, 10000)
            self.store['content'][function]['dynamic_mode_offset'].setValue(int(var.settings['local']['dynamic_mode_offset']))
            self.store['content'][function]['dynamic_mode_offset'].valueChanged.connect(lambda: self.settings_set('dynamic_mode_offset'))

            #upshift offset
            self.store['content'][function]['upshift_offset_label'] = QLabel()
            self.store['content'][function]['upshift_offset_label'].setText(var.lang['upshift_offset_label'])

            self.store['content'][function]['upshift_offset'] = CustomSpinBox()
            self.store['content'][function]['upshift_offset'].setFixedSize(70, 20)
            self.store['content'][function]['upshift_offset'].setRange(-10000, 10000)
            self.store['content'][function]['upshift_offset'].setValue(int(var.settings['local']['upshift_offset']))
            self.store['content'][function]['upshift_offset'].valueChanged.connect(lambda: self.settings_set('upshift_offset'))

            #downshift offset
            self.store['content'][function]['downshift_offset_label'] = QLabel()
            self.store['content'][function]['downshift_offset_label'].setText(var.lang['downshift_offset_label'])

            self.store['content'][function]['downshift_offset'] = CustomSpinBox()
            self.store['content'][function]['downshift_offset'].setFixedSize(70, 20)
            self.store['content'][function]['downshift_offset'].setRange(-10000, 10000)
            self.store['content'][function]['downshift_offset'].setValue(int(var.settings['local']['downshift_offset']))
            self.store['content'][function]['downshift_offset'].valueChanged.connect(lambda: self.settings_set('downshift_offset'))

            # p2p behind audio enabled
            self.store['content'][function]['p2p_behind_audio_label'] = QLabel()
            self.store['content'][function]['p2p_behind_audio_label'].setText(var.lang['p2p_behind_audio_label'])

            self.store['content'][function]['p2p_behind_audio'] = CustomComboBox()
            self.store['content'][function]['p2p_behind_audio'].setFixedSize(200, 25)
            self.store['content'][function]['p2p_behind_audio'].addItem("Yes")
            self.store['content'][function]['p2p_behind_audio'].addItem("No")
            self.store['content'][function]['p2p_behind_audio'].setCurrentText(str(var.settings['local']['p2p_behind_audio']))
            self.store['content'][function]['p2p_behind_audio'].currentIndexChanged.connect(lambda: self.settings_set('p2p_behind_audio'))

            # p2p behind audio continuous enabled
            self.store['content'][function]['p2p_behind_audio_cont_label'] = QLabel()
            self.store['content'][function]['p2p_behind_audio_cont_label'].setText(var.lang['p2p_behind_audio_cont_label'])

            self.store['content'][function]['p2p_behind_audio_cont'] = CustomComboBox()
            self.store['content'][function]['p2p_behind_audio_cont'].setFixedSize(200, 25)
            self.store['content'][function]['p2p_behind_audio_cont'].addItem("Yes")
            self.store['content'][function]['p2p_behind_audio_cont'].addItem("No")
            self.store['content'][function]['p2p_behind_audio_cont'].setCurrentText(str(var.settings['local']['p2p_behind_audio_cont']))
            self.store['content'][function]['p2p_behind_audio_cont'].currentIndexChanged.connect(lambda: self.settings_set('p2p_behind_audio_cont'))

            # p2p behind stop audio under braking
            self.store['content'][function]['p2p_behind_nobrake_label'] = QLabel()
            self.store['content'][function]['p2p_behind_nobrake_label'].setText(var.lang['p2p_behind_nobrake_label'])

            self.store['content'][function]['p2p_behind_nobrake'] = CustomComboBox()
            self.store['content'][function]['p2p_behind_nobrake'].setFixedSize(200, 25)
            self.store['content'][function]['p2p_behind_nobrake'].addItem("Yes")
            self.store['content'][function]['p2p_behind_nobrake'].addItem("No")
            self.store['content'][function]['p2p_behind_nobrake'].setCurrentText(str(var.settings['local']['p2p_behind_nobrake']))
            self.store['content'][function]['p2p_behind_nobrake'].currentIndexChanged.connect(lambda: self.settings_set('p2p_behind_nobrake'))

            # p2p behind single warning threshold
            self.store['content'][function]['p2p_behind_thresh_label'] = QLabel()
            self.store['content'][function]['p2p_behind_thresh_label'].setText(var.lang['p2p_behind_thresh_label'])

            self.store['content'][function]['p2p_behind_thresh'] = CustomSpinBox()
            self.store['content'][function]['p2p_behind_thresh'].setFixedSize(70, 20)
            self.store['content'][function]['p2p_behind_thresh'].setRange(-1, 1000000)
            self.store['content'][function]['p2p_behind_thresh'].setValue(int(var.settings['local']['p2p_behind_thresh']))
            self.store['content'][function]['p2p_behind_thresh'].valueChanged.connect(lambda: self.settings_set('p2p_behind_thresh'))

            # p2p behind continuous warning threshold
            self.store['content'][function]['p2p_behind_thresh_cont_label'] = QLabel()
            self.store['content'][function]['p2p_behind_thresh_cont_label'].setText(var.lang['p2p_behind_thresh_cont_label'])

            self.store['content'][function]['p2p_behind_thresh_cont'] = CustomSpinBox()
            self.store['content'][function]['p2p_behind_thresh_cont'].setFixedSize(70, 20)
            self.store['content'][function]['p2p_behind_thresh_cont'].setRange(-1, 1000000)
            self.store['content'][function]['p2p_behind_thresh_cont'].setValue(int(var.settings['local']['p2p_behind_thresh_cont']))
            self.store['content'][function]['p2p_behind_thresh_cont'].valueChanged.connect(lambda: self.settings_set('p2p_behind_thresh_cont'))

            # p2p behind audio for any car within range vs closest car only
            self.store['content'][function]['p2p_behind_closest_car_label'] = QLabel()
            self.store['content'][function]['p2p_behind_closest_car_label'].setText(var.lang['p2p_behind_closest_car_label'])

            self.store['content'][function]['p2p_behind_closest_car'] = CustomComboBox()
            self.store['content'][function]['p2p_behind_closest_car'].setFixedSize(200, 25)
            self.store['content'][function]['p2p_behind_closest_car'].addItem("Yes")
            self.store['content'][function]['p2p_behind_closest_car'].addItem("No")
            self.store['content'][function]['p2p_behind_closest_car'].setCurrentText(str(var.settings['local']['p2p_behind_closest_car']))
            self.store['content'][function]['p2p_behind_closest_car'].currentIndexChanged.connect(lambda: self.settings_set('p2p_behind_closest_car'))
            


        row, column = 0, 0
        for element in self.store['content'][function]:
            if element == "profile_create" or element == "profile_delete":
                self.tabs[function].layout.addWidget(self.store['content'][function][element], row, column, alignment=Qt.AlignmentFlag.AlignRight)
            else:
                self.tabs[function].layout.addWidget(self.store['content'][function][element], row, column)
            if element != "profile_create_name" and element != "profile_select":
                column += 1
                if function == "settings" or function == "rpm":
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
                    # var.status[function]['secondary'] = (value * var.step[function]) + 0.5
                    value = int(round((value - 0.5)/var.step[function]))
                elif function == "clutch" or function == "throttle":
                    # var.status[function]['secondary'] = value/100
                    value = float(value*100)
                #elif function == "settings":
                    #self.refresh_profile_list()
                elif function == "regen" or function == "deploy":
                    value = value * (self.store['content'][function]['switch'].maximum() - self.store['content'][function]['switch'].minimum()) + self.store['content'][function]['switch'].minimum()
                else:
                    # var.status[function]['secondary'] = (value * var.step[function]) - var.step[function]
                    value = int(round((value / var.step[function]) + 1))

                self.store['content'][function]['switch'].setValue(value)

        self.display()

        if not self.ir.is_initialized:
            self.ir.startup()
            fn.check_uid(self.ir)
            
        if self.ir.is_initialized and self.ir.is_connected:
            length = len(self.ir['DriverInfo']['Drivers'])
            index = length-1
            check = True
            if self.lastval['CarIdx'] in self.ir['DriverInfo']['Drivers'] and self.lastval['CarIdx'] == self.ir['DriverInfo']['Drivers']:
                check = False
            while index >= 0 and check:
                if self.ir['DriverInfo']['Drivers'][index]['CarIdx'] == self.ir['PlayerCarIdx']:
                    check = False
                else:
                    index -= 1
            if self.store['content']['axes_display']['car_id'] != int(self.ir['DriverInfo']['Drivers'][index]['CarID']):
                self.store['content']['axes_display']['car_id'] = int(self.ir['DriverInfo']['Drivers'][index]['CarID'])
                self.update_limits()
            if self.lastval['CarIdx'] != index:
                self.lastval['CarIdx'] = index
            if self.ir['IsOnTrack'] != self.lastval['IsOnTrack'] and not self.lastval['IsOnTrack']:
                self.store['running'] = False
                var.status['calibration'] = "None"
                var.bindings['status']['active'] = False
                self.stop_flash_tab_all()
                var.status['flash_tab'] = []
                sleep(0.01)
                var.bindings['status']['active'] = True
                sleep(0.01)
                vjoy.set('weight_jacker', vjoy.axis_values['weight_jacker']) # bad hack to make sure vjoy is actually 'active'
                var.bindings['status']['active'] = False
            self.lastval['IsOnTrack'] = self.ir['IsOnTrack']
            if self.lastval['CarIdx'] in car_settings and 'limiter' in car_settings[self.lastval['CarIdx']]: # if limiter in car_settings, save limiter minus settings offset for up and down
                var.status['upshift_val'] = car_settings[self.lastval['CarIdx']]['limiter'] - var.settings['local']['upshift_offset']
                var.status['downshift_val'] = car_settings[self.lastval['CarIdx']]['limiter'] - var.settings['local']['downshift_offset']
            else:
                try:
                    var.status['upshift_val'] = self.ir['PlayerCarSLBlinkRPM'] - var.settings['local']['upshift_offset']
                    var.status['downshift_val'] = self.ir['PlayerCarSLBlinkRPM'] - var.settings['local']['downshift_offset']
                except:
                    print("upshift and downshift values failed in updater()")
            if (var.settings['local']['audio'] and (var.settings['local']['upshift_beep'] or var.settings['local']['downshift_beep'] or var.settings['local']['hybrid_low_audio'] or var.settings['local']['hybrid_high_audio'] or var.settings['local']['hybrid_limit_audio'] or var.settings['local']['p2p_behind_audio'] or var.settings['local']['p2p_behind_audio_cont'])):
                self.irsdk_audio()
            # if driver just got in car, self.store['running'] = False; var.status['calibration'] = "None"; var.bindings['status'] = { "active": False, "function": None, "control": None, "input": None, }; self.stop_flash_tab_all()
        elif self.ir.is_initialized and not self.ir.is_connected and self.store['content']['axes_display']['car_id'] != "None":
            self.ir.shutdown()
            self.store['content']['axes_display']['car_id'] = "None"
            self.store['content']['hybrid']['soc_axis'].setValue(0)
            self.store['content']['hybrid']['soc_axis'].update()
            self.store['content']['hybrid']['deploy_lim_axis'].setValue(0)
            self.store['content']['hybrid']['deploy_lim_axis'].update()
            self.store['content']['hybrid']['soc_lcd'].display(str(0.00))
            self.store['content']['hybrid']['soc_lcd'].update()
            self.store['content']['hybrid']['deploy_lim_lcd'].display(str(0.00))
            self.store['content']['hybrid']['deploy_lim_lcd'].update()
            self.store['content']['hybrid']['soc_label'].setStyleSheet("color: red;")
            self.store['content']['hybrid']['deploy_lim_label'].setStyleSheet("color: red;")
            self.update_limits()
            var.gearing = []
        if var.status['refresh_labels']:
            self.update_label_all()
            var.status['refresh_labels'] = False

    def display(self):
        for func in vjoy.axis_values:
            if func in self.store['content']: #only because not every tab has been developed yet...
                pct = vjoy.axis_values[func]
                # print("display check1: ", func, pct)
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
                self.lastval['soc'] = 999.0
                self.store['content']['hybrid']['deploy_lim_axis'].setValue(0)
                self.store['content']['hybrid']['deploy_lim_axis'].update()
                self.store['content']['hybrid']['deploy_lim_lcd'].display(str(0.00))
                self.store['content']['hybrid']['deploy_lim_lcd'].update()
                self.store['content']['hybrid']['deploy_lim_label'].setStyleSheet("color: red;")
                self.lastval['deploy_lim'] = 999.0
            if self.store['content']['settings']['sound'].currentText() == "Yes":
                if self.lastval['soc'] != 999.0:
                    if self.store['content']['hybrid']['soc_axis'].value() <= var.settings['local']['hybrid_low_val'] < self.lastval['soc'] and var.settings['local']['hybrid_low_audio']:
                        print("call play low")
                        fn.start_thread(sfx.play('low'))
                    if self.store['content']['hybrid']['soc_axis'].value() >= var.settings['local']['hybrid_high_val'] > self.lastval['soc'] and var.settings['local']['hybrid_high_audio']:
                        print("call play high")
                        fn.start_thread(sfx.play('high'))
                if self.lastval['deploy_lim'] != 999.0:
                    if self.store['content']['hybrid']['deploy_lim_axis'].value() >= var.settings['local']['hybrid_limit_val'] > self.lastval['deploy_lim'] and var.settings['local']['hybrid_limit_audio']:
                        print("call play deploy limit")
                        fn.start_thread(sfx.play('limit'))
                self.lastval['soc'] = self.store['content']['hybrid']['soc_axis'].value()
                self.lastval['deploy_lim'] = self.store['content']['hybrid']['deploy_lim_axis'].value()
        if var.status['set_list_count'] % 50 == 0:
            self.refresh_profile_list()
            var.status['set_list_count'] = 1
        else:
            var.status['set_list_count'] += 1
        

    @pyqtSlot()
    def calibrate(self):
        if self.store['axis'] in self.store['content']:
            self.store['content'][self.store['axis']]['calibrate'].setText(var.lang['calibrating'])
        else:
            print("Warning: calibrate()")

        vjoy.calibrate(self.store['axis'])
        var.status['calibration'] += "Done"
        while self.store['running']:
            sleep(0.1)
        self.store['content'][self.store['axis']]['calibrate'].setText(var.lang['calibrate'])
        vjoy.set(self.store['axis'], self.store['pct'])

    @pyqtSlot()
    def calibrate_start(self, func):
        if not self.store['running'] and var.status['calibration'] == "None":
            self.store['axis'] = func
            self.store['running'] = True
            var.status['calibration'] = func
            sleep(0.1) #wait for loops to stop
            if not var.status[func]['switched']:
                self.store['pct'] = var.status[func]['primary']
            elif var.status[func]['switched']:
                self.store['pct'] = var.status[func]['secondary']
            self.store['thread_pool'].start(self.calibrate)
        elif func + "Done" == var.status['calibration']:
            var.status['calibration'] = "None"
            self.store['running'] = False
            if func in var.status['flash_tab']:
                var.status['flash_tab'].remove(func)
                self.stop_flash_tab(func)
        elif var.status['calibration'] != "None":
            func_pass = var.status['calibration']
            for function in var.bindings:
                if function + "Done" == func_pass:
                    func_pass = function
            self.start_flash_tab(func_pass)

    @pyqtSlot()
    def increment(self, func):
        var.settings[func]['increment'] = self.store['content'][func]['increment'].value()
        fn.write_profile()

    @pyqtSlot()
    def switch(self, func):
        value = self.store['content'][func]['switch'].value()
        var.settings[func]['switch_value'] = value
        if func == "weight_jacker":
            var.status[func]['secondary'] = (value * var.step[func]) + 0.5
        elif func == "clutch" or func == "throttle":
            var.status[func]['secondary'] = value/100
        else:
            var.status[func]['secondary'] = (value * var.step[func]) - var.step[func]
        if var.status[func]['switched']:
            vjoy.set(func, var.status[func]['secondary'])
        fn.write_profile()

    @pyqtSlot()
    def increment_mode(self, func):
        if self.store['content'][func]['increment_mode'].currentText() == "Continuous":
            var.settings[func]['continuous'] = True
        elif self.store['content'][func]['increment_mode'].currentText() == "Single":
            var.settings[func]['continuous'] = False
        fn.write_profile()

    @pyqtSlot()
    def switch_mode(self, func):
        if self.store['content'][func]['switch_mode'].currentText() == "Toggle":
            var.settings[func]['toggle'] = True
        elif self.store['content'][func]['switch_mode'].currentText() == "Hold":
            var.status[func]['switched'] = False
            vjoy.set(func, var.status[func]['primary'])
            var.settings[func]['toggle'] = False
        fn.write_profile()

    @pyqtSlot()
    def settings_set(self, func):
        if func == 'sound' or func == 'upshift_beep' or func == 'downshift_beep' or func == 'beep_mode' or func == "hybrid_low_audio" or func == "hybrid_high_audio" or func == "hybrid_limit_audio" or func == "p2p_behind_audio" or func == "p2p_behind_audio_cont" or func == "p2p_behind_nobrake" or func == "p2p_behind_closest_car":
            value = self.store['content']['settings'][func].currentText()
        else:
            value = self.store['content']['settings'][func].value()
        if func == 'high_threshold':
            print("settings_set, func = high_threshold, ", value)
            if value/100 > var.settings['local']['low_threshold']:
                print("changing low")
                self.store['content']['settings']['low_threshold'].setRange(1, value-1)
                fn.reset_bind_thresh(func, value/100)
                var.settings['local'][func] = value/100
                fn.write_profile()
        elif func == 'low_threshold':
            print("settings_set, func = low_threshold, ", value)
            if value/100 < var.settings['local']['high_threshold']:
                print("changing high")
                self.store['content']['settings']['high_threshold'].setRange(value+1, 99)
                fn.reset_bind_thresh(func, value/100)
                var.settings['local'][func] = value/100
                fn.write_profile()
        elif func == 'sound':
            var.settings['local']['audio'] = (value == "Yes")
            fn.write_profile()
        elif func == 'upshift_beep' or func == 'downshift_beep' or func == "hybrid_low_audio" or func == "hybrid_high_audio" or func == "hybrid_limit_audio" or func == "p2p_behind_audio" or func == "p2p_behind_audio_cont" or func == "p2p_behind_nobrake" or func == "p2p_behind_closest_car":
            var.settings['local'][func] = (value == "Yes")
            fn.write_profile()
        elif func == 'beep_mode':
            var.settings['local']['beep_mode'] = (value == "Fixed")
            fn.write_profile()
        elif func == 'volume':
            var.settings['local']['volume'] = value/100
            fn.write_profile()
        elif func == "hybrid_low_val" or func == "hybrid_high_val" or func == "hybrid_limit_val" or func == "dynamic_mode_offset" or func == "upshift_offset" or func == "downshift_offset" or func == "p2p_behind_thresh" or func == "p2p_behind_thresh_cont":
            var.settings['local'][func] = value
            fn.write_profile()
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
        # self.store['running'] = True
        function = var.bindings['status']['function']
        control = var.bindings['status']['control']
        history.clear()

        self.store['index'][function][control]['bind'].setText(var.lang['binding'])

        var.event = {
            "guid": 0,
            "type": "",
            "num": 0,
            "value": None,
        }
        var.potential_bind = {}
        # var.bindings[function][control] = {}
        while not var.potential_bind and var.bindings['status']['active']:
            # if not self.store['running']:
            #     var.potential_bind = {"label": "None", "guid": 0, "type": "none", "num": 0}

            if var.event['guid'] != 0:
                if var.event['type'] == "button":
                    if var.event['value'] and not var.bindings['status']['input']:
                        var.potential_bind = {
                            "label": "Unknown device",
                            "guid": var.event['guid'],
                            "type": var.event['type'],
                            "num": var.event['num'],
                        }
                elif var.event['type'] == "axis":
                    if var.bindings['status']['input']:
                        var.potential_bind = {
                            "label": "Unknown device",
                            "guid": var.event['guid'],
                            "type": var.event['type'],
                            "num": var.event['num'],
                            "input": True,
                        }
                    else:
                        if var.event['value'] >= var.settings['local']['high_threshold'] and history.check_valid(var.event['guid'], var.event['num'], var.event['value'], True):
                            var.potential_bind = {
                            "label": "Unknown device",
                                "guid": var.event['guid'],
                                "type": var.event['type'],
                                "num": var.event['num'],
                                "value": var.settings['local']['high_threshold']
                            }
                        if var.event['value'] <= var.settings['local']['low_threshold'] and history.check_valid(var.event['guid'], var.event['num'], var.event['value'], False):
                            var.potential_bind = {
                            "label": "Unknown device",
                                "guid": var.event['guid'],
                                "type": var.event['type'],
                                "num": var.event['num'],
                                "value": var.settings['local']['low_threshold']
                            }
                elif var.event['type'] == "hat":
                    if var.event['value'] != "none" and not var.bindings['status']['input']:
                        var.potential_bind = {
                            "label": "Unknown device",
                            "guid": var.event['guid'],
                            "type": var.event['type'],
                            "num": var.event['num'],
                            "dir": var.event['value'],
                        }
                elif var.event['type'] == "key" and var.event['value']:
                    if not var.event['value'].endswith('ctrl') and not var.event['value'].endswith('shift') and not var.event['value'].endswith('alt') and not var.event['value'].endswith('alt gr'):
                        if var.event['value'] and not var.bindings['status']['input']:
                            var.potential_bind = {
                                "label": "Unknown device",
                                "guid": var.event['guid'],
                                "type": var.event['type'],
                                "num": var.event['num'],
                                "value": var.event['value'],
                            }
            sleep(0.001)

        if var.bindings['status']['active']: # for if binding is suddenly deactiviated due to driver getting in car, keep the last bind
            var.bindings[function][control] = var.potential_bind

        self.store['index'][function][control]['bind'].setText(var.lang['bind'])

        self.store['index'][function][control]['device'].setText(dev.format_device(function, control))

        var.bindings['status'] = {
            "active": False,
            "function": None,
            "control": None,
            "input": None,
        }
        var.potential_bind = {}
        fn.write_profile()
        var.status['refresh_labels'] = True
        # self.store['running'] = False

    @pyqtSlot()
    def bind_start(self, func, ctrl, input=False):
        if not var.bindings['status']['active']:
            var.bindings['status'] = {
                "active": True,
                "function": func,
                "control": ctrl,
                "input": input,
            }
            self.store['thread_pool'].start(self.bind)
        elif func == var.bindings['status']['function'] and ctrl == var.bindings['status']['control'] and input == var.bindings['status']['input']:
            var.potential_bind = {"label": "None", "guid": 0, "type": "none", "num": 0}
        else:
            var.bindings['status']['active'] = False
            # self.store['running'] = False
            sleep(0.01) # race condition, potentially
            var.bindings['status'] = {
                "active": True,
                "function": func,
                "control": ctrl,
                "input": input,
            }
            self.store['thread_pool'].start(self.bind)

    @pyqtSlot()
    def refresh_profile_list(self):
        self.store['profile_busy'] = True
        file = self.store['content']['settings']['profile_select'].currentText()
        self.store['content']['settings']['profile_select'].clear()
        for name in fn.get_profiles():
            self.store['content']['settings']['profile_select'].addItem(name)
        self.store['content']['settings']['profile_select'].setCurrentText(file)
        self.store['profile_busy'] = False

    @pyqtSlot()
    def create_profile(self, name):
        if name not in fn.get_profiles():
            fn.write_profile(name)
        self.refresh_profile_list()
        self.store['content']['settings']['profile_select'].setCurrentText(name)

    @pyqtSlot()
    def delete_profile(self, name):
        fn.delete_profile(name)
        if len(fn.get_profiles()) == 0:
            var.settings['profile']['current'] = 'Default'
            fn.write_profile()
            fn.write_config()
        self.refresh_profile_list()
        self.store['content']['settings']['profile_select'].setCurrentIndex(0)
        var.settings['profile']['current'] = self.store['content']['settings']['profile_select'].currentText()
        fn.read_profile()

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
                var.step['weight_jacker'] = 1 / (max - min)
                self.store['content']['weight_jacker']['switch'].setRange(min, max)
                self.store['content']['axes_display']['weight_jacker_label'].setStyleSheet(QLabel.styleSheet(self.store['index']['car_id']))
            else:
                self.store['content']['axes_display']['weight_jacker_label'].setStyleSheet("color: red;")
            if 'front_roll_bar' in car_settings[car_id]:
                min = car_settings[car_id]['front_roll_bar'][0]
                max = car_settings[car_id]['front_roll_bar'][1]
                var.step['front_roll_bar'] = 1 / (max - min)
                self.store['content']['front_roll_bar']['switch'].setRange(min, max)
                self.store['content']['axes_display']['front_roll_bar_label'].setStyleSheet(QLabel.styleSheet(self.store['index']['car_id']))
            else:
                self.store['content']['axes_display']['front_roll_bar_label'].setStyleSheet("color: red;")
            if 'rear_roll_bar' in car_settings[car_id]:
                min = car_settings[car_id]['rear_roll_bar'][0]
                max = car_settings[car_id]['rear_roll_bar'][1]
                var.step['rear_roll_bar'] = 1 / (max - min)
                self.store['content']['rear_roll_bar']['switch'].setRange(min, max)
                self.store['content']['axes_display']['rear_roll_bar_label'].setStyleSheet(QLabel.styleSheet(self.store['index']['car_id']))
            else:
                self.store['content']['axes_display']['rear_roll_bar_label'].setStyleSheet("color: red;")
            if 'fuel_map' in car_settings[car_id]:
                min = car_settings[car_id]['fuel_map'][0]
                max = car_settings[car_id]['fuel_map'][1]
                var.step['fuel_map'] = 1 / (max - min)
                self.store['content']['fuel_map']['switch'].setRange(min, max)
                self.store['content']['axes_display']['fuel_map_label'].setStyleSheet(QLabel.styleSheet(self.store['index']['car_id']))
            else:
                self.store['content']['axes_display']['fuel_map_label'].setStyleSheet("color: red;")
        else:
            car_id = self.store['content']['axes_display']['car_id']
            self.store['index']['car_id'].setText(str(car_id) + " (not in car_settings list yet)")
            print("current_car " + str(car_id) + " not in car_settings!")
            self.store['content']['axes_display']['weight_jacker_label'].setStyleSheet("color: red;")
            self.store['content']['axes_display']['front_roll_bar_label'].setStyleSheet("color: red;")
            self.store['content']['axes_display']['rear_roll_bar_label'].setStyleSheet("color: red;")
            self.store['content']['axes_display']['fuel_map_label'].setStyleSheet("color: red;")
        text = "WJ: " + str(int(self.store['content']['weight_jacker']['switch'].minimum())) + " to " + str(int(self.store['content']['weight_jacker']['switch'].maximum()))
        text += ", FARB: " + str(int(self.store['content']['front_roll_bar']['switch'].minimum())) + " to " + str(int(self.store['content']['front_roll_bar']['switch'].maximum()))
        text += ", RARB: " + str(int(self.store['content']['rear_roll_bar']['switch'].minimum())) + " to " + str(int(self.store['content']['rear_roll_bar']['switch'].maximum()))
        text += ", Fuel Map: " + str(int(self.store['content']['fuel_map']['switch'].minimum())) + " to " + str(int(self.store['content']['fuel_map']['switch'].maximum()))
        self.store['content']['axes_display']['car_id_limits'].setText(text)

    @pyqtSlot()
    def update_label(self, function, control):
        try:
            if var.bindings[function][control]:
                if var.bindings[function][control]['label'] != "None" and var.bindings[function][control]['guid'] == 0:
                    self.store['content'][function][control + '_device'].setStyleSheet("color: firebrick;")
                else:
                    self.store['content'][function][control + '_device'].setStyleSheet(QLabel.styleSheet(self.store['index']['car_id']))
                if var.bindings[function][control]['label'] and var.bindings[function][control]['guid'] in dev.device_info:
                    var.status['rewrite']['profile'] = True
                    self.store['content'][function][control + '_device'].setText(dev.format_device(function, control))
                    if var.status['rewrite']['profile']:
                        fn.write_profile()
                        var.status['rewrite']['profile'] = False
                self.store['content'][function][control + '_device'].setText(var.bindings[function][control]['label'])
        except KeyError as error:
            print("in update_label(func,ctrl): ", error)
    
    def update_label_all(self):
        try:
            for function in var.bindings:
                if function != "status":
                    for control in var.bindings[function]:
                        self.update_label(function, control)
        except KeyError as error:
            print("in update_label_all(): ", error)

    @pyqtSlot()
    def apply_settings(self, file):
        # print("try apply_settings")
        if self.store['profile_busy']: #if list is getting cleared or current text is being reset during list refresh, skip this function
            return
        print("proceeding with apply_settings")

        fn.read_profile(file)
        fn.write_config()

        for type in self.tabs['types']:
            for function in self.tabs['types'][type]:
                if type == "adjustment" or type == "input":
                    self.store['content'][function]['increment'].setValue(var.settings[function]['increment'])
                    self.store['content'][function]['switch'].setValue(var.settings[function]['switch_value'])
                    if var.settings[function]['continuous']:
                        self.store['content'][function]['increment_mode'].setCurrentText(var.lang['continuous'])
                    else:
                        self.store['content'][function]['increment_mode'].setCurrentText(var.lang['single'])
                    if var.settings[function]['toggle']:
                        self.store['content'][function]['switch_mode'].setCurrentText(var.lang['toggle'])
                    else:
                        self.store['content'][function]['switch_mode'].setCurrentText(var.lang['hold'])

        # self.store['content']['settings']['axis_samples'].setValue(int(var.settings['axis_samples']))
        self.store['content']['settings']['scale'].setCurrentText(str(var.settings['scale']) + "x")
        self.store['content']['settings']['timer_first'].setValue(int(var.settings['timer_first']))
        self.store['content']['settings']['timer_loop'].setValue(int(var.settings['timer_loop']))
        self.store['content']['settings']['profile_select'].setCurrentText(var.settings['profile']['current'])
        for setting in var.settings['local']:
            if setting == "audio":
                if var.settings['local']['audio']:
                    self.store['content']['settings']['sound'].setCurrentText('Yes')
                else:
                    self.store['content']['settings']['sound'].setCurrentText('No')
            elif setting == 'low_threshold' or setting == 'high_threshold':
                print("apply_settings before ", setting)
                self.store['content']['settings']['high_threshold'].setRange(min(int(var.settings['local']['low_threshold']*100)+1,51), 99)
                self.store['content']['settings']['low_threshold'].setRange(1, max(int(var.settings['local']['high_threshold']*100)-1,49))
                self.store['content']['settings']['high_threshold'].setValue(int(var.settings['local']['high_threshold'] * 100))
                self.store['content']['settings']['low_threshold'].setValue(int(var.settings['local']['low_threshold'] * 100))
                print("apply_settings after, ", setting)
            elif isinstance(var.settings['local'][setting], bool):
                if var.settings['local'][setting]:
                    self.store['content']['settings'][setting].setCurrentText('Yes')
                else:
                    self.store['content']['settings'][setting].setCurrentText('No')
            elif isinstance(var.settings['local'][setting], (float, int)):
                if setting == 'volume':
                    self.store['content']['settings']['volume'].setValue(int(var.settings['local']['volume']*100))
                else:
                    self.store['content']['settings'][setting].setValue(int(var.settings['local'][setting]))
            else:
                if not setting == 'version':
                    print("isinstance check failed", setting, var.settings['local'][setting])
        print ("end apply_settings")

    @pyqtSlot()
    def start_flash_tab(self, func):
        if not func in var.status['flash_tab']:
            var.status['flash_tab'].append(func)
            index = self.tabs['obj'].indexOf(self.tabs[func])
            self.default_tab_color = self.tabs['obj'].tabBar().tabTextColor(index)
            self.tabs['obj'].tabBar().setTabTextColor(index, QColor("red"))
            self.flashtimer[func] = QTimer()
            self.flashtimer[func].timeout.connect(lambda: self.alt_flash(index))
            self.flashtimer[func].start(250)

    @pyqtSlot()
    def stop_flash_tab(self, func):
        self.flashtimer[func].stop()
        index = self.tabs['obj'].indexOf(self.tabs[func])
        self.default_tab_color = self.tabs['obj'].tabBar().setTabTextColor(index, self.default_tab_color)

    @pyqtSlot()
    def stop_flash_tab_all(self):
        for func in var.status['flash_tab']:
            self.flashtimer[func].stop()
            index = self.tabs['obj'].indexOf(self.tabs[func])
            self.default_tab_color = self.tabs['obj'].tabBar().setTabTextColor(index, self.default_tab_color)

    @pyqtSlot()
    def alt_flash(self, index):
        if self.tabs['obj'].tabBar().tabTextColor(index) == self.default_tab_color:
                self.tabs['obj'].tabBar().setTabTextColor(index, QColor("red"))
        else:
            self.tabs['obj'].tabBar().setTabTextColor(index, self.default_tab_color)

    @pyqtSlot()
    def irsdk_audio(self):
        # print("shift_beep() start")
        if self.lastval['SessionTick'] != self.ir['SessionTick']: # if the information is not new, do nothing because there is no new information
            # ideally would copy a snapshot of self.ir at this moment to make sure all the information is from the same set, but this is probably close enough
            self.lastval['IsOnTrack_beep'] = self.ir['IsOnTrack']
            self.lastval['OnPitRoad'] = self.ir['OnPitRoad']
            self.lastval['Throttle'] = self.ir['Throttle']
            self.lastval['Brake'] = self.ir['Brake']
            self.lastval['Clutch'] = self.ir['Clutch']
            self.lastval['Gear'] = self.ir['Gear']
            self.lastval['RPM'] = self.ir['RPM']
            self.lastval['Speed'] = self.ir['Speed']
            self.lastval['p2p'] = self.ir['P2P_Status']
            self.lastval['CarIdxp2p'] = self.ir['CarIdxP2P_Status']
            self.lastval['CarIdxEstTime'] = self.ir['CarIdxEstTime']
            self.lastval['CarIdx_Within_p2p_Range'] = []
            self.lastval['CarIdx_Within_Cont_p2p_Range'] = []
            length = len(self.ir['DriverInfo']['Drivers'])
            index = length-1
            self.lastval['CarIdxList'] = [-1] * length
            while index >= 0:
                self.lastval['CarIdxList'][index] = self.ir['DriverInfo']['Drivers'][index]['CarIdx']
                if (var.settings['local']['p2p_behind_thresh'] == -1 or (self.lastval['CarIdxEstTime'][index] - self.lastval['CarIdxEstTime'][self.lastval['CarIdx']] > 0 and self.lastval['CarIdxEstTime'][index] - self.lastval['CarIdxEstTime'][self.lastval['CarIdx']] < var.settings['local']['p2p_behind_thresh']/1000)) and self.ir['DriverInfo']['Drivers'][index]['CarIsPaceCar'] == 0 and self.ir['CarIdxOnPitRoad'][index] == False and not self.lastval['CarIdx'] == index:
                    if not var.settings['local']['p2p_behind_closest_car']:
                        self.lastval['CarIdx_Within_p2p_Range'].append(index)
                    else:
                        if (self.lastval['CarIdx_Within_p2p_Range'] == [] or self.lastval['CarIdxEstTime'][index] < self.lastval['CarIdxEstTime'][self.lastval['CarIdx_Within_p2p_Range'][0]]) and self.ir['DriverInfo']['Drivers'][index]['CarIsPaceCar'] == 0 and self.ir['CarIdxOnPitRoad'][index] == False and not self.lastval['CarIdx'] == index:
                            self.lastval['CarIdx_Within_p2p_Range'] = [index]
                if (var.settings['local']['p2p_behind_thresh_cont'] == -1 (self.lastval['CarIdxEstTime'][index] - self.lastval['CarIdxEstTime'][self.lastval['CarIdx']] > 0 and self.lastval['CarIdxEstTime'][index] - self.lastval['CarIdxEstTime'][self.lastval['CarIdx']] < var.settings['local']['p2p_behind_thresh_cont']/1000)) and self.ir['DriverInfo']['Drivers'][index]['CarIsPaceCar'] == 0 and self.ir['CarIdxOnPitRoad'][index] == False and not self.lastval['CarIdx'] == index:
                    if not var.settings['local']['p2p_behind_closest_car']:
                        self.lastval['CarIdx_Within_Cont_p2p_Range'].append(index)
                    else:
                        if (self.lastval['CarIdx_Within_Cont_p2p_Range'] == [] or self.lastval['CarIdxEstTime'][index] < self.lastval['CarIdxEstTime'][self.lastval['CarIdx_Within_Cont_p2p_Range'][0]]) and self.ir['DriverInfo']['Drivers'][index]['CarIsPaceCar'] == 0 and self.ir['CarIdxOnPitRoad'][index] == False and not self.lastval['CarIdx'] == index:
                            self.lastval['CarIdx_Within_Cont_p2p_Range'] = [index]
                index -= 1
            # print(self.lastval['CarIdx_Within_p2p_Range'], self.lastval['CarIdx_Within_Cont_p2p_Range'])
            if var.settings['local']['p2p_behind_audio'] or var.settings['local']['p2p_behind_audio_cont']:
                if var.settings['local']['p2p_behind_nobrake'] and self.lastval['Brake'] > 0.05:
                    var.status['p2p_sound_active']['single'] = False
                    var.status['p2p_sound_active']['loop'] = False
                    sfx.p2p_active.stop()
                else:
                    if var.settings['local']['p2p_behind_audio_cont']:
                        if self.lastval['CarIdx_Within_Cont_p2p_Range'] == []:
                            var.status['p2p_sound_active']['loop'] = False
                        # elif var.status['p2p_sound_active']['loop'] == False:
                        else:
                            var.status['p2p_sound_active']['loop'] = False
                            for CarIdx in self.lastval['CarIdx_Within_Cont_p2p_Range']:
                                if self.lastval['CarIdxp2p'][CarIdx] == True:
                                    var.status['p2p_sound_active']['loop'] = True
                            if var.status['p2p_sound_active']['loop'] == True:
                                fn.start_thread(sfx.play_loop('p2p_active'))
                    else:
                        var.status['p2p_sound_active']['loop'] = False
                    if var.settings['local']['p2p_behind_audio']:
                        if self.lastval['CarIdx_Within_p2p_Range'] == []:
                            var.status['p2p_sound_active']['single'] = False
                        elif var.status['p2p_sound_active']['single'] == False:
                        # else:
                            var.status['p2p_sound_active']['single'] = False
                            for CarIdx in self.lastval['CarIdx_Within_p2p_Range']:
                                if self.lastval['CarIdxp2p'][CarIdx] == True:
                                    var.status['p2p_sound_active']['single'] = True
                            if var.status['p2p_sound_active']['single'] == True:
                                fn.start_thread(sfx.play('p2p_active'))
                            elif sfx.p2p_active.get_num_channels() == 0:
                                sfx.status['p2p_active_single'] = False
                            var.status['p2p_sound_active']['single'] = False
                    else:
                        var.status['p2p_sound_active']['single'] = False
            else:
                var.status['p2p_sound_active']['single'] = False
                var.status['p2p_sound_active']['loop'] = False
                sfx.status["p2p_active"] = False
                sfx.status["p2p_active_single"] = False
            if var.status['p2p_sound_active']['loop'] == False and sfx.status['p2p_active_loop']:
                fn.start_thread(sfx.stop_loop('p2p_active'))


            if self.lastval['Speed'] == 0:
                self.lastval['RPM/Speed'] = 0
            else:
                self.lastval['RPM/Speed'] = self.lastval['RPM']/self.lastval['Speed']
            if self.lastval['IsOnTrack_beep'] and not self.lastval['OnPitRoad'] and self.lastval['Throttle'] == 1.0 and self.lastval['Brake'] == 0.0 and self.lastval['Clutch'] == 1.0 and self.lastval['Gear'] > 0: # update RPM to gear guesses
                if len(var.gearing) < self.lastval['Gear']:
                    ind = 0
                    while ind <= self.lastval['Gear']:
                        if len(var.gearing) < ind:
                            var.gearing.append([])
                        ind += 1
                # print(self.lastval['Gear'], len(var.gearing))
                if var.gearing[self.lastval['Gear']-1] == [] or var.gearing[self.lastval['Gear']-1][0] == 0:
                    var.gearing[self.lastval['Gear']-1] = [1, self.lastval['RPM/Speed'], 0.0]
                else:
                    if var.gearing[self.lastval['Gear']-1][0] < 1:
                        print("WARNING: something with sample count in shift_beep() has gone wrong, number of samples is below 1")
                    std_dev = math.sqrt(var.gearing[self.lastval['Gear']-1][2])
                    old_avg = var.gearing[self.lastval['Gear']-1][1]
                    # print(self.lastval['RPM/Speed'])
                    if var.gearing[self.lastval['Gear']-1][0] < 10 or abs(self.lastval['RPM/Speed'] - old_avg) < std_dev*3:
                        var.gearing[self.lastval['Gear']-1][0] += 1 # update number of samples
                        var.gearing[self.lastval['Gear']-1][1] += (self.lastval['RPM/Speed']-var.gearing[self.lastval['Gear']-1][1])/(var.gearing[self.lastval['Gear']-1][0]) # update average
                        var.gearing[self.lastval['Gear']-1][2] *= var.gearing[self.lastval['Gear']-1][0]-2 # update std dev, in 3 parts
                        var.gearing[self.lastval['Gear']-1][2] += (self.lastval['RPM/Speed']-var.gearing[self.lastval['Gear']-1][1])*(self.lastval['RPM/Speed']-old_avg)
                        var.gearing[self.lastval['Gear']-1][2] /= var.gearing[self.lastval['Gear']-1][0]-1
                # print(var.gearing)
            elif not self.lastval['IsOnTrack_beep']: # if the car physics are reset, wipe gearing data as don't know if setup changed or not
                i = 0
                while i < len(var.gearing):
                    var.gearing[i] = [0, 0, 0]
                    i += 1
            else: # if on track but not in a state to update gearing data, still update the length of the gearing list if needed
                if len(var.gearing) < self.lastval['Gear']:
                    ind = 0
                    while ind <= self.lastval['Gear']:
                        if len(var.gearing) < ind:
                            var.gearing.append([])
                        ind += 1

            
            if self.lastval['IsOnTrack_beep'] and self.lastval['Gear'] > 0: # determine if a beep is required now
                if var.settings['local']['audio'] and (var.settings['local']['upshift_beep'] or var.settings['local']['downshift_beep']):
                    if var.settings['local']['beep_mode'] == True: # True -> fixed beep setting
                        if var.settings['local']['upshift_beep'] and len(var.gearing) >= self.lastval['Gear'] and var.gearing[self.lastval['Gear']-1] != [] and var.gearing[self.lastval['Gear']-1][1] != 0 and var.status['upshift_val'] > 0:
                            if self.lastval['Speed'] * var.gearing[self.lastval['Gear']-1][1] > var.status['upshift_val'] + (self.lastval['p2p'] == True)*300: # p2p pushes upshift beep up by 300RPM
                                # print("call play upshift_beep ", var.status['upshift_val'], self.lastval['Speed'], self.lastval['Gear'], var.gearing)
                                fn.start_thread(sfx.play('upshift_beep'))
                            else:
                                sfx.status['upshift_beep'] = False
                        if var.settings['local']['downshift_beep'] and self.lastval['Gear'] > 1 and var.gearing[self.lastval['Gear']-2] != [] and var.gearing[self.lastval['Gear']-2][1] != 0 and var.status['downshift_val'] > 0:
                            if self.lastval['Speed'] * var.gearing[self.lastval['Gear']-2][1] < var.status['downshift_val']:
                                # print("call play downshift_beep ", var.status['downshift_val'])
                                fn.start_thread(sfx.play('downshift_beep'))
                            else:
                                sfx.status['downshift_beep'] = False
                    # elif var.settings['local']['beep_mode'] == "Dynamic":
                    #     return
            elif self.lastval['Gear'] == 0:
                sfx.status['upshift_beep'] = False # maybe only do this after upshifting?
                sfx.status['downshift_beep'] = False # maybe only reset this when an upshift happens?
        # print("shift_beep() end")

class CustomComboBox(QComboBox):
    def wheelEvent(self ,event: QWheelEvent):
        event.ignore()

class CustomSpinBox(QSpinBox):
    def wheelEvent(self, event: QWheelEvent):
        event.ignore()

class CustomDoubleSpinBox(QDoubleSpinBox):
    def wheelEvent(self, event: QWheelEvent):
        event.ignore()

def main():
    os.environ["QT_SCALE_FACTOR"] = str(var.settings['scale'])

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    window.update()
    # app.setStyle('Fusion')
    app.exec()