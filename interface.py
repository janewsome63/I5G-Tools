import sys
import os
import time
import threading
import devices as dev
import functions as fn
import variables as var
import vjoy

from PyQt5.QtCore import (
    QSize,
    Qt,
    QObject,
    QTimer,
    QRunnable,
    QThreadPool,
    pyqtSlot
)
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QLabel,
    QLCDNumber,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QGridLayout,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QLineEdit
)

lang = {
    "title": "I5G Tools",
    "version": "v0.1",
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
}

ui = {
    "width": 560,
    "height": 250,
    "timer": QTimer(),
    "thread_pool": QThreadPool(),
}

var.settings = {
    "update_frequency": 10,
    "scale_factor": "1.25",
    "vjoy_device": 1,
    "axis_threshold": 0.9,
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_running = False

        self.setWindowTitle(lang['title'] + " " + lang['version'])
        self.setFixedSize(QSize(ui['width'], ui['height']))
        self.layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.weight_jacker = QWidget()
        self.roll_bars = QWidget()
        self.fuel_map = QWidget()
        self.bite_point = QWidget()
        self.engine_warming = QWidget()
        self.settings = QWidget()

        self.tabs.addTab(self.weight_jacker, "Weight Jacker")
        self.tabs.addTab(self.roll_bars, "Roll Bars")
        self.tabs.addTab(self.fuel_map, "Fuel Map")
        self.tabs.addTab(self.bite_point, "Bite Point")
        self.tabs.addTab(self.engine_warming, "Engine Warming")
        self.tabs.addTab(self.settings, "Settings")
        self.tabs.setUsesScrollButtons(False)

        #--------Weight Jacker Tab--------#
        self.weight_jacker_content = {}
        self.weight_jacker.layout = QGridLayout()

        self.weight_jacker_content['lcd'] = QLCDNumber()
        self.weight_jacker_content['lcd'].display(0)
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['lcd'], 0, 0)

        self.weight_jacker_content['axis'] = QProgressBar()
        self.weight_jacker_content['axis'].setTextVisible(False)
        self.weight_jacker_content['axis'].setMinimum(0)
        self.weight_jacker_content['axis'].setMaximum(100)
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['axis'], 0, 1)

        self.weight_jacker_content['calibrate'] = QPushButton()
        self.weight_jacker_content['calibrate'].setText(lang['calibrate'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['calibrate'], 0, 2)
        self.weight_jacker_content['calibrate'].clicked.connect(self.wj_calibrate)

        self.weight_jacker_content['increment_label'] = QLabel()
        self.weight_jacker_content['increment_label'].setAlignment(Qt.AlignLeft)
        self.weight_jacker_content['increment_label'].setText(lang['increment'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['increment_label'], 1, 0)

        self.weight_jacker_content['switch_label'] = QLabel()
        self.weight_jacker_content['switch_label'].setAlignment(Qt.AlignRight)
        self.weight_jacker_content['switch_label'].setText(lang['switch_value'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['switch_label'], 1, 1)

        self.weight_jacker_content['increment'] = QSpinBox()
        self.weight_jacker_content['increment'].setFixedSize(38, 20)
        self.weight_jacker_content['increment'].setRange(1, 20)
        self.weight_jacker_content['increment'].setValue(var.wj_values['increment'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['increment'], 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        self.weight_jacker_content['switch'] = QSpinBox()
        self.weight_jacker_content['switch'].setFixedSize(40, 20)
        self.weight_jacker_content['switch'].setRange(-20, 20)
        self.weight_jacker_content['switch'].setValue(var.wj_values['switch_value'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['switch'], 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)

        self.weight_jacker_content['increment_mode_label'] = QLabel()
        self.weight_jacker_content['increment_mode_label'].setAlignment(Qt.AlignRight)
        self.weight_jacker_content['increment_mode_label'].setText(lang['increment_mode'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['increment_mode_label'], 2, 0)

        self.weight_jacker_content['switch_mode_label'] = QLabel()
        self.weight_jacker_content['switch_mode_label'].setAlignment(Qt.AlignRight)
        self.weight_jacker_content['switch_mode_label'].setText(lang['switch_mode'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['switch_mode_label'], 2, 1)

        self.weight_jacker_content['increment_mode'] = QComboBox()
        self.weight_jacker_content['increment_mode'].setFixedSize(93, 22)
        self.weight_jacker_content['increment_mode'].addItem(lang['continuous'])
        self.weight_jacker_content['increment_mode'].addItem(lang['single'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['increment_mode'], 2, 1)

        self.weight_jacker_content['switch_mode'] = QComboBox()
        self.weight_jacker_content['switch_mode'].addItem(lang['hold'])
        self.weight_jacker_content['switch_mode'].addItem(lang['toggle'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['switch_mode'], 2, 2)

        self.weight_jacker_content['up_label'] = QLabel()
        self.weight_jacker_content['up_label'].setAlignment(Qt.AlignLeft)
        self.weight_jacker_content['up_label'].setText(lang['up'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['up_label'], 3, 0)

        self.weight_jacker_content['up_device'] = QLineEdit()
        self.weight_jacker_content['up_device'].setAlignment(Qt.AlignCenter)
        self.weight_jacker_content['up_device'].setText(var.bindings['wj_up_device'] + " - " + var.bindings['wj_up_button'])
        self.weight_jacker_content['up_device'].setReadOnly(True)
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['up_device'], 3, 1)

        self.weight_jacker_content['up_bind'] = QPushButton()
        self.weight_jacker_content['up_bind'].setText(lang['bind'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['up_bind'], 3, 2)
        self.weight_jacker_content['up_bind'].clicked.connect(self.wj_up_bind)

        self.weight_jacker_content['down_label'] = QLabel()
        self.weight_jacker_content['down_label'].setAlignment(Qt.AlignLeft)
        self.weight_jacker_content['down_label'].setText(lang['down'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['down_label'], 4, 0)

        self.weight_jacker_content['down_device'] = QLineEdit()
        self.weight_jacker_content['down_device'].setAlignment(Qt.AlignCenter)
        self.weight_jacker_content['down_device'].setText(var.bindings['wj_down_device'] + " - " + var.bindings['wj_down_button'])
        self.weight_jacker_content['down_device'].setReadOnly(True)
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['down_device'], 4, 1)

        self.weight_jacker_content['down_bind'] = QPushButton()
        self.weight_jacker_content['down_bind'].setText(lang['bind'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['down_bind'], 4, 2)
        self.weight_jacker_content['down_bind'].clicked.connect(self.wj_down_bind)

        self.weight_jacker_content['switch_label'] = QLabel()
        self.weight_jacker_content['switch_label'].setAlignment(Qt.AlignLeft)
        self.weight_jacker_content['switch_label'].setText(lang['switch'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['switch_label'], 5, 0)

        self.weight_jacker_content['switch_device'] = QLineEdit()
        self.weight_jacker_content['switch_device'].setAlignment(Qt.AlignCenter)
        self.weight_jacker_content['switch_device'].setText(var.bindings['wj_switch_device'] + " - " + var.bindings['wj_switch_button'])
        self.weight_jacker_content['switch_device'].setReadOnly(True)
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['switch_device'], 5, 1)

        self.weight_jacker_content['switch_bind'] = QPushButton()
        self.weight_jacker_content['switch_bind'].setText(lang['bind'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['switch_bind'], 5, 2)
        self.weight_jacker_content['switch_bind'].clicked.connect(self.wj_switch_bind)

        self.weight_jacker.setLayout(self.weight_jacker.layout)

        #--------Roll Bars Tab--------#
        self.roll_bars.layout = QGridLayout()
        self.roll_bars.layout.addWidget(QLabel("Roll Bars"), 0, 0)
        self.roll_bars.setLayout(self.roll_bars.layout)

        #--------Fuel Map Tab--------#
        self.fuel_map.layout = QGridLayout()
        self.fuel_map.layout.addWidget(QLabel("Fuel Map"), 0, 0)
        self.fuel_map.setLayout(self.fuel_map.layout)

        #--------Bite Point Tab--------#
        self.bite_point.layout = QGridLayout()
        self.bite_point.layout.addWidget(QLabel("Bite Point"), 0, 0)
        self.bite_point.setLayout(self.bite_point.layout)

        #--------Engine Warming Tab--------#
        self.engine_warming.layout = QGridLayout()
        self.engine_warming.layout.addWidget(QLabel("Engine Warming"), 0, 0)
        self.engine_warming.setLayout(self.engine_warming.layout)

        #--------Settings Tab--------#
        self.settings.layout = QGridLayout()
        self.settings.layout.addWidget(QLabel("Settings"), 0, 0)
        self.settings.setLayout(self.settings.layout)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.setCentralWidget(self.tabs)

        ui['timer'].timeout.connect(self.updater)
        ui['timer'].start(var.settings['update_frequency'])

    def updater(self):
        self.wj_display()

    def wj_display(self):
        pct = vjoy.axis_values["wj"]
        self.weight_jacker_content['axis'].setValue(int(pct * 100))
        self.weight_jacker_content['axis'].update()

        pct = pct - 0.5
        self.weight_jacker_content['lcd'].display(int(pct / 0.025))
        self.weight_jacker_content['lcd'].update()

    @pyqtSlot()
    def calibrate(self):
        self.is_running = True
        vjoy.calibrate(self.axis, self.pct)
        self.is_running = False

    @pyqtSlot()
    def wj_calibrate(self):
        self.axis = "wj"
        self.pct = 0.5
        if not self.is_running:
            ui['thread_pool'].start(self.calibrate)

    @pyqtSlot()
    def bind(self):
        self.is_running = True
        fn.bind(var.bindings['status']['function'], var.bindings['status']['control'])
        self.weight_jacker_content['up_bind'].setText(lang['bind'])
        var.bindings['status'] = {
            "function": "",
            "control": "",
        }
        self.is_running = False

    @pyqtSlot()
    def wj_up_bind(self):
        var.bindings['status'] = {
            "function": "weight_jacker",
            "control": "up",
        }
        if not self.is_running:
            ui['thread_pool'].start(self.bind)
            self.weight_jacker_content['up_bind'].setText(lang['binding'])
        else:
            var.bindings['active'] = False
        self.weight_jacker_content['up_bind'].update()

    @pyqtSlot()
    def wj_down_bind(self):
        self.type = "wj"
        self.weight_jacker_content['up_bind'].setText(lang['binding'])
        if not self.is_running:
            ui['thread_pool'].start(self.bind)
        self.weight_jacker_content['up_bind'].setText(lang['bind'])

    @pyqtSlot()
    def wj_switch_bind(self):
        self.type = "wj"
        self.weight_jacker_content['up_bind'].setText(lang['binding'])
        if not self.is_running:
            ui['thread_pool'].start(self.bind)
        self.weight_jacker_content['up_bind'].setText(lang['bind'])

def main():
    os.environ["QT_SCALE_FACTOR"] = var.settings['scale_factor']

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    window.update()
    app.exec()