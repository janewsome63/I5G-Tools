import os
import sys

import history
from time import sleep

from PyQt6.QtCore import (
    QSize,
    Qt,
    QTimer,
    QThreadPool,
    pyqtSlot
)

from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QLabel,
    QLCDNumber,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QGridLayout,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QLineEdit
)

from PyQt6.QtGui import (
    QIcon,
)

from controls import step
import functions as fn
import variables as var
import vjoy
import devices as dev
import irsdk
from car_settings_list import car_settings

lang = {
    "title": "I5G Tools",
    "version": "v0.2.2b",
    "pedal": "Pedal Axis:",
    "up": "Increase:",
    "down": "Decrease:",
    "switch": "Switch:",
    "increment": "Increment:",
    "switch_value": "Switch Value:",
    "switch_mode": "Switch Mode:",
    "hold": "Hold",
    "toggle": "Toggle",
    "increment_mode": "Increment Mode:",
    "continuous": "Continuous",
    "single": "Single",
    "bind": "Bind",
    "binding": "<-Binding->",
    "calibrate": "Calibrate",
    "calibrating": "<-Calibrating->",
    "high_threshold": "High Axis Threshold:",
    "low_threshold": "Low Axis Threshold:",
    "axis_samples": "Number of Axis Samples:",
    "scale": "Scale Factor:",
    "timer_loop": "Continuous Mode Loop Timer (in ms):",
    "timer_first": "Continuous Mode Initial Loop Timer (in ms)",
    "none": "None",
    "weight_jacker": "Weight Jacker",
    "front_roll_bar": "Front Bar",
    "rear_roll_bar": "Rear Bar",
    "fuel_map": "Fuel Map",
    "bite_point": "Clutch",
    "engine_warming": "Throttle",
    "settings": "Settings",
    "settings_filename": "Current Settings File:",
    "axes_display": "Display",
    "car_id": "Car ID:",
}

ui = {
    "width": 575,
    "height": 250,
    "timer": QTimer(),
    "thread_pool": QThreadPool(),
}

var.settings = {
    "high_threshold": 0.90,
    "low_threshold": 0.10,
    "frequency": 0.1,
    "scale": 1.25,
    "axis_samples": 2,
    "timer_loop": 150,
    "timer_first": 300,

    "weight_jacker": {
        "continuous": True,
        "toggle": False,
        "increment": 1,
        "switch_value": 20,
    },
    "front_roll_bar": {
        "continuous": False,
        "toggle": False,
        "increment": 1,
        "switch_value": 1,
    },
    "rear_roll_bar": {
        "continuous": False,
        "toggle": False,
        "increment": 1,
        "switch_value": 6,
    },
    "fuel_map": {
        "continuous": False,
        "toggle": True,
        "increment": 1,
        "switch_value": 8,
    },
    "bite_point": {
        "continuous": False,
        "toggle": False,
        "increment": 1,
        "switch_value": 50,
    },
    "engine_warming": {
        "continuous": False,
        "toggle": False,
        "increment": 1,
        "switch_value": 50,
    },
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_running = False

        if getattr(sys, 'frozen', False):
            applicationPath = sys._MEIPASS
        elif __file__:
            applicationPath = os.path.dirname(__file__)
        self.setWindowIcon(QIcon(os.path.join(applicationPath, "icon.ico")))

        self.setWindowTitle(lang['title'] + " " + lang['version'])
        self.setFixedSize(QSize(ui['width'], ui['height']))
        self.layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.weight_jacker = QWidget()
        self.front_roll_bar = QWidget()
        self.rear_roll_bar = QWidget()
        self.fuel_map = QWidget()
        self.bite_point = QWidget()
        self.engine_warming = QWidget()
        self.settings = QWidget()
        self.axes_display = QWidget()

        self.tabs.addTab(self.weight_jacker, lang['weight_jacker'])
        self.tabs.addTab(self.front_roll_bar, lang['front_roll_bar'])
        self.tabs.addTab(self.rear_roll_bar, lang['rear_roll_bar'])
        self.tabs.addTab(self.fuel_map, lang['fuel_map'])
        self.tabs.addTab(self.bite_point, lang['bite_point'])
        self.tabs.addTab(self.engine_warming, lang['engine_warming'])
        self.tabs.addTab(self.settings, lang['settings'])
        self.tabs.addTab(self.axes_display, lang['axes_display'])

        self.content = {
            "weight_jacker": {
                "weight_jacker": {},
            },
            "front_roll_bar": {
                "front_roll_bar": {},
            },
            "rear_roll_bar": {
                "rear_roll_bar": {},
            },
            "fuel_map": {
               "fuel_map": {},
            },
            "bite_point": {
                "bite_point": {},
            },
            "engine_warming": {
                "engine_warming": {},
            },
            "settings": {},
            "axes_display":{
                "car_id": {},
                "weight_jacker": {},
                "front_roll_bar": {},
                "rear_roll_bar": {},
                "fuel_map": {},
                "bite_point": {},
                "engine_warming": {},
            },
            }
        
                # --------Weight Jacker Tab--------#
        self.weight_jacker.layout = QGridLayout()

        self.content['weight_jacker']['lcd'] = QLCDNumber()
        self.content['weight_jacker']['lcd'].display(0)
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['lcd'], 0, 0)

        self.content['weight_jacker']['axis'] = QProgressBar()
        self.content['weight_jacker']['axis'].setTextVisible(False)
        self.content['weight_jacker']['axis'].setMinimum(0)
        self.content['weight_jacker']['axis'].setMaximum(100)
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['axis'], 0, 1)

        self.content['weight_jacker']['calibrate'] = QPushButton()
        self.content['weight_jacker']['calibrate'].setFixedSize(100, 25)
        self.content['weight_jacker']['calibrate'].setText(lang['calibrate'])
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['calibrate'], 0, 2)
        self.content['weight_jacker']['calibrate'].clicked.connect(lambda: self.calibrate_start("weight_jacker"))

        self.content['weight_jacker']['increment_label'] = QLabel()
        self.content['weight_jacker']['increment_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['weight_jacker']['increment_label'].setText(lang['increment'])
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['increment_label'], 1, 0)

        self.content['weight_jacker']['switch_label'] = QLabel()
        self.content['weight_jacker']['switch_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['weight_jacker']['switch_label'].setText(lang['switch_value'])
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['switch_label'], 1, 1)

        self.content['weight_jacker']['increment'] = QSpinBox()
        self.content['weight_jacker']['increment'].setFixedSize(70, 25)
        self.content['weight_jacker']['increment'].setRange(1, 20)
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['increment'], 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['weight_jacker']['increment'].valueChanged.connect(lambda: self.increment("weight_jacker"))

        self.content['weight_jacker']['switch'] = QSpinBox()
        self.content['weight_jacker']['switch'].setFixedSize(70, 25)
        self.content['weight_jacker']['switch'].setRange(-20, 20)
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['switch'], 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['weight_jacker']['switch'].valueChanged.connect(lambda: self.switch("weight_jacker"))

        self.content['weight_jacker']['increment_mode_label'] = QLabel()
        self.content['weight_jacker']['increment_mode_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['weight_jacker']['increment_mode_label'].setText(lang['increment_mode'])
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['increment_mode_label'], 2, 0)

        self.content['weight_jacker']['switch_mode_label'] = QLabel()
        self.content['weight_jacker']['switch_mode_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['weight_jacker']['switch_mode_label'].setText(lang['switch_mode'])
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['switch_mode_label'], 2, 1)

        self.content['weight_jacker']['increment_mode'] = QComboBox()
        self.content['weight_jacker']['increment_mode'].setFixedSize(100, 25)
        self.content['weight_jacker']['increment_mode'].addItem(lang['continuous'])
        self.content['weight_jacker']['increment_mode'].addItem(lang['single'])
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['increment_mode'], 2, 1)
        self.content['weight_jacker']['increment_mode'].currentIndexChanged.connect(lambda: self.increment_mode("weight_jacker"))

        self.content['weight_jacker']['switch_mode'] = QComboBox()
        self.content['weight_jacker']['switch_mode'].setFixedSize(70, 25)
        self.content['weight_jacker']['switch_mode'].addItem(lang['hold'])
        self.content['weight_jacker']['switch_mode'].addItem(lang['toggle'])
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['switch_mode'], 2, 2)
        self.content['weight_jacker']['switch_mode'].currentIndexChanged.connect(lambda: self.switch_mode("weight_jacker"))

        self.content['weight_jacker']['up_label'] = QLabel()
        self.content['weight_jacker']['up_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['weight_jacker']['up_label'].setText(lang['up'])
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['up_label'], 3, 0)

        self.content['weight_jacker']['up_device'] = QLineEdit()
        self.content['weight_jacker']['up_device'].setFixedHeight(25)
        self.content['weight_jacker']['up_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['weight_jacker']['up_device'].setReadOnly(True)
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['up_device'], 3, 1)

        self.content['weight_jacker']['up_bind'] = QPushButton()
        self.content['weight_jacker']['up_bind'].setFixedSize(100, 25)
        self.content['weight_jacker']['up_bind'].setText(lang['bind'])
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['up_bind'], 3, 2)
        self.content['weight_jacker']['up_bind'].clicked.connect(lambda: self.bind_start("weight_jacker","up"))

        self.content['weight_jacker']['down_label'] = QLabel()
        self.content['weight_jacker']['down_label'].setAlignment(Qt.AlignmentFlag.AlignVCenter.AlignLeft)
        self.content['weight_jacker']['down_label'].setText(lang['down'])
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['down_label'], 4, 0)

        self.content['weight_jacker']['down_device'] = QLineEdit()
        self.content['weight_jacker']['down_device'].setFixedHeight(25)
        self.content['weight_jacker']['down_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['weight_jacker']['down_device'].setReadOnly(True)
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['down_device'], 4, 1)

        self.content['weight_jacker']['down_bind'] = QPushButton()
        self.content['weight_jacker']['down_bind'].setFixedSize(100, 25)
        self.content['weight_jacker']['down_bind'].setText(lang['bind'])
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['down_bind'], 4, 2)
        self.content['weight_jacker']['down_bind'].clicked.connect(lambda: self.bind_start("weight_jacker","down"))

        self.content['weight_jacker']['switch_label'] = QLabel()
        self.content['weight_jacker']['switch_label'].setFixedHeight(25)
        self.content['weight_jacker']['switch_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['weight_jacker']['switch_label'].setText(lang['switch'])
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['switch_label'], 5, 0)

        self.content['weight_jacker']['switch_device'] = QLineEdit()
        self.content['weight_jacker']['switch_device'].setFixedHeight(25)
        self.content['weight_jacker']['switch_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['weight_jacker']['switch_device'].setReadOnly(True)
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['switch_device'], 5, 1)

        self.content['weight_jacker']['switch_bind'] = QPushButton()
        self.content['weight_jacker']['switch_bind'].setFixedSize(100, 25)
        self.content['weight_jacker']['switch_bind'].setText(lang['bind'])
        self.weight_jacker.layout.addWidget(self.content['weight_jacker']['switch_bind'], 5, 2)
        self.content['weight_jacker']['switch_bind'].clicked.connect(lambda: self.bind_start("weight_jacker","switch"))

        self.weight_jacker.setLayout(self.weight_jacker.layout)

        # --------Front Roll Bar Tab--------#
        self.front_roll_bar.layout = QGridLayout()

        self.content['front_roll_bar']['lcd'] = QLCDNumber()
        self.content['front_roll_bar']['lcd'].display(1)
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['lcd'], 1, 0)

        self.content['front_roll_bar']['axis'] = QProgressBar()
        self.content['front_roll_bar']['axis'].setTextVisible(False)
        self.content['front_roll_bar']['axis'].setMinimum(0)
        self.content['front_roll_bar']['axis'].setMaximum(100)
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['axis'], 1, 1)

        self.content['front_roll_bar']['calibrate'] = QPushButton()
        self.content['front_roll_bar']['calibrate'].setFixedSize(100, 25)
        self.content['front_roll_bar']['calibrate'].setText(lang['calibrate'])
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['calibrate'], 1, 2)
        self.content['front_roll_bar']['calibrate'].clicked.connect(lambda: self.calibrate_start("front_roll_bar"))

        self.content['front_roll_bar']['increment_label'] = QLabel()
        self.content['front_roll_bar']['increment_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['front_roll_bar']['increment_label'].setText(lang['increment'])
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['increment_label'], 2, 0)

        self.content['front_roll_bar']['switch_label'] = QLabel()
        self.content['front_roll_bar']['switch_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['front_roll_bar']['switch_label'].setText(lang['switch_value'])
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['switch_label'], 2, 1)

        self.content['front_roll_bar']['increment'] = QSpinBox()
        self.content['front_roll_bar']['increment'].setFixedSize(70, 25)
        self.content['front_roll_bar']['increment'].setRange(1, 5)
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['increment'], 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['front_roll_bar']['increment'].valueChanged.connect(lambda: self.increment("front_roll_bar"))

        self.content['front_roll_bar']['switch'] = QSpinBox()
        self.content['front_roll_bar']['switch'].setFixedSize(70, 25)
        self.content['front_roll_bar']['switch'].setRange(1, 6)
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['switch'], 2, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['front_roll_bar']['switch'].valueChanged.connect(lambda: self.switch("front_roll_bar"))

        self.content['front_roll_bar']['increment_mode_label'] = QLabel()
        self.content['front_roll_bar']['increment_mode_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['front_roll_bar']['increment_mode_label'].setText(lang['increment_mode'])
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['increment_mode_label'], 3, 0)

        self.content['front_roll_bar']['switch_mode_label'] = QLabel()
        self.content['front_roll_bar']['switch_mode_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['front_roll_bar']['switch_mode_label'].setText(lang['switch_mode'])
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['switch_mode_label'], 3, 1)

        self.content['front_roll_bar']['increment_mode'] = QComboBox()
        self.content['front_roll_bar']['increment_mode'].setFixedSize(100, 25)
        self.content['front_roll_bar']['increment_mode'].addItem(lang['continuous'])
        self.content['front_roll_bar']['increment_mode'].addItem(lang['single'])
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['increment_mode'], 3, 1)
        self.content['front_roll_bar']['increment_mode'].currentIndexChanged.connect(lambda: self.increment_mode("front_roll_bar"))

        self.content['front_roll_bar']['switch_mode'] = QComboBox()
        self.content['front_roll_bar']['switch_mode'].setFixedSize(70, 25)
        self.content['front_roll_bar']['switch_mode'].addItem(lang['hold'])
        self.content['front_roll_bar']['switch_mode'].addItem(lang['toggle'])
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['switch_mode'], 3, 2)
        self.content['front_roll_bar']['switch_mode'].currentIndexChanged.connect(lambda: self.switch_mode("front_roll_bar"))

        self.content['front_roll_bar']['up_label'] = QLabel()
        self.content['front_roll_bar']['up_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['front_roll_bar']['up_label'].setText(lang['up'])
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['up_label'], 4, 0)

        self.content['front_roll_bar']['up_device'] = QLineEdit()
        self.content['front_roll_bar']['up_device'].setFixedHeight(25)
        self.content['front_roll_bar']['up_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['front_roll_bar']['up_device'].setReadOnly(True)
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['up_device'], 4, 1)

        self.content['front_roll_bar']['up_bind'] = QPushButton()
        self.content['front_roll_bar']['up_bind'].setFixedSize(100, 25)
        self.content['front_roll_bar']['up_bind'].setText(lang['bind'])
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['up_bind'], 4, 2)
        self.content['front_roll_bar']['up_bind'].clicked.connect(lambda: self.bind_start("front_roll_bar","up"))

        self.content['front_roll_bar']['down_label'] = QLabel()
        self.content['front_roll_bar']['down_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['front_roll_bar']['down_label'].setText(lang['down'])
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['down_label'], 5, 0)

        self.content['front_roll_bar']['down_device'] = QLineEdit()
        self.content['front_roll_bar']['down_device'].setFixedHeight(25)
        self.content['front_roll_bar']['down_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['front_roll_bar']['down_device'].setReadOnly(True)
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['down_device'], 5, 1)

        self.content['front_roll_bar']['down_bind'] = QPushButton()
        self.content['front_roll_bar']['down_bind'].setFixedSize(100, 25)
        self.content['front_roll_bar']['down_bind'].setText(lang['bind'])
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['down_bind'], 5, 2)
        self.content['front_roll_bar']['down_bind'].clicked.connect(lambda: self.bind_start("front_roll_bar","down"))

        self.content['front_roll_bar']['switch_label'] = QLabel()
        self.content['front_roll_bar']['switch_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['front_roll_bar']['switch_label'].setText(lang['switch'])
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['switch_label'], 6, 0)

        self.content['front_roll_bar']['switch_device'] = QLineEdit()
        self.content['front_roll_bar']['switch_device'].setFixedHeight(25)
        self.content['front_roll_bar']['switch_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['front_roll_bar']['switch_device'].setReadOnly(True)
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['switch_device'], 6, 1)

        self.content['front_roll_bar']['switch_bind'] = QPushButton()
        self.content['front_roll_bar']['switch_bind'].setFixedSize(100, 25)
        self.content['front_roll_bar']['switch_bind'].setText(lang['bind'])
        self.front_roll_bar.layout.addWidget(self.content['front_roll_bar']['switch_bind'], 6, 2)
        self.content['front_roll_bar']['switch_bind'].clicked.connect(lambda: self.bind_start("front_roll_bar","switch"))

        self.front_roll_bar.setLayout(self.front_roll_bar.layout)

        # --------Rear Roll Bar Tab--------#
        self.rear_roll_bar.layout = QGridLayout()

        self.content['rear_roll_bar']['lcd'] = QLCDNumber()
        self.content['rear_roll_bar']['lcd'].display(1)
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['lcd'], 1, 0)

        self.content['rear_roll_bar']['axis'] = QProgressBar()
        self.content['rear_roll_bar']['axis'].setTextVisible(False)
        self.content['rear_roll_bar']['axis'].setMinimum(0)
        self.content['rear_roll_bar']['axis'].setMaximum(100)
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['axis'], 1, 1)

        self.content['rear_roll_bar']['calibrate'] = QPushButton()
        self.content['rear_roll_bar']['calibrate'].setFixedSize(100, 25)
        self.content['rear_roll_bar']['calibrate'].setText(lang['calibrate'])
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['calibrate'], 1, 2)
        self.content['rear_roll_bar']['calibrate'].clicked.connect(lambda: self.calibrate_start("rear_roll_bar"))

        self.content['rear_roll_bar']['increment_label'] = QLabel()
        self.content['rear_roll_bar']['increment_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['rear_roll_bar']['increment_label'].setText(lang['increment'])
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['increment_label'], 2, 0)

        self.content['rear_roll_bar']['switch_label'] = QLabel()
        self.content['rear_roll_bar']['switch_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['rear_roll_bar']['switch_label'].setText(lang['switch_value'])
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['switch_label'], 2, 1)

        self.content['rear_roll_bar']['increment'] = QSpinBox()
        self.content['rear_roll_bar']['increment'].setFixedSize(70, 25)
        self.content['rear_roll_bar']['increment'].setRange(1, 5)
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['increment'], 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['rear_roll_bar']['increment'].valueChanged.connect(lambda: self.increment("rear_roll_bar"))

        self.content['rear_roll_bar']['switch'] = QSpinBox()
        self.content['rear_roll_bar']['switch'].setFixedSize(70, 25)
        self.content['rear_roll_bar']['switch'].setRange(1, 6)
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['switch'], 2, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['rear_roll_bar']['switch'].valueChanged.connect(lambda: self.switch("rear_roll_bar"))

        self.content['rear_roll_bar']['increment_mode_label'] = QLabel()
        self.content['rear_roll_bar']['increment_mode_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['rear_roll_bar']['increment_mode_label'].setText(lang['increment_mode'])
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['increment_mode_label'], 3, 0)

        self.content['rear_roll_bar']['switch_mode_label'] = QLabel()
        self.content['rear_roll_bar']['switch_mode_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['rear_roll_bar']['switch_mode_label'].setText(lang['switch_mode'])
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['switch_mode_label'], 3, 1)

        self.content['rear_roll_bar']['increment_mode'] = QComboBox()
        self.content['rear_roll_bar']['increment_mode'].setFixedSize(100, 25)
        self.content['rear_roll_bar']['increment_mode'].addItem(lang['continuous'])
        self.content['rear_roll_bar']['increment_mode'].addItem(lang['single'])
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['increment_mode'], 3, 1)
        self.content['rear_roll_bar']['increment_mode'].currentIndexChanged.connect(lambda: self.increment_mode("rear_roll_bar"))

        self.content['rear_roll_bar']['switch_mode'] = QComboBox()
        self.content['rear_roll_bar']['switch_mode'].setFixedSize(70, 25)
        self.content['rear_roll_bar']['switch_mode'].addItem(lang['hold'])
        self.content['rear_roll_bar']['switch_mode'].addItem(lang['toggle'])
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['switch_mode'], 3, 2)
        self.content['rear_roll_bar']['switch_mode'].currentIndexChanged.connect(lambda: self.switch_mode("rear_roll_bar"))

        self.content['rear_roll_bar']['up_label'] = QLabel()
        self.content['rear_roll_bar']['up_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['rear_roll_bar']['up_label'].setText(lang['up'])
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['up_label'], 4, 0)

        self.content['rear_roll_bar']['up_device'] = QLineEdit()
        self.content['rear_roll_bar']['up_device'].setFixedHeight(25)
        self.content['rear_roll_bar']['up_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['rear_roll_bar']['up_device'].setReadOnly(True)
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['up_device'], 4, 1)

        self.content['rear_roll_bar']['up_bind'] = QPushButton()
        self.content['rear_roll_bar']['up_bind'].setFixedSize(100, 25)
        self.content['rear_roll_bar']['up_bind'].setText(lang['bind'])
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['up_bind'], 4, 2)
        self.content['rear_roll_bar']['up_bind'].clicked.connect(lambda: self.bind_start("rear_roll_bar","up"))

        self.content['rear_roll_bar']['down_label'] = QLabel()
        self.content['rear_roll_bar']['down_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['rear_roll_bar']['down_label'].setText(lang['down'])
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['down_label'], 5, 0)

        self.content['rear_roll_bar']['down_device'] = QLineEdit()
        self.content['rear_roll_bar']['down_device'].setFixedHeight(25)
        self.content['rear_roll_bar']['down_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['rear_roll_bar']['down_device'].setReadOnly(True)
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['down_device'], 5, 1)

        self.content['rear_roll_bar']['down_bind'] = QPushButton()
        self.content['rear_roll_bar']['down_bind'].setFixedSize(100, 25)
        self.content['rear_roll_bar']['down_bind'].setText(lang['bind'])
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['down_bind'], 5, 2)
        self.content['rear_roll_bar']['down_bind'].clicked.connect(lambda: self.bind_start("rear_roll_bar","down"))

        self.content['rear_roll_bar']['switch_label'] = QLabel()
        self.content['rear_roll_bar']['switch_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['rear_roll_bar']['switch_label'].setText(lang['switch'])
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['switch_label'], 6, 0)

        self.content['rear_roll_bar']['switch_device'] = QLineEdit()
        self.content['rear_roll_bar']['switch_device'].setFixedHeight(25)
        self.content['rear_roll_bar']['switch_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['rear_roll_bar']['switch_device'].setReadOnly(True)
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['switch_device'], 6, 1)

        self.content['rear_roll_bar']['switch_bind'] = QPushButton()
        self.content['rear_roll_bar']['switch_bind'].setFixedSize(100, 25)
        self.content['rear_roll_bar']['switch_bind'].setText(lang['bind'])
        self.rear_roll_bar.layout.addWidget(self.content['rear_roll_bar']['switch_bind'], 6, 2)
        self.content['rear_roll_bar']['switch_bind'].clicked.connect(lambda: self.bind_start("rear_roll_bar","switch"))

        self.rear_roll_bar.setLayout(self.rear_roll_bar.layout)

        # --------Fuel Map Tab--------#
        self.fuel_map.layout = QGridLayout()

        self.content['fuel_map']['lcd'] = QLCDNumber()
        self.content['fuel_map']['lcd'].display(0)
        self.fuel_map.layout.addWidget(self.content['fuel_map']['lcd'], 0, 0)

        self.content['fuel_map']['axis'] = QProgressBar()
        self.content['fuel_map']['axis'].setTextVisible(False)
        self.content['fuel_map']['axis'].setMinimum(0)
        self.content['fuel_map']['axis'].setMaximum(100)
        self.fuel_map.layout.addWidget(self.content['fuel_map']['axis'], 0, 1)

        self.content['fuel_map']['calibrate'] = QPushButton()
        self.content['fuel_map']['calibrate'].setFixedSize(100, 25)
        self.content['fuel_map']['calibrate'].setText(lang['calibrate'])
        self.fuel_map.layout.addWidget(self.content['fuel_map']['calibrate'], 0, 2)
        self.content['fuel_map']['calibrate'].clicked.connect(lambda: self.calibrate_start("fuel_map"))

        self.content['fuel_map']['increment_label'] = QLabel()
        self.content['fuel_map']['increment_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['fuel_map']['increment_label'].setText(lang['increment'])
        self.fuel_map.layout.addWidget(self.content['fuel_map']['increment_label'], 1, 0)

        self.content['fuel_map']['switch_label'] = QLabel()
        self.content['fuel_map']['switch_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['fuel_map']['switch_label'].setText(lang['switch_value'])
        self.fuel_map.layout.addWidget(self.content['fuel_map']['switch_label'], 1, 1)

        self.content['fuel_map']['increment'] = QSpinBox()
        self.content['fuel_map']['increment'].setFixedSize(70, 25)
        self.content['fuel_map']['increment'].setRange(1, 7)
        self.fuel_map.layout.addWidget(self.content['fuel_map']['increment'], 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['fuel_map']['increment'].valueChanged.connect(lambda: self.increment("fuel_map"))

        self.content['fuel_map']['switch'] = QSpinBox()
        self.content['fuel_map']['switch'].setFixedSize(70, 25)
        self.content['fuel_map']['switch'].setRange(1, 8)
        self.fuel_map.layout.addWidget(self.content['fuel_map']['switch'], 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['fuel_map']['switch'].valueChanged.connect(lambda: self.switch("fuel_map"))

        self.content['fuel_map']['increment_mode_label'] = QLabel()
        self.content['fuel_map']['increment_mode_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['fuel_map']['increment_mode_label'].setText(lang['increment_mode'])
        self.fuel_map.layout.addWidget(self.content['fuel_map']['increment_mode_label'], 2, 0)

        self.content['fuel_map']['switch_mode_label'] = QLabel()
        self.content['fuel_map']['switch_mode_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['fuel_map']['switch_mode_label'].setText(lang['switch_mode'])
        self.fuel_map.layout.addWidget(self.content['fuel_map']['switch_mode_label'], 2, 1)

        self.content['fuel_map']['increment_mode'] = QComboBox()
        self.content['fuel_map']['increment_mode'].setFixedSize(100, 25)
        self.content['fuel_map']['increment_mode'].addItem(lang['continuous'])
        self.content['fuel_map']['increment_mode'].addItem(lang['single'])
        self.fuel_map.layout.addWidget(self.content['fuel_map']['increment_mode'], 2, 1)
        self.content['fuel_map']['increment_mode'].currentIndexChanged.connect(lambda: self.increment_mode("fuel_map"))

        self.content['fuel_map']['switch_mode'] = QComboBox()
        self.content['fuel_map']['switch_mode'].setFixedSize(70, 25)
        self.content['fuel_map']['switch_mode'].addItem(lang['hold'])
        self.content['fuel_map']['switch_mode'].addItem(lang['toggle'])
        self.fuel_map.layout.addWidget(self.content['fuel_map']['switch_mode'], 2, 2)
        self.content['fuel_map']['switch_mode'].currentIndexChanged.connect(lambda: self.switch_mode("fuel_map"))

        self.content['fuel_map']['up_label'] = QLabel()
        self.content['fuel_map']['up_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['fuel_map']['up_label'].setText(lang['up'])
        self.fuel_map.layout.addWidget(self.content['fuel_map']['up_label'], 3, 0)

        self.content['fuel_map']['up_device'] = QLineEdit()
        self.content['fuel_map']['up_device'].setFixedHeight(25)
        self.content['fuel_map']['up_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['fuel_map']['up_device'].setReadOnly(True)
        self.fuel_map.layout.addWidget(self.content['fuel_map']['up_device'], 3, 1)

        self.content['fuel_map']['up_bind'] = QPushButton()
        self.content['fuel_map']['up_bind'].setFixedSize(100, 25)
        self.content['fuel_map']['up_bind'].setText(lang['bind'])
        self.fuel_map.layout.addWidget(self.content['fuel_map']['up_bind'], 3, 2)
        self.content['fuel_map']['up_bind'].clicked.connect(lambda: self.bind_start("fuel_map","up"))

        self.content['fuel_map']['down_label'] = QLabel()
        self.content['fuel_map']['down_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['fuel_map']['down_label'].setText(lang['down'])
        self.fuel_map.layout.addWidget(self.content['fuel_map']['down_label'], 4, 0)

        self.content['fuel_map']['down_device'] = QLineEdit()
        self.content['fuel_map']['down_device'].setFixedHeight(25)
        self.content['fuel_map']['down_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['fuel_map']['down_device'].setReadOnly(True)
        self.fuel_map.layout.addWidget(self.content['fuel_map']['down_device'], 4, 1)

        self.content['fuel_map']['down_bind'] = QPushButton()
        self.content['fuel_map']['down_bind'].setFixedSize(100, 25)
        self.content['fuel_map']['down_bind'].setText(lang['bind'])
        self.fuel_map.layout.addWidget(self.content['fuel_map']['down_bind'], 4, 2)
        self.content['fuel_map']['down_bind'].clicked.connect(lambda: self.bind_start("fuel_map","down"))

        self.content['fuel_map']['switch_label'] = QLabel()
        self.content['fuel_map']['switch_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['fuel_map']['switch_label'].setText(lang['switch'])
        self.fuel_map.layout.addWidget(self.content['fuel_map']['switch_label'], 5, 0)

        self.content['fuel_map']['switch_device'] = QLineEdit()
        self.content['fuel_map']['switch_device'].setFixedHeight(25)
        self.content['fuel_map']['switch_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['fuel_map']['switch_device'].setReadOnly(True)
        self.fuel_map.layout.addWidget(self.content['fuel_map']['switch_device'], 5, 1)

        self.content['fuel_map']['switch_bind'] = QPushButton()
        self.content['fuel_map']['switch_bind'].setFixedSize(100, 25)
        self.content['fuel_map']['switch_bind'].setText(lang['bind'])
        self.fuel_map.layout.addWidget(self.content['fuel_map']['switch_bind'], 5, 2)
        self.content['fuel_map']['switch_bind'].clicked.connect(lambda: self.bind_start("fuel_map","switch"))

        self.fuel_map.setLayout(self.fuel_map.layout)

        # --------Bite Point Tab--------#
        self.bite_point.layout = QGridLayout()

        self.content['bite_point']['lcd'] = QLCDNumber()
        self.content['bite_point']['lcd'].display(0)
        self.content['bite_point']['lcd'].setSmallDecimalPoint(False)
        self.bite_point.layout.addWidget(self.content['bite_point']['lcd'], 0, 0)

        self.content['bite_point']['axis'] = QProgressBar()
        self.content['bite_point']['axis'].setTextVisible(False)
        self.content['bite_point']['axis'].setMinimum(0)
        self.content['bite_point']['axis'].setMaximum(100)
        self.bite_point.layout.addWidget(self.content['bite_point']['axis'], 0, 1)

        self.content['bite_point']['calibrate'] = QPushButton()
        self.content['bite_point']['calibrate'].setFixedSize(100, 25)
        self.content['bite_point']['calibrate'].setText(lang['calibrate'])
        self.bite_point.layout.addWidget(self.content['bite_point']['calibrate'], 0, 2)
        self.content['bite_point']['calibrate'].clicked.connect(lambda: self.calibrate_start("bite_point"))

        self.content['bite_point']['increment_label'] = QLabel()
        self.content['bite_point']['increment_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['bite_point']['increment_label'].setText(lang['increment'])
        self.bite_point.layout.addWidget(self.content['bite_point']['increment_label'], 1, 0)

        self.content['bite_point']['switch_label'] = QLabel()
        self.content['bite_point']['switch_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['bite_point']['switch_label'].setText(lang['switch_value'])
        self.bite_point.layout.addWidget(self.content['bite_point']['switch_label'], 1, 1)

        self.content['bite_point']['increment'] = QDoubleSpinBox()
        self.content['bite_point']['increment'].setFixedSize(70, 25)
        self.content['bite_point']['increment'].setRange(0.1, 5)
        self.content['bite_point']['increment'].setSingleStep(0.1)
        self.content['bite_point']['increment'].setDecimals(1)
        self.bite_point.layout.addWidget(self.content['bite_point']['increment'], 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['bite_point']['increment'].valueChanged.connect(lambda: self.increment("bite_point"))

        self.content['bite_point']['switch'] = QDoubleSpinBox()
        self.content['bite_point']['switch'].setFixedSize(70, 25)
        self.content['bite_point']['switch'].setRange(0.0, 100.0)
        self.content['bite_point']['switch'].setSingleStep(0.1)
        self.content['bite_point']['switch'].setDecimals(1)
        self.bite_point.layout.addWidget(self.content['bite_point']['switch'], 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['bite_point']['switch'].valueChanged.connect(lambda: self.switch("bite_point"))

        self.content['bite_point']['increment_mode_label'] = QLabel()
        self.content['bite_point']['increment_mode_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['bite_point']['increment_mode_label'].setText(lang['increment_mode'])
        self.bite_point.layout.addWidget(self.content['bite_point']['increment_mode_label'], 2, 0)

        self.content['bite_point']['switch_mode_label'] = QLabel()
        self.content['bite_point']['switch_mode_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['bite_point']['switch_mode_label'].setText(lang['switch_mode'])
        self.bite_point.layout.addWidget(self.content['bite_point']['switch_mode_label'], 2, 1)

        self.content['bite_point']['increment_mode'] = QComboBox()
        self.content['bite_point']['increment_mode'].setFixedSize(100, 25)
        self.content['bite_point']['increment_mode'].addItem(lang['continuous'])
        self.content['bite_point']['increment_mode'].addItem(lang['single'])
        self.bite_point.layout.addWidget(self.content['bite_point']['increment_mode'], 2, 1)
        self.content['bite_point']['increment_mode'].currentIndexChanged.connect(lambda: self.increment_mode("bite_point"))

        self.content['bite_point']['switch_mode'] = QComboBox()
        self.content['bite_point']['switch_mode'].setFixedSize(70, 25)
        self.content['bite_point']['switch_mode'].addItem(lang['hold'])
        self.content['bite_point']['switch_mode'].addItem(lang['toggle'])
        self.bite_point.layout.addWidget(self.content['bite_point']['switch_mode'], 2, 2)
        self.content['bite_point']['switch_mode'].currentIndexChanged.connect(lambda: self.switch_mode("bite_point"))

        self.content['bite_point']['pedal_label'] = QLabel()
        self.content['bite_point']['pedal_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['bite_point']['pedal_label'].setText(lang['pedal'])
        self.bite_point.layout.addWidget(self.content['bite_point']['pedal_label'], 3, 0)

        self.content['bite_point']['pedal_device'] = QLineEdit()
        self.content['bite_point']['pedal_device'].setFixedHeight(25)
        self.content['bite_point']['pedal_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['bite_point']['pedal_device'].setReadOnly(True)
        self.bite_point.layout.addWidget(self.content['bite_point']['pedal_device'], 3, 1)

        self.content['bite_point']['pedal_bind'] = QPushButton()
        self.content['bite_point']['pedal_bind'].setFixedSize(100, 25)
        self.content['bite_point']['pedal_bind'].setText(lang['bind'])
        self.bite_point.layout.addWidget(self.content['bite_point']['pedal_bind'], 3, 2)
        self.content['bite_point']['pedal_bind'].clicked.connect(lambda: self.bind_start("bite_point","pedal"))

        self.content['bite_point']['up_label'] = QLabel()
        self.content['bite_point']['up_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['bite_point']['up_label'].setText(lang['up'])
        self.bite_point.layout.addWidget(self.content['bite_point']['up_label'], 4, 0)

        self.content['bite_point']['up_device'] = QLineEdit()
        self.content['bite_point']['up_device'].setFixedHeight(25)
        self.content['bite_point']['up_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['bite_point']['up_device'].setReadOnly(True)
        self.bite_point.layout.addWidget(self.content['bite_point']['up_device'], 4, 1)

        self.content['bite_point']['up_bind'] = QPushButton()
        self.content['bite_point']['up_bind'].setFixedSize(100, 25)
        self.content['bite_point']['up_bind'].setText(lang['bind'])
        self.bite_point.layout.addWidget(self.content['bite_point']['up_bind'], 4, 2)
        self.content['bite_point']['up_bind'].clicked.connect(lambda: self.bind_start("bite_point","up"))

        self.content['bite_point']['down_label'] = QLabel()
        self.content['bite_point']['down_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['bite_point']['down_label'].setText(lang['down'])
        self.bite_point.layout.addWidget(self.content['bite_point']['down_label'], 5, 0)

        self.content['bite_point']['down_device'] = QLineEdit()
        self.content['bite_point']['down_device'].setFixedHeight(25)
        self.content['bite_point']['down_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['bite_point']['down_device'].setReadOnly(True)
        self.bite_point.layout.addWidget(self.content['bite_point']['down_device'], 5, 1)

        self.content['bite_point']['down_bind'] = QPushButton()
        self.content['bite_point']['down_bind'].setFixedSize(100, 25)
        self.content['bite_point']['down_bind'].setText(lang['bind'])
        self.bite_point.layout.addWidget(self.content['bite_point']['down_bind'], 5, 2)
        self.content['bite_point']['down_bind'].clicked.connect(lambda: self.bind_start("bite_point","down"))

        self.content['bite_point']['switch_label'] = QLabel()
        self.content['bite_point']['switch_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['bite_point']['switch_label'].setText(lang['switch'])
        self.bite_point.layout.addWidget(self.content['bite_point']['switch_label'], 6, 0)

        self.content['bite_point']['switch_device'] = QLineEdit()
        self.content['bite_point']['switch_device'].setFixedHeight(25)
        self.content['bite_point']['switch_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['bite_point']['switch_device'].setReadOnly(True)
        self.bite_point.layout.addWidget(self.content['bite_point']['switch_device'], 6, 1)

        self.content['bite_point']['switch_bind'] = QPushButton()
        self.content['bite_point']['switch_bind'].setFixedSize(100, 25)
        self.content['bite_point']['switch_bind'].setText(lang['bind'])
        self.bite_point.layout.addWidget(self.content['bite_point']['switch_bind'], 6, 2)
        self.content['bite_point']['switch_bind'].clicked.connect(lambda: self.bind_start("bite_point","switch"))

        self.bite_point.setLayout(self.bite_point.layout)

        # --------Engine Warming Tab--------#
        self.engine_warming.layout = QGridLayout()
        
        self.content['engine_warming']['lcd'] = QLCDNumber()
        self.content['engine_warming']['lcd'].display(0)
        self.content['engine_warming']['lcd'].setSmallDecimalPoint(False)
        self.engine_warming.layout.addWidget(self.content['engine_warming']['lcd'], 0, 0)

        self.content['engine_warming']['axis'] = QProgressBar()
        self.content['engine_warming']['axis'].setTextVisible(False)
        self.content['engine_warming']['axis'].setMinimum(0)
        self.content['engine_warming']['axis'].setMaximum(100)
        self.engine_warming.layout.addWidget(self.content['engine_warming']['axis'], 0, 1)

        self.content['engine_warming']['calibrate'] = QPushButton()
        self.content['engine_warming']['calibrate'].setFixedSize(100, 25)
        self.content['engine_warming']['calibrate'].setText(lang['calibrate'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['calibrate'], 0, 2)
        self.content['engine_warming']['calibrate'].clicked.connect(lambda: self.calibrate_start("engine_warming"))

        self.content['engine_warming']['increment_label'] = QLabel()
        self.content['engine_warming']['increment_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['engine_warming']['increment_label'].setText(lang['increment'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['increment_label'], 1, 0)

        self.content['engine_warming']['switch_label'] = QLabel()
        self.content['engine_warming']['switch_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['engine_warming']['switch_label'].setText(lang['switch_value'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['switch_label'], 1, 1)

        self.content['engine_warming']['increment'] = QDoubleSpinBox()
        self.content['engine_warming']['increment'].setFixedSize(70, 25)
        self.content['engine_warming']['increment'].setRange(0.1, 5)
        self.content['engine_warming']['increment'].setSingleStep(0.1)
        self.content['engine_warming']['increment'].setDecimals(1)
        self.engine_warming.layout.addWidget(self.content['engine_warming']['increment'], 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['engine_warming']['increment'].valueChanged.connect(lambda: self.increment("engine_warming"))

        self.content['engine_warming']['switch'] = QDoubleSpinBox()
        self.content['engine_warming']['switch'].setFixedSize(70, 25)
        self.content['engine_warming']['switch'].setRange(0.0, 100.0)
        self.content['engine_warming']['switch'].setSingleStep(0.1)
        self.content['engine_warming']['switch'].setDecimals(1)
        self.engine_warming.layout.addWidget(self.content['engine_warming']['switch'], 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['engine_warming']['switch'].valueChanged.connect(lambda: self.switch("engine_warming"))

        self.content['engine_warming']['increment_mode_label'] = QLabel()
        self.content['engine_warming']['increment_mode_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['engine_warming']['increment_mode_label'].setText(lang['increment_mode'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['increment_mode_label'], 2, 0)

        self.content['engine_warming']['switch_mode_label'] = QLabel()
        self.content['engine_warming']['switch_mode_label'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['engine_warming']['switch_mode_label'].setText(lang['switch_mode'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['switch_mode_label'], 2, 1)

        self.content['engine_warming']['increment_mode'] = QComboBox()
        self.content['engine_warming']['increment_mode'].setFixedSize(100, 25)
        self.content['engine_warming']['increment_mode'].addItem(lang['continuous'])
        self.content['engine_warming']['increment_mode'].addItem(lang['single'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['increment_mode'], 2, 1)
        self.content['engine_warming']['increment_mode'].currentIndexChanged.connect(lambda: self.increment_mode("engine_warming"))

        self.content['engine_warming']['switch_mode'] = QComboBox()
        self.content['engine_warming']['switch_mode'].setFixedSize(70, 25)
        self.content['engine_warming']['switch_mode'].addItem(lang['hold'])
        self.content['engine_warming']['switch_mode'].addItem(lang['toggle'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['switch_mode'], 2, 2)
        self.content['engine_warming']['switch_mode'].currentIndexChanged.connect(lambda: self.switch_mode("engine_warming"))

        self.content['engine_warming']['pedal_label'] = QLabel()
        self.content['engine_warming']['pedal_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['engine_warming']['pedal_label'].setText(lang['pedal'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['pedal_label'], 3, 0)

        self.content['engine_warming']['pedal_device'] = QLineEdit()
        self.content['engine_warming']['pedal_device'].setFixedHeight(25)
        self.content['engine_warming']['pedal_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['engine_warming']['pedal_device'].setReadOnly(True)
        self.engine_warming.layout.addWidget(self.content['engine_warming']['pedal_device'], 3, 1)

        self.content['engine_warming']['pedal_bind'] = QPushButton()
        self.content['engine_warming']['pedal_bind'].setFixedSize(100, 25)
        self.content['engine_warming']['pedal_bind'].setText(lang['bind'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['pedal_bind'], 3, 2)
        self.content['engine_warming']['pedal_bind'].clicked.connect(lambda: self.bind_start("engine_warming","pedal"))

        self.content['engine_warming']['up_label'] = QLabel()
        self.content['engine_warming']['up_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['engine_warming']['up_label'].setText(lang['up'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['up_label'], 4, 0)

        self.content['engine_warming']['up_device'] = QLineEdit()
        self.content['engine_warming']['up_device'].setFixedHeight(25)
        self.content['engine_warming']['up_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['engine_warming']['up_device'].setReadOnly(True)
        self.engine_warming.layout.addWidget(self.content['engine_warming']['up_device'], 4, 1)

        self.content['engine_warming']['up_bind'] = QPushButton()
        self.content['engine_warming']['up_bind'].setFixedSize(100, 25)
        self.content['engine_warming']['up_bind'].setText(lang['bind'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['up_bind'], 4, 2)
        self.content['engine_warming']['up_bind'].clicked.connect(lambda: self.bind_start("engine_warming","up"))

        self.content['engine_warming']['down_label'] = QLabel()
        self.content['engine_warming']['down_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['engine_warming']['down_label'].setText(lang['down'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['down_label'], 5, 0)

        self.content['engine_warming']['down_device'] = QLineEdit()
        self.content['engine_warming']['down_device'].setFixedHeight(25)
        self.content['engine_warming']['down_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['engine_warming']['down_device'].setReadOnly(True)
        self.engine_warming.layout.addWidget(self.content['engine_warming']['down_device'], 5, 1)

        self.content['engine_warming']['down_bind'] = QPushButton()
        self.content['engine_warming']['down_bind'].setFixedSize(100, 25)
        self.content['engine_warming']['down_bind'].setText(lang['bind'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['down_bind'], 5, 2)
        self.content['engine_warming']['down_bind'].clicked.connect(lambda: self.bind_start("engine_warming","down"))

        self.content['engine_warming']['switch_label'] = QLabel()
        self.content['engine_warming']['switch_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['engine_warming']['switch_label'].setText(lang['switch'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['switch_label'], 6, 0)

        self.content['engine_warming']['switch_device'] = QLineEdit()
        self.content['engine_warming']['switch_device'].setFixedHeight(25)
        self.content['engine_warming']['switch_device'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content['engine_warming']['switch_device'].setReadOnly(True)
        self.engine_warming.layout.addWidget(self.content['engine_warming']['switch_device'], 6, 1)

        self.content['engine_warming']['switch_bind'] = QPushButton()
        self.content['engine_warming']['switch_bind'].setFixedSize(100, 25)
        self.content['engine_warming']['switch_bind'].setText(lang['bind'])
        self.engine_warming.layout.addWidget(self.content['engine_warming']['switch_bind'], 6, 2)
        self.content['engine_warming']['switch_bind'].clicked.connect(lambda: self.bind_start("engine_warming","switch"))

        self.engine_warming.setLayout(self.engine_warming.layout)

        # --------Settings Tab--------#
        self.settings.layout = QGridLayout()

        self.content['settings']['high_threshold_label'] = QLabel()
        self.content['settings']['high_threshold_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['settings']['high_threshold_label'].setText(lang['high_threshold'])
        self.settings.layout.addWidget(self.content['settings']['high_threshold_label'], 0, 0)

        self.content['settings']['high_threshold'] = QSpinBox()
        self.content['settings']['high_threshold'].setFixedSize(60, 20)
        self.settings.layout.addWidget(self.content['settings']['high_threshold'], 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['settings']['high_threshold'].setRange(min(int(var.settings['low_threshold']*100)+1,51), 99)
        self.content['settings']['high_threshold'].setValue(int(var.settings['high_threshold'] * 100))
        self.content['settings']['high_threshold'].valueChanged.connect(lambda: self.settings_set('high_threshold'))

        self.content['settings']['low_threshold_label'] = QLabel()
        self.content['settings']['low_threshold_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['settings']['low_threshold_label'].setText(lang['low_threshold'])
        self.settings.layout.addWidget(self.content['settings']['low_threshold_label'], 1, 0)

        self.content['settings']['low_threshold'] = QSpinBox()
        self.content['settings']['low_threshold'].setFixedSize(60, 20)
        self.settings.layout.addWidget(self.content['settings']['low_threshold'], 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['settings']['low_threshold'].setRange(1, max(int(var.settings['high_threshold']*100)-1,49))
        self.content['settings']['low_threshold'].setValue(int(var.settings['low_threshold'] * 100))
        self.content['settings']['low_threshold'].valueChanged.connect(lambda: self.settings_set('low_threshold'))

        self.content['settings']['axis_samples'] = QLabel()
        self.content['settings']['axis_samples'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['settings']['axis_samples'].setText(lang['axis_samples'])
        self.settings.layout.addWidget(self.content['settings']['axis_samples'], 2, 0)

        self.content['settings']['axis_samples'] = QSpinBox()
        self.content['settings']['axis_samples'].setFixedSize(60, 20)
        self.content['settings']['axis_samples'].setRange(2, 10)
        self.settings.layout.addWidget(self.content['settings']['axis_samples'], 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['settings']['axis_samples'].valueChanged.connect(lambda: self.settings_set('axis_samples'))

        self.content['settings']['scale_label'] = QLabel()
        self.content['settings']['scale_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['settings']['scale_label'].setText(lang['scale'])
        self.settings.layout.addWidget(self.content['settings']['scale_label'], 3, 0)

        self.content['settings']['scale'] = QComboBox()
        self.content['settings']['scale'].setFixedSize(70, 22)
        self.content['settings']['scale'].addItem("0.50" + "x")
        self.content['settings']['scale'].addItem("0.75" + "x")
        self.content['settings']['scale'].addItem("1.00" + "x")
        self.content['settings']['scale'].addItem("1.25" + "x")
        self.content['settings']['scale'].addItem("1.50" + "x")
        self.settings.layout.addWidget(self.content['settings']['scale'], 3, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['settings']['scale'].currentTextChanged.connect(self.scale)

        self.content['settings']['timer_first'] = QLabel()
        self.content['settings']['timer_first'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['settings']['timer_first'].setText(lang['timer_first'])
        self.settings.layout.addWidget(self.content['settings']['timer_first'], 4, 0)

        self.content['settings']['timer_first'] = QSpinBox()
        self.content['settings']['timer_first'].setFixedSize(70, 20)
        self.content['settings']['timer_first'].setRange(1, 1000)
        self.settings.layout.addWidget(self.content['settings']['timer_first'], 4, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['settings']['timer_first'].valueChanged.connect(lambda: self.settings_set('timer_first'))

        self.content['settings']['timer_loop'] = QLabel()
        self.content['settings']['timer_loop'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['settings']['timer_loop'].setText(lang['timer_loop'])
        self.settings.layout.addWidget(self.content['settings']['timer_loop'], 5, 0)

        self.content['settings']['timer_loop'] = QSpinBox()
        self.content['settings']['timer_loop'].setFixedSize(70, 20)
        self.content['settings']['timer_loop'].setRange(1, 1000)
        self.settings.layout.addWidget(self.content['settings']['timer_loop'], 5, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content['settings']['timer_loop'].valueChanged.connect(lambda: self.settings_set('timer_loop'))

        self.content['settings']['settings_filename_label'] = QLabel()
        self.content['settings']['settings_filename_label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['settings']['settings_filename_label'].setText(lang['settings_filename'])
        self.settings.layout.addWidget(self.content['settings']['settings_filename_label'], 6, 0)

        self.content['settings']['busy'] = False
        self.content['settings']['settings_filename'] = QComboBox()
        self.content['settings']['settings_filename'].setFixedSize(200, 25)
        self.settings.layout.addWidget(self.content['settings']['settings_filename'], 6, 1)
        if var.settings_active:
            self.content['settings']['settings_filename'].setCurrentText(var.settings_active)
            self.content['settings']['settings_filename'].addItem(var.settings_active)
        else:
            self.content['settings']['settings_filename'].setCurrentText('None')
            self.content['settings']['settings_filename'].addItem("settings.ini")
        self.content['settings']['settings_filename'].activated.connect(lambda: self.refresh_settings_list())
        self.content['settings']['settings_filename'].currentTextChanged.connect(lambda: self.apply_settings(self.content['settings']['settings_filename'].currentText()))

        self.settings.setLayout(self.settings.layout)

        # --------Display Tab--------#
        self.axes_display.layout = QGridLayout()


        self.content['axes_display']['car_id']['label'] = QLabel()
        self.content['axes_display']['car_id']['label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['axes_display']['car_id']['label'].setText(lang['car_id'])
        self.axes_display.layout.addWidget(self.content['axes_display']['car_id']['label'], 0, 0)

        self.content['axes_display']['car_id']['car_id'] = QLabel()
        self.content['axes_display']['car_id']['car_id'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['axes_display']['car_id']['car_id'].setText("None")
        self.axes_display.layout.addWidget(self.content['axes_display']['car_id']['car_id'], 0, 1)

        self.content['axes_display']['car_id']['limits'] = QLabel()
        self.content['axes_display']['car_id']['limits'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content['axes_display']['car_id']['limits'].setText("Placeholder")
        self.axes_display.layout.addWidget(self.content['axes_display']['car_id']['limits'], 0, 2)

        self.content['axes_display']['weight_jacker']['label'] = QLabel()
        self.content['axes_display']['weight_jacker']['label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['axes_display']['weight_jacker']['label'].setText(lang['weight_jacker'])
        self.axes_display.layout.addWidget(self.content['axes_display']['weight_jacker']['label'], 1, 0)

        self.content['axes_display']['weight_jacker']['lcd'] = QLCDNumber()
        self.content['axes_display']['weight_jacker']['lcd'].display(0)
        self.axes_display.layout.addWidget(self.content['axes_display']['weight_jacker']['lcd'], 1, 1)

        self.content['axes_display']['weight_jacker']['axis'] = QProgressBar()
        self.content['axes_display']['weight_jacker']['axis'].setTextVisible(False)
        self.content['axes_display']['weight_jacker']['axis'].setMinimum(0)
        self.content['axes_display']['weight_jacker']['axis'].setMaximum(100)
        self.axes_display.layout.addWidget(self.content['axes_display']['weight_jacker']['axis'], 1, 2)


        self.content['axes_display']['front_roll_bar']['label'] = QLabel()
        self.content['axes_display']['front_roll_bar']['label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['axes_display']['front_roll_bar']['label'].setText(lang['front_roll_bar'])
        self.axes_display.layout.addWidget(self.content['axes_display']['front_roll_bar']['label'], 2, 0)

        self.content['axes_display']['front_roll_bar']['lcd'] = QLCDNumber()
        self.content['axes_display']['front_roll_bar']['lcd'].display(0)
        self.axes_display.layout.addWidget(self.content['axes_display']['front_roll_bar']['lcd'], 2, 1)

        self.content['axes_display']['front_roll_bar']['axis'] = QProgressBar()
        self.content['axes_display']['front_roll_bar']['axis'].setTextVisible(False)
        self.content['axes_display']['front_roll_bar']['axis'].setMinimum(0)
        self.content['axes_display']['front_roll_bar']['axis'].setMaximum(100)
        self.axes_display.layout.addWidget(self.content['axes_display']['front_roll_bar']['axis'], 2, 2)


        self.content['axes_display']['rear_roll_bar']['label'] = QLabel()
        self.content['axes_display']['rear_roll_bar']['label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['axes_display']['rear_roll_bar']['label'].setText(lang['rear_roll_bar'])
        self.axes_display.layout.addWidget(self.content['axes_display']['rear_roll_bar']['label'], 3, 0)

        self.content['axes_display']['rear_roll_bar']['lcd'] = QLCDNumber()
        self.content['axes_display']['rear_roll_bar']['lcd'].display(0)
        self.axes_display.layout.addWidget(self.content['axes_display']['rear_roll_bar']['lcd'], 3, 1)

        self.content['axes_display']['rear_roll_bar']['axis'] = QProgressBar()
        self.content['axes_display']['rear_roll_bar']['axis'].setTextVisible(False)
        self.content['axes_display']['rear_roll_bar']['axis'].setMinimum(0)
        self.content['axes_display']['rear_roll_bar']['axis'].setMaximum(100)
        self.axes_display.layout.addWidget(self.content['axes_display']['rear_roll_bar']['axis'], 3, 2)


        self.content['axes_display']['fuel_map']['label'] = QLabel()
        self.content['axes_display']['fuel_map']['label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['axes_display']['fuel_map']['label'].setText(lang['fuel_map'])
        self.axes_display.layout.addWidget(self.content['axes_display']['fuel_map']['label'], 4, 0)

        self.content['axes_display']['fuel_map']['lcd'] = QLCDNumber()
        self.content['axes_display']['fuel_map']['lcd'].display(0)
        self.axes_display.layout.addWidget(self.content['axes_display']['fuel_map']['lcd'], 4, 1)

        self.content['axes_display']['fuel_map']['axis'] = QProgressBar()
        self.content['axes_display']['fuel_map']['axis'].setTextVisible(False)
        self.content['axes_display']['fuel_map']['axis'].setMinimum(0)
        self.content['axes_display']['fuel_map']['axis'].setMaximum(100)
        self.axes_display.layout.addWidget(self.content['axes_display']['fuel_map']['axis'], 4, 2)


        self.content['axes_display']['bite_point']['label'] = QLabel()
        self.content['axes_display']['bite_point']['label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['axes_display']['bite_point']['label'].setText(lang['bite_point'])
        self.axes_display.layout.addWidget(self.content['axes_display']['bite_point']['label'], 5, 0)

        self.content['axes_display']['bite_point']['lcd'] = QLCDNumber()
        self.content['axes_display']['bite_point']['lcd'].display(0)
        self.axes_display.layout.addWidget(self.content['axes_display']['bite_point']['lcd'], 5, 1)

        self.content['axes_display']['bite_point']['axis'] = QProgressBar()
        self.content['axes_display']['bite_point']['axis'].setTextVisible(False)
        self.content['axes_display']['bite_point']['axis'].setMinimum(0)
        self.content['axes_display']['bite_point']['axis'].setMaximum(100)
        self.axes_display.layout.addWidget(self.content['axes_display']['bite_point']['axis'], 5, 2)


        self.content['axes_display']['engine_warming']['label'] = QLabel()
        self.content['axes_display']['engine_warming']['label'].setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content['axes_display']['engine_warming']['label'].setText(lang['engine_warming'])
        self.axes_display.layout.addWidget(self.content['axes_display']['engine_warming']['label'], 6, 0)

        self.content['axes_display']['engine_warming']['lcd'] = QLCDNumber()
        self.content['axes_display']['engine_warming']['lcd'].display(0)
        self.axes_display.layout.addWidget(self.content['axes_display']['engine_warming']['lcd'], 6, 1)

        self.content['axes_display']['engine_warming']['axis'] = QProgressBar()
        self.content['axes_display']['engine_warming']['axis'].setTextVisible(False)
        self.content['axes_display']['engine_warming']['axis'].setMinimum(0)
        self.content['axes_display']['engine_warming']['axis'].setMaximum(100)
        self.axes_display.layout.addWidget(self.content['axes_display']['engine_warming']['axis'], 6, 2)


        self.axes_display.setLayout(self.axes_display.layout)



        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.setCentralWidget(self.tabs)


        self.apply_settings('settings.ini')
        self.refresh_settings_list()

        self.index = {
            "weight_jacker": {
                "up": {
                    "bind": self.content['weight_jacker']['up_bind'],
                    "device": self.content['weight_jacker']['up_device'],
                    "label": self.content['weight_jacker']['up_label'],
                },
                "down": {
                    "bind": self.content['weight_jacker']['down_bind'],
                    "device": self.content['weight_jacker']['down_device'],
                    "label": self.content['weight_jacker']['down_label'],
                },
                "switch": {
                    "bind": self.content['weight_jacker']['switch_bind'],
                    "device": self.content['weight_jacker']['switch_device'],
                    "label": self.content['weight_jacker']['switch_label'],
                }
            },
            "front_roll_bar": {
                "up": {
                    "bind": self.content['front_roll_bar']['up_bind'],
                    "device": self.content['front_roll_bar']['up_device'],
                    "label": self.content['front_roll_bar']['up_label'],
                },
                "down": {
                    "bind": self.content['front_roll_bar']['down_bind'],
                    "device": self.content['front_roll_bar']['down_device'],
                    "label": self.content['front_roll_bar']['down_label'],
                },
                "switch": {
                    "bind": self.content['front_roll_bar']['switch_bind'],
                    "device": self.content['front_roll_bar']['switch_device'],
                    "label": self.content['front_roll_bar']['switch_label'],
                }
            },
            "rear_roll_bar": {
                "up": {
                    "bind": self.content['rear_roll_bar']['up_bind'],
                    "device": self.content['rear_roll_bar']['up_device'],
                    "label": self.content['rear_roll_bar']['up_label'],
                },
                "down": {
                    "bind": self.content['rear_roll_bar']['down_bind'],
                    "device": self.content['rear_roll_bar']['down_device'],
                    "label": self.content['rear_roll_bar']['down_label'],
                },
                "switch": {
                    "bind": self.content['rear_roll_bar']['switch_bind'],
                    "device": self.content['rear_roll_bar']['switch_device'],
                    "label": self.content['rear_roll_bar']['switch_label'],
                }
            },
            "fuel_map": {
                "up": {
                    "bind": self.content['fuel_map']['up_bind'],
                    "device": self.content['fuel_map']['up_device'],
                    "label": self.content['fuel_map']['up_label'],
                },
                "down": {
                    "bind": self.content['fuel_map']['down_bind'],
                    "device": self.content['fuel_map']['down_device'],
                    "label": self.content['fuel_map']['down_label'],
                },
                "switch": {
                    "bind": self.content['fuel_map']['switch_bind'],
                    "device": self.content['fuel_map']['switch_device'],
                    "label": self.content['fuel_map']['switch_label'],
                }
            },
            "bite_point": {
                "pedal": {
                    "bind": self.content['bite_point']['pedal_bind'],
                    "device": self.content['bite_point']['pedal_device'],
                    "label": self.content['bite_point']['pedal_label'],
                },
                "up": {
                    "bind": self.content['bite_point']['up_bind'],
                    "device": self.content['bite_point']['up_device'],
                    "label": self.content['bite_point']['up_label'],
                },
                "down": {
                    "bind": self.content['bite_point']['down_bind'],
                    "device": self.content['bite_point']['down_device'],
                    "label": self.content['bite_point']['down_label'],
                },
                "switch": {
                    "bind": self.content['bite_point']['switch_bind'],
                    "device": self.content['bite_point']['switch_device'],
                    "label": self.content['bite_point']['switch_label'],
                }
            },
            "engine_warming": {
                "pedal": {
                    "bind": self.content['engine_warming']['pedal_bind'],
                    "device": self.content['engine_warming']['pedal_device'],
                    "label": self.content['engine_warming']['pedal_label'],
                },
                "up": {
                    "bind": self.content['engine_warming']['up_bind'],
                    "device": self.content['engine_warming']['up_device'],
                    "label": self.content['engine_warming']['up_label'],
                },
                "down": {
                    "bind": self.content['engine_warming']['down_bind'],
                    "device": self.content['engine_warming']['down_device'],
                    "label": self.content['engine_warming']['down_label'],
                },
                "switch": {
                    "bind": self.content['engine_warming']['switch_bind'],
                    "device": self.content['engine_warming']['switch_device'],
                    "label": self.content['engine_warming']['switch_label'],
                }
            },
            "car_id": self.content['axes_display']['car_id']['car_id']
        }

        self.ir = irsdk.IRSDK()
        self.ir.startup()
        self.content['axes_display']['car_id']['car_id'] = "None"
        self.update_limits()

        ui['timer'].timeout.connect(self.updater)
        ui['timer'].start(int((var.settings['frequency'] * 1000) / 10))

    def updater(self):
        for function in var.status:
            if function in self.content:
                value = var.status[function]['secondary']
                if function == "weight_jacker":
                    # var.status[function]['secondary'] = (value * step[function]) + 0.5
                    value = int(round((value - 0.5)/step[function]))
                elif function == "bite_point" or function == "engine_warming":
                    # var.status[function]['secondary'] = value/100
                    value = float(value*100)
                #elif function == "settings":
                    #self.refresh_settings_list()
                else:
                    # var.status[function]['secondary'] = (value * step[function]) - step[function]
                    value = int(round((value / step[function]) + 1))

                self.content[function]['switch'].setValue(value)

        self.display()

        if not self.ir.is_initialized:
            self.ir.startup()
        if self.ir.is_initialized and self.ir.is_connected:
            length = len(self.ir['DriverInfo']['Drivers'])
            index = length-1
            check = True
            while index >= 0 and check:
                if self.ir['DriverInfo']['Drivers'][index]['CarID'] == self.ir['PlayerCarIdx']:
                    check = False
                else:
                    index -= 1
            if self.content['axes_display']['car_id']['car_id'] != int(self.ir['DriverInfo']['Drivers'][index]['CarID']):
                self.content['axes_display']['car_id']['car_id'] = int(self.ir['DriverInfo']['Drivers'][index]['CarID'])
                self.update_limits()
        elif self.ir.is_initialized and not self.ir.is_connected and self.content['axes_display']['car_id']['car_id'] != "None":
            self.ir.shutdown()
            self.content['axes_display']['car_id']['car_id'] = "None"
            self.update_limits()

    def display(self):
        for func in vjoy.axis_values:
            if func in self.content: #only because not every tab has been developed yet...
                pct = vjoy.axis_values[func]
                #print("display check1: ", func, pct)
                self.content[func]['axis'].setValue(int(pct * 100))
                self.content[func]['axis'].update()
                self.content['axes_display'][func]['axis'].setValue(int(pct * 100))
                self.content['axes_display'][func]['axis'].update()

                if func == 'bite_point' or func == "engine_warming":
                    if (pct*100)%1 == 0:
                        self.content[func]['lcd'].display(str(round(pct*100)) + ".0") # bad hack to get the lcd to always display one decimal place
                        self.content['axes_display'][func]['lcd'].display(str(round(pct*100)) + ".0")
                    else:
                        self.content[func]['lcd'].display(round(pct*100, 1))
                        self.content['axes_display'][func]['lcd'].display(round(pct*100, 1))
                else:
                    value = pct * (self.content[func]['switch'].maximum() - self.content[func]['switch'].minimum()) + self.content[func]['switch'].minimum()
                    self.content[func]['lcd'].display(round(value))
                    self.content['axes_display'][func]['lcd'].display(round(value))
                self.content[func]['lcd'].update()
                self.content['axes_display'][func]['lcd'].update()
        #self.refresh_settings_list()

    @pyqtSlot()
    def calibrate(self):
        if self.axis in self.content:
            self.content[self.axis]['calibrate'].setText(lang['calibrating'])
        else:
            print("Warning: calibrate()")

        vjoy.calibrate(self.axis)
        while self.is_running == True:
            sleep(0.1)
        self.content[self.axis]['calibrate'].setText(lang['calibrate'])
        vjoy.set(self.axis,self.pct)
        var.status['calibration'] = False

    @pyqtSlot()
    def calibrate_start(self, func):
        self.axis = func
        if not self.is_running:
            self.is_running = True
            var.status['calibration'] = True
            sleep(0.1) #wait for loops to stop
            if not var.status[func]['switched']:
                self.pct = var.status[func]['primary']
            elif var.status[func]['switched']:
                self.pct = var.status[func]['secondary']
            ui['thread_pool'].start(self.calibrate)
        else:
            self.is_running = False

    @pyqtSlot()
    def increment(self, func):
        var.settings[func]['increment'] = self.content[func]['increment'].value()
        fn.write_config()

    @pyqtSlot()
    def switch(self, func):
        value = self.content[func]['switch'].value()
        var.settings[func]['switch_value'] = value
        if func == "weight_jacker":
            var.status[func]['secondary'] = (value * step[func]) + 0.5
        elif func == "bite_point" or func == "engine_warming":
            var.status[func]['secondary'] = value/100
        else:
            var.status[func]['secondary'] = (value * step[func]) - step[func]
        if var.status[func]['switched'] == True:
            vjoy.set(func, var.status[func]['secondary'])
        fn.write_config()

    @pyqtSlot()
    def increment_mode(self, func):
        if self.content[func]['increment_mode'].currentText() == "Continuous":
            var.settings[func]['continuous'] = True
        elif self.content[func]['increment_mode'].currentText() == "Single":
            var.settings[func]['continuous'] = False
        fn.write_config()

    @pyqtSlot()
    def switch_mode(self, func):
        if self.content[func]['switch_mode'].currentText() == "Toggle":
            var.settings[func]['toggle'] = True
        elif self.content[func]['switch_mode'].currentText() == "Hold":
            var.status[func]['switched'] = False
            vjoy.set(func, var.status[func]['primary'])
            var.settings[func]['toggle'] = False
        fn.write_config()

    @pyqtSlot()
    def settings_set(self, func):
        value = self.content['settings'][func].value()
        if func == 'high_threshold':
            if value/100 > var.settings['low_threshold']:
                self.content['settings']['low_threshold'].setRange(1, value-1)
                fn.reset_bind_thresh(func, value/100)
                var.settings[func] = value/100
                fn.write_config()
        elif func == 'low_threshold':
            if value/100 < var.settings['high_threshold']:
                self.content['settings']['high_threshold'].setRange(value+1, 99)
                fn.reset_bind_thresh(func, value/100)
                var.settings[func] = value/100
                fn.write_config()
        else:
            var.settings[func] = value
            fn.write_config()

    @pyqtSlot()
    def scale(self):
        scale = self.content['settings']['scale'].currentText()
        scale = scale.replace("x", "")
        var.settings['scale'] = scale
        fn.write_config()

    @pyqtSlot()
    def bind(self):
        self.is_running = True
        var.bindings['status']['active'] = True
        function = var.bindings['status']['function']
        control = var.bindings['status']['control']
        history.clear()

        self.index[function][control]['bind'].setText(lang['binding'])

        var.event = {
            "guid": 0,
            "type": "",
            "num": 0,
            "value": None,
        }
        var.bindings[function][control] = None
        while not var.bindings[function][control]:
            if self.is_running == False:
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
                    if (function == 'bite_point' or function == 'engine_warming') and control == 'pedal':
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

        self.index[function][control]['bind'].setText(lang['bind'])

        self.index[function][control]['device'].setText(dev.format(function, control))

        var.bindings['status'] = {
            "active": False,
            "function": None,
            "control": None,
        }
        fn.write_config()
        self.is_running = False

    @pyqtSlot()
    def bind_start(self, func, ctrl):
        var.bindings['status'] = {
            "function": func,
            "control": ctrl,
        }
        if not self.is_running:
            ui['thread_pool'].start(self.bind)
        else:
            self.is_running = False

    @pyqtSlot()
    def refresh_settings_list(self):
        self.content['settings']['busy'] = True
        file = self.content['settings']['settings_filename'].currentText()
        self.content['settings']['settings_filename'].clear()
        for name in fn.get_settings_files():
            self.content['settings']['settings_filename'].addItem(name)
        self.content['settings']['settings_filename'].setCurrentText(file)
        self.content['settings']['busy'] = False

    @pyqtSlot()
    def update_limits(self):
        if self.content['axes_display']['car_id']['car_id'] == "None":
            self.index['car_id'].setText("None")
            print("Updating car_id to None")
            self.content['axes_display']['weight_jacker']['label'].setStyleSheet("color: red;")
            self.content['axes_display']['front_roll_bar']['label'].setStyleSheet("color: red;")
            self.content['axes_display']['rear_roll_bar']['label'].setStyleSheet("color: red;")
            self.content['axes_display']['fuel_map']['label'].setStyleSheet("color: red;")
        elif self.content['axes_display']['car_id']['car_id'] in car_settings:
            car_id = self.content['axes_display']['car_id']['car_id']
            self.index['car_id'].setText(car_settings[car_id]['name'])
            print("Updating for car_id: " + str(car_id) + " " + car_settings[car_id]['name'])
            if 'weight_jacker' in car_settings[car_id]:
                min = car_settings[car_id]['weight_jacker'][0]
                max = car_settings[car_id]['weight_jacker'][1]
                step['weight_jacker'] = 1 / (max - min)
                self.content['weight_jacker']['switch'].setRange(min, max)
                self.content['axes_display']['weight_jacker']['label'].setStyleSheet(QLabel.styleSheet(self.index['car_id']))
            else:
                self.content['axes_display']['weight_jacker']['label'].setStyleSheet("color: red;")
            if 'front_roll_bar' in car_settings[car_id]:
                min = car_settings[car_id]['front_roll_bar'][0]
                max = car_settings[car_id]['front_roll_bar'][1]
                step['front_roll_bar'] = 1 / (max - min)
                self.content['front_roll_bar']['switch'].setRange(min, max)
                self.content['axes_display']['front_roll_bar']['label'].setStyleSheet(QLabel.styleSheet(self.index['car_id']))
            else:
                self.content['axes_display']['front_roll_bar']['label'].setStyleSheet("color: red;")
            if 'rear_roll_bar' in car_settings[car_id]:
                min = car_settings[car_id]['rear_roll_bar'][0]
                max = car_settings[car_id]['rear_roll_bar'][1]
                step['rear_roll_bar'] = 1 / (max - min)
                self.content['rear_roll_bar']['switch'].setRange(min, max)
                self.content['axes_display']['rear_roll_bar']['label'].setStyleSheet(QLabel.styleSheet(self.index['car_id']))
            else:
                self.content['axes_display']['rear_roll_bar']['label'].setStyleSheet("color: red;")
            if 'fuel_map' in car_settings[car_id]:
                min = car_settings[car_id]['fuel_map'][0]
                max = car_settings[car_id]['fuel_map'][1]
                step['fuel_map'] = 1 / (max - min)
                self.content['fuel_map']['switch'].setRange(min, max)
                self.content['axes_display']['fuel_map']['label'].setStyleSheet(QLabel.styleSheet(self.index['car_id']))
            else:
                self.content['axes_display']['fuel_map']['label'].setStyleSheet("color: red;")
        else:
            car_id = self.content['axes_display']['car_id']['car_id']
            self.index['car_id'].setText(str(car_id) + " (not in car_settings list yet)")
            print("current_car " + str(car_id) + " not in car_settings!")
            self.content['axes_display']['weight_jacker']['label'].setStyleSheet("color: red;")
            self.content['axes_display']['front_roll_bar']['label'].setStyleSheet("color: red;")
            self.content['axes_display']['rear_roll_bar']['label'].setStyleSheet("color: red;")
            self.content['axes_display']['fuel_map']['label'].setStyleSheet("color: red;")
        text = "WJ: " + str(self.content['weight_jacker']['switch'].minimum()) + " to " + str(self.content['weight_jacker']['switch'].maximum())
        text += ", FARB: " + str(self.content['front_roll_bar']['switch'].minimum()) + " to " + str(self.content['front_roll_bar']['switch'].maximum())
        text += ", RARB: " + str(self.content['rear_roll_bar']['switch'].minimum()) + " to " + str(self.content['rear_roll_bar']['switch'].maximum())
        text += ", Fuel Map: " + str(self.content['fuel_map']['switch'].minimum()) + " to " + str(self.content['fuel_map']['switch'].maximum())
        self.content['axes_display']['car_id']['limits'].setText(text)

    @pyqtSlot()
    def apply_settings(self, file):
        if self.content['settings']['busy']: #if list is getting cleared or current text is being reset during list refresh, skip this function
            return

        fn.re_read_config(file)
        

        self.content['weight_jacker']['increment'].setValue(var.settings['weight_jacker']['increment'])
        self.content['weight_jacker']['switch'].setValue(var.settings['weight_jacker']['switch_value'])
        if var.settings['weight_jacker']['continuous']:
            self.content['weight_jacker']['increment_mode'].setCurrentText(lang['continuous'])
        else:
            self.content['weight_jacker']['increment_mode'].setCurrentText(lang['single'])
        if var.settings['weight_jacker']['toggle']:
            self.content['weight_jacker']['switch_mode'].setCurrentText(lang['toggle'])
        else:
            self.content['weight_jacker']['switch_mode'].setCurrentText(lang['hold'])
        self.content['weight_jacker']['up_device'].setText(dev.format("weight_jacker", "up"))
        self.content['weight_jacker']['down_device'].setText(dev.format("weight_jacker", "down"))
        self.content['weight_jacker']['switch_device'].setText(dev.format("weight_jacker", "switch"))

        self.content['front_roll_bar']['increment'].setValue(var.settings['front_roll_bar']['increment'])
        self.content['front_roll_bar']['switch'].setValue(var.settings['front_roll_bar']['switch_value'])
        if var.settings['front_roll_bar']['continuous']:
            self.content['front_roll_bar']['increment_mode'].setCurrentText(lang['continuous'])
        else:
            self.content['front_roll_bar']['increment_mode'].setCurrentText(lang['single'])
        if var.settings['front_roll_bar']['toggle']:
            self.content['front_roll_bar']['switch_mode'].setCurrentText(lang['toggle'])
        else:
            self.content['front_roll_bar']['switch_mode'].setCurrentText(lang['hold'])
        self.content['front_roll_bar']['up_device'].setText(dev.format("front_roll_bar", "up"))
        self.content['front_roll_bar']['down_device'].setText(dev.format("front_roll_bar", "down"))
        self.content['front_roll_bar']['switch_device'].setText(dev.format("front_roll_bar", "switch"))


        self.content['rear_roll_bar']['increment'].setValue(var.settings['rear_roll_bar']['increment'])
        self.content['rear_roll_bar']['switch'].setValue(var.settings['rear_roll_bar']['switch_value'])
        if var.settings['rear_roll_bar']['continuous']:
            self.content['rear_roll_bar']['increment_mode'].setCurrentText(lang['continuous'])
        else:
            self.content['rear_roll_bar']['increment_mode'].setCurrentText(lang['single'])
        if var.settings['rear_roll_bar']['toggle']:
            self.content['rear_roll_bar']['switch_mode'].setCurrentText(lang['toggle'])
        else:
            self.content['rear_roll_bar']['switch_mode'].setCurrentText(lang['hold'])
        self.content['rear_roll_bar']['up_device'].setText(dev.format("rear_roll_bar", "up"))
        self.content['rear_roll_bar']['down_device'].setText(dev.format("rear_roll_bar", "down"))
        self.content['rear_roll_bar']['switch_device'].setText(dev.format("rear_roll_bar", "switch"))


        self.content['fuel_map']['increment'].setValue(var.settings['fuel_map']['increment'])
        self.content['fuel_map']['switch'].setValue(var.settings['fuel_map']['switch_value'])
        if var.settings['fuel_map']['continuous']:
            self.content['fuel_map']['increment_mode'].setCurrentText(lang['continuous'])
        else:
            self.content['fuel_map']['increment_mode'].setCurrentText(lang['single'])
        if var.settings['fuel_map']['toggle']:
            self.content['fuel_map']['switch_mode'].setCurrentText(lang['toggle'])
        else:
            self.content['fuel_map']['switch_mode'].setCurrentText(lang['hold'])
        self.content['fuel_map']['up_device'].setText(dev.format("fuel_map", "up"))
        self.content['fuel_map']['down_device'].setText(dev.format("fuel_map", "down"))
        self.content['fuel_map']['switch_device'].setText(dev.format("fuel_map", "switch"))


        self.content['bite_point']['increment'].setValue(var.settings['bite_point']['increment'])
        self.content['bite_point']['switch'].setValue(var.settings['bite_point']['switch_value'])
        if var.settings['bite_point']['continuous']:
            self.content['bite_point']['increment_mode'].setCurrentText(lang['continuous'])
        else:
            self.content['bite_point']['increment_mode'].setCurrentText(lang['single'])
        if var.settings['bite_point']['toggle']:
            self.content['bite_point']['switch_mode'].setCurrentText(lang['toggle'])
        else:
            self.content['bite_point']['switch_mode'].setCurrentText(lang['hold'])
        self.content['bite_point']['pedal_device'].setText(dev.format("bite_point", "pedal"))
        self.content['bite_point']['up_device'].setText(dev.format("bite_point", "up"))
        self.content['bite_point']['down_device'].setText(dev.format("bite_point", "down"))
        self.content['bite_point']['switch_device'].setText(dev.format("bite_point", "switch"))


        self.content['engine_warming']['increment'].setValue(var.settings['engine_warming']['increment'])
        self.content['engine_warming']['switch'].setValue(var.settings['engine_warming']['switch_value'])
        if var.settings['engine_warming']['continuous']:
            self.content['engine_warming']['increment_mode'].setCurrentText(lang['continuous'])
        else:
            self.content['engine_warming']['increment_mode'].setCurrentText(lang['single'])
        if var.settings['engine_warming']['toggle']:
            self.content['engine_warming']['switch_mode'].setCurrentText(lang['toggle'])
        else:
            self.content['engine_warming']['switch_mode'].setCurrentText(lang['hold'])
        self.content['engine_warming']['pedal_device'].setText(dev.format("engine_warming", "pedal"))
        self.content['engine_warming']['up_device'].setText(dev.format("engine_warming", "up"))
        self.content['engine_warming']['down_device'].setText(dev.format("engine_warming", "down"))
        self.content['engine_warming']['switch_device'].setText(dev.format("engine_warming", "switch"))


        self.content['settings']['high_threshold'].setRange(min(int(var.settings['low_threshold']*100)+1,51), 99)
        self.content['settings']['high_threshold'].setValue(int(var.settings['high_threshold'] * 100))
        self.content['settings']['low_threshold'].setRange(1, max(int(var.settings['high_threshold']*100)-1,49))
        self.content['settings']['low_threshold'].setValue(int(var.settings['low_threshold'] * 100))
        self.content['settings']['axis_samples'].setValue(int(var.settings['axis_samples']))
        self.content['settings']['scale'].setCurrentText(str(var.settings['scale']) + "x")
        self.content['settings']['timer_first'].setValue(int(var.settings['timer_first']))
        self.content['settings']['timer_loop'].setValue(int(var.settings['timer_loop']))
        self.content['settings']['settings_filename'].setCurrentText(var.settings_active)



def main():
    os.environ["QT_SCALE_FACTOR"] = str(var.settings['scale'])

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    window.update()
    app.exec()
