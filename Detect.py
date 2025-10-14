from ultralytics import YOLO
import os
from PIL import Image
import make_tiles
from Signal import ProgressSignals

class Detect:
    def __init__(self, signals: ProgressSignals):
        super().__init__()
        self.signals = signals
        self.Mypices = make_tiles.Tiles()
        self.prog = 0
    def _emit(self, v):
        self.signals.set_value.emit(int(max(0, min(100, v))))
    def detect(self,path):
        try:
            model_path = "C:\\Users\\macar\\PycharmProjects\\1077\\Models\\YOLO11n_B.pt"
            self.Mypices.split_image(path, 5, 6)
            self._emit(10)
            model = YOLO(model_path)
            results = model(self.Mypices.pices)
            self._emit(25)
            j = 0
            for result in results:
                j = j + 1
                if j < 10:
                    filename = f"Resources/result0{j}.png"
                else:
                    filename = f"Resources/result{j}.png"
                total = len(results)
                result.save(filename, labels=False, boxes=True, probs=False)
                self._emit(25 + int(65 * j / max(1, total)))
            filess = os.listdir('Resources/')
            for file in filess:
                image = Image.open(f'Resources/{file}')
                self.Mypices.annotated_pices.append(image)

            self._emit(100)
            return self.Mypices.assemble_image(self.Mypices.annotated_pices, 5, 6)
        except Exception as e:
            return f"Error in {e}"