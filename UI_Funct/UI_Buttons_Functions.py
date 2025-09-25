from PyQt6.QtWidgets import QFileDialog, QMainWindow
from PyQt6.QtGui import QPixmap
from UI_Funct.Main_w_UI import Ui_MainWindow


class UI_func(QMainWindow, Ui_MainWindow):
    path = ""
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.open_f_dialog)

    def open_f_dialog(self):
         file_d = QFileDialog()
         file_d.setNameFilter('Images (*.png *.jpg)')
         image, _ = file_d.getOpenFileName()
         if image:
             UI_func.path = image
             print(image)
         pixmap = QPixmap(image)
         self.label.setPixmap(pixmap)
#pyqtgraph