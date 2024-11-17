from pdf2image import convert_from_path
from PIL import Image
import numpy as np
from datetime import datetime


class Finder:
    
    def find_rectangle(self, pdf_path: str) -> None:
        binary_matrices = self.__pdf_to_binary_matrix(pdf_path)
        print("The image was converted to binary")

        new_image_name = "output" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.__highlight_largest_rectangle(binary_matrices[0], new_image_name)
        print(f"The image with the colored rectangle was saved with the name {new_image_name}")


    def __pdf_to_binary_matrix(self, pdf_path: str, dpi: int = 200, threshold: int = 128) -> list:
        """
        Return a binary matrix with 1 - black pixel, 0 - while pixel for the bottom right corner of the pdf
        """
        pages = convert_from_path(pdf_path, dpi=dpi)
        binary_matrices: list = []

        for page in pages:
            width, height = page.size
            right_bottom_region = page.crop((width // 2, height // 2, width, height))
            grayscale_image = right_bottom_region.convert("L")
            binary_image = np.array(grayscale_image) < threshold
            binary_matrix = binary_image.astype(int)
            binary_matrices.append(binary_matrix)

        return binary_matrices

    def __find_largest_rectangle(self, binary_matrix: list) -> tuple:
        rows, cols = binary_matrix.shape
        heights = [0] * cols
        max_area = 0
        max_rectangle = (0, 0, 0, 0)  # top_left_y, top_left_x, bottom_right_y, bottom_right_x

        for row in range(rows):
            # Actualizăm înălțimea fiecărei coloane în funcție de rândul curent
            for col in range(cols):
                heights[col] = heights[col] + 1 if binary_matrix[row, col] == 1 else 0

            # Găsim cel mai mare dreptunghi din histograma curentă de înălțimi
            stack = []
            for col in range(cols + 1):
                while stack and (col == cols or heights[col] < heights[stack[-1]]):
                    h = heights[stack.pop()]
                    w = col if not stack else col - stack[-1] - 1
                    area = h * w
                    if area > max_area:
                        max_area = area
                        top_left_y = row - h + 1
                        top_left_x = stack[-1] + 1 if stack else 0
                        bottom_right_y = row
                        bottom_right_x = col - 1
                        max_rectangle = (top_left_y, top_left_x, bottom_right_y, bottom_right_x)
                stack.append(col)

        return max_rectangle

    def __highlight_largest_rectangle(self, binary_matrix: list, filename: str) -> None:
        top_left_y, top_left_x, bottom_right_y, bottom_right_x = self.__find_largest_rectangle(binary_matrix)
        height, width = binary_matrix.shape
        color_image = Image.new("RGB", (width, height), (255, 255, 255))

        # Colorează doar cel mai mare dreptunghi în roșu
        for y in range(height):
            for x in range(width):
                if top_left_y <= y <= bottom_right_y and top_left_x <= x <= bottom_right_x:
                    color_image.putpixel((x, y), (255, 0, 0))  # roșu
                elif binary_matrix[y, x] == 1:
                    color_image.putpixel((x, y), (0, 0, 0))  # negru pentru alte valori de 1
                else:
                    color_image.putpixel((x, y), (255, 255, 255))  # alb

        color_image.save(filename)
