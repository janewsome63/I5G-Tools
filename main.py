# Only needed for access to command line arguments
import sys
import os

from PyQt5.QtCore import QSize, Qt
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

# Variables and lists
# Global



# Static dictionaries
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
    "calibrate": "Calibrate",
}

# Malleable dictionaries
devices = {}
bindings = {}
wj_values = {}

def init_vars():
    bindings['wj_up_device'] = "Placeholder Device"
    bindings['wj_up_button'] = "1"    
    bindings['wj_down_device'] = "Placeholder Device"
    bindings['wj_down_button'] = "2"
    bindings['wj_switch_device'] = "Placeholder Device"
    bindings['wj_switch_button'] = "3"

    wj_values['percent'] = 50
    wj_values['raw'] = 12345
    wj_values['value'] = -20
    wj_values['increment'] = 1
    wj_values['switch_value'] = -20
    wj_values['switch_mode'] = 1
    wj_values['increment_mode'] = 1

init_vars()

os.environ["QT_SCALE_FACTOR"] = "1.25"  # Set scale to 130%

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(lang['title'] + " " + lang['version'])
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
        wj_number.display(wj_values['value'])
        wj.layout.addWidget(wj_number, 0, 0)

        wj_axis = QProgressBar()
        wj_axis.setTextVisible(False)
        wj_axis.setMinimum(0)
        wj_axis.setMaximum(100)
        wj_axis.setValue(wj_values['percent'])
        wj.layout.addWidget(wj_axis, 0, 1)

        wj_calibrate = QPushButton()
        wj_calibrate.setText(lang['calibrate'])
        wj.layout.addWidget(wj_calibrate, 0, 2)

        wj_increment_label = QLabel()
        wj_increment_label.setAlignment(Qt.AlignLeft)
        wj_increment_label.setText(lang['increment'])
        wj.layout.addWidget(wj_increment_label, 1, 0)

        wj_switch_value_label = QLabel()
        wj_switch_value_label.setAlignment(Qt.AlignRight)
        wj_switch_value_label.setText(lang['switch_value'])
        wj.layout.addWidget(wj_switch_value_label, 1, 1)

        wj_increment = QSpinBox()
        wj_increment.setFixedSize(38, 20)
        wj_increment.setRange(1, 20)
        wj_increment.setValue(wj_values['increment'])
        wj.layout.addWidget(wj_increment, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        wj_switch_value = QSpinBox()
        wj_switch_value.setFixedSize(40, 20)
        wj_switch_value.setRange(-20, 20)
        wj_switch_value.setValue(wj_values['switch_value'])
        wj.layout.addWidget(wj_switch_value, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)

        wj_increment_mode_label = QLabel()
        wj_increment_mode_label.setAlignment(Qt.AlignRight)
        wj_increment_mode_label.setText(lang['increment_mode'])
        wj.layout.addWidget(wj_increment_mode_label, 2, 0)

        wj_switch_mode_label = QLabel()
        wj_switch_mode_label.setAlignment(Qt.AlignRight)
        wj_switch_mode_label.setText(lang['switch_mode'])
        wj.layout.addWidget(wj_switch_mode_label, 2, 1)

        wj_increment_mode = QComboBox()
        wj_increment_mode.setFixedSize(93, 22)
        wj_increment_mode.addItem(lang['continuous'])
        wj_increment_mode.addItem(lang['single'])
        wj.layout.addWidget(wj_increment_mode, 2, 1)

        wj_switch_mode = QComboBox()
        wj_switch_mode.addItem(lang['hold'])
        wj_switch_mode.addItem(lang['toggle'])
        wj.layout.addWidget(wj_switch_mode, 2, 2)





        wj_up = QLabel()
        wj_up.setAlignment(Qt.AlignLeft)
        wj_up.setText(lang['up'])
        wj.layout.addWidget(wj_up, 3, 0)

        wj_up_current = QLineEdit()
        wj_up_current.setAlignment(Qt.AlignCenter)
        wj_up_current.setText(bindings['wj_up_device'] + " - " + bindings['wj_up_button'])
        wj_up_current.setReadOnly(True)
        wj.layout.addWidget(wj_up_current, 3, 1)

        wj_up_bind = QPushButton()
        wj_up_bind.setText(lang['bind'])
        wj.layout.addWidget(wj_up_bind, 3, 2)

        wj_down = QLabel()
        wj_down.setAlignment(Qt.AlignLeft)
        wj_down.setText(lang['down'])
        wj.layout.addWidget(wj_down, 4, 0)

        wj_down_current = QLineEdit()
        wj_down_current.setAlignment(Qt.AlignCenter)
        wj_down_current.setText(bindings['wj_down_device'] + " - " + bindings['wj_down_button'])
        wj_down_current.setReadOnly(True)
        wj.layout.addWidget(wj_down_current, 4, 1)

        wj_down_bind = QPushButton()
        wj_down_bind.setText(lang['bind'])
        wj.layout.addWidget(wj_down_bind, 4, 2)

        wj_switch = QLabel()
        wj_switch.setAlignment(Qt.AlignLeft)
        wj_switch.setText(lang['switch'])
        wj.layout.addWidget(wj_switch, 5, 0)

        wj_switch_current = QLineEdit()
        wj_switch_current.setAlignment(Qt.AlignCenter)
        wj_switch_current.setText(bindings['wj_switch_device'] + " - " + bindings['wj_switch_button'])
        wj_switch_current.setReadOnly(True)
        wj.layout.addWidget(wj_switch_current, 5, 1)

        wj_switch_bind = QPushButton()
        wj_switch_bind.setText(lang['bind'])
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

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
