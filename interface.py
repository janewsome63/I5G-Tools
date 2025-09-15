import sys
import os
import time

import devices as dev
import functions as fn
import variables as var
import vjoy

from PyQt5.QtCore import QSize, Qt, QObject, QTimer
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

timer = QTimer()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(var.lang['title'] + " " + var.lang['version'])
        self.setFixedSize(QSize(433, 250))
        layout = QVBoxLayout()

        tabs = QTabWidget()
        wj = QWidget()
        farb = QWidget()
        rarb = QWidget()
        fm = QWidget()
        settings = QWidget()

        tabs.addTab(wj, "Weight Jacker")
        tabs.addTab(farb, "Front Bar")
        tabs.addTab(rarb, "Rear Bar")
        tabs.addTab(fm, "Fuel Map")
        tabs.addTab(settings, "Settings")

        #--------Weight Jacker Tab--------#
        wj.layout = QGridLayout()

        wj_number = QLCDNumber()
        wj_number.display(var.wj_values['value'])
        wj.layout.addWidget(wj_number, 0, 0)

        self.wj_axis = QProgressBar()
        self.wj_axis.setTextVisible(False)
        self.wj_axis.setMinimum(0)
        self.wj_axis.setMaximum(100)
        self.wj_axis.setValue(50)
        wj.layout.addWidget(self.wj_axis, 0, 1)

        self.wj_calibrate = QPushButton()
        self.wj_calibrate.setText(var.lang['calibrate'])
        wj.layout.addWidget(self.wj_calibrate, 0, 2)

        wj_increment_label = QLabel()
        wj_increment_label.setAlignment(Qt.AlignLeft)
        wj_increment_label.setText(var.lang['increment'])
        wj.layout.addWidget(wj_increment_label, 1, 0)

        wj_switch_value_label = QLabel()
        wj_switch_value_label.setAlignment(Qt.AlignRight)
        wj_switch_value_label.setText(var.lang['switch_value'])
        wj.layout.addWidget(wj_switch_value_label, 1, 1)

        wj_increment = QSpinBox()
        wj_increment.setFixedSize(38, 20)
        wj_increment.setRange(1, 20)
        wj_increment.setValue(var.wj_values['increment'])
        wj.layout.addWidget(wj_increment, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        wj_switch_value = QSpinBox()
        wj_switch_value.setFixedSize(40, 20)
        wj_switch_value.setRange(-20, 20)
        wj_switch_value.setValue(var.wj_values['switch_value'])
        wj.layout.addWidget(wj_switch_value, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)

        wj_increment_mode_label = QLabel()
        wj_increment_mode_label.setAlignment(Qt.AlignRight)
        wj_increment_mode_label.setText(var.lang['increment_mode'])
        wj.layout.addWidget(wj_increment_mode_label, 2, 0)

        wj_switch_mode_label = QLabel()
        wj_switch_mode_label.setAlignment(Qt.AlignRight)
        wj_switch_mode_label.setText(var.lang['switch_mode'])
        wj.layout.addWidget(wj_switch_mode_label, 2, 1)

        wj_increment_mode = QComboBox()
        wj_increment_mode.setFixedSize(93, 22)
        wj_increment_mode.addItem(var.lang['continuous'])
        wj_increment_mode.addItem(var.lang['single'])
        wj.layout.addWidget(wj_increment_mode, 2, 1)

        wj_switch_mode = QComboBox()
        wj_switch_mode.addItem(var.lang['hold'])
        wj_switch_mode.addItem(var.lang['toggle'])
        wj.layout.addWidget(wj_switch_mode, 2, 2)





        wj_up = QLabel()
        wj_up.setAlignment(Qt.AlignLeft)
        wj_up.setText(var.lang['up'])
        wj.layout.addWidget(wj_up, 3, 0)

        wj_up_current = QLineEdit()
        wj_up_current.setAlignment(Qt.AlignCenter)
        wj_up_current.setText(var.bindings['wj_up_device'] + " - " + var.bindings['wj_up_button'])
        wj_up_current.setReadOnly(True)
        wj.layout.addWidget(wj_up_current, 3, 1)

        wj_up_bind = QPushButton()
        wj_up_bind.setText(var.lang['bind'])
        wj.layout.addWidget(wj_up_bind, 3, 2)

        wj_down = QLabel()
        wj_down.setAlignment(Qt.AlignLeft)
        wj_down.setText(var.lang['down'])
        wj.layout.addWidget(wj_down, 4, 0)

        wj_down_current = QLineEdit()
        wj_down_current.setAlignment(Qt.AlignCenter)
        wj_down_current.setText(var.bindings['wj_down_device'] + " - " + var.bindings['wj_down_button'])
        wj_down_current.setReadOnly(True)
        wj.layout.addWidget(wj_down_current, 4, 1)

        wj_down_bind = QPushButton()
        wj_down_bind.setText(var.lang['bind'])
        wj.layout.addWidget(wj_down_bind, 4, 2)

        wj_switch = QLabel()
        wj_switch.setAlignment(Qt.AlignLeft)
        wj_switch.setText(var.lang['switch'])
        wj.layout.addWidget(wj_switch, 5, 0)

        wj_switch_current = QLineEdit()
        wj_switch_current.setAlignment(Qt.AlignCenter)
        wj_switch_current.setText(var.bindings['wj_switch_device'] + " - " + var.bindings['wj_switch_button'])
        wj_switch_current.setReadOnly(True)
        wj.layout.addWidget(wj_switch_current, 5, 1)

        wj_switch_bind = QPushButton()
        wj_switch_bind.setText(var.lang['bind'])
        wj.layout.addWidget(wj_switch_bind, 5, 2)

        wj.setLayout(wj.layout)

        #--------Front Bar Tab--------#
        farb.layout = QGridLayout()
        farb.layout.addWidget(QLabel("WJ"), 0, 0)
        farb.setLayout(farb.layout)

        #--------Rear Bar Tab--------#
        rarb.layout = QGridLayout()
        rarb.layout.addWidget(QLabel("WJ"), 0, 0)
        rarb.setLayout(rarb.layout)

        #--------Fuel Map Tab--------#
        fm.layout = QGridLayout()
        fm.layout.addWidget(QLabel("WJ"), 0, 0)
        fm.setLayout(fm.layout)

        #--------Settings Tab--------#
        settings.layout = QGridLayout()
        settings.layout.addWidget(QLabel("WJ"), 0, 0)
        settings.setLayout(settings.layout)

        layout.addWidget(tabs)
        self.setLayout(layout)
        self.setCentralWidget(tabs)

        timer.timeout.connect(self.update_axis)
        timer.start(40)


    def update_axis(self):
        self.wj_axis.setValue(int(dev.device_info[vjoy.find_vjoy()]['axes'][0] * 100))
        self.wj_axis.update()

def ui():
    os.environ["QT_SCALE_FACTOR"] = "1.25"

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    window.update()
    app.exec()