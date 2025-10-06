# библиотеки
import os
from PIL import Image
from PyQt6.QtWidgets import QFileDialog, QMainWindow
from PyQt6.QtGui import QPixmap
from ultralytics import YOLO
import asyncio
from qasync import asyncSlot

# рукописные классы
from storage import MyStorage
from UI_Funct.Main_w_UI1 import Ui_MainWindow
import make_tiles


class UI_func(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.myStorage = MyStorage()
        self.Mypices = make_tiles.Tiles()
        self.setupUi(self)
        self.pushButton_5.clicked.connect(self.open_f_dialog)
        self.pushButton_6.clicked.connect(self.detect)
        self.pushButton_4.clicked.connect(self.Save)
        self.progressBar.setValue(self.myStorage.prog_bar_value)
        self.progressBar.setVisible(False)

    def open_f_dialog(self):
         file_d = QFileDialog()
         file_d.setNameFilter('Images (*.png *.jpg)')
         image, _ = file_d.getOpenFileName()
         if image:
             self.myStorage.file_path = image
         pixmap = QPixmap(image)
         self.label.setPixmap(pixmap)

    @asyncSlot()
    async def detect(self):
        try:
            await self.setvis()
            model_path = "C:\\Users\\macar\\PycharmProjects\\1077\\Models\\YOLO11n_B.pt"
            self.Mypices.split_image(self.myStorage.file_path, 5, 6)
            await self.addProgress(10)
            model = YOLO(model_path)
            results = model(self.Mypices.pices)
            await self.addProgress(15)
            j = 0
            for result in results:
                j = j + 1
                if j < 10:
                    filename = f"Resources/result0{j}.png"
                else:
                    filename = f"Resources/result{j}.png"
                result.save(filename, labels=False, boxes=True, probs=False)
                await self.addProgress(1)
            filess = os.listdir('Resources/')
            for file in filess:
                image = Image.open(f'Resources/{file}')
                self.Mypices.annotated_pices.append(image)
                await self.addProgress(1)
            self.Mypices.assemble_image(self.Mypices.annotated_pices, 5, 6)
            await self.addProgress(15)
            pixmap = QPixmap('assembled.png')
            self.label.setPixmap(pixmap)
        except:
            return "ERROR"
    async def addProgress(self, proc):
        self.myStorage.prog_bar_value += proc
        self.progressBar.setValue(self.myStorage.prog_bar_value)
        await asyncio.sleep(0.01)
    async def setvis(self):
        self.progressBar.setVisible(True)
        await  asyncio.sleep(0.01)
    def Save(self):
        pixmap = QPixmap("")
        self.label.setPixmap(pixmap)

        os.remove("Resources/result.jpg")
#pyqtgraph