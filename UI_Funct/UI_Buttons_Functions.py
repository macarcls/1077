from PyQt6.QtWidgets import QFileDialog, QMainWindow
from PyQt6.QtGui import QPixmap
from storage import MyStorage
from ultralytics import YOLO
from UI_Funct.Main_w_UI import Ui_MainWindow


class UI_func(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.myStorage = MyStorage()
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.open_f_dialog)
        self.pushButton.clicked.connect(self.detect)

    def open_f_dialog(self):
         file_d = QFileDialog()
         file_d.setNameFilter('Images (*.png *.jpg)')
         image, _ = file_d.getOpenFileName()
         if image:
             self.myStorage.file_path = image
         pixmap = QPixmap(image)
         self.label.setPixmap(pixmap)

    def detect(self):
        try:
            model_path = "C:\\Users\\macar\\PycharmProjects\\1077\\Models\\YOLO11n_B.pt"
            img = self.myStorage.file_path
            model = YOLO(model_path)
            results = model([img])

            for result in results:
                boxes = result.boxes  # Boxes object for bounding box outputs
                masks = result.masks  # Masks object for segmentation masks outputs
                keypoints = result.keypoints  # Keypoints object for pose outputs
                probs = result.probs  # Probs object for classification outputs
                obb = result.obb  # Oriented boxes object for OBB outputs
                result.save(filename="result.jpg")  # save to disk
            pixmap = QPixmap("result.jpg")
            self.label.setPixmap(pixmap)
        except:
            print("")
#pyqtgraph