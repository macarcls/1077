from typing import List, Tuple
import pandas as pd

def find_adjacent_cells(markup):
    # Получаем уникальные комбинации индексов
    unique_cells = markup[['row_index', 'col_index']].drop_duplicates()

    # Создаем словарь для хранения соседних ячеек
    adjacent_cells = {}

    for _, (row, col) in unique_cells.iterrows():
        # Определяем соседние ячейки справа и снизу
        right_neighbor = (row, col + 1)
        bottom_neighbor = (row + 1, col)

        # Проверяем, есть ли такие соседи в датафрейме
        neighbors = []
        if ((markup['row_index'] == right_neighbor[0]) & (markup['col_index'] == right_neighbor[1])).any():
            neighbors.append(right_neighbor)
        if ((markup['row_index'] == bottom_neighbor[0]) & (markup['col_index'] == bottom_neighbor[1])).any():
            neighbors.append(bottom_neighbor)

        # Добавляем в словарь, если есть соседи
        if neighbors:
            adjacent_cells[(row, col)] = neighbors

    return adjacent_cells


def find_matching_pairs(invalid_diameter_df, adjacent_cells, tolerance=10):
    matching_pairs = []

    for (row, col), neighbors in adjacent_cells.items():
        for neighbor in neighbors:
            neighbor_row, neighbor_col = neighbor

            if neighbor_row == row + 1 and neighbor_col == col:  # Сосед снизу
                upper_rects = invalid_diameter_df[(invalid_diameter_df['row_index'] == row) &
                                                  (invalid_diameter_df['col_index'] == col) &
                                                  (abs(invalid_diameter_df['ymax'] - 640) <= 2)]
                lower_rects = invalid_diameter_df[(invalid_diameter_df['row_index'] == neighbor_row) &
                                                  (invalid_diameter_df['col_index'] == neighbor_col) &
                                                  (abs(invalid_diameter_df['ymin'] - 0) <= 2)]

                upper_set = set(upper_rects.itertuples(index=False))
                lower_set = set(lower_rects.itertuples(index=False))

                for upper in list(upper_set):
                    for lower in list(lower_set):
                        if abs(upper.xmin - lower.xmin) <= tolerance and \
                                abs(upper.xmax - lower.xmax) <= tolerance:
                            matching_pairs.append(
                                ((upper.xmin, upper.ymin, upper.xmax, upper.ymax, upper.row_index, upper.col_index),
                                 (lower.xmin, lower.ymin, lower.xmax, lower.ymax, lower.row_index, lower.col_index)))
                            upper_set.remove(upper)
                            lower_set.remove(lower)
                            break  # Берем только первую подходящую пару

    return matching_pairs


def merge_rectangles(matching_pairs, cell_size=640):
    merged_rects = []

    for (upper, lower) in matching_pairs:
        uxmin, uymin, uxmax, uymax, urow, ucol = upper
        lxmin, lymin, lxmax, lymax, lrow, lcol = lower

        # Вычисляем площади
        upper_area = (uxmax - uxmin) * (uymax - uymin)
        lower_area = (lxmax - lxmin) * (lymax - lymin)

        # Определяем главный прямоугольник
        if lower_area > upper_area:
            # Главный - нижний
            xmin, ymin = lxmin + (lcol * cell_size), uymin + (urow * cell_size)
            xmax, ymax = lxmax + (lcol * cell_size), lymax + (lrow * cell_size)
        else:
            # Главный - верхний
            xmin, ymin = uxmin + (ucol * cell_size), uymin + (urow * cell_size)
            xmax, ymax = uxmax + (ucol * cell_size), lymax + (lrow * cell_size)

        merged_rects.append((xmin, ymin, xmax, ymax))

    return merged_rects


def find_matching_pairs_right(invalid_diameter_df, adjacent_cells, tolerance=10):
    matching_pairs = []

    for (row, col), neighbors in adjacent_cells.items():
        for neighbor in neighbors:
            neighbor_row, neighbor_col = neighbor

            if neighbor_row == row and neighbor_col == col + 1:  # Сосед справа
                left_rects = invalid_diameter_df[(invalid_diameter_df['row_index'] == row) &
                                                 (invalid_diameter_df['col_index'] == col) &
                                                 (abs(invalid_diameter_df['xmax'] - 640) <= 2)]
                right_rects = invalid_diameter_df[(invalid_diameter_df['row_index'] == neighbor_row) &
                                                  (invalid_diameter_df['col_index'] == neighbor_col) &
                                                  (abs(invalid_diameter_df['xmin'] - 0) <= 2)]

                left_set = set(left_rects.itertuples(index=False))
                right_set = set(right_rects.itertuples(index=False))

                for left in list(left_set):
                    for right in list(right_set):
                        if abs(left.ymin - right.ymin) <= tolerance and \
                                abs(left.ymax - right.ymax) <= tolerance:
                            matching_pairs.append(
                                ((left.xmin, left.ymin, left.xmax, left.ymax, left.row_index, left.col_index),
                                 (right.xmin, right.ymin, right.xmax, right.ymax, right.row_index, right.col_index)))
                            left_set.remove(left)
                            right_set.remove(right)
                            break  # Берем только первую подходящую пару

    return matching_pairs


def merge_rectangles_right(matching_pairs, cell_size=640):
    merged_rects = []

    for (left, right) in matching_pairs:
        l_xmin, l_ymin, l_xmax, l_ymax, l_row, l_col = left
        r_xmin, r_ymin, r_xmax, r_ymax, r_row, r_col = right

        # Вычисляем площади
        left_area = (l_xmax - l_xmin) * (l_ymax - l_ymin)
        right_area = (r_xmax - r_xmin) * (r_ymax - r_ymin)

        # Определяем главный прямоугольник
        if right_area > left_area:
            # Главный - правый
            xmin, ymin = l_xmin + (l_col * cell_size), r_ymin + (r_row * cell_size)
            xmax, ymax = r_xmax + (r_col * cell_size), r_ymax + (r_row * cell_size)
        else:
            # Главный - левый
            xmin, ymin = l_xmin + (l_col * cell_size), l_ymin + (l_row * cell_size)
            xmax, ymax = r_xmax + (r_col * cell_size), l_ymax + (l_row * cell_size)

        merged_rects.append((xmin, ymin, xmax, ymax))

    return merged_rects

def drop_matching_boxes(markup,matching_pairs,matching_pairs_right):
    coords = ["row_index", "col_index", 'xmin', 'ymin', 'xmax', 'ymax']
    coords1 = ['xmin', 'ymin', 'xmax', 'ymax']

    datas_for_delete = []

    for left, right in matching_pairs:
        for (xmin, ymin, xmax, ymax, row_i, col_i) in (left, right):
            gxmin = xmin + col_i * 640
            gymin = ymin + row_i * 640
            gxmax = xmax + col_i * 640
            gymax = ymax + row_i * 640
            datas_for_delete.append((gxmin, gymin, gxmax, gymax))

    for left, right in matching_pairs_right:
        for (xmin, ymin, xmax, ymax, row_i, col_i) in (left, right):
            gxmin = xmin + col_i * 640
            gymin = ymin + row_i * 640
            gxmax = xmax + col_i * 640
            gymax = ymax + row_i * 640
            datas_for_delete.append((gxmin, gymin, gxmax, gymax))

    new_markup = markup[coords].drop_duplicates().reset_index(drop=True)
    for_norm = new_markup.values.tolist()
    norm = []
    for row_i, col_i, xmin, ymin, xmax, ymax in for_norm:

         xmin, ymin = xmin + (col_i * 640), ymin + (row_i * 640)
         xmax, ymax = xmax + (col_i * 640), ymax + (row_i * 640)
         norm.append((xmin,ymin,xmax,ymax))
    data = pd.DataFrame(norm, columns=coords1)
    # Создаем DataFrame для удаления
    to_remove_df = pd.DataFrame(datas_for_delete, columns=coords1).drop_duplicates()

    # Фильтруем new_markup, удаляя строки, совпадающие с to_remove_df
    mask = ~data.apply(lambda row: ((to_remove_df['xmin'] == row['xmin']) &
                                          (to_remove_df['ymin'] == row['ymin']) &
                                          (to_remove_df['xmax'] == row['xmax']) &
                                          (to_remove_df['ymax'] == row['ymax'])).any(), axis=1)
    filtered_markup = data[mask].reset_index(drop=True)
    filtered_markup = filtered_markup.values.tolist()
    return filtered_markup