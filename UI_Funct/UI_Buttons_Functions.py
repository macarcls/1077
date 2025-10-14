# библиотеки
import os
from PIL import Image
from PyQt6.QtWidgets import QFileDialog, QMainWindow
from PyQt6.QtGui import QPixmap

import asyncio
from qasync import asyncSlot

# рукописные классы
from storage import MyStorage
from UI_Funct.Main_w_UI1 import Ui_MainWindow
from Detect import Detect
from Signal import ProgressSignals


class UI_func(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.myStorage = MyStorage()
        self.setupUi(self)
        self.pushButton_5.clicked.connect(self.open_f_dialog)
        self.pushButton_6.clicked.connect(self.detect_UI)
        self.pushButton_4.clicked.connect(self.Save)
        self.signals = ProgressSignals()
        self.signals.set_visible.connect(self.progressBar.setVisible)
        self.signals.set_value.connect(self.progressBar.setValue)
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)
        self.detector = Detect(self.signals)

    def open_f_dialog(self):
         file_d = QFileDialog()
         file_d.setNameFilter('Images (*.png *.jpg)')
         image, _ = file_d.getOpenFileName()
         if image:
             self.myStorage.file_path = image
         pixmap = QPixmap(image)
         self.label.setPixmap(pixmap)
    @asyncSlot()
    async def detect_UI(self):
        path = getattr(self.myStorage, "file_path", None)
        if not path:
            return
        try:
            # показать и сбросить прогресс
            self.signals.set_visible.emit(True)
            self.signals.set_value.emit(0)

            # выполнить синхронный detect в фоне, чтобы не блокировать UI
            result = await asyncio.to_thread(self.detector.detect, path)

            if result and os.path.exists(result):
                pixmap = QPixmap(result)
                if not pixmap.isNull():
                    self.label.setPixmap(pixmap)
        except Exception as e:
            print("detect error:", e)
        finally:
            self.signals.set_visible.emit(False)

    def Save(self):
        pixmap = QPixmap("")
        self.label.setPixmap(pixmap)

        os.remove("Resources/result.jpg")
#pyqtgraph