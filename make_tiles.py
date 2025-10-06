from PIL import Image

class Tiles:
    def __init__(self):
        self.pices = []
        self.annotated_pices = []
    def split_image(self, image_path, rows, cols):
        """
        Делит изображение на rows x cols кусочков.
        Возвращает список кусочков (PIL.Image).
        """

        img = Image.open(image_path)
        crinp = img.crop((0, 0, 3840, 3200))
        width, height = crinp.size
        piece_width = width // cols
        piece_height = height // rows
        for row in range(rows):
            for col in range(cols):
                left = col * piece_width
                upper = row * piece_height
                right = left + piece_width
                lower = upper + piece_height
                box = (left, upper, right, lower)
                piece = crinp.crop(box)
                #piece.save(f'tiled_image/tile{row}_{col}.png')
                self.pices.append(piece)
    #    return pieces

    def assemble_image(self, pieces, rows, cols):
        """
        Собирает изображение из кусочков pieces в сетку rows x cols.
        Возвращает итоговое изображение (PIL.Image).
        """
        piece_width, piece_height = 640, 640
        assembled_img = Image.new('RGB', (3840, 3200))

        for i, piece in enumerate(pieces):
            x = (i % cols) * piece_width
            y = (i // cols) * piece_height
            assembled_img.paste(piece, (x, y))
        assembled_img.save('assembled.png')
    #    return assembled_img
