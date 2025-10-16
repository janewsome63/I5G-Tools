import os
import sys
from string import capwords
import history
from time import sleep

from PyQt5.QtCore import (
    QSize,
    Qt,
    QTimer,
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

import variables as var
import vjoy
from devices import device_info

lang = {
    "title": "I5G Tools",
    "version": "v0.2a",
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
    "high_threshold": "High Axis Threshold:",
    "low_threshold": "Low Axis Threshold:",
    "axis_samples": "Number of Axis Samples:",
    "scale": "Scale Factor:",
    "timer_loop": "Continuous Mode Loop Timer (in ms):",
    "timer_first": "Continuous Mode Initial Loop Timer (in ms)",
    "none": "None",
}

ui = {
    "width": 560,
    "height": 250,
    "timer": QTimer(),
    "thread_pool": QThreadPool(),
}

var.settings = {
    "high_threshold": 0.90,
    "low_threshold": 0.10,
    "frequency": 0.1,
    "scale": "1.25",
    "device": 1,
    "axis_samples": 2,
    "timer_loop": 150,
    "timer_first": 300,

    "weight_jacker": {
        "continuous": True,
        "toggle": False,
        "increment": 1,
        "switch": -20,
    },
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

        # --------Weight Jacker Tab--------#
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
        self.weight_jacker_content['increment'].setValue(var.settings['weight_jacker']['increment'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['increment'], 1, 1,
                                            alignment=Qt.AlignmentFlag.AlignLeft)
        self.weight_jacker_content['increment'].valueChanged.connect(self.wj_increment)

        self.weight_jacker_content['switch'] = QSpinBox()
        self.weight_jacker_content['switch'].setFixedSize(40, 20)
        self.weight_jacker_content['switch'].setRange(-20, 20)
        self.weight_jacker_content['switch'].setValue(var.settings['weight_jacker']['switch'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['switch'], 1, 2,
                                            alignment=Qt.AlignmentFlag.AlignLeft)
        self.weight_jacker_content['switch'].valueChanged.connect(self.wj_switch)

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
        self.weight_jacker_content['increment_mode'].currentIndexChanged.connect(self.wj_increment_mode)

        self.weight_jacker_content['switch_mode'] = QComboBox()
        self.weight_jacker_content['switch_mode'].addItem(lang['hold'])
        self.weight_jacker_content['switch_mode'].addItem(lang['toggle'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['switch_mode'], 2, 2)
        self.weight_jacker_content['switch_mode'].currentIndexChanged.connect(self.wj_switch_mode)

        self.weight_jacker_content['up_label'] = QLabel()
        self.weight_jacker_content['up_label'].setAlignment(Qt.AlignLeft)
        self.weight_jacker_content['up_label'].setText(lang['up'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['up_label'], 3, 0)

        self.weight_jacker_content['up_device'] = QLineEdit()
        self.weight_jacker_content['up_device'].setAlignment(Qt.AlignCenter)
        var.bindings['weight_jacker']['up'] = None
        self.weight_jacker_content['up_device'].setText(str(var.bindings['weight_jacker']['up']))
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
        var.bindings['weight_jacker']['down'] = None
        self.weight_jacker_content['down_device'].setText(str(var.bindings['weight_jacker']['down']))
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
        var.bindings['weight_jacker']['switch'] = None
        self.weight_jacker_content['switch_device'].setText(str(var.bindings['weight_jacker']['switch']))
        self.weight_jacker_content['switch_device'].setReadOnly(True)
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['switch_device'], 5, 1)

        self.weight_jacker_content['switch_bind'] = QPushButton()
        self.weight_jacker_content['switch_bind'].setText(lang['bind'])
        self.weight_jacker.layout.addWidget(self.weight_jacker_content['switch_bind'], 5, 2)
        self.weight_jacker_content['switch_bind'].clicked.connect(self.wj_switch_bind)

        self.weight_jacker.setLayout(self.weight_jacker.layout)

        # --------Roll Bars Tab--------#
        self.roll_bars.layout = QGridLayout()
        self.roll_bars.layout.addWidget(QLabel("Roll Bars"), 0, 0)
        self.roll_bars.setLayout(self.roll_bars.layout)

        # --------Fuel Map Tab--------#
        self.fuel_map.layout = QGridLayout()
        self.fuel_map.layout.addWidget(QLabel("Fuel Map"), 0, 0)
        self.fuel_map.setLayout(self.fuel_map.layout)

        # --------Bite Point Tab--------#
        self.bite_point.layout = QGridLayout()
        self.bite_point.layout.addWidget(QLabel("Bite Point"), 0, 0)
        self.bite_point.setLayout(self.bite_point.layout)

        # --------Engine Warming Tab--------#
        self.engine_warming.layout = QGridLayout()
        self.engine_warming.layout.addWidget(QLabel("Engine Warming"), 0, 0)
        self.engine_warming.setLayout(self.engine_warming.layout)

        # --------Settings Tab--------#
        self.settings.layout = QGridLayout()
        self.settings_content = {}

        self.settings_content['high_threshold_label'] = QLabel()
        self.settings_content['high_threshold_label'].setAlignment(Qt.AlignLeft)
        self.settings_content['high_threshold_label'].setText(lang['high_threshold'])
        self.settings.layout.addWidget(self.settings_content['high_threshold_label'], 0, 0)

        self.settings_content['high_threshold'] = QSpinBox()
        self.settings_content['high_threshold'].setFixedSize(42, 20)
        self.settings_content['high_threshold'].setRange(51, 99)
        self.settings_content['high_threshold'].setValue(int(var.settings['high_threshold'] * 100))
        self.settings.layout.addWidget(self.settings_content['high_threshold'], 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.settings_content['high_threshold'].valueChanged.connect(self.high_threshold)

        self.settings_content['low_threshold_label'] = QLabel()
        self.settings_content['low_threshold_label'].setAlignment(Qt.AlignLeft)
        self.settings_content['low_threshold_label'].setText(lang['low_threshold'])
        self.settings.layout.addWidget(self.settings_content['low_threshold_label'], 1, 0)

        self.settings_content['low_threshold'] = QSpinBox()
        self.settings_content['low_threshold'].setFixedSize(42, 20)
        self.settings_content['low_threshold'].setRange(1, 49)
        self.settings_content['low_threshold'].setValue(int(var.settings['low_threshold'] * 100))
        self.settings.layout.addWidget(self.settings_content['low_threshold'], 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.settings_content['low_threshold'].valueChanged.connect(self.low_threshold)

        self.settings_content['axis_samples'] = QLabel()
        self.settings_content['axis_samples'].setAlignment(Qt.AlignLeft)
        self.settings_content['axis_samples'].setText(lang['axis_samples'])
        self.settings.layout.addWidget(self.settings_content['axis_samples'], 2, 0)

        self.settings_content['axis_samples'] = QSpinBox()
        self.settings_content['axis_samples'].setFixedSize(42, 20)
        self.settings_content['axis_samples'].setRange(2, 10)
        self.settings_content['axis_samples'].setValue(int(var.settings['axis_samples']))
        self.settings.layout.addWidget(self.settings_content['axis_samples'], 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.settings_content['axis_samples'].valueChanged.connect(self.axis_samples)

        self.settings_content['scale_label'] = QLabel()
        self.settings_content['scale_label'].setAlignment(Qt.AlignLeft)
        self.settings_content['scale_label'].setText(lang['scale'])
        self.settings.layout.addWidget(self.settings_content['scale_label'], 3, 0)

        self.settings_content['scale'] = QComboBox()
        self.settings_content['scale'].setFixedSize(60, 22)
        self.settings_content['scale'].addItem("0.50" + "x")
        self.settings_content['scale'].addItem("0.75" + "x")
        self.settings_content['scale'].addItem("1.00" + "x")
        self.settings_content['scale'].addItem("1.25" + "x")
        self.settings_content['scale'].addItem("1.50" + "x")
        self.settings_content['scale'].setCurrentText(var.settings['scale'] + "x")
        self.settings.layout.addWidget(self.settings_content['scale'], 3, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.settings_content['scale'].currentTextChanged.connect(self.scale)

        self.settings_content['timer_first'] = QLabel()
        self.settings_content['timer_first'].setAlignment(Qt.AlignLeft)
        self.settings_content['timer_first'].setText(lang['timer_first'])
        self.settings.layout.addWidget(self.settings_content['timer_first'], 4, 0)

        self.settings_content['timer_first'] = QSpinBox()
        self.settings_content['timer_first'].setFixedSize(42, 20)
        self.settings_content['timer_first'].setRange(1, 1000)
        self.settings_content['timer_first'].setValue(int(var.settings['timer_first']))
        self.settings.layout.addWidget(self.settings_content['timer_first'], 4, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.settings_content['timer_first'].valueChanged.connect(self.timer_first)

        self.settings_content['timer_loop'] = QLabel()
        self.settings_content['timer_loop'].setAlignment(Qt.AlignLeft)
        self.settings_content['timer_loop'].setText(lang['timer_loop'])
        self.settings.layout.addWidget(self.settings_content['timer_loop'], 5, 0)

        self.settings_content['timer_loop'] = QSpinBox()
        self.settings_content['timer_loop'].setFixedSize(42, 20)
        self.settings_content['timer_loop'].setRange(1, 1000)
        self.settings_content['timer_loop'].setValue(int(var.settings['timer_loop']))
        self.settings.layout.addWidget(self.settings_content['timer_loop'], 5, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.settings_content['timer_loop'].valueChanged.connect(self.timer_loop)

        self.settings.setLayout(self.settings.layout)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.setCentralWidget(self.tabs)

        ui['timer'].timeout.connect(self.updater)
        ui['timer'].start(int((var.settings['frequency'] * 1000) / 10))

        self.index = {
            "weight_jacker": {
                "up": {
                    "bind": self.weight_jacker_content['up_bind'],
                    "device": self.weight_jacker_content['up_device'],
                    "label": self.weight_jacker_content['up_label'],
                },
                "down": {
                    "bind": self.weight_jacker_content['down_bind'],
                    "device": self.weight_jacker_content['down_device'],
                    "label": self.weight_jacker_content['down_label'],
                },
                "switch": {
                    "bind": self.weight_jacker_content['switch_bind'],
                    "device": self.weight_jacker_content['switch_device'],
                    "label": self.weight_jacker_content['switch_label'],
                }
            }
        }

    def updater(self):
        self.wj_display()
        # self.wj_switch_value()

    def wj_display(self):
        pct = vjoy.axis_values["weight_jacker"]
        self.weight_jacker_content['axis'].setValue(int(pct * 100))
        self.weight_jacker_content['axis'].update()

        pct = pct - 0.5
        self.weight_jacker_content['lcd'].display(round(pct / 0.025))
        self.weight_jacker_content['lcd'].update()

    @pyqtSlot()
    def calibrate(self):
        self.is_running = True
        vjoy.calibrate(self.axis)
        self.is_running = False

    @pyqtSlot()
    def wj_calibrate(self):
        self.axis = "weight_jacker"
        if not var.status['weight_jacker']['switched']:
            self.pct = var.status['weight_jacker']['primary']
        elif var.status['weight_jacker']['switched']:
            self.pct = var.status['weight_jacker']['secondary']
        if not self.is_running:
            ui['thread_pool'].start(self.calibrate)

    @pyqtSlot()
    def wj_increment(self):
        var.settings['weight_jacker']['increment'] = self.weight_jacker_content['increment'].value()

    @pyqtSlot()
    def wj_switch(self):
        wj = self.weight_jacker_content['switch'].value()
        var.settings['weight_jacker']['switch'] = wj
        var.status['weight_jacker']['secondary'] = (wj * 0.025) + 0.5
        if var.status['weight_jacker']['switched'] == True:
            vjoy.set("weight_jacker", var.status['weight_jacker']['secondary'])

    @pyqtSlot()
    def wj_switch_value(self):
        pct = round((var.status['weight_jacker']['secondary'] - 0.5) / 0.025)
        self.weight_jacker_content['switch'].setValue(pct)
        self.weight_jacker_content['switch'].update()

    @pyqtSlot()
    def wj_increment_mode(self):
        if self.weight_jacker_content['increment_mode'].currentText() == "Continuous":
            var.settings['weight_jacker']['continuous'] = True
        elif self.weight_jacker_content['increment_mode'].currentText() == "Single":
            var.settings['weight_jacker']['continuous'] = False

    @pyqtSlot()
    def wj_switch_mode(self):
        if self.weight_jacker_content['switch_mode'].currentText() == "Toggle":
            var.settings['weight_jacker']['toggle'] = True
        elif self.weight_jacker_content['switch_mode'].currentText() == "Hold":
            var.settings['weight_jacker']['toggle'] = False

    @pyqtSlot()
    def high_threshold(self):
        var.settings['high_threshold'] = (self.settings_content['high_threshold'].value() / 100)

    @pyqtSlot()
    def low_threshold(self):
        var.settings['low_threshold'] = (self.settings_content['low_threshold'].value() / 100)

    @pyqtSlot()
    def axis_samples(self):
        var.settings['axis_samples'] = self.settings_content['axis_samples'].value()

    @pyqtSlot()
    def scale(self):
        scale = self.settings_content['scale'].currentText()
        scale = scale.replace("x", "")
        var.settings['scale'] = scale

    @pyqtSlot()
    def timer_loop(self):
        var.settings['timer_loop'] = self.settings_content['timer_loop'].value()

    @pyqtSlot()
    def timer_first(self):
        var.settings['timer_first'] = self.settings_content['timer_first'].value()

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
                break

            if var.event['guid'] != 0:
                if var.event['type'] == "button":
                    if var.event['value'] != False:
                        var.bindings[function][control] = {
                            "guid": var.event['guid'],
                            "type": var.event['type'],
                            "num": var.event['num'],
                        }
                elif var.event['type'] == "axis":
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

        if var.bindings[function][control]:
            if "dir" in var.bindings[function][control]:
                name = device_info[var.bindings[function][control]['guid']]['name']
                type = capwords(var.bindings[function][control]['type'])
                num = str(var.bindings[function][control]['num'])
                dir = capwords(var.bindings[function][control]['dir'])
                dev_pretty = name + " - " + type + " " + num + " " + dir
            elif "value" in var.bindings[function][control]:
                name = device_info[var.bindings[function][control]['guid']]['name']
                type = capwords(var.bindings[function][control]['type'])
                num = str(var.bindings[function][control]['num'])
                axis_dir = var.bindings[function][control]['value'] > 0.5
                dev_pretty = name + " - " + type + " " + num
                if axis_dir:
                    dev_pretty += "+"
                else:
                    dev_pretty += "-"
            else:
                name = device_info[var.bindings[function][control]['guid']]['name']
                type = capwords(var.bindings[function][control]['type'])
                num = str(var.bindings[function][control]['num'])
                dev_pretty = name + " - " + type + " " + num
            self.index[function][control]['device'].setText(dev_pretty)
        else:
            self.index[function][control]['device'].setText(lang['none'])

        var.bindings['status'] = {
            "active": False,
            "function": None,
            "control": None,
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
        else:
            self.is_running = False

    @pyqtSlot()
    def wj_down_bind(self):
        var.bindings['status'] = {
            "function": "weight_jacker",
            "control": "down",
        }
        if not self.is_running:
            ui['thread_pool'].start(self.bind)
        else:
            self.is_running = False

    @pyqtSlot()
    def wj_switch_bind(self):
        var.bindings['status'] = {
            "function": "weight_jacker",
            "control": "switch",
        }
        if not self.is_running:
            ui['thread_pool'].start(self.bind)
        else:
            self.is_running = False


def main():
    os.environ["QT_SCALE_FACTOR"] = var.settings['scale']

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    window.update()
    app.exec()
