from PyQt6.QtCore import QObject, pyqtSignal

class ProgressSignals(QObject):
    set_visible = pyqtSignal(bool)
    set_value = pyqtSignal(int)