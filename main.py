# Only needed for access to command line arguments
import sys
import os

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
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
    "wj_up": " Increase: ",
    "wj_down": " Decrease: ",
    "wj_switch": " Switch: ",
    "wj_step": " Step: ",
    "wj_toggle": " Toggle: ",
    "wj_continuous": " " * 17 + " Continuous: ",
    "enabled": "Enabled",
    "disabled": "Disabled",
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
    wj_values['step'] = 1
    wj_values['toggle'] = True
    wj_values['continuous'] = True

init_vars()

os.environ["QT_SCALE_FACTOR"] = "1.5"  # Set scale to 130%

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

        wj_step_label = QLabel()
        wj_step_label.setAlignment(Qt.AlignLeft)
        wj_step_label.setText(lang['wj_step'])
        wj.layout.addWidget(wj_step_label, 1, 0)

        wj_step = QSpinBox()
        wj_step.setFixedSize(38, 20)
        wj_step.setRange(1, 20)
        wj_step.setValue(wj_values['step'])
        wj.layout.addWidget(wj_step, 1, 1)
        
        wj_continuous_label = QLabel()
        wj_continuous_label.setAlignment(Qt.AlignCenter)
        wj_continuous_label.setText(lang['wj_continuous'])
        wj.layout.addWidget(wj_continuous_label, 1, 1)
        
        wj_continuous = QCheckBox()
        wj_continuous.setChecked(wj_values['continuous'])
        wj.layout.addWidget(wj_continuous, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)

        wj_toggle_label = QLabel()
        wj_toggle_label.setAlignment(Qt.AlignLeft)
        wj_toggle_label.setText(lang['wj_toggle'])
        wj.layout.addWidget(wj_toggle_label, 1, 2)

        wj_toggle = QCheckBox()
        wj_toggle.setChecked(wj_values['toggle'])
        wj.layout.addWidget(wj_toggle, 1, 2, alignment=Qt.AlignmentFlag.AlignRight)

        wj_up = QLabel()
        wj_up.setAlignment(Qt.AlignLeft)
        wj_up.setText(lang['wj_up'])
        wj.layout.addWidget(wj_up, 2, 0)

        wj_up_current = QLineEdit()
        wj_up_current.setAlignment(Qt.AlignCenter)
        wj_up_current.setText(bindings['wj_up_device'] + " - " + bindings['wj_up_button'])
        wj_up_current.setReadOnly(True)
        wj.layout.addWidget(wj_up_current, 2, 1)

        wj_up_bind = QPushButton()
        wj_up_bind.setText(lang['bind'])
        wj.layout.addWidget(wj_up_bind, 2, 2)

        wj_down = QLabel()
        wj_down.setAlignment(Qt.AlignLeft)
        wj_down.setText(lang['wj_down'])
        wj.layout.addWidget(wj_down, 3, 0)

        wj_down_current = QLineEdit()
        wj_down_current.setAlignment(Qt.AlignCenter)
        wj_down_current.setText(bindings['wj_down_device'] + " - " + bindings['wj_down_button'])
        wj_down_current.setReadOnly(True)
        wj.layout.addWidget(wj_down_current, 3, 1)

        wj_down_bind = QPushButton()
        wj_down_bind.setText(lang['bind'])
        wj.layout.addWidget(wj_down_bind, 3, 2)

        wj_switch = QLabel()
        wj_switch.setAlignment(Qt.AlignLeft)
        wj_switch.setText(lang['wj_switch'])
        wj.layout.addWidget(wj_switch, 4, 0)

        wj_switch_current = QLineEdit()
        wj_switch_current.setAlignment(Qt.AlignCenter)
        wj_switch_current.setText(bindings['wj_switch_device'] + " - " + bindings['wj_switch_button'])
        wj_switch_current.setReadOnly(True)
        wj.layout.addWidget(wj_switch_current, 4, 1)

        wj_switch_bind = QPushButton()
        wj_switch_bind.setText(lang['bind'])
        wj.layout.addWidget(wj_switch_bind, 4, 2)

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
