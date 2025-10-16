from ultralytics import YOLO
import os
import pandas as pd
from PIL import Image, ImageDraw
import make_tiles
from Signal import ProgressSignals
from Tracker import find_adjacent_cells, find_matching_pairs, merge_rectangles, \
    find_matching_pairs_right, merge_rectangles_right, drop_matching_boxes
from typing import List, Tuple

class Detect:
    def __init__(self, signals: ProgressSignals):
        super().__init__()
        self.signals = signals
        self.Mypices = make_tiles.Tiles()
        self.prog = 0
    def _emit_abs(self, v):
        self.signals.set_value.emit(int(max(0, min(100, v))))

    def _draw_boxes(self, image_path: str, boxes: List[Tuple[int, int, int, int]], out_path: str) -> str:
        """Нарисовать прямоугольники (xmin,ymin,xmax,ymax) на изображении и сохранить."""
        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        for (x1, y1, x2, y2) in boxes:
            draw.rectangle([x1, y1, x2, y2], outline=(255, 0, 0), width=3)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        img.save(out_path)
        return out_path

    def detect(self, path: str) -> str | None:
        """
        Детект по тайлам + сборка + объединение боксов, пересекающих границы тайлов,
        с помощью функций из Tracker.py. Возвращает путь к финальному изображению.
        """
        try:
            if not path or not os.path.exists(path):
                raise FileNotFoundError("Input image not found")

            out_dir = "Resources"
            os.makedirs(out_dir, exist_ok=True)

            # Параметры сетки (должны совпадать с тем, как режете изображение)
            rows, cols = 5, 6
            cell_size = 640

            # --- 1) Разрезаем изображение на тайлы
            self._emit_abs(0)
            self.Mypices.annotated_pices = []  # на всякий случай очистим
            self.Mypices.split_image(path, rows, cols)
            self._emit_abs(10)

            # --- 2) Загружаем модель и делаем инференс по каждому тайлу
            model_path = r"C:\Users\macar\PycharmProjects\1077\Models\YOLO11n_B.pt"
            model = YOLO(model_path)
            results = model(self.Mypices.pices)
            self._emit_abs(25)

            # --- 3) Сохраним аннотированные тайлы (как и раньше) и накопим детекции в DataFrame
            data = []  # строки для invalid_diameter_df
            total = len(results)
            for idx, result in enumerate(results, start=1):
                # индексы ячейки в сетке
                tile_index = idx - 1
                r = tile_index // cols
                c = tile_index % cols

                # Собираем боксы в локальных координатах тайла
                # (Ultralytics: result.boxes.xyxy -> [N,4], .conf -> [N], .cls -> [N])
                if result.boxes is not None and len(result.boxes) > 0:
                    xyxy = result.boxes.xyxy.cpu().numpy()
                    conf = result.boxes.conf.cpu().numpy()
                    cls = result.boxes.cls.cpu().numpy()
                    for (xmin, ymin, xmax, ymax), cf, cl in zip(xyxy, conf, cls):
                        data.append({
                            "row_index": r,
                            "col_index": c,
                            "xmin": float(xmin),
                            "ymin": float(ymin),
                            "xmax": float(xmax),
                            "ymax": float(ymax),
                            "confidence": float(cf),
                            "class": int(cl),
                        })

                # Сохраняем картинку тайла с боксами (как у вас было)
                filename = os.path.join(out_dir, f"result{idx:02d}.png")
                # В разных версиях Ultralytics сигнатуры сохранялок отличаются.
                # Если .save(...) ругнётся — можно заменить на:
                #   ann = result.plot(); Image.fromarray(ann[:, :, ::-1]).save(filename)
                #result.save(filename, labels=False, boxes=True, probs=False)

                self._emit_abs(25 + int(60 * idx / max(1, total)))

            # --- 4) Составляем список аннотированных тайлов и собираем большое изображение
            filess = os.listdir('Resources/')
            for file in filess:
                image = Image.open(f'Resources/{file}')
                self.Mypices.annotated_pices.append(image)
            #self.Mypices.assemble_image(self.Mypices.annotated_pices, rows, cols)
            # assemble_image может вернуть PIL.Image или путь — поддержим оба случая
            assembled_path = r'C:\Users\macar\PycharmProjects\1077\Test_im\0019.jpg'
            # --- 5) Подготовим данные для трекинга через границы тайлов
            invalid_diameter_df = pd.DataFrame(data, columns=["row_index", "col_index", "xmin", "ymin", "xmax", "ymax",
                                                              "confidence", "class"])

            # Если нужно трекать не все классы — здесь можно отфильтровать:
            # invalid_diameter_df = invalid_diameter_df[invalid_diameter_df["class"] == <id_нужного_класса>]

            # markup_df — просто список существующих ячеек (по детекциям); можно и полную сетку
            if len(invalid_diameter_df) > 0:
                markup_df = invalid_diameter_df[["row_index", "col_index"]].drop_duplicates().reset_index(drop=True)
            else:
                # Если детекций нет — соберём полную сетку, чтобы функции не падали
                markup_df = pd.DataFrame([(r, c) for r in range(rows) for c in range(cols)],
                                         columns=["row_index", "col_index"])

            # --- 6) Находим соседей и пары по нижней/правой границе
            adjacent = find_adjacent_cells(markup_df)

            matching_bottom = find_matching_pairs(invalid_diameter_df, adjacent, tolerance=10)
            merged_bottom = merge_rectangles(matching_bottom, cell_size=cell_size)

            matching_right = find_matching_pairs_right(invalid_diameter_df, adjacent, tolerance=10)
            merged_right = merge_rectangles_right(matching_right, cell_size=cell_size)
            normalized = drop_matching_boxes(invalid_diameter_df,matching_bottom,matching_right)
            merged_global_boxes = merged_bottom + merged_right  # список (xmin,ymin,xmax,ymax) в глобальных координатах
            data_for_draw = normalized + merged_global_boxes
            # --- 7) Рисуем объединённые боксы поверх собранного изображения
            result_tracked_path = os.path.join(out_dir, "result_tracked1.png")
            if merged_global_boxes:
                self._draw_boxes(assembled_path, data_for_draw, result_tracked_path)
                out_path = result_tracked_path
            else:
                # если нечего рисовать, вернём просто собранную картинку
                out_path = assembled_path

            self._emit_abs(100)
            return out_path

        except Exception as e:
            # Желательно логировать e
            print("Detect error:", e)
            return None